"""
The yoda_factories module contains three main components in the middle of the data flow, sitting between the high level steering
in :class:`contur.factories.Depot` class and the lower level statistics in the :class:`contur.factories.Likelihood` class
"""

import os
import re
from io import StringIO

from joblib import Parallel

import contur
import contur.factories.test_observable
import contur.config.config as cfg
import contur.data.static_db as cdb
import contur.util.file_readers as cfr
import contur.util.utils as cutil
from contur.data.build_covariance import CovarianceBuilder

import rivet
import yoda
import yoda.plotting
import yoda.plotting.utils
import numpy as np

def mkConturFriendlyScatter(ao,mkthy=False):
    # send it a binned estimate, and it will make a scatter that contur can deal with.
    # takes care of cases where overflow/underflow bins may have useful measurements,
    # retain the useful ones (assigning an arbitrary bin width for display purposes)
    # and delete any unused ones.

    # if being used to make the SM theory (mkthy=True), then for measurements where one or more of the
    # overflow bins are useful, it will simply pass both through
    
    ana, hist = cutil.splitPath(ao.path())
    path = "/" + ana + "/" + hist

    over  = cdb.use_overflow(path)
    under = cdb.use_underflow(path)

    # if this is a 2D estimate (likely a covariance or correlation matrix) mask
    # off the underflow pr overflow bin if only the other is being used
    if ao.type() == "Estimate2D" and not mkthy:
        if over and not under:
            ao.maskSlice(0,0)
            ao.maskSlice(1,0)
        elif under and not over:
            ao.maskSlice(0,ao.numBinsX()-1)
            ao.maskSlice(1,ao.numYinsY()-1)

    # make the scatter
    scatter = yoda.plotting.utils.mkPlotFriendlyScatter(ao,includeOverflows=(over or under),includeMaskedBins=False)
    
    # if making SM predictions, that's all.
    if mkthy: return scatter

    # for 2D scatters, the slice masking did the trick.
    if ao.type() == "Estimate2D": return scatter

    # if we don't care about underflows and overflows, we're done.
    if not (over or under): return scatter
    
    if not under:
        # not using underflow bin, so remove it
        scatter.rmPoint(0)

    if not over:
        # not using overflow bin, so remove it
        scatter.rmPoint(scatter.numPoints()-1)

    if over:
        # overwrite the inf x values
        # get point and the adjacent point.
        p1 = scatter.point(scatter.numPoints()-1)
        p2 = scatter.point(scatter.numPoints()-2)
        try:
            p1.setXErrs(p2.xErrs())
        except TypeError:
            cfg.contur_log.error("YODA problem worked around... carry on.")
            p1.setXErrs(p2.xErrs()[0],p2.xErrs()[1])
        p1.setX(p2.x()+2*p2.xErrs()[1])

    if under:
        # overwrite the -inf x values
        # get point and the adjacent point.
        p1 = scatter.point(0)
        p2 = scatter.point(1)
        p1.setXErrs(p2.xErrs())
        p1.setX(p2.x()-2*p2.xErrs()[1])

    return scatter

def load_bg_data(path,sm_id="A",smtest=False):
    """
    load the background (THY) and data (REF) for all the observables associated with this rivet analysis
    if smtest then read all SM predictions, if not then only read the default/selected one.
    """
    try:
        ana_id, tag = cutil.splitPath(path)
    except ValueError:
        ana_id = path

    analysis = cdb.get_analysis(ana_id)

    # see if this is analysis that has been selected on the command line
    if not cutil.analysis_select(analysis.name):
        return

    # first the measurement data. This is specified by the shortname, and is all in the same file.
    # check we haven't got it already
    if not (analysis.shortname in cfg.found_ref):

        f = cutil.find_ref_file(analysis)
        cfg.contur_log.debug("Reading data from {}".format(f))
        if len(f)==0:
            cfg.contur_log.error("Cannot find REF data for {}".format(analysis.name))
        else:
            load_ref_aos(f,analysis)
            cfg.found_ref.append(analysis.shortname)

    # now see if there is any SM theory for this. These are specified by the full analysis name including options.
    if (not (analysis.name in cfg.found_thy )) or (smtest) :

        # get this list of predictions for this analysis.
        sm_predictions = cutil.find_thy_predictions(analysis)
        if sm_predictions is None:
            cfg.contur_log.debug("Cannot find SM theory for {}".format(analysis.name))
        else:
            for sm in sm_predictions:
                # selection on prediction ID here
                if sm.id == sm_id:
                    load_sm_aos(sm)
                    cfg.sm_prediction[analysis.name]=sm
                    cfg.found_thy.append(analysis.name)


