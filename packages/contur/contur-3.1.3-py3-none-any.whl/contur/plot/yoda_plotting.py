# -*- python -*-

"""
Functions to deal with plotting yoda/rivet histograms

"""
import os
import contur
import contur.config.config as cfg
import contur.factories.likelihood as lh
import contur.util.utils as cutil
from rivet import stripOptions, getAnalysisPlotPaths
import rivet.plotting.make_plots as rivet_make_plots


def createYODAPlotObjects(observable, nostack=False, smtest=False):
    """
    Make YODA objects for theory, theory+BSM and/or data+BSM and return in-memory objects
    in a dictionary.

    :param observable: dressed YODA ao
    :type observable: :class:`contur.factories.Observable`

    :param nostack: flag saying whether to plot data along or stack it on the background (default)
    :type boolean:

    :param smtest: flag saying whether we are doing a SM comparison or the more usual SM+BSM.
    :type boolean:

    the output directory is determined by cfg.plot_dir

    """
    CLs = {}
    YODAinMemory = {}

    histopath = observable.signal.path()
    ## Check if we have reference data for this observable. If not, then abort.
    if not observable.ref:
        cfg.contur_log.warning("No REF data for {}. Not writing dat file. ".format(observable.signal.path()))
        return

    # placeholders to include yoda strings later
    yodastr_sigback_databg = yodastr_theory = yodastr_sigback_smbg = None

    # do we want to shown the plot with data as background?
    # yes if it the chosen primary statistic, or it this plot has no SM prediction.
    # no, otherwise.
    if (cfg.primary_stat == cfg.databg or observable.thyplot is None) and (not smtest):
        show_databg = True
        if nostack:
            # in this case we are just plotting signal, without stacking it on any background
            sigback_databg  = observable.sigplot
        else:
            sigback_databg = observable.stack_databg
    else:
        show_databg = False

    # get the data and set the legend title.
    refdata = observable._refplot
    refdata.setAnnotation('Title', '{} Data'.format(observable.analysis.experiment()))
    refdata.setAnnotation('RatioPlot', True)
    refdata.setAnnotation('RatioPlotYLabel', 'Ratio to Data')

    # get analysis and histogram name
    ana = observable.analysis.name

    # write data-as-background signal plot 
    if show_databg:
        # set annotations in the YODA object, used later to go on the legend label
        legendLabel = get_legend_label(observable, nostack, cfg.databg)
        sigback_databg.setAnnotation('Title', legendLabel)
        YODAinMemory['Data as BG'] = {histopath : {'0' : sigback_databg}}

    # things we only do if there's a SM prediction.
    if observable.thyplot:

        # get theory histogram
        theory = observable._thyplot.clone()

        # write theory.yoda file, for mpl based plotting
        theory.setPath(theory.path().split("/THY")[1]) # for mpl-based plotting, remove prepending THY in YODA
        YODAinMemory['Theory'] = {histopath : {'0' : theory}}
        
        legendLabel = get_legend_label(observable, nostack, background=cfg.smbg, smtest=smtest)
        if smtest:
            theory.setAnnotation('Title', legendLabel)
        
        # if we want to add SM plus BSM
        if not smtest:
            if nostack:
                sigback_smbg   = observable.sigplot
            else:
                sigback_smbg   = observable.stack_smbg
            sigback_smbg.setAnnotation('Title', legendLabel)
            YODAinMemory['SM as BG'] = {histopath : {'0' : sigback_smbg}}

    return YODAinMemory

def assemble_plotting_data(observable, yodaMCs, config_files=[], plotdirs=[]):
    """
    Contur version of rivet assemble_plotting_data, takes histogram path,
    YODA histograms and rivet references string as input, returns 'outputdict'
    which is the required input for rivet.script_generator

    :param hpath: string referring to the histogram path, normally of the form
        <ANALYSIS>/<OBSERVABLE> where rivet.stripOptions has been used to strip off
        the run mode of the analysis

    :param yodaMCs: dictionary containing MC YODA files, with either theory,
        theory+BSM or data+BSM. Is obtained from createYODAPLOTObjects and looks like:
        yodaMCs = {'Data as BG' : {'<hpath>' : {'0': <YODA 2D scatter>} } }

    :param thisRefYODA: YODA object for reference data

    """

    thisRefYODA = observable._refplot
    hpath = observable.signal.path()
    hbasepath = stripOptions(hpath)


    # find reference data, which is already loaded in config fileg
    refhistos = {hbasepath : thisRefYODA}

    reftitle = thisRefYODA.title()

    # fetch plot options from .plot file for each analysis (e.g. Title, axis labels)
    plotdirs += getAnalysisPlotPaths()
    plotoptions = { }

    # set the title for YODA files to appear in the legend, including the exclusion
    for YODAtype, histogram in yodaMCs.items():
        plotoptions[YODAtype] = {'Title' : histogram[hpath]['0'].annotation('Title') }

    # make output dictionary which is used to write executable python scripts
    return rivet_make_plots._make_output(
            hbasepath, plotdirs, config_files, yodaMCs, refhistos,
            plotoptions, style='default', rc_params={}, mc_errs=False, nRatioTicks=1,
            showWeights=True, removeOptions=True, deviation=True, canvasText=None,
            refLabel = refhistos[hbasepath].title(),
            ratioPlotLabel = refhistos[hbasepath].annotation('RatioPlotYLabel'),
            showRatio=True, verbose=False
          )

