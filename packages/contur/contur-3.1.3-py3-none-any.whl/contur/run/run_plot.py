""" 
Making plots (heatmap etc) out of database
"""

from inspect import getmembers, isfunction
import importlib

HAVE_INTERACT = False
try:
    import tkinter as tk
    from ttkbootstrap import Style
    from contur.plot.contur_interactivity import Interactivity
    HAVE_INTERACT = True
except ImportError:
    HAVE_INTERACT = False

import matplotlib
#matplotlib.use('Agg')

import contur
import contur.config.config as cfg
import contur.factories.depot
import contur.plot.contur_plot
from contur.run.arg_utils import setup_common
import contur.util.utils as cutil
from contur.util.utils import pairwise
from contur.plot.contur_plot import conturPlot

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import sys, os, pickle
import logging

def load_external_function(file_name):
    """ 
    Load exteral functions for plotting additonal contours, from command line.

    :param file_name: the name of the file containing the functions, with or without a .py extension. can be specified with a (rel or abs) path, otherwise with be assumed to be in the current working directory.


    """   

    if "/" not in file_name:
        directory = os.path.join(".", file_name)

        
    moddir, modfile = os.path.split(file_name)
    modname = os.path.splitext(modfile)[0]

    # Set the import path as needed, and import the module from there
    sys.path.append(moddir)
    i = importlib.import_module(modname)
    store = [o for o in getmembers(i) if isfunction(o[1])]

    # Alphabetically sort this list in place so the colors are consistently trackable
    store.sort(key=lambda v: (v[0].upper(), v[0].islower()))
    cfg.contur_log.info("Imported additional constraints from {}".format(file_name))
    return store