def load_sm_aos(sm):
    """
    Load the relevant analysis objects (REF or THY) from the file f.

    """

    f = rivet.findAnalysisRefFile(sm.file_name)
    if os.path.isfile(f):
        cfg.contur_log.debug("Reading theory from {}".format(f))
    else:
        cfg.contur_log.error("Could not find {}".format(sm.file_name))
        return

    aos = yoda.read(f)

    for path,ao in aos.items():
        if not rivet.isTheoryPath(path) or path in sm.ao.keys():
            continue

        load_sm_ao(path,ao,sm)

def load_ref_aos(f,analysis):
    """
    Load the relevant analysis objects (REF or THY) from the file f.

    """
    aos = yoda.read(f)

    anas = cdb.get_analyses(analysisid=analysis.shortname)
    for path,ao in aos.items():
        if rivet.isRefPath(path):
            # some gymnastics to filter out histograms we don't need to read (which can be huge)
            # need to make sure we pick up all the appropriate analysis options
            for ana in anas:
                test_path = "/"+ana.name+"/"+ao.name()
                if cdb.validHisto(test_path,filter=False):
                    load_ref_ao(path,ao,aos)
                    break

def load_ref_ao(path, orig_ao, aos):
    """
    Load the ao, with the path=path, into memory, as THY or REF object
    """

    # Find out whether the cross-section has been scaled by some factor (e.g. to area-normalise it)
    # and whether it is a differential in number of events (usually searches), and if so in how many GeV.
    # The latter is only needed if it is an N_events plot with zero uncertainty (again, usually searches),
    # so we can calculate and use the Poisson error from the event number.
    try:
        _isScaled, _scaleFactorData, _nev_differential = cdb.isNorm(orig_ao.path())
    except cdb.InvalidPath:
        raise

    if _isScaled:

        # if we are not running in grid mode, save the original for display purposes only.
        if not cfg.silenceWriter:
            cfg.plotObj[path] = mkConturFriendlyScatter(orig_ao)
        cfg.contur_log.debug("Scaling {}".format(path))
        orig_ao.scale(_scaleFactorData)
        cfg.contur_log.debug("Scaled {}".format(path))
    
    # Convert all types to Scatter2D, including Scatter1Ds
    ao = mkConturFriendlyScatter(orig_ao)
    if ao.dim() > 2:
        cfg.contur_log.debug("Skipping Scatter{}D {}".format(ao.dim(),ao.path()))
        return

    if rivet.isRefPath(path) and not path in cfg.refObj.keys():

        if not _nev_differential==0:
            # root(n) errors on event count histos
            root_n_errors(ao,True,nx=_nev_differential,replace=True)

        # object to build the covariance matrix
        cfg.contur_log.debug("AO TYPE IS {}".format(orig_ao.type()))
        cbuilder = CovarianceBuilder(orig_ao,ao,aos,_isScaled,_scaleFactorData,ignore_corrs=cfg.diag)

        cfg.contur_log.debug("Loading {}".format(path))
        cfg.refObj[path] = ao

        # always fill the unCorr case in case we need it later
        cfg.refUncorr[path] = cbuilder.diagonal
        cfg.refCorr[path] = cbuilder.covM
        cfg.refErrors[path] = cbuilder.errorBreakdown

        # add flat uncertainty
        if cfg.flat_uncertainty is not None and cfg.flat_uncertainty!=0:
            unc = ao.yVals()*cfg.flat_uncertainty
            points = ao.points()
            ao.reset()
            for i, p in enumerate(points):
                p.setYErrs(unc[i])
                ao.addPoint(p)
            cfg.refUncorr[path] += np.diag(unc*unc)
            cfg.refCorr[path] += np.diag(unc*unc)

#        cfg.contur_log.warn("cov matrix for {}".format(ao.path()))
#        cfg.contur_log.warn("{}".format(cbuilder.covM))
#        cfg.contur_log.warn("{}".format(cbuilder.diagonal))
#        cfg.contur_log.warn("{}".format(cbuilder.errorBreakdown))
                