def get_legend_label(observable, nostack=cfg.nostack, background="", smtest=False):
    """
    return the figure of merit and an appropriate legend label.

    """

    if smtest:
        legendLabel = ""
    elif background == cfg.databg:
        legendLabel = "BSM+Data "
    elif background == cfg.smbg:
        legendLabel = "BSM+SM "

    # set annotations for the data-as-background signal plot
    if smtest:

        theory = observable.thyplot
    
        if cfg.use_spey:
            mu_lower_limit = observable.likelihood.get_mu_lower_limit(cfg.smbg)
            mu_upper_limit = observable.likelihood.get_mu_upper_limit(cfg.smbg)
            mu_hat = observable.likelihood.get_mu_hat(cfg.smbg)
            if mu_lower_limit is not None and mu_upper_limit is not None:
                indextag = r"{}, \newline $\mu \in$  [{:4.2f}, {:4.2f}] @ 95\% $CL_s$, $\hat\mu={:4.2f}$".format(theory.title(),mu_lower_limit,mu_upper_limit,mu_hat)
            else:
                indextag=r"{}, \newline not fitted".format(theory.title())

        else:
            # Calculate the compatibility between SM and data, using chi2 survival for the number of points
            pval = observable.get_sm_pval()
            try:
                indextag="{}, p = {:4.2f}".format(theory.title(),pval)
            except TypeError:
                indextag="{}, p value not found".format(theory.title())

        legendLabel += indextag
        
        return legendLabel

    else:

        if observable.thyplot:

            # things we only do if there's a SM prediction.
            if cfg.use_spey:
                mu_lower_limit = observable.likelihood.get_mu_lower_limit(cfg.smbg)
                mu_upper_limit = observable.likelihood.get_mu_upper_limit(cfg.smbg)
                excl = observable.likelihood.getCLs(cfg.smbg)

                mu_lower_limit_exp = observable.likelihood.get_mu_lower_limit(cfg.expected)
                mu_upper_limit_exp = observable.likelihood.get_mu_upper_limit(cfg.expected)
                excl_exp = observable.likelihood.getCLs(cfg.expected)

                if all(x is not None for x in (mu_lower_limit,mu_lower_limit_exp,mu_upper_limit,mu_upper_limit_exp)):
                    if observable.likelihood._index is not None and cfg.smbg in observable.likelihood._index.keys():
                        indextag = r"Bin {},".format(observable.likelihood._index[cfg.smbg])
                    else:
                        indextag = ""

                        # indextag += r"$\mu \in$ [{:4.2f}, {:4.2f}] @ 95\% $\text{{CL}}_\text{{s}}$, $\hat\mu$ = {:4.2f} \newline (expected $\mu \in$ [{:4.2f}, {:4.2f}] @ 95\% $\text{{CL}}_\text{{s}}$, $\hat\mu$ = {:4.2f})".format(mu_lower_limit,mu_upper_limit,mu_hat,mu_lower_limit_exp,mu_upper_limit_exp,mu_hat_exp)
                    indextag += r"$\mu \in$ [{:3.1f}, {:3.1f}] @ 95\% $\text{{CL}}_\text{{s}}$, $\mu=1$ excl. {:3.1f}\% \newline (expected $\mu \in$ [{:3.1f}, {:3.1f}] @ 95\% $\text{{CL}}_\text{{s}}$, $\mu=1$ excl. {:3.1f}\%".format(mu_lower_limit,mu_upper_limit,100.*excl,mu_lower_limit_exp,mu_upper_limit_exp,100.*excl_exp)


                elif mu_lower_limit_exp is not None and mu_upper_limit_exp is not None:
                    indextag = r"No limits; expected $\mu \in$ [{:3.1f}, {:3.1f}] @ 95\% $\text{{CL}}_\text{{s}}$, $\mu = 1$ disfavoured at {:3.1f}\%".format(mu_lower_limit_exp,mu_upper_limit_exp,excl_exp)

                elif excl is not None and excl > 0.0:
                    indextag = "$\mu = 1$ disfavoured at {:3.1f}\%".format(100.*excl)
                else:
                    indextag = "No exclusion"

            else:
                
                # get the dominant test likelihood for this plot.
                CLs = observable.likelihood.getCLs(cfg.smbg)
                CLs_exp = None
                if cfg.expected in cfg.stat_types:
                    CLs_exp = observable.likelihood.getCLs(cfg.expected)

                # add them to the legend.
                if CLs is not None and CLs > 0:
                    if observable.likelihood._index is not None and cfg.smbg in observable.likelihood._index.keys():
                        indextag=r"Bin {},excl. {:2.0f}\%".format(observable.likelihood._index[cfg.smbg],100.*CLs)
                    else:
                        indextag=r"excl. {:2.0f}\%".format(100.*CLs)
                    if CLs_exp is not None:
                        indextag += r"\newline ({:2.0f}\% expected)".format(100.*CLs_exp)
                elif CLs_exp is not None:
                    indextag=r"No exclusion; expected exclusion was {:2.0f}\%".format(100.*CLs_exp)
                else:
                    indextag="No exclusion"

            # set annotations for the sm-as-background signal plot
            legendLabel += indextag

    return legendLabel