def main(args):
    """
    Main method Executable to make contur/contour plots from database files.
    args should be a dictionary
    """

    print("OUT",cfg.output_dir)
    print(args['OUTPUTDIR'])
    setup_common(args)
    print("OUT2",cfg.output_dir)

    print("Writing log to {}".format(cfg.logfile_name))


    # don't write bytecode, since this isn't CPU intensive
    sys.dont_write_bytecode = True
    
    # Error catching
    parsing_error_msg = ("To call contur-plot you must specify an input file "
                         "and 2 variables to plot!\nThe format must "
                         "follow:\ncontur-plot .db_file x_variable "
                         "y_variable [optional_arguments]")

    # check input file exists
    #cfg.input_dir = args['INPUTDIR']

    if args['interactive_mode'] and HAVE_INTERACT:
       try:
            matplotlib.use('TkAgg')
       except:
            cfg.contur_log.error("Interactive mode was requested, but unable to impot tk interactive framework")
            cfg.contur_log.error("Falling back to static heatmap")
            args['interactive_mode'] = False
            matplotlib.use('Agg')
    else:
        matplotlib.use('Agg')
        
    file_b = args['file'][0]
    file_b = os.path.join(cfg.input_dir,file_b)

    if os.path.exists(file_b):
        file = file_b
    else:
        cfg.contur_log.critical("Input file {} does not  exist!\n\n".format(file_b))
        sys.exit(1)

    cfg.contur_log.info("Looking for map info in {}".format(file))

    # make the output directory, if not already present
    cutil.mkoutdir(cfg.output_dir)
    
    if len(args['variables']) != 2:
        cfg.contur_log.critical("Error parsing arguments!\n\n" + parsing_error_msg)
        sys.exit()

    if len(args["levels"]) > 3:
        cfg.contur_log.critical("Error parsing arguments! --levels takes up to 3 float values")
        sys.exit()

    # Import a module containing grids to define extra contours    
    if args['externalGrid']:
    
    	if len(args['variables']) != 2:
        	cfg.contur_log.critical("Error parsing arguments!\n\n" + parsing_error_msg)
        	sys.exit()

    # Import a module containing grids to define extra contours    
    if args['externalGrid']:
        external_grids=load_external_function(args['externalGrid'])
    # Import a module containing functions to define extra contours    
    if args['externalFunction']:
        external_functions=load_external_function(args['externalFunction'])

    # set the out file format
    cfg.plot_format = args['plot_format']

    # First try reading as a database
    try:

        # Run the conturPlot processing, should allow to read the input db file from command line
        contur_depot = contur.factories.depot.Depot()
        # read the result database into Depot class
        contur_depot.add_points_from_db(file)
        cfg.contur_log.info("Read DB file {}".format(file))

    except Exception as ex:

        cfg.contur_log.info("Could not read {} as db file.".format(args['file']))
        cfg.contur_log.info("Caught exception:{}".format(ex))
        raise

    if args['DATABG']:
        cfg.primary_stat = cfg.databg
    else:
        cfg.primary_stat = cfg.smbg
    
    # create contur plotbase object which extends the contur depot class
    ctrPlot = contur.plot.contur_plot.ConturPlotBase(contur_depot,
                                cfg.output_dir, plotTitle=args['title'],
                                                     savePlotFile=args['save_plots'], omittedPools=args['omit'],
                                                     iLevel=args['ilevel'],iOrder=args['iorder'], iSigma=args['isigma'],
                                                     cpow=args['cpow'], style=args['style'], showcls=args['showcls'],
                                                     simplecls=args['simplecls'],
                                                     show_secondary=args['secondary_contours'], show_exp=not args['NO_EXP'],
                                                     show_hl=args['hl_estimate'],
                                                     interactive_mode=args['interactive_mode'],
                                                     min_cls=args['CLS'],
                                                     show_legend=args['show_legend'])
    
    # tell the plotbase object whether or not we are plotting the separate analysis pool plots
    ctrPlot.do_plot_pools = args['plot_pools']

    # validate plot variables
    plot_x, plot_y = ctrPlot.validate_plot_params(args['variables'])
    levels = ctrPlot.validate_levels(args['levels'])

    # get a slice string if required
    unassigned_slice_params = [x for x in ctrPlot.get_parameters(variables_only=True) if not x in (plot_x,plot_y)]
    slice_prompt = "Enter parameter value pairs for {} in the format: parameter1 value1 parameter2 value2 ... > ".format(unassigned_slice_params)

    if len(unassigned_slice_params) > 0 and args['slice'] == "":
        cfg.contur_log.warning("More than 2 variable parameters found.")
        try:
            if cutil.permission_to_continue("Do you want to specify a slice for {}?".format(unassigned_slice_params)):
                args['slice'] = input(slice_prompt)
        except OSError:
            cfg.contur_log.info("No keyboard input. Assuming the answer is no.")


    
    if args['slice'] != '':
        # validate slice
        while ctrPlot.validate_slice(args['slice'],[plot_x,plot_y]) == False:
            args['slice'] = input(slice_prompt)

        # slice grid
        ctrPlot.slice_grid(args['slice'])

           
    # add the external grids and functions to the plotbase, if present
    if args['externalFunction']:
        ctrPlot.add_external_functions(external_functions)
    if args['externalGrid']:
        ctrPlot.add_external_grids(external_grids)

    interactive=True
    if args['interactive_mode']:

        if HAVE_INTERACT:
            # build the axes
            ctrPlot.build_axes_from_grid(xarg=plot_x, yarg=plot_y, logX=args['xlog'],
                                         logY=args['ylog'],
                                         xlabel=args['xlabel'], ylabel=args['ylabel'])
            inter = Interactivity(ctrPlot, level=0)
            inter.show()

        else:
            print(
                "\nERROR: Interactive plotting requires the following Python packages:\n"
                "  - tkinter\n"
                "  - ttkbootstrap\n"
                "Please install them in your Python environment.\n"
                "Falling back to static heatmap."
            )
            interactive=False

    else:
        interactive=False

    if not interactive:
        
        for plot_metric in cfg.plot_metrics.keys():
            # check plot metric has been generated (check for .db without mu_upper_limit etc.)
            if not ctrPlot.is_plot_metric_valid(plot_metric, file):
                continue
            # build the axes
            ctrPlot.build_axes_from_grid(xarg=plot_x, yarg=plot_y, logX=args['xlog'],
                                         logY=args['ylog'],
                                         xlabel=args['xlabel'], ylabel=args['ylabel'], plot_metric=plot_metric)

            # plot them
            ctrPlot.plot_figures(plot_metric, levels, args['scale'])

    if args['save_plots']:
        # save the plot objects for later matplotlib manipulation
        ctrPlot.dump_plot_objects()

    cfg.contur_log.info("Done")

    

def doc_argparser():
    """ wrap the arg parser for the documentation pages """    
    from contur.run.arg_utils import get_argparser    
    return get_argparser('plot')