def load_sm_ao(path,orig_ao,sm):
    """
    Load the ao, with the path=path, into memory, as THY or REF object
    """

    if not rivet.isTheoryPath(path):
        cfg.contur_log.warning("{} is not a SM theory object".format(path))

    # Convert all types to Scatter2D, including Scatter1Ds
    ao = mkConturFriendlyScatter(orig_ao)
    if ao.dim() > 2:
        cfg.contur_log.debug("Skipping Scatter{}D {}".format(ao.dim(),ao.path()))
        return

    # Find out whether the cross-section has been scaled by some factor (e.g. to area-normalise it)
    # and whether it is a differential in number of events (usually searches), and if so in how many GeV.
    # The latter is only needed if it is an N_events plot with zero uncertainty (again, usually searches),
    # so we can calculate and use the Poisson error from the event number.
    try:
        _isScaled, _scaleFactorData, _nev_differential = cdb.isNorm(path)
    except cdb.InvalidPath:
        raise

    if _isScaled:
        if not cfg.silenceWriter:
            sm.plotObj[path] = ao.clone()
        ao.scale(ao.dim()-1, _scaleFactorData)
    cfg.contur_log.debug("Loading {}".format(path))
    sm.ao[path] = ao

    # Build the covariance object to fill the dictionaries
    # For theory, we will not apply the "minimum number of error sources" criteria.
    # This means the systematics are always assumed correlated, unless the theory
    # correlations switch, or the master correlations switch, turns them off.
    # (or the data has no correlations, in which case we fall back to the single bin method anyway)
    cbuilder = CovarianceBuilder(orig_ao,ao,None,_isScaled,_scaleFactorData,apply_min=False,ignore_corrs=cfg.diag)

    if cbuilder.hasBreakdown:
        if cfg.useTheoryCorr:
            sm.corr[path] = cbuilder.covM
        else:
            sm.corr[path] = cbuilder.diagonal.copy()
        # always fill the unCorr case in case we need it later
#        sm.uncorr[path] = np.diag(sm.corr[path][np.eye(sm.corr[path].shape[0],dtype=bool)])
        sm.uncorr[path] = cbuilder.diagonal

    else:
        sm.uncorr[path] = cbuilder.diagonal
        sm.corr[path] = cbuilder.diagonal.copy()

    # NB don't need to scale the errors again because they were already scaled in the "scale_scatter" step.
    sm.errors[path] = cbuilder.getErrorBreakdown()



def root_n_errors(ao, is_evcount, nx=0.0, lumi=1.0, replace=False):
    """Function to include root(number of expected events) errors in the uncertainties of 2D scatter.

    The uncertainty based on the expected events for the relevant integrated luminosity. This is
    not about MC statistics!

    The minimum uncertainty is one event... we are not doing proper low-stat treatment in tails,
    so this is a conservative fudge.

    :arg ao:
           The ``YODA`` analysis object to be manipulated.
    :type: :class:`YODA.AnalysisObject`

    :arg nx: factor needed to convert to number of events for none-uniform bin widths (<0, not used, ==0, do nothing).
    :type: float

    :arg is_evcount:
           True is the plot is in event numbers. Otherwise assumed to be a differential cross section.
    :type: boolean

    :arg lumi:
           Integrated luminosity used to get event counts from differential cross sections
    :type: float

    :arg replace:
           If True replace the uncertainties. If False (default) add them in quadrature.
    :type: bool

    """


    cfg.contur_log.debug("Adding expected signal stat errors for {}. Evtc={},  Lumi={}, replace={}".format(ao.path(),is_evcount,lumi,replace))

    cfg.contur_log.debug("Before: VALUES {} :\n UNCERTAINTIES {}".format(ao.yVals(),ao.yErrs()))
    try:
        for point in ao.points():

            yup, ydown = point.yErrs()
            if replace and not (yup==0 and ydown==0):
                cfg.contur_log.warning("Overwriting non-zero uncertainty for {}.".format(ao.path()))

            if is_evcount:
                if nx < 0:
                    # all we need is the square root
                    uncertainty = max(np.sqrt(point.y()),1.0)
                else:
                    # plot was presented as a differential number of events with non-constant bin width, need to multiply
                    # by bin width and divide the differential factor.
                    bw = point.xErrs()[0]*2.0
                    if nx > 0:
                        num_events = max(point.y()*bw/nx,1.0)
                        uncertainty = max(nx*np.sqrt(num_events)/bw,1.0)
                    else:
                        cfg.contur_log.warning("nx=0 for event count histo {}. Should not happen.".format(ao.path()))

            else:
                # cross section plots.
                bw = point.xErrs()[0]*2.0
                num_events = max(point.y()*bw*lumi,1.0)
                try:
                    uncertainty = np.sqrt(num_events)/(bw*lumi)
                except:
                    cfg.contur_log.error("Divide by zero. {} has bin width {} and lumi {} val {}.".format(ao.path(),bw,lumi,point.x()))
                    uncertainty = 0

            if replace:
                point.setYErrs(uncertainty,uncertainty)
            else:
                point.setYErrs(np.sqrt(uncertainty**2+yup**2),np.sqrt(uncertainty**2+ydown**2))

        cfg.contur_log.debug("After: VALUES {} :\n UNCERTAINTIES {}".format(ao.yVals(),ao.yErrs()))

    except AttributeError as ate:

        cfg.contur_log.error("No points for {}. {}".format(ao.path(),ate))
        raise

