
import rivet

import sys
import os
import shutil
import pickle
import logging
import yoda
import math
import matplotlib
import matplotlib.pyplot as pyp
matplotlib.use('Agg')

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

from multiprocessing import Pool, cpu_count

import contur
import contur.config.config as cfg
import contur.config.paths
import contur.data.static_db as cdb
import contur.factories.likelihood as lh
import contur.factories.yoda_factories
import contur.factories.test_observable
import contur.util.utils as cutil
import contur.util.file_readers as cfr
from contur.plot.html_utils import writeAnaHTML, writeAlistHTML
from contur.run.arg_utils import setup_stats, setup_common, setup_selection

import contur.plot.yoda_plotting as cplot
from yoda.plotting import script_generator

def fake_thy_paths(ana,aos):
    '''
    make thy paths read from a file look like generated signal yoda paths for analysis ana.
    '''

    for ao in aos.values():

        old_ana, hname = cutil.splitPath(ao.path())

        new_path = "/"+ana + "/" + hname
        ao.setPath(new_path)


def main(args):
    '''
    arguments should be passed as a dictionary.
    '''

    #    cfg.setup_logger(filename=args['LOG'])
    # set up / respond to the common argument flags.
    setup_common(args)
    print("Writing log to {}".format(cfg.logfile_name))

    modeMessage = "Performing SM test \n"
    modeMessage += "Contur is running in {} \n".format(os.getcwd())

    if 'SMPRED' in args and args['SMPRED']:
        cfg.prediction_choice = args['SMPRED']
        modeMessage += "       Using predictions {} \n".format(cfg.prediction_choice)

    modeMessage = setup_stats(args,modeMessage)

    # run on maximum available cores
    numcores = cutil.get_numcores(0)
    numcores = numcores-2
    if numcores == 0: numcores = 1

    cfg.graphics = False
    if args["graphics"] is not None:
        cfg.graphics = args["graphics"]

    if args['ANAPATTERNS']:
        cfg.onlyAnalyses = args['ANAPATTERNS']
        modeMessage += "Only using analysis objects whose path includes %s. \n" % args['ANAPATTERNS']

    if args['ANAUNPATTERNS']:
        cfg.vetoAnalyses = args['ANAUNPATTERNS']
        modeMessage += "Excluding analyses names: %s. \n" % args['ANAUNPATTERNS']

    cfg.contur_log.info(modeMessage)

    cfg.exclude_met_ratio=False
    cfg.exclude_hgg=False
    cfg.exclude_hww=False
    cfg.exclude_b_veto=False
    cfg.exclude_awz=False
    cfg.exclude_searches=False
    cfg.exclude_soft_physics=False
    cfg.tracks_only=False

    # Set the config file
    if cfg.config_file == args['CONFIG']:
        # the user didn't set one, so use the smtest default.
        cfg.config_file = cfg.smtest_config
    else:
        cfg.config_file = args['CONFIG']

    cfg.noStack=True

    cfg.stat_types = [cfg.smbg]

    if args["OUTPUTDIR"] is not None:
        plotdirs = [args["OUTPUTDIR"]]
        cfg.plot_dir = args["OUTPUTDIR"]
    else:
        plotdirs = [cfg.smdir]
        cfg.plot_dir = cfg.smdir

    cfg.contur_log.info("SM plotting scripts will be written to {}".format(plotdirs[0]))

    # to make sure we don't read the same file more than once.
    read_once = []
    aolist= []
    pvalues = {}
    analyses = cdb.get_analyses(filter=False)
    pyScripts = []
    analysis_index_dict = {}
    for analysis in sorted(analyses, key=lambda a: a.poolid):

        plotsOutdir = os.path.join(cfg.plot_dir, analysis.poolid, analysis.name) if not cfg.gridMode else os.path.join(cfg.plot_dir, cfg.runpoint, analysis.poolid, analysis.name)
        cutil.mkoutdir(plotsOutdir)

        ana = analysis.name
        if not cutil.analysis_select(ana):
            continue

        sm_theory = analysis.sm()
        if sm_theory is not None:
            for prediction in sm_theory:

                histoList = []
                excl = {}

                pvfile = "{}.txt".format(prediction.id)

                cfg.contur_log.info("Comparing {} to {}".format(ana,prediction.short_description))
                aos = {}
                try:
                    if prediction.file_name not in read_once:

                        aos = yoda.read(contur.config.paths.data_path("data","Theory",prediction.file_name))
                        read_once.append(prediction.file_name)
                        fake_thy_paths(ana,aos)

                        for orig_thy in aos.values():
                            thy=contur.factories.yoda_factories.mkConturFriendlyScatter(orig_thy)

                            if cdb.validHisto(thy.path()):

                                # now load the REF and SM THY info for this analysis
                                contur.factories.yoda_factories.load_bg_data(thy.path(),prediction.id,smtest=True)

                                hist = contur.factories.test_observable.Observable(thy, None, None, prediction)
                                if hist.pool is None:
                                    continue

                                if cfg.use_spey:

                                    # read in the config file if necessary
                                    if (not hist.signal.path() in cfg.spey_model_config) or not cfg.spey_calculation_config:
                                        cfr.read_config_file(cfg.config_file, [hist.signal.path()])

                                # Note that we treat the SM as signal here, so in the "BSM" input, not the (background) SM one.
                                sm_likelihood = lh.Likelihood(calculate=True,
                                                              ratio=hist._isRatio,
                                                              profile=hist._isProfile,
                                                              lumi=hist._lumi,
                                                              tags=hist.signal.path(),
                                                              sm_values=hist.get_zero_values(),
                                                              bsm_values=hist.sm_values,
                                                              measured_values=hist.measured_values,smtest=True)

                                hist.likelihood = sm_likelihood

                                # write the python scripts for plotting
                                if hist.thyplot is not None:
                                    thypath = thy.path()
                                    hpath = thypath+"_"+prediction.id
                                    h_name = hpath.split("/")[2]
                                    histoList.append(h_name)

                                    # get YODA objects for BSM + SM, theory and data + BG
                                    thisPathYodaFiles = cplot.createYODAPlotObjects(hist, nostack=cfg.nostack, smtest=True)

                                    # get plot contents, pass YODA dict and reference data YODA object.
                                    plotContents = cplot.assemble_plotting_data(hist, thisPathYodaFiles)

                                    # create scripts
                                    pyScript = script_generator.process(plotContents, hpath, plotsOutdir.rsplit('/',1)[0], ["PDF", "PNG"])
                                    pyScripts.append((pyScript,""))

                                    name = "{}, {} prediction {}".format(hist.pool, hist._ref.path()[5:], prediction.id)
                                    pv = hist.get_sm_pval()
                                    try:
                                        if math.isnan(pv):
                                            cfg.contur_log.warning("{} has {} p-value".format(name,pv))
                                        else:
                                            pvalues[name] = pv
                                    except TypeError:
                                        cfg.contur_log.warning("{} has no p-value".format(name))

                            else:
                                cfg.contur_log.debug("{} was invalid.".format(thy.path()))
                except:
                    raise

                excl[cfg.smbg] = sm_likelihood.get_sm_pval()
                #print(sm_likelihood.get_mu_upper_limit(cfg.databg),sm_likelihood.get_mu_hat(cfg.databg),
                #      sm_likelihood.get_mu_lower_limit(cfg.databg),sm_likelihood.get_sm_pval())


                if excl[cfg.smbg] is not None:
                    with open(os.path.join(plotsOutdir,pvfile), "w") as file:
                        file.write(str(excl[cfg.smbg]))

                    writeAnaHTML(analysis, excl, plotsOutdir, histoList, prediction=prediction)
                    analysis_index_dict[os.path.join(analysis.poolid,analysis.name,"index{}.html".format(prediction.id))]=(analysis, prediction)

    cfg.contur_log.debug("Theory predictions were read from these files: {}.".format(read_once))

    pvalues = dict(sorted(pvalues.items(), key=lambda x:x[1]))

    probs = []
    pv_cut = 0.05
    cfg.contur_log.info("These distributions have a p value < {}".format(pv_cut))
    for name, value in pvalues.items():

        if name[-1:] == cfg.prediction_choice or cfg.prediction_choice=="ALL":
            probs.append(value)

        if (value < pv_cut) and (cfg.prediction_choice == "ALL" or cfg.prediction_choice == name[-1:]):
            cfg.contur_log.info("Measurement: {}, p-value = {}".format(name,value))

    cfg.contur_log.info("{} distributions were checked.".format(len(pvalues)))

    # make a plot of the more reliable probabilities... should be uniform 0->1 but never is.
    with matplotlib.rc_context({"text.usetex": bool(shutil.which('tex'))}):
      pyp.hist(probs,40,(0,1))
      pyp.ylabel('Frequency')
      pyp.xlabel('p-values')
      plotfile=os.path.join(cfg.plot_dir,"probs.pdf")
      pyp.savefig(plotfile)

    # write a basic index of analysis/prediction index files
    writeAlistHTML(cfg.plot_dir,analysis_index_dict)

    if cfg.graphics:
        cutil.make_mpl_plots(pyScripts,numcores)

def doc_argparser():
    """ wrap the arg parser for the documentation pages """
    from contur.run.arg_utils import get_argparser
    return get_argparser('smtest')