class YodaFactory(object):
    """Class controlling Conturs YODA file processing ability

    This class is initialised from an os path to a ``YODA`` file and
    dresses it by iterating through each ao and wrapping that in an instance of
    :class:`~contur.factories.test_observable.Observable` which encapsulates a YODA analysis object and derives the required
    :class:`~contur.factories.likelihood.Likelihood` block for it. This class then contains
    the aggregated information for all of these instances across the entire ``YODA`` file.

    :param yodaFilePath: Valid :mod:`os.path` filesystem YODA file location
    :type yodaFilePath: ``string``

    """

    def __init__(self, yodaFilePath):

        self.yodaFilePath = yodaFilePath

        self._likelihood_blocks = []
        self.observables = []
        self.__get_likelihood_blocks()


    def __get_likelihood_blocks(self):
        """
        Private function to collect all of the conturBuckets from a YODA file

        These are not combined, to each block contains all stat_types

        :Built variables:
        * **conturBuckets** (:class:`contur.block`) --
          List of all conturBuckets created from YODA file
        """

        mc_histos, x_sec, nev = cfr.get_histos(self.yodaFilePath)
        if mc_histos is None or len(mc_histos)==0:
            return
        
        self.num_events = nev.numEntries()

        yodaFilesDict = {}

        # read in the config file (once per beam energy, or every time if we don't know the beam energy)
        try:
            beam = self.yodaFilePath.split("/")[-3]
        except:
            beam = 'unknown'

        if beam == 'unknown' or not beam in cfg.config_read_for_beams:
            cfg.contur_log.info("Reading config file {}".format(cfg.config_file))
            cfr.read_config_file(cfg.config_file, mc_histos.keys())
            
            cfg.config_read_for_beams.append(beam)
            cfg.contur_log.debug(f'read config file, now cfg.config_read_for_beams = {cfg.config_read_for_beams}')

        for histopath, orig_ao in cutil.progress_bar(mc_histos.items(), total=len(mc_histos)):

            if cdb.validHisto(histopath):
                # get the theory prediction to use 
                ana = cutil.splitPath(histopath)[0]
                try:
                    id = cfg.sm_prediction_choices[ana]
                except KeyError:
                    cfg.contur_log.error("No prediction chosen for {}. Trying A".format(ana))
                    cfg.sm_prediction_choices[ana]="A"
                    id = "A"
                    
                # now load the REF and SM THY info for this analysis, if not already there.
                load_bg_data(histopath,sm_id=id)

                ao =  mkConturFriendlyScatter(orig_ao)
            
                observable = contur.factories.test_observable.Observable(ao, x_sec, nev)

                # if we are running on theory only, require it exists.
                if (observable._ref is not None) and not (observable._theoryComp and observable._thy is None):

                    cfg.contur_log.debug("Processed measurement {}".format(observable.signal.path()))
                    self._likelihood_blocks.append(observable._likelihood)
                    self.observables.append(observable)

        # we cannot pickle yoda objects so we just declare them in this scope when we are scrubbing the yodafile
        del mc_histos, x_sec, nev

    def __repr__(self):
        return "{} with {} blocks".format(self.__class__.__name__, len(self._likelihood_blocks))

