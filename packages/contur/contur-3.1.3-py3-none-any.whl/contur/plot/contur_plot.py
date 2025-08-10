""" main module of heatmap plotting functions

"""

import os
import sys
import shutil
import warnings
import sqlite3
import traceback
import re 

import contur
from contur.plot.axis_labels import get_axis_labels
from contur.factories.depot import Depot
from contur.plot import color_config
import contur.config.config as cfg
import contur.config.paths as paths 
import contur.util.utils as cutil
from contur.util.utils import pairwise
import contur.plot.label_maker as legend
from contur.data.data_access_db import open_for_reading

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.colors as colors
#matplotlib.use('TkAgg')
import copy
import math
import numpy as np
from matplotlib import rcParams
from matplotlib.gridspec import GridSpec
from collections import OrderedDict, defaultdict


import scipy
import matplotlib.colors as mcolors

warnings.filterwarnings("ignore")



def color_tint(col, tintfrac):
    """
    Return a colour as rgb tuple, with a fraction tintfrac of white mixed in
    (or pass a negative tintfrac to mix with black, giving a shade rather than tint
    """
    tintfrac = max(-1.0, min(1.0, tintfrac))
    maincol = mpl.colors.to_rgb(col) if type(col) is str else col
    if tintfrac > 0:
        return (1-tintfrac)*np.array(maincol) + tintfrac*np.array([1., 1., 1.])
    elif tintfrac < 0:
        return (1-abs(tintfrac))*np.array(maincol)
    else:
        return maincol


def get_pool_color(pool, tints=True, cpow=0.1):
    """
    Return the colour for a given analysis pool, optionally tinted
    according to beam energy
    """

    color = None
    for poolGroupName, poolGroup in color_config.POOLCOLORS.items():
        # find pool group
        pools = poolGroup["pools"]
        if pool not in pools:
            continue
        color = poolGroup["color"]
        #tfrac = 0.1*pow(-1, len(pools)) * pools.index(pool) if tints else 0.0
        
        if tints:
            frac = cpow*pow(-1, len(pools))
            tfrac = frac*(pools.index(pool)-(len(pools)-1)/2.0)
        else:
            tfrac = 0.0

    if color is None:
        cfg.contur_log.warn("No pool group found for {}".format(pool))
        color = "whitesmoke"
        tfrac = 0.0
        
    return color_tint(color, tfrac)

    # if we get here, we didn't find a colour for this pool.
    if cfg.map_colorCycle==None:
        cfg.map_colorCycle = iter(color_config.CONTURCOLORS())
    c = next(cfg.map_colorCycle)["color"]

    cfg.contur_log.warning('No colour found for pool {}. Using {}.'.format(pool,c))
    return c

class ConturPlotBase(Depot):
    """
    ConturPlotBase extends the depot class to dress things nicely for plotting, it also contains all the steering
    functions the default plotting macro needs

    .. todo:: a config file based setup to stop the command line argument bloat in the plotting macro
    """

    def __init__(self, conturDepot, outPath, plotTitle="", savePlotFile=False, omittedPools="", iLevel=3, iOrder=3,
                 iSigma=0.75, cpow=0.1, style="DRAFT", showcls=False, simplecls=False,
                 show_secondary=False, show_exp=True, show_hl=False, interactive_mode=False, min_cls=0.68,
                 show_legend=True, base_plot=None):

        # extend from a depot class instance
        self.__dict__.update(conturDepot.__dict__)

        # mapAxis is the true sampled points
        # _bookmapAxis is just for bookkeeping
        self._bookmapAxis = defaultdict(list)
        self._mapAxis = {}
        self._show_secondary = show_secondary
        self._show_exp = show_exp
        self._show_hl = show_hl
        self.min_cls = min_cls

        self.build_axes()

        self.outputPath = outPath

        self.plotList = []
        self.plotTitle = plotTitle
        self.do_plot_pools = True
        self.doSavePlotfile = savePlotFile
        self.omittedPools = omittedPools
        self.iLevel = iLevel
        self.iOrder = iOrder
        self.iSigma = iSigma
        self.cpow = cpow
        self.showcls = showcls
        self.style = style.upper()
        self.simplecls = simplecls
        self.made_cbar = False
        self.interactive_mode = interactive_mode
        self.show_legend = show_legend
        self.base_plot = base_plot

        if self.doSavePlotfile:
            # tell mpl to not worry if we keep a lot of figures open
            rcParams['figure.max_open_warning'] = 100

        self.external_grids = []
        self.alt_grids = []
        self.external_functions=[]
        self.plot_objects = {}

        # Look up table for some convenient default axis labels
        self.axisLabels = get_axis_labels()

    def dump_plot_objects(self):
        """
        Small function to dump a pickle of the plot objects if requested, this is to allow any mpl image manipulation
        without using the contur package at all
        """
        path_out = os.path.join(self.outputPath, 'contur.plot')
        import pickle
        with open(path_out, 'w') as f:
            pickle.dump(self.plot_objects, f)
        cfg.contur_log.info("Writing output plot dict to:", path_out)

    def dump_color_palette_tex(self):
        """
        Function to dump a .tex file containing a LaTeX legend for the dominant pools plots.
        """
        pools = set() # list with unique elements
        anas = {}

        if cfg.offline:
            cfg.contur_log.info("Building colour palette. Running offline so not searching inspire.")
        else:
            cfg.contur_log.info("Building colour palette and bibliography: slow, depending on inspire access.")

        # get pools
        for poolGroupName, poolGroup in color_config.POOLCOLORS.items():                    
            anas[poolGroupName]=set()
            for level, anaNames_level in enumerate(self.poolNames):
                for anaName in anaNames_level:
                    if anaName in poolGroup["pools"]:
                        pools.add(poolGroupName)
                        # get the dominant analysis for each point and for each pool in the dominant pool class
                        for point in self.points:
                            analysis = point.get_dominant_analysis(cfg.primary_stat,poolid=anaName,cls_cut=self.min_cls)
                            if analysis is not None:
                                anas[poolGroupName].add(analysis)                                

        # print latex commands
        tex_output = r"\documentclass{article}" + "\n\n"
        tex_output += r"\usepackage{tikz}" + "\n\n"
        tex_output += r"\DeclareRobustCommand{\swatch}[1]{\tikz[baseline=-0.6ex]"
        tex_output += r"\node[fill=#1,shape=rectangle,draw=black,thick,minimum width=5mm,rounded corners=0.5pt](){};}" + "\n"
        tex_output += r"\newcommand{\MET}{\ensuremath{E_T^{\rm miss}}}" +"\n\n"
        tex_output += r"% color definitions" + "\n"

        bibtex_output = r""
        
        # dump color definitions
        for pool in pools:
            colorName = color_config.POOLCOLORS[pool]["color"]
            colorHex = mpl.colors.to_hex(colorName)[1:] # first char is "#"
            tex_output += r"\definecolor{%s}{HTML}{%s}" % (colorName, colorHex.upper()) + "\n"
            for ana in anas[pool]:
                bibtex_output += r"{}".format(ana.bibtex())
            
        # dump pool colors
        num_cols = 4
        tex_output += "\n" + r"\begin{document}" + "\n"
        tex_output += "    % pool-name legend\n"
        tex_output += "    % Citations are given for any analysis that gives the highest exclusion for any dominant pool anywhere in the plot. Note that if there is no citation, it means that the exclusion for that pool never got above your CLS cut of {})\n".format(self.min_cls)
        tex_output += r"    \begin{tabular}{" + num_cols*"l" + "}\n"

        for num, pool in enumerate(pools):
            colorName = color_config.POOLCOLORS[pool]["color"]
            latexName = color_config.POOLCOLORS[pool]["latexName"]
            tex_output += r"        \swatch{{{}}}~{} \cite{{{}}}".format(colorName, latexName, ",".join([(ana.bibkey()) for ana in anas[pool]]))
            if num % num_cols == num_cols-1:
                tex_output += r" \\"
            else:
                tex_output += r" &"
            tex_output += " \n"

        tex_output += r"    \end{tabular}" + "\n"

        # remove blank cites from text
        tex_output = tex_output.replace(r"\cite{}",r"")
        
        tex_output += r"\bibliography{dominantPoolsLegend}" + "\n"        

        tex_output += r"\end{document}"

        path_out = os.path.join(self.outputPath, "dominantPoolsLegend.tex")
        with open(path_out, 'w') as f:
            f.write(tex_output)

        path_out = os.path.join(self.outputPath, "dominantPoolsLegend.bib")
        with open(path_out, 'w') as f:
            f.write(bibtex_output)
            
    def build_axes_from_grid(self, xarg, yarg, logX=False, logY=False, xlabel=None, ylabel=None, plot_metric='CLs'):
        """
        Function to build the axes out of the underlying map, creates an AxesHolder instance to store the info and pass
        nicely to the plotting engine

        .. todo:: Refactor how we store the grids in general, should just reuse the initial scanning functions to build the space OTF

        """
        try:
            self.check_args(xarg, yarg)
            self.build_grid(xarg, yarg, plot_metric)
            self.xarg = xarg
            self.yarg = yarg
        except cfg.ConturError:
            sys.exit(1)

        if xlabel:
            xlabel = xlabel
        elif xarg in self.axisLabels:
            xlabel = self.axisLabels[xarg]
        else:
            xlabel = xarg

        if ylabel:
            ylabel = ylabel
        elif yarg in self.axisLabels:
            ylabel = self.axisLabels[yarg]
        else:
            ylabel = yarg

        self.build_axes()

        self.axHolder = AxesHolder(xAxis=self.map_axis[xarg], xLabel=xlabel,
                                   xLog=logX, yAxis=self.map_axis[yarg],
                                   yLabel=ylabel, yLog=logY, title=self.plotTitle)


    def plot_figures(self, plot_metric, levels, scale):
        """
        make the various figures
        """

        # First the combined
        plotBase = conturPlot(saveAxes=self.doSavePlotfile, plotTitle=self.plotTitle,
                              iLevel=self.iLevel, iOrder=self.iOrder, iSigma=self.iSigma, cpow=self.cpow,
                              style=self.style, showcls=self.showcls, show_legend=self.show_legend, plot_metric=plot_metric)
        cutil.mkoutdir(self.outputPath)
        cfg.contur_log.info("Starting plotting engine, outputs written to {}".format(self.outputPath))

        plotBase.add_grid(self.conturGrid, "combined",
                          self.outputPath, self.axHolder)
        #if self.external_grids or self.external_functions:
        cfg.contur_log.info("Adding grids {}".format([grid.label for grid in self.alt_grids]))
        plotBase.add_external_data_grids(self.alt_grids, callback=self.reset_alt_grids)

        # Only produce overlay plot UNLESS plot_metric is CLs
        if plot_metric != 'CLs': 
            plotBase.plot_mesh_overlay_mu(plot_metric, levels, scale)
            return
        
        # Plot the mesh with limit-contour overlays
        plotBase.plot_mesh_overlay_cls(plot_metric)
        # Plot the heatmap and levels side-by-side
        plotBase.plot_hybrid()
        # Plot the separated limit contour and mesh plots
        plotBase.plot_mesh(make_cbar=True)
        plotBase.plot_levels()

        # Now plot dominant pools
        cfg.contur_log.info("Plotting dominant pools")
        plotBase.add_grid(self.conturGrid, "dominantPools", self.outputPath, self.axHolder)
        #if self.external_grids or self.external_functions:
        plotBase.add_external_data_grids(self.alt_grids, callback=self.reset_alt_grids)
        plotBase.plot_pool_names(self, 0)
        plotBase.plot_overlay_and_pools(self, 0)
        self.plot_objects["dominantPools"] = plotBase.figs

        # dump latex legend for colors
        if self.style == "FINAL":
            self.dump_color_palette_tex()

        # Save the plot data for later cosmetic tweaking
        if self.doSavePlotfile:
            self.plot_objects["combined"] = plotBase.figs

        # Now the individual pools' plots
        if self.do_plot_pools:
            outpath = os.path.join(self.outputPath, "pools")
            cutil.mkoutdir(outpath)

            cfg.contur_log.info("Requested plotting of individual analysis pools, found %s pools to plot" % len(
                self.conturGridPools.keys()))

            for idx, (title, grid) in enumerate(self.conturGridPools.items()):
                cfg.contur_log.info("plot %s (%d/%d done)" %
                                              (title, idx+1, len(self.conturGridPools.keys())))
                plotBase = conturPlot(saveAxes=self.doSavePlotfile, iLevel=self.iLevel, cpow=self.cpow, iOrder=self.iOrder,
                                      iSigma=self.iSigma, style=self.style, showcls=self.showcls, show_legend=self.show_legend, plot_metric=plot_metric)
                plotBase.add_grid(grid, title, outpath, self.axHolder)
                plotBase.plot_levels()
                plotBase.plot_mesh_overlay()
                if self.doSavePlotfile:
                    self.plot_objects[title] = plotBase.figs

    def set_output_path(self, outputpath):
        """Convenience switch to set the output path name for the PlotBase instance"""
        self.outputPath = outputpath

    def check_args(self, xarg, yarg):
        """Function to call to check the requested arguments of what to plot are compatible with what is in the map"""
        # for now lets just check against the first point in the list, this should be properly declared from the input file
        try:
            if not all([x in self.points[0].param_point.keys() for x in (xarg, yarg)]):
                cfg.contur_log.critical("Arguments for plotting do not match the available parameters in this map, ensure the parameters are from: {}".format(self.points[0].param_point.keys()))

                raise cfg.ConturError("Arguments for plotting do not match the available parameters in this map, ensure the parameters are from: {}".format(self.points[0].param_point.keys()))
        except IndexError as e:
            cfg.contur_log.error(
                'Exception raised: {}. Is it possible this is an empty results file?'.format(e))
            raise
    
    def read_scan_mode(self):
        """
        Read the (parameter, scan_mode) pairs from the db into a dict.
        """
        # cfg.results_dbfile is set already
        conn = open_for_reading(cfg.results_dbfile)
        c = conn.cursor()

        c.execute('select parameter_name, mode from scan_mode;')
        result = c.fetchall()
        param_mode_dict  = {item[0]:item[1] for item in result}
        self.scan_mode_dict = param_mode_dict

    def get_parameters(self, variables_only=False):
        """
        Returns a list of parameters in the db.
        Returns only independent variables if variables_only=True
        """
        all_params = [param for param, values in self.map_axis.items()]
        if variables_only==False:
            return all_params

        # variables only from here on
        if not hasattr(self,'scan_mode_dict'):
            try:
                self.read_scan_mode()
            except sqlite3.OperationalError:
                cfg.contur_log.warning('No scan_mode table in {}. Assuming parameters with multiple values are independent.'.format(cfg.results_dbfile))
                return [param for param, values in self.map_axis.items() if len(values)>1]

        # work out which parameters need to be sliced
        variable_params = []
        remaining_params = all_params
        # first deal with straightforward cases
        for param, mode in self.scan_mode_dict.items():
            if mode in ['LIN','LOG']:
                variable_params.append(param)
                remaining_params.remove(param)
            if mode in ['CONST','REL']:
                remaining_params.remove(param)
        # handle other cases
        if remaining_params:
            cfg.contur_log.warning('Unable to resolve whether {} are independent. Assuming parameters with multiple values are independent.'.format(remaining_params))
            variable_params.extend([param for param in remaining_params if len(self.map_axis[param])>1])

        return variable_params

    def parse_slice(self, slice_str):
        """
        Function to parse the slice string from the command line to a dictionary.
        """
        slice_str = slice_str.split(" ")
        # Iterate over pairs
        self.slice_dict = {}
        for param, value in pairwise(slice_str):
            self.slice_dict[param] =float(value)
   
    def add_external_grids(self, ExternalGrids):
        """Switch to provide the external exclusion grid files to the PlotBase instance"""
        self.external_grids = ExternalGrids

    def add_external_functions(self, ExternalFunctions):
        """Switch to provide the external exclusion function files to the PlotBase instance"""
        self.external_functions = ExternalFunctions

    def build_grid_from_grid(self, xarg, yarg):
        """
        Build a plotting grid from the supplied external grids
        Assumes the keys for the parameters are the same for all points and grabs them from first point
        :param xarg: the x-axis variable name
        :param yarg: the y-axis variable name

        """

        paramkeys = self.points[0].param_point.keys()

        for fn_name, fn in self.external_grids:

            store = []
            try:
                store  = fn(paramkeys)
            except TypeError:
                cfg.contur_log.critical("Error parsing extrnal grid in {}. Did you mean to treat this as a function instead? (-ef)".format(fn_name))
                sys.exit(1)

            if store[0] is not None:
                new_grid = grid()
                try:
                    new_grid.fill = store[2]
                    new_grid.color = store[3]
                except IndexError:
                    cfg.contur_log.error("fill and colour not defined for {}".format(fn_name))
                    raise

                xaxis = list(np.unique([i[xarg] for i in store[0]]))
                yaxis = list(np.unique([i[yarg] for i in store[0]]))


                new_grid.axes = AxesHolder(xaxis, xarg, 0, yaxis, yarg, 0, self.plotTitle)
                new_grid.label = fn_name
                new_grid.grid = np.zeros((len(xaxis), len(yaxis)))
                new_grid.styles = ["solid"]
                for p, v in zip(store[0], store[1]):
                    xpos = xaxis.index(p[xarg])
                    ypos = yaxis.index(p[yarg])
                    new_grid.grid[xpos][ypos] = v
                self.alt_grids.append(new_grid)
                cfg.contur_log.info("Loaded data grid {}".format(fn_name))

    def build_grid_from_data(self, stat_type, xarg, yarg, plot_metric):
        """
        Build a plotting grid from the expected and secondary statistics
        Assumes the keys for the parameters are the same for all points and grabs them from first point
        :param xarg: the x-axis variable name
        :param yarg: the y-axis variable name

        """

        xaxis = self.map_axis[xarg]
        yaxis = self.map_axis[yarg]

        new_grid = grid()
        new_grid.grid = np.zeros((len(xaxis), len(yaxis)))
        new_grid.label = str(stat_type)
        new_grid.fill = False
        new_grid.color = cfg.contour_colour[stat_type]
        new_grid.axes = AxesHolder(xaxis, xarg, 0, yaxis, yarg, 0, self.plotTitle)
        new_grid.styles = [cfg.contour_style[stat_type]]


        for point in self.points:
            missing_pools=False
            xpos = list(xaxis).index(float(point.param_point[xarg]))
            ypos = list(yaxis).index(float(point.param_point[yarg]))

            try:
                if self.omittedPools:
                    new_grid.grid[xpos][ypos] = point.recalculate_CLs(stat_type, self.omittedPools)
                else:
                    new_grid.grid[xpos][ypos] = point.combined_exclusion_dict[stat_type][plot_metric]
            except KeyError:
                cfg.contur_log.warning("No {} stat for point ({},{})".format(stat_type,xpos,ypos))
                point.combined_exclusion_dict[stat_type][plot_metric] = 0.0
                new_grid.grid[xpos][ypos] = 0.0

        self.alt_grids.append(new_grid)

    def build_grid_from_functions(self, xarg, yarg):
        """
        Builds the grid to pointwise evaluate external function on
        :param xarg: the x-axis variable name
        :param yarg: the y-axis variable name

        """

        xaxis = self.map_axis[xarg]
        yaxis = self.map_axis[yarg]
        paramkeys = self.points[0].param_point.keys()

        try:

            # Just a bit of book keeping to ensure the theory functions defined are always in alphabetical order
            # Can't remember why I thought this was necessary?
            _temp = {k: np.zeros((len(xaxis), len(yaxis))) for k, v in [t for t in self.external_functions]}
            contur_grid_theory = OrderedDict(
                sorted(_temp.items(), key=lambda v: (v[0].upper(), v[0].islower())))

            theory_axes = AxesHolder(xaxis, xarg, 0, yaxis, yarg, 0, self.plotTitle)

            fills = {}
            colors = {}
            for point in self.points:
                xpos = list(xaxis).index(float(point.param_point[xarg]))
                ypos = list(yaxis).index(float(point.param_point[yarg]))

                for k, v in self.external_functions:
                    try:
                        contur_grid_theory[k][xpos][ypos], fills[k], colors[k] = v(point.param_point)
                    except KeyError as ke:
                        cfg.contur_log.critical(
                            "Could not parse the parameters requested by {}. \nThe known parameters are {}. The exception was:{}".format(
                                k, point.param_point.keys(),ke))

                        sys.exit(1)

            for k,v in contur_grid_theory.items():
                new_grid = grid()
                new_grid.grid = v
                new_grid.label = k
                new_grid.axes = theory_axes
                new_grid.fill = fills[k]
                new_grid.color = colors[k]

                cfg.contur_log.info("Built theory grid")

            self.alt_grids.append(new_grid)
        except:
            cfg.contur_log.error("Failed to read external function. Perhaps this is an external grid? (-eg instead of -ef)")
            raise

    def build_special_grid(self, xarg, yarg):
        """
        build_special_grid allows us to build an empty grid from the sampled points dictionary, this is used for adding custom
        functions to evaluate on the grid. For example see the log-read snippets prepared for the BL paper
        """

        xaxis = self.map_axis[xarg]
        yaxis = self.map_axis[yarg]
        self.conturGrid = np.zeros((len(xaxis), len(yaxis)))
        for point in self.points:
            xpos = list(xaxis).index(float(point.param_point[xarg]))
            ypos = list(yaxis).index(float(point.param_point[yarg]))
            # need to change
            # self.conturGrid[xpos][ypos] = point.yoda_factory

    def get_pool_name_from_ID(self, currID):
        """
        return the name of the analysis pool, given the ID number
        """
        return list(self.conturGridPools.keys())[currID]
    
    def validate_plot_params(self,params):
        """
        ensures the parameters entered are in the map and distinct.
        returns a list of the validated parameters.
        """
        available_params = self.get_parameters()
        valiated_params = []
        for plot_param in params:
            while plot_param not in available_params:
                cfg.contur_log.info(f"Parameter '{plot_param}' not found. Available parameters are: {available_params}")
                plot_param = input("Choose an available parameter: ")

            valiated_params.append(plot_param)
            # can't plot the same variable on both axes
            available_params.remove(plot_param)

        return valiated_params

    def validate_levels(self, params):
        """
        checks if the countour levels entered are valid.
        returns a list of the validated parameters.
        """
        while True:
            # check negatives
            if any(param < 0 for param in params):
                for i in range(len(params)):
                    if params[i] < 0:
                        cfg.contur_log.warning(f"Found {params[i]}. Contour levels cannot be negative!")
                        try:
                            params[i] = float(input("Choose a valid level: "))
                        except ValueError:
                            cfg.contur_log.warning("Ensure single float value is entered.")
                continue
            # check duplicates        
            if len(set(params)) != len(params):  
                cfg.contur_log.warning(f"Found duplicates! Re-enter values.")
                for i in range(len(params)):
                    try:
                        params[i] = float(input("Choose a contour level: "))
                    except ValueError:
                        cfg.contur_log.warning("Ensure single float is entered.")  
                continue
            # sort
            params = np.sort(params)
            break
        
        return params

    def validate_slice(self, slice_str, plot_variables):
        """
        checks if the parameters and values passed are in the map. 
        returns True if the string is valid, otherwise False
        """
        slice_str = slice_str.split(' ')
        unassigned_slice_params = [x for x in self.get_parameters(variables_only=True) if not x in plot_variables]

        def check_values(slice_str, param_list):
            for param, value in pairwise(slice_str):
                if param not in param_list:
                    cfg.contur_log.info(f"Parameter {param} not in {param_list}")
                    return False
                    
                try: 
                    float(value)
                except ValueError:
                    cfg.contur_log.info(f"Value {value} for parameter {param} is invalid. Choose from: {self.map_axis[param]}")
                    return False
                
                if not any(np.isclose(float(value), self.map_axis[param])):
                    cfg.contur_log.info(f"Value {float(value)} for parameter {param} not found. Choose from: {self.map_axis[param]}")
                    return False
                
                # can't specify multiple values for one parameter
                param_list.remove(param)

            # valid string if it reaches here
            return True

        # wrong number of params
        if len(slice_str) != 2*len(unassigned_slice_params):
            cfg.contur_log.info(f"Slice string has incorrect number of items. It should be a string of {len(unassigned_slice_params)} space separated 'parameter value' pairs.")
            return False

        # check the values
        return check_values(slice_str,unassigned_slice_params)

    def slice_grid(self, slice_str):
        """Filter the list of points to those which meet the 2D slice parameters"""
        # parse slice string into a dictionary
        slice_str = slice_str.split(" ")
        slice_dict = {}
        for param, value in pairwise(slice_str):
            slice_dict[param] =float(value)

        sliced_points = []
        for point in self.points:
            # True for points which meet the slice criteria
            res = all((np.isclose(point.param_point.get(k),v) for k, v in slice_dict.items()))
            if res:
                sliced_points.append(point)

        self.points = sliced_points


    def build_grid(self, xarg, yarg, plot_metric='CLs'):
        """
        Build the grid in the style mpl needs to make it easy to plot, converts the unordered dictionary of paramPoints into
        a structured numpy array

        .. todo:: revive ND capabilities, might need a total overhaul of how we do this
        """
        # for now we will just scope all the grids we need in the projection
        # fix signs if necessary
        xaxis = self.map_axis[xarg]
        yaxis = self.map_axis[yarg]

        self.conturGrid = np.zeros((len(xaxis), len(yaxis)))
        # need to build a set of all pools here by checking all point,
        #since not all pools will in general be there for all points
        pools = set()
        for p in self.points:
            try:
                for key in p.pool_exclusion_dict[cfg.primary_stat].keys():
                    pools.add(key)
            except KeyError:
                cfg.contur_log.error("No results available for requested statistic {}".format(cfg.primary_stat))
                sys.exit()
                    
        self.conturGridPools = {key: np.zeros((len(xaxis), len(yaxis))) for key in pools}
        # It would be nicer to reuse the sampled grid but that isn't high enough resolution
        if self.external_grids:
            self.build_grid_from_grid(xarg, yarg)
        if self.external_functions:
            self.build_grid_from_functions(xarg,yarg)

        if self._show_secondary:
            # add stats other than the primary one

            if cfg.primary_stat==cfg.databg:
                self.build_grid_from_data(cfg.smbg,xarg,yarg, plot_metric)

            if cfg.primary_stat==cfg.smbg:
                self.build_grid_from_data(cfg.databg,xarg,yarg, plot_metric)

            if self._show_exp:
                self.build_grid_from_data(cfg.expected,xarg,yarg,plot_metric)

            if self._show_hl:
                self.build_grid_from_data(cfg.hlexpected,xarg,yarg, plot_metric)

        elif cfg.primary_stat==cfg.smbg:
            # if primary stat is smbg, we always want to plot the expected.
            if self._show_exp:
                self.build_grid_from_data(cfg.expected,xarg,yarg,plot_metric)
            if self._show_hl:
                self.build_grid_from_data(cfg.hlexpected,xarg,yarg, plot_metric)
            
        self.poolIDs = np.full((len(xaxis), len(yaxis), len(
            self.conturGridPools.keys())), -1, dtype=int)
        self.poolCLs = np.full((len(xaxis), len(yaxis), len(
            self.conturGridPools.keys())), -1, dtype=float)
        self.poolHistos = np.full((len(xaxis), len(yaxis), len(
            self.conturGridPools.keys())), -1, dtype=object)

        for point in self.points:
            missing_pools=False
            xpos = list(xaxis).index(float(point.param_point[xarg]))
            ypos = list(yaxis).index(float(point.param_point[yarg]))

            try:
                if self.omittedPools:
                    self.conturGrid[xpos][ypos] = point.recalculate_CLs(cfg.primary_stat, self.omittedPools)
                else:
                    self.conturGrid[xpos][ypos] = point.combined_exclusion_dict[cfg.primary_stat][plot_metric]
            except KeyError:
                cfg.contur_log.warning("No {} stat for point ({},{})".format(cfg.primary_stat,xpos,ypos))
                point.combined_exclusion_dict[cfg.primary_stat][plot_metric] = 0.0
                self.conturGrid[xpos][ypos] = 0.0

            # Only run for CLs i.e when not using spey
            if plot_metric == 'CLs':
                try:
                    for zpos, pool in enumerate(point.pool_exclusion_dict[cfg.primary_stat].keys()):

                        try:
                            self.conturGridPools[pool][xpos][ypos] = point.pool_exclusion_dict[cfg.primary_stat][pool][plot_metric]
                            try:
                                self.poolIDs[xpos][ypos][zpos] = list(self.conturGridPools.keys()).index(pool)
                                self.poolCLs[xpos][ypos][zpos] = point.pool_exclusion_dict[cfg.primary_stat][pool][plot_metric] * 100  # in %
                                self.poolHistos[xpos][ypos][zpos] = point.pool_histos_dict[cfg.primary_stat][pool]

                            except IndexError as ie:
                                missing_pools=True

                        except KeyError:
                            KeyError("Could not find pool {} for point {}, grid might be malformed".format(pool, point.param_point))

                        if missing_pools:
                            cfg.contur_log.warning("Missing pools for {}".format(point.param_point))
                except KeyError:
                    cfg.contur_log.warning("Can't build per pool entries for {}, ({},{})".format(cfg.primary_stat,xpos,ypos))

        # sort by CLs: get sorting index from poolCLs, z-axis; reverse order by "-"
        index = np.argsort(-self.poolCLs, axis=2)
        # sort poolGrids
        try:
            self.poolIDs = np.take_along_axis(self.poolIDs, index, axis=2)
            self.poolCLs = np.take_along_axis(self.poolCLs, index, axis=2)
            self.poolHistos = np.take_along_axis(self.poolHistos, index, axis=2)
        except Exception as e:
            cfg.contur_log.error(e)
            cfg.contur_log.error(
                "The problem may be you have numpy older than 1.15.0. Upgrade, or set --num-dpools 0")
            sys.exit(1)


            
        # keep all of pools if we want to show more information
        self.full_poolIDs = copy.deepcopy(self.poolIDs)
        self.full_poolCLs = copy.deepcopy(self.poolCLs)
        self.full_poolHistos = copy.deepcopy(self.poolHistos)

        # remove unneccessary entries
        self.poolIDs = self.poolIDs[:, :, :1]
        self.poolCLs = self.poolCLs[:, :, :1]

        self.poolNames = [[]]
        level=0
        # make lists out of 2D arrays
        listCLs = self.poolCLs[:, :, level].flatten()
        listIDs = self.poolIDs[:, :, level].flatten()

        # sort IDs by CLs
        listIDs = np.take_along_axis(listIDs, np.argsort(-listCLs), axis=0)

        # remove duplicates
        distinctListIDs = []
        for currID in listIDs:
            if not currID in distinctListIDs:
                distinctListIDs.append(currID)

        # find up to max_pools-1/ max_pools highest-CLs pools
        usefulKeys = []
        max_pools = 20
        # we have exactly max_pools or less contributing pools, which our colormap can support
        if len(distinctListIDs) <= max_pools:
            usefulKeys = distinctListIDs
        else:  # select only up to max_pools-1 leading pools so we can add one pool "others"
            usefulKeys = distinctListIDs[:max_pools-1]

        # create shortlist of pool names
        self.poolNames.append([])
        for entry in usefulKeys:
            pn = self.get_pool_name_from_ID(entry)
            # the veto on -1 here deals with the case when a certain point hasn't actually been run.
            if pn not in self.poolNames[level] and entry>-1:
                self.poolNames[level].append(pn)
            elif entry==-1 and "No data" not in self.poolNames[level]:
                self.poolNames[level].append("No data")

        # sort poolKeys and poolNames
        sort_by_hue = True
        if sort_by_hue:  # get sort index for hue sort
            import matplotlib.colors as mcolors
            poolhsvs = []
            for poolName in self.poolNames[level]:
                poolhsvs.append(tuple(mcolors.rgb_to_hsv(mcolors.to_rgb(
                    get_pool_color(poolName,cpow=self.cpow)))))  
            sort_index = np.argsort(poolhsvs, axis=0)[:, 0]
        else:  # get sort index for alphabetical sort
            poolInfo = np.array(
                [np.array([x.split("_")[0], x.split("_")[2]]) for x in self.poolNames[level]])
            poolEnergies = np.array([int(x.split("_")[1])
                                        for x in self.poolNames[level]])
            sort_index = np.lexsort((poolInfo[:, 1], poolEnergies, poolInfo[:, 0]))[
                ::-1]  # get sort index, [::-1] for reverse order

        self.poolNames[level] = list(np.take_along_axis(
            np.array(self.poolNames[level]), sort_index, axis=0))  # sort by given index
        usefulKeys = list(np.take_along_axis(
            np.array(usefulKeys), sort_index, axis=0))  # sort by given index

        # insert dummy for all other pools if not <=max_pools contributing pools
        if not len(distinctListIDs) <= max_pools:
            # need to add to usefulKeys as well so that indices match
            usefulKeys.insert(0, -1)
            self.poolNames[level].insert(0, "other")

        # change IDs in poolIDs to shorter ID list
        otherPools = []
        # loop over all entries of 3D matrix, allowing for modifications
        with np.nditer(self.poolIDs[:, :, level], op_flags=['readwrite']) as it:
            for entry in it:
                if entry >= 0:
                    try:
                        newID = usefulKeys.index(entry)
                    except ValueError:  # pool is not important enough for shorter index; list as "other"
                        poolName = self.get_pool_name_from_ID(entry)
                        if not poolName in otherPools:
                            otherPools.append(poolName)
                        newID = -1
                    entry[...] = newID


    def build_axes(self):
        """Function to build the axis dictionaries used for plotting, parameter space points are otherwise stored unordered

        :Built variables:
            * **mapAxis** (``dict``)
            * **plotAxis** (``dict``)

        @TODO should seperate the data structures from the plotting.

        """
        # hack
        # self._bookmapAxis['AUX:Zp']=[]

        for i in self.points:
            for k, v in i.param_point.items():
                if (k=="AUX:Zp"):
                    width = float(i.param_point['AUX:Zp'])
                    mass = float(i.param_point['mZp'])
                    ratio = str(width/mass)
                    self._bookmapAxis[k].append(ratio)
                else:
                    self._bookmapAxis[k].append(v)

        for k, v in self._bookmapAxis.items():
            try:
                self._mapAxis[k] = np.unique(np.array(v, dtype=float))

            except ValueError:
                # some parameters are not numeric, so we can't build an axis. But this is fine.
                pass
    
    def reset_alt_grids(self):
        """
        Resets the alt_grids attribute in ConturPlotBase to prevent adding multiple duplicate external data grids. 
        Used as a callback function in conturPlot.add_external_data_grids method
        """
        self.alt_grids = []
    
    @property
    def map_axis(self):
        """Dictionary of the sampled values in each axis

        **type** (``dict``) --
        **key** -- Parameter name (``string``),
        **value** -- (:class:`numpy.ndarray`)
        """
        return self._mapAxis

    @map_axis.setter
    def map_axis(self, value):
        self._mapAxis = value

    # add a setter for slice plotting
    @Depot.points.setter
    def points(self, new_points):
        self._point_list = new_points

class AxesHolder(object):
    """
    Data structure to keep things legible in the code, holds the Axes scoped from the results file and information about
    how we visualise it. Just used for book keeping
    """

    def __init__(self, xAxis, xLabel, xLog, yAxis, yLabel, yLog, title):
        self.xAxis = xAxis
        self.xLabel = xLabel
        self.xLog = xLog
        self.yAxis = yAxis
        self.yLabel = yLabel
        self.yLog = yLog
        self.title = title


class grid(object):
    """
    A grid of values which can be plotted (as a heatmap or a contour)
    """
    def __init__(self):
        self.label = None
        self.grid  = None
        self.axis  = None
        self.fill  = None
        self.color = None
        self.styles = ["dashed", "solid"]

class conturPlot(object):
    """conturPlot is the engine that interacts with the matplotlib.pyplot plotting library"""

    def __init__(self, saveAxes=False, plotTitle="", iLevel=3, iOrder=3, iSigma=0.75, cpow=0.1, style="DRAFT", showcls=False, simplecls=False, interactive_mode=False, primary_stat=cfg.smbg, show_legend=True, plot_metric='CLs', base_plot=None):
        # Initialise the basic single plot style
        self.style = style.upper()
        self.load_style_defaults()
        self.figs = []
        self.saveAxes = saveAxes
        self.plotTitle = plotTitle
        self.iLevel = iLevel
        self.iOrder = iOrder
        self.iSigma = iSigma
        self.cpow = cpow
        self.showcls = showcls
        self.simplecls = simplecls
        self.cmap = plt.cm.viridis
        self.alt_grids = []
        self.transformed_grid = None
        self.interactive_mode = interactive_mode
        self.show_legend = show_legend
        self.plot_metric = plot_metric
        self.contour_levels = []
        self.base_plot = base_plot

    def add_limits(self, ax, level=3, sigma=0.75):
        "Add the overlaid extra limit contours"

        sigma_store=sigma
        plot_objects = []
        for grid in self.alt_grids:

            if "gw_masses" in grid.label:
                sigma=0.01
            else:
                sigma=sigma_store
            grid.axes.xAxisZoom = scipy.ndimage.zoom(grid.axes.xAxis, level)
            grid.axes.yAxisZoom = scipy.ndimage.zoom(grid.axes.yAxis, level)
            gZoom = scipy.ndimage.zoom(grid.grid, level)
            gZoom = scipy.ndimage.gaussian_filter(gZoom, sigma*level)
            if grid.fill:
                ax.contourf(grid.axes.xAxisZoom, grid.axes.yAxisZoom, gZoom.T, colors=grid.color, levels=[0.95,10.0], alpha=0.3)  # , snap=True)
            contour = ax.contour(grid.axes.xAxisZoom, grid.axes.yAxisZoom, gZoom.T, colors=grid.color, levels=[0.95], linestyles=grid.styles)

            handle = contour.legend_elements()[0][0]
            try:
                label = cfg.stat_to_human[grid.label]+r" @ $2\,\sigma$"
                plot_objects.append((handle, label))
            except KeyError:
                cfg.contur_log.info("No label defined for {}, add one in config/config.py if needed.".format(grid.label))
                
        # .. todo:: The contur/plot directory has a file LabelMaker to define
        # labels to add here, in future we could replicate
        #  the theory function file input to give a label input from file?
        # LabelMaker.BLCaseDE(self.axes[0])
        # LabelMaker.BLCaseA(self.axes[0])
        # LabelMaker.BLCaseB(self.axes[0])
        # LabelMaker.BLCaseC(self.axes[0])
        # LabelMaker.DM_LF(self.axes[0])
        #legend.typeIIseesaw(ax)

        return plot_objects

    def plot_hybrid(self):
        """
        Build the default contur output for combined limit, a hybrid plot showing both a colormesh of the underlying
        exclusion and the derived 1 and 2 sigma confidence intervals from this space
        Makes the file combinedHybrid.pdf.
        """

        cfg.contur_log.info("Plotting combined hybrid: heatmap and contours side-by-side.")

        self.fig, self.axes = plt.subplots(nrows=1, ncols=3, figsize=self.fig_dims_hybrid,
                                           gridspec_kw={"width_ratios": [1, 1, 0.08]})
        self.axes[1].set_title(
            label=r"\textsc{Contur}" + str(self.plotTitle), loc="right")  # \textsc{Contur}

        try:
            im0 = self.axes[1].pcolormesh(self.xAxis, self.yAxis, self.grid.T, cmap=self.cmap, vmin=0, vmax=1,
                                          snap=True,shading='nearest')
        except:
            cfg.contur_log.error("This can happen when you try to plot variables which were not those scanned over.")
            raise
            
        path_out = os.path.join(self.destination, self.label + "Hybrid")
        if self.xLog:
            self.axes[1].set_xscale("log", nonpositive='clip')
        if self.yLog:
            self.axes[1].set_yscale("log", nonpositive='clip')
        self.axes[0].set_ylabel(self.yLabel)
        self.axes[1].set_xlabel(self.xLabel)

        self.interpolate_grid(self.iLevel, self.iSigma, self.iOrder)

        self.axes[0].contourf(self.xaxisZoom, self.yaxisZoom, self.gridZoom.T, cmap=self.cmap,
                              levels=[0.68, 0.95, 10], linestyles=["dashed", "solid"], vmin=0.0, vmax=1.0) # , alpha=0.6, snap=True) # need level=10 for filling
        contours = self.axes[0].contour(self.xaxisZoom, self.yaxisZoom, self.gridZoom.T, colors=cfg.contour_colour[cfg.primary_stat],
                             levels=[0.68, 0.95], linestyles=["dashed", "solid"], vmin=0.0, vmax=1.0)

        # add theory/previous experiment limits
        colorCycle = iter(color_config.CONTURCOLORS())
        alt_details = self.add_limits(self.axes[0], level=self.iLevel, sigma=self.iSigma)

        if self.xLog:
            self.axes[0].set_xscale("log", nonpositive='clip')
        if self.yLog:
            self.axes[0].set_yscale("log", nonpositive='clip')
        self.axes[0].set_ylabel(self.yLabel)
        self.axes[0].set_xlabel(self.xLabel)

        self.axes[0].set_ylim(top=max(self.yaxisZoom),
                             bottom=min(self.yaxisZoom))
        self.axes[0].set_xlim(right=max(self.xaxisZoom),
                              left=min(self.xaxisZoom))
        self.axes[1].set_ylim(top=max(self.yaxisZoom),
                             bottom=min(self.yaxisZoom))
        self.axes[1].set_xlim(right=max(self.xaxisZoom),
                              left=min(self.xaxisZoom))

        if self.show_legend:
            self.make_legend(self.axes[0], contours, alt_details)
  
        # self.axes[0].set_ymin(min(self.yaxisZoom))
        # self.axes[0].set_ymax(max(self.yaxisZoom))

        # self.axes[1].get_shared_y_axes().join(self.axes[0], self.axes[1])
        # the shares axes are being a bugger
        self.axes[1].set_yticklabels([])
        # self.axes[1].set_yticks(self.axes[0].get_yticks())
        cbar = self.fig.colorbar(im0, cax=self.axes[2])
        cbar.set_label(r"CL$_{s}$")

        if self.showcls:
            self.induce_CLs_grid(self.axes[1], self.grid)

        try:
            # self.fig.tight_layout(pad=0.32)
            self.fig.savefig(path_out + "."+cfg.plot_format, format=cfg.plot_format)
            if not self.saveAxes:
                plt.close(self.fig)
        except Exception as e:
            cfg.contur_log.error("Failed to make combinedHybrid plot. This may be due to the interpolation step. Try a different iLevel?")
            cfg.contur_log.error(traceback.format_exc())
            sys.exit()

        if self.interactive_mode:
            def hybrid_click(event):
                """
                Single callback for the hybrid figure:
                - Only fires if the click lands in the contour (axes[0]) or mesh (axes[1]).
                - Aliases self.ax0 to the clicked Axes so on_button_click can use it unchanged.
                """
                # event.inaxes is the Axes instance that was clicked 
                if event.inaxes in (self.axes[0], self.axes[1]):
                    # record which panel the user clicked
                    self.ax0 = event.inaxes
                    self.on_button_click(event, self.base_plot)

            self.fig.canvas.mpl_connect(
                'button_press_event',
                hybrid_click
            )


    def plot_levels(self):
        """
        Make an individual levels plot, currently just used for compatibility to show the individual pools
        Makes the file combinedLevels.pdf
        .. todo:: Derive these from the main hybrid plot
        """

        cfg.contur_log.info("Plotting levels: contours without heatmap")

        # make a styled blank canvas
        self.make_canvas()

        # interpolate the meshgrid to make things smoother for a levels plot
        self.interpolate_grid(self.iLevel, self.iSigma, self.iOrder)
        self.ax0.contourf(self.xaxisZoom, self.yaxisZoom, self.gridZoom.T, cmap=self.cmap,
                          levels=[0.68, 0.95, 10], linestyles=["dashed", "solid"], vmin=0.0, vmax=1.0) # , alpha=0.6, snap=True) # need level=10 for filling
        contours = self.ax0.contour(self.xaxisZoom, self.yaxisZoom, self.gridZoom.T, colors=cfg.contour_colour[cfg.primary_stat],
                         levels=[0.68, 0.95], linestyles=["dashed", "solid"], vmin=0.0, vmax=1.0)

        path_out = os.path.join(self.destination, self.label + "Levels")
        if self.xLog:
            self.ax0.set_xscale("log", nonpositive='clip')
        if self.yLog:
            self.ax0.set_yscale("log", nonpositive='clip')
        self.ax0.set_ylim(top=max(self.yaxisZoom), bottom=min(self.yaxisZoom))
        self.ax0.set_xlim(right=max(self.xaxisZoom), left=min(self.xaxisZoom))
        self.ax0.set_ylim(top=max(self.yaxisZoom), bottom=min(self.yaxisZoom))
        self.ax0.set_xlim(right=max(self.xaxisZoom), left=min(self.xaxisZoom))

        self.ax0.set_ylabel(self.yLabel)
        self.ax0.set_xlabel(self.xLabel)

        if self.show_legend:
            handles, labels = contours.legend_elements()
            labels=[r"$1\,\sigma$", r"$2\,\sigma$"]
            self.ax0.legend(handles=handles, labels=labels, title=cfg.stat_to_human[cfg.primary_stat])

        self.figs.append(self.fig)
        # too small padding may clip ticklabels, see https://gitlab.com/hepcedar/contur/-/issues/480
        # padding of larger than 0.3 is recommended: https://matplotlib.org/3.7.5/tutorials/intermediate/tight_layout_guide.html#caveats
        self.fig.tight_layout(pad=0.3)
        self.fig.savefig(path_out + "."+cfg.plot_format, format=cfg.plot_format)
        if not self.saveAxes:
            plt.close(self.fig)
        if self.interactive_mode:
            self.fig.canvas.mpl_connect(
                'button_press_event',
                lambda event: self.on_button_click(event, self.base_plot)
                if event.inaxes is self.ax0 else None
            )

    def plot_mesh(self, make_cbar):
        """
        Make an individual colormesh plot, currently just used for compatibility to show the individual pools
        .. todo:: Derive these from the main hybrid plot
        Makes the file combinedMesh.pdf
        """

        cfg.contur_log.info("Plotting mesh: heatmap without contours")

        # make a styled blank canvas
        self.make_canvas()
        self.ax0.pcolormesh(self.xAxis, self.yAxis,
                            self.grid.T, cmap=self.cmap, vmin=0, vmax=1, snap=True, shading='nearest')

        path_out = os.path.join(self.destination, self.label + "Mesh")
        if self.xLog:
            self.ax0.set_xscale("log", nonpositive='clip')
        if self.yLog:
            self.ax0.set_yscale("log", nonpositive='clip')
        self.ax0.set_ylim(top=max(self.yaxisZoom), bottom=min(self.yaxisZoom))
        self.ax0.set_xlim(right=max(self.xaxisZoom), left=min(self.xaxisZoom))
        self.ax0.set_ylim(top=max(self.yaxisZoom), bottom=min(self.yaxisZoom))
        self.ax0.set_xlim(right=max(self.xaxisZoom), left=min(self.xaxisZoom))
        self.ax0.set_ylabel(self.yLabel)
        self.ax0.set_xlabel(self.xLabel)

        if self.showcls:
            self.induce_CLs_grid(self.ax0, self.grid)

        self.figs.append(self.fig)
        # too small padding may clip ticklabels, see https://gitlab.com/hepcedar/contur/-/issues/480
        # padding of larger than 0.3 is recommended: https://matplotlib.org/3.7.5/tutorials/intermediate/tight_layout_guide.html#caveats
        self.fig.tight_layout(pad=0.3)
        self.fig.savefig(path_out + "."+cfg.plot_format, format=cfg.plot_format)
        if not self.saveAxes:
            plt.close(self.fig)

        # make (one!) separate fig colorbar
        if make_cbar:
            self.fig_cbar = plt.figure(figsize=self.fig_dims_cbar)  # _cbar)
            self.axcbar = self.fig_cbar.add_subplot(1, 1, 1)
            norm = mpl.colors.Normalize(vmin=0, vmax=1)
            cb1 = mpl.colorbar.ColorbarBase(
                self.axcbar, cmap=self.cmap, norm=norm, orientation="vertical")  # ,orientation="vertical")
            cb1.set_label(r"CL$_{s}$")
            self.fig_cbar.tight_layout(pad=0.1)
            self.fig_cbar.savefig(path_out + "cbar.pdf", format=cfg.plot_format)
            if not self.saveAxes:
                plt.close(self.fig)
                plt.close(self.fig_cbar)
        if self.interactive_mode:
            self.fig.canvas.mpl_connect(
                'button_press_event',
                # Inline lambda: check if click was in the mesh Axes, then delegate
                lambda event: self.on_button_click(event, self.base_plot)
                if event.inaxes is self.ax0 else None
            )
                
    def plot_mesh_overlay(self, make_cbar=False):
        """
        Make an individual colormesh plot with overlaid limit contours
        Makes the file combinedOverlay.pdf
        """

        cfg.contur_log.info("Plotting combined overlay: heatmap with contours.")

        # self.make_canvas()

        # draw the mesh
        self.fig, self.ax0 = plt.subplots(nrows=1, ncols=2, figsize=self.fig_dims_overlay, gridspec_kw={"width_ratios": [1, 0.06]})


        im0 = self.ax0[0].pcolormesh(self.xAxis, self.yAxis,
                            self.grid.T, cmap=self.cmap, vmin=0, vmax=1, snap=True, shading='nearest')
        if self.xLog:
            self.ax0[0].set_xscale("log", nonpositive='clip')
        if self.yLog:
            self.ax0[0].set_yscale("log", nonpositive='clip')
        self.ax0[0].set_ylim(top=max(self.yaxisZoom), bottom=min(self.yaxisZoom))
        self.ax0[0].set_xlim(right=max(self.xaxisZoom), left=min(self.xaxisZoom))
        self.ax0[0].set_ylim(top=max(self.yaxisZoom), bottom=min(self.yaxisZoom))
        self.ax0[0].set_xlim(right=max(self.xaxisZoom), left=min(self.xaxisZoom))
        self.ax0[0].set_ylabel(self.yLabel)
        self.ax0[0].set_xlabel(self.xLabel)

        # interpolate the meshgrid to make things smoother for a levels plot
        self.interpolate_grid(self.iLevel, self.iSigma, self.iOrder)
        contours = self.ax0[0].contour(self.xaxisZoom, self.yaxisZoom, self.gridZoom.T, colors=cfg.contour_colour[cfg.primary_stat],
                         levels=[0.68, 0.95], linestyles=["dashed", "solid"], vmin=0.0, vmax=1.0)



        if self.showcls:
            self.induce_CLs_grid(self.ax0[0], self.grid)

        # add theory/previous experiment limits WHY DOESNT THIS WORK?
        colorCycle = iter(color_config.CONTURCOLORS())
        alt_details = self.add_limits(self.ax0[0], level=self.iLevel, sigma=self.iSigma)

        if self.show_legend:
            self.make_legend(self.ax0[0], contours, alt_details)

        # add colourbar to this plot
        cbar = self.fig.colorbar(im0, cax=self.ax0[1])
        cbar.set_label(r"CL$_{s}$")

        self.figs.append(self.fig)
        # too small padding may clip ticklabels, see https://gitlab.com/hepcedar/contur/-/issues/480
        # padding of larger than 0.3 is recommended: https://matplotlib.org/3.7.5/tutorials/intermediate/tight_layout_guide.html#caveats
        self.fig.tight_layout(pad=0.3)

        path_out = os.path.join(self.destination, self.label + "Overlay")
        self.fig.savefig(path_out + "."+cfg.plot_format, format=cfg.plot_format)
        if not self.saveAxes:
            plt.close(self.fig)

        # make a separate fig colorbar
        if make_cbar:
            self.fig_cbar = plt.figure(figsize=self.fig_dims_cbar)  # _cbar)
            self.axcbar = self.fig_cbar.add_subplot(1, 1, 1)
            norm = mpl.colors.Normalize(vmin=0, vmax=1)
            cb1 = mpl.colorbar.ColorbarBase(
                self.axcbar, cmap=self.cmap, norm=norm, orientation="vertical")  # ,orientation="vertical")
            cb1.set_label(r"CL$_{s}$")
            self.fig_cbar.tight_layout(pad=0.1)
            self.fig_cbar.savefig(path_out + "cbar.pdf", format=cfg.plot_format)
            if not self.saveAxes:
                plt.close(self.fig)
                plt.close(self.fig_cbar)
    

    def plot_mesh_overlay_mu(self, plot_metric, levels, scale):
        """
        Make an individual colormesh plot with overlaid limit contours
        Makes the file combinedOverlay_mu.pdfs
        """

        cfg.contur_log.info("Plotting combined overlay: heatmap with contours.")

        # scaling heatmap with user inputs
        vmax = 1.0
        self.transformed_grid = self.grid
        if scale == 'max':
            vmax = np.max(self.grid)
            cbar_label = cfg.plot_metrics[plot_metric]
        elif scale == 'zero to one':
            vmax = 1.0
            cbar_label = cfg.plot_metrics[plot_metric]
        elif scale == 'logn':
            self.transformed_grid = self.log_transform(self.grid, base='e')
            vmax = np.max(self.transformed_grid)
            cbar_label = r'$log_{e}$' + f'({cfg.plot_metrics[plot_metric]})'
        elif scale == 'log10':
            self.transformed_grid = self.log_transform(self.grid, base='10')
            vmax = np.max(self.transformed_grid)
            cbar_label = r'$log_{10}$' + f'({cfg.plot_metrics[plot_metric]})'
        else:
            cbar_label = cfg.plot_metrics[plot_metric]


        # draw the mesh
        self.fig, self.ax0 = plt.subplots(nrows=1, ncols=2, figsize=self.fig_dims_overlay, gridspec_kw={"width_ratios": [1, 0.06]})

        im0 = self.ax0[0].pcolormesh(self.xAxis, self.yAxis,
                            self.transformed_grid.T, cmap=self.cmap, vmin=0, vmax=vmax, snap=True, shading='nearest')
        if self.xLog:
            self.ax0[0].set_xscale("log", nonpositive='clip')
        if self.yLog:
            self.ax0[0].set_yscale("log", nonpositive='clip')
        self.ax0[0].set_ylim(top=max(self.yaxisZoom), bottom=min(self.yaxisZoom))
        self.ax0[0].set_xlim(right=max(self.xaxisZoom), left=min(self.xaxisZoom))
        self.ax0[0].set_ylim(top=max(self.yaxisZoom), bottom=min(self.yaxisZoom))
        self.ax0[0].set_xlim(right=max(self.xaxisZoom), left=min(self.xaxisZoom))
        self.ax0[0].set_ylabel(self.yLabel)
        self.ax0[0].set_xlabel(self.xLabel)

        # interpolate the meshgrid to make things smoother for a levels plot
        self.interpolate_grid(self.iLevel, self.iSigma, self.iOrder)
        contours = self.ax0[0].contour(self.xaxisZoom, self.yaxisZoom, self.gridZoom.T, colors=cfg.contour_colour[cfg.primary_stat],
                        levels=levels, linestyles=["dotted", "dashed", "solid"], vmin=0.0, vmax=vmax)
        
        if self.showcls:
            self.induce_CLs_grid(self.ax0[0], self.grid)

        if self.show_legend:
            self.make_legend(self.ax0[0], contours, None, plot_metric, levels)

        # add colourbar to this plot
        cbar = self.fig.colorbar(im0, cax=self.ax0[1])
        cbar.set_label(cbar_label)

        self.figs.append(self.fig)
        # too small padding may clip ticklabels, see https://gitlab.com/hepcedar/contur/-/issues/480
        # padding of larger than 0.3 is recommended: https://matplotlib.org/3.7.5/tutorials/intermediate/tight_layout_guide.html#caveats
        self.fig.tight_layout(pad=0.3)

        path_out = os.path.join(self.destination, self.label + "Overlay" + "_" + self.plot_metric)
        self.fig.savefig(path_out + "."+cfg.plot_format, format=cfg.plot_format)
        if not self.saveAxes:
            plt.close(self.fig)

    def plot_mesh_overlay_cls(self, plot_metric, make_cbar=False):
        """
        Make an individual colormesh plot with overlaid limit contours
        Makes the file combinedOverlay_CLs.pdf
        """

        cfg.contur_log.info("Plotting combined overlay: heatmap with contours.")

        # self.make_canvas()

        # draw the mesh
        self.fig, self.ax0 = plt.subplots(nrows=1, ncols=2, figsize=self.fig_dims_overlay, gridspec_kw={"width_ratios": [1, 0.06]})


        im0 = self.ax0[0].pcolormesh(self.xAxis, self.yAxis,
                            self.grid.T, cmap=self.cmap, vmin=0, vmax=1, snap=True, shading='nearest')
        if self.xLog:
            self.ax0[0].set_xscale("log", nonpositive='clip')
        if self.yLog:
            self.ax0[0].set_yscale("log", nonpositive='clip')
        self.ax0[0].set_ylim(top=max(self.yaxisZoom), bottom=min(self.yaxisZoom))
        self.ax0[0].set_xlim(right=max(self.xaxisZoom), left=min(self.xaxisZoom))
        self.ax0[0].set_ylim(top=max(self.yaxisZoom), bottom=min(self.yaxisZoom))
        self.ax0[0].set_xlim(right=max(self.xaxisZoom), left=min(self.xaxisZoom))
        self.ax0[0].set_ylabel(self.yLabel)
        self.ax0[0].set_xlabel(self.xLabel)

        # interpolate the meshgrid to make things smoother for a levels plot
        self.interpolate_grid(self.iLevel, self.iSigma, self.iOrder)
        contours = self.ax0[0].contour(self.xaxisZoom, self.yaxisZoom, self.gridZoom.T, colors=cfg.contour_colour[cfg.primary_stat],
                         levels=[0.68, 0.95], linestyles=["dashed", "solid"], vmin=0.0, vmax=1.0)



        if self.showcls:
            self.induce_CLs_grid(self.ax0[0], self.grid)

        # add theory/previous experiment limits WHY DOESNT THIS WORK?
        colorCycle = iter(color_config.CONTURCOLORS())
        alt_details = self.add_limits(self.ax0[0], level=self.iLevel, sigma=self.iSigma)

        if self.show_legend:
            self.make_legend(self.ax0[0], contours, alt_details)

        # add colourbar to this plot
        cbar = self.fig.colorbar(im0, cax=self.ax0[1])
        cbar.set_label(cfg.plot_metrics[plot_metric])

        self.figs.append(self.fig)
        # too small padding may clip ticklabels, see https://gitlab.com/hepcedar/contur/-/issues/480
        # padding of larger than 0.3 is recommended: https://matplotlib.org/3.7.5/tutorials/intermediate/tight_layout_guide.html#caveats
        self.fig.tight_layout(pad=0.3)

        path_out = os.path.join(self.destination, self.label + "Overlay" + "_" + self.plot_metric)
        self.fig.savefig(path_out + "."+cfg.plot_format, format=cfg.plot_format)
        if not self.saveAxes:
            plt.close(self.fig)

        # make a separate fig colorbar
        if make_cbar:
            self.fig_cbar = plt.figure(figsize=self.fig_dims_cbar)  # _cbar)
            self.axcbar = self.fig_cbar.add_subplot(1, 1, 1)
            norm = mpl.colors.Normalize(vmin=0, vmax=1)
            cb1 = mpl.colorbar.ColorbarBase(
                self.axcbar, cmap=self.cmap, norm=norm, orientation="vertical")  # ,orientation="vertical")
            cb1.set_label(cfg.plot_metrics[plot_metric])
            self.fig_cbar.tight_layout(pad=0.1)
            self.fig_cbar.savefig(path_out + "cbar.pdf", format=cfg.plot_format)
            if not self.saveAxes:
                plt.close(self.fig)
                plt.close(self.fig_cbar)

        if self.interactive_mode:
            def overlay_click(event):
                if event.inaxes is self.ax0[0]:
                    self.ax0 = event.inaxes
                    self.on_button_click(event, self.base_plot)

            self.fig.canvas.mpl_connect(
                'button_press_event',
                overlay_click
            )

                
    def plot_overlay_and_pools(self, cpb, level):
        """
        Plot the overlay and dominant pools side-by-side
        Makes the file combinedOverlayPools.pdf.
        """

        cfg.contur_log.info("Plotting combined hybrid: overlay and dominant pools side-by-side.")

        path_out = os.path.join(self.destination, "combinedOverlayPools")

        self.fig, self.axes = plt.subplots(nrows=1, ncols=3, figsize=self.fig_dims_overlay_and_dp,
                                           gridspec_kw={"width_ratios": [1, 0.06, 1]},
                                           constrained_layout=True)
        self.axes[2].set_title(
            label=r"\textsc{Contur}" + str(self.plotTitle), loc="right")  # \textsc{Contur}
        
        # overlay
        im0 = self.axes[0].pcolormesh(self.xAxis, self.yAxis, self.grid.T, cmap=self.cmap, vmin=0, vmax=1,
                                          snap=True,shading='nearest')
        
        self.interpolate_grid(self.iLevel, self.iSigma, self.iOrder)
        contours = self.axes[0].contour(self.xaxisZoom, self.yaxisZoom, self.gridZoom.T, colors=cfg.contour_colour[cfg.primary_stat],
                         levels=[0.68, 0.95], linestyles=["dashed", "solid"], vmin=0.0, vmax=1.0)
        
        # dominant pools
        # self.make_canvas(dims=self.fig_dims_dp)

        # Plot styling
        showtitle = (self.style == "DRAFT")
        showcbar = (self.style == "DRAFT")

        nColors = len(cpb.poolNames[level])
        
        usetints = not (self.style == "FINAL")
        
        poolcmap = plt.matplotlib.colors.ListedColormap(
            [get_pool_color(pool,  tints=usetints, cpow=self.cpow) for pool in cpb.poolNames[level]])
        plotHighest = self.axes[2].pcolormesh(
            self.xAxis, self.yAxis, cpb.poolIDs[:, :, level].T, snap=True, cmap=poolcmap, vmin=0, vmax=nColors, shading='nearest')

        self.interpolate_grid(self.iLevel, self.iSigma, self.iOrder)
        contours = self.axes[2].contour(self.xaxisZoom, self.yaxisZoom, self.gridZoom.T, colors=cfg.contour_colour[cfg.primary_stat],
                         levels=[0.68, 0.95], linestyles=["dashed", "solid"], vmin=0.0, vmax=1.0)

        # only want a legend on the overlay plot
        # if self.show_legend:
        #     self.make_legend(self.axes[2], contours, alt_details)

        if self.showcls:
            self.induce_CLs_grid(self.axes[2], self.grid)

        # pools colour bar
        bounds = np.linspace(0, nColors, num=nColors+1)
        ticks = [x+0.5 for x in bounds[:-1]]
        labels = []
        for pool in cpb.poolNames[level]:
            # have to escape underscores
            labels.append(pool.replace("_", r"\_"))

        if showcbar:
            # self.fig.savefig(path_out + "nocbar.pdf", format=cfg.plot_format) #< save before adding the cbar
            cbar = self.fig.colorbar(
                plotHighest, boundaries=bounds, ticks=ticks)
            cbar.ax.set_yticklabels(labels)
            cbar.ax.tick_params(labelsize=4)

        # add expected limit contours to pools plot
        colorCycle = iter(color_config.CONTURCOLORS())
        alt_details = self.add_limits(self.axes[2],level=self.iLevel,sigma=self.iSigma)

        # formatting
        self.prepare_axis(self.axes[0])

        # self.prepare_axis(self.axes[2], ylabel_right=(self.style == "FINAL"))
        self.prepare_axis(self.axes[2], ylabel_right=False)
        
        # add theory/previous experiment limits
        colorCycle = iter(color_config.CONTURCOLORS())
        alt_details = self.add_limits(self.axes[0], level=self.iLevel, sigma=self.iSigma)

        if self.show_legend:
            self.make_legend(self.axes[0], contours, alt_details)
  
        cbar = self.fig.colorbar(im0, cax=self.axes[1])
        cbar.set_label(r"CL$_{s}$")

        try:
            # self.fig.tight_layout(pad=0.1)
            self.fig.savefig(path_out + "."+cfg.plot_format, format=cfg.plot_format)
            if not self.saveAxes:
                plt.close(self.fig)
        except Exception as e:
            cfg.contur_log.error("Failed to make combinedHybrid plot. This may be due to the interpolation step. Try a different iLevel?")
            cfg.contur_log.error(traceback.format_exc())
            sys.exit()
        if self.interactive_mode and self.base_plot is not None:
            def ovp_click(event):
                # We want clicks on the *overlay* panel (axes[0]) to pop up details,
                # not on the legend or the pools panel (axes[2]).
                if event.inaxes is self.axes[0]:
                    # alias for on_button_click
                    self.ax0 = event.inaxes
                    self.on_button_click(event, self.base_plot)

            self.fig.canvas.mpl_connect(
                'button_press_event',
                ovp_click
            )


    def induce_CLs_grid(self, axis, grid, inPercent=False):
        """  show the bin contents as text """
        for i in range(len(self.xAxis)):
            for j in range(len(self.yAxis)):
                z = "%.2f" % grid[i, j]
                if inPercent:
                    z = "%.1f" % grid[i, j]
                axis.text(self.xAxis[i], self.yAxis[j], z, color="w",
                          ha="center", va="center", fontsize="4")

    def prepare_axis(self, axis, ylabel_right=False):
        if self.xLog:
            axis.set_xscale("log", nonpositive='clip')
        if self.yLog:
            axis.set_yscale("log", nonpositive='clip')
        axis.set_ylim(top=max(self.yaxisZoom), bottom=min(self.yaxisZoom))
        axis.set_xlim(right=max(self.xaxisZoom), left=min(self.xaxisZoom))
        axis.set_ylabel(self.yLabel)
        axis.set_xlabel(self.xLabel)

        if ylabel_right:
            axis.yaxis.tick_right()
            axis.yaxis.set_label_position("right")
        else:
            axis.yaxis.tick_left()
            axis.yaxis.set_label_position("left")

        axis.set_ylabel(self.yLabel)



    def plot_CLs(self, gridSpecs, grid, title, extend='neither'):
        """ plot a mesh of the grid with CLs values """

        axis = self.fig.add_subplot(gridSpecs[0])
        axisCbar = self.fig.add_subplot(gridSpecs[1])
        axis.set_title(title)

        vmin = 0
        cmap = self.cmap
        if extend == 'min':
            vmin = -1
            newcolors = self.cmap(np.linspace(0, 1, num=255))
            np.insert(newcolors, 0, [0, 0, 0, 1])
            newcolors[0, :] = np.array([0, 0, 0, 1])
            cmap = mpl.colors.ListedColormap(newcolors)

        plot = axis.pcolormesh(self.xAxis, self.yAxis,
                               grid.T, cmap=cmap, vmin=vmin, vmax=100, snap=True, shading='nearest')
        self.prepare_axis(axis)

        cbarTotal = self.fig.colorbar(plot, cax=axisCbar, extend=extend)
        cbarTotal.set_label(r"CL$_{s}$")

        if self.showcls:
            self.induce_CLs_grid(axis, grid, inPercent=True)

    def interactive_find_index(self, list, value):
        low = 0
        high = len(list) - 1
        while low <= high:
            mid = (low + high) // 2
            if list[mid] == value:
                return mid
            elif list[mid] < value:
                low = mid + 1
            else:
                high = mid - 1
        return low - 1

    def on_mouse_hover(self, event, cpb, annotations):
        if event.inaxes == self.ax0:
            x_hover = event.xdata
            y_hover = event.ydata
            x_coordinate = self.interactive_find_index(self.xAxis, x_hover)
            y_coordinate = self.interactive_find_index(self.yAxis, y_hover)
            clicked_point_poolIDs = cpb.full_poolIDs[x_coordinate][y_coordinate]
            clicked_point_poolCLs = cpb.full_poolCLs[x_coordinate][y_coordinate]
            pool_name_list = []
            for ID in clicked_point_poolIDs:
                pool_name_list.append(cpb.get_pool_name_from_ID(ID))

            # display information on the current figure
            # middle_x = (self.ax0.get_xlim()[0] + self.ax0.get_xlim()[1]) / 2
            # middle_y = (self.ax0.get_ylim()[0] + self.ax0.get_ylim()[1]) / 2

            # calculate the middle point in log scale (seems both fine for normal scale)
            middle_x = math.sqrt((self.ax0.get_xlim()[0] * self.ax0.get_xlim()[1]))
            middle_y = math.sqrt((self.ax0.get_ylim()[0] * self.ax0.get_ylim()[1]))

            for annotation in annotations:
                annotation.remove()
            annotations.clear()
            annotation = self.ax0.annotate(
                "{}: {:.2f} \n {}: {:.2f} \n {}: {:.2f} \n {}: {:.2f} \n {}: {:.2f} \n".format(pool_name_list[0], clicked_point_poolCLs[0],
                                                                           pool_name_list[1], clicked_point_poolCLs[1],
                                                                           pool_name_list[2], clicked_point_poolCLs[2],
                                                                           pool_name_list[3], clicked_point_poolCLs[3],
                                                                           pool_name_list[4], clicked_point_poolCLs[4]),
                (middle_x, middle_y))
            annotations.append(annotation)
            self.fig.canvas.manager.set_window_title(cpb.xarg+': '+ str(cpb.map_axis[cpb.xarg][y_coordinate]) + ',' +
                                             cpb.yarg+': '+ str(cpb.map_axis[cpb.yarg][x_coordinate]))
            self.fig.canvas.draw()


    def on_button_click(self, event, cpb):
        if event.inaxes == self.ax0:
            x = event.xdata
            y = event.ydata
            x_coordinate = self.interactive_find_index(self.yAxis, y)
            y_coordinate = self.interactive_find_index(self.xAxis, x)
            clicked_point_poolIDs = cpb.full_poolIDs[x_coordinate][y_coordinate]
            clicked_point_poolCLs = cpb.full_poolCLs[x_coordinate][y_coordinate]
            clicked_point_poolHistos = cpb.full_poolHistos[x_coordinate][y_coordinate]
            pool_name_list = []
            for ID in clicked_point_poolIDs:
                pool_name_list.append(cpb.get_pool_name_from_ID(ID))

            # Detailed GUI
            fig, (ax_bar, ax_table) = plt.subplots(
                ncols=2,                    # two plots side-by-side
                figsize=(16, 8),            # overall size of the window
                gridspec_kw={'width_ratios': [1, 1.5]}
            )
            fig.suptitle(
                "Details for the Parameters “{} vs {}”".format(cpb.xarg, cpb.yarg),
                fontsize=18,
                fontweight='bold',
                y=0.98      
            )
            

            fig.canvas.manager.set_window_title("Details window")
            fig.canvas.manager.set_window_title(cpb.xarg + ': ' + str(cpb.map_axis[cpb.xarg][y_coordinate]) + ',' +
                                                cpb.yarg + ': ' + str(cpb.map_axis[cpb.yarg][x_coordinate]))
            bar = ax_bar.bar(pool_name_list[:5], clicked_point_poolCLs[:5], color='#1f77b4')
            ax_bar.tick_params(axis='x', labelsize=8)
            ax_bar.bar_label(bar)
            _db = sqlite3.connect(paths.user_path("analyses.db"))
            _DESC_MAP = dict(_db.execute("SELECT pool, description FROM analysis_pool;"))
            _db.close()
            table_data = []
            colLabels = ['Pool Name', 'Description', 'Confidence Level', 'Histos']
            expand_cell_dict = {}  # dictionary records which row need to be expanded
            for index, pool_name in enumerate(pool_name_list):
                if not math.isclose(clicked_point_poolCLs[index], 0, rel_tol=1e-2): # |a-b| < 0.01
                    pool_Histos = clicked_point_poolHistos[index].replace(',', '\n')
                    desc = _DESC_MAP.get(pool_name, "")
                    trimmed = re.sub(r"\s*\(.*?\)", "", desc)
                    max_len = 60
                    if len(trimmed) > max_len:
                        trimmed = trimmed[: max_len - 1].rstrip()
                    count = pool_Histos.count('\n')
                    if count > 0:
                        expand_cell_dict[index] = count
                    table_data.append([pool_name, trimmed, "{:.2f}".format(clicked_point_poolCLs[index]), pool_Histos])
            ax_table.axis('off')
            colWidths = [0.20, 0.45, 0.10, 0.30]
            table = ax_table.table(cellText=table_data, colLabels=colLabels, loc='center', colWidths=colWidths)
            table.auto_set_font_size(False)
            # Expand the height of row whose sub-histos is more than 1
            for key in expand_cell_dict:
                default_height = table[key, 0].get_height()
                count = expand_cell_dict[key]
                for col in range(0, len(colLabels)):
                    cell = table[key + 1, col]  # ignore the header, so the row plus 1
                    cell.set_height(default_height * (count + 1))  # since the height should not be 0
            table.auto_set_column_width(2)
            table.set_fontsize(8)
            table.auto_set_column_width(2)
            plt.tight_layout()
            plt.show()


    def plot_pool_names(self, cpb, level):
        """Make a 2D plot of the dominant pool names and their CLs values"""
        self.make_canvas(dims=self.fig_dims_dp)
        path_out = os.path.join(self.destination, self.label)

        if self.interactive_mode:
            self.click_cid = self.ax0.figure.canvas.mpl_connect('button_press_event',
                                                            lambda event: self.on_button_click(event, cpb))

        # Plot styling
        showtitle = (self.style == "DRAFT")
        showcbar = (self.style == "DRAFT")

        # Painstakingly assemble a nice title
        if showtitle:
            title = "Leading CLs analysis pools"
            if level > 0:
                suffix = "th"
                if level < 3:
                    suffix = "st" if level == 1 else "nd"
                title = "{lev:d}{suff}-subleading-CLs analysis pools".format(
                    lev=level, suff=suffix)
            self.ax0.set_title(title)

        # TODO: can we somehow get a more semantically ordered pool list, e.g. using the POOLCOLORS dict order?
        nColors = len(cpb.poolNames[level])
        
        usetints = not (self.style == "FINAL")
        # plotHighest = self.ax0.pcolormesh(self.xAxisMesh, self.yAxisMesh, cpb.poolIDs[:,:,level].T, snap=True, cmap=plt.get_cmap("tab20", nColors), vmin=0, vmax=nColors)
        poolcmap = plt.matplotlib.colors.ListedColormap(
            [get_pool_color(pool,  tints=usetints, cpow=self.cpow) for pool in cpb.poolNames[level]])
        plotHighest = self.ax0.pcolormesh(
            self.xAxis, self.yAxis, cpb.poolIDs[:, :, level].T, snap=True, cmap=poolcmap, vmin=0, vmax=nColors, shading='nearest')
        self.prepare_axis(self.ax0)

        self.interpolate_grid(self.iLevel, self.iSigma, self.iOrder)
        contours = self.ax0.contour(self.xaxisZoom, self.yaxisZoom, self.gridZoom.T, colors=cfg.contour_colour[cfg.primary_stat],
                         levels=[0.68, 0.95], linestyles=["dashed", "solid"], vmin=0.0, vmax=1.0)

        # Add theory/previous experiment limits
        colorCycle = iter(color_config.CONTURCOLORS())
        alt_details = self.add_limits(self.ax0,level=self.iLevel,sigma=self.iSigma)

        if self.show_legend:
            self.make_legend(self.ax0, contours, alt_details)

        if self.showcls:
            self.induce_CLs_grid(self.ax0, self.grid)

        # Colour bar
        bounds = np.linspace(0, nColors, num=nColors+1)

        ticks = [x+0.5 for x in bounds[:-1]]
        labels = []
        for pool in cpb.poolNames[level]:
            # have to escape underscores
            labels.append(pool.replace("_", r"\_"))

        if showcbar:
            # self.fig.savefig(path_out + "nocbar.pdf", format=cfg.plot_format) #< save before adding the cbar
            cbar = self.fig.colorbar(
                plotHighest, boundaries=bounds, ticks=ticks)
            cbar.ax.set_yticklabels(labels)
            cbar.ax.tick_params(labelsize=4)

        # Tidy the presentation
        self.figs.append(self.fig)
        self.fig.tight_layout(pad=0.1)

        # Save fig and cbar
        self.fig.savefig(path_out + "."+cfg.plot_format, format=cfg.plot_format)

        # plt.show() will release the figure, so call it after saving.
        if self.interactive_mode:
            plt.show()

        # Clean up
        if not self.saveAxes:
            plt.close(self.fig)

    def make_canvas(self,dims=None):
        """Convenience function for the individual plots"""
        if dims is None:
            dims=self.fig_dims
        self.fig = plt.figure(figsize=dims)
        self.ax0 = self.fig.add_subplot(1,1,1)

    def add_grid(self, numpyGrid, label, dest, axHolder):
        """Main access method to give the plot all the attributes it needs in a numpy format that feeds directly into mpl"""
        self.grid = numpyGrid
        self.label = label
        self.destination = dest
        self.__dict__.update(axHolder.__dict__)

        self.interpolate_grid(self.iLevel)

    def add_external_data_grids(self, external_data_grids, callback=None):
        """
        Add the alternative data grids, this is a workaround for now
        .. todo:: Revisit the implementation of smoothing using scipy's interpolator here
        """

        self.alt_grids.extend(external_data_grids)
        if callback:
            callback()


    def interpolate_grid(self, level=3, sigma=0.75, order=3):
        """Use scipy's interpolators to create smoothed & zoomed versions of the grid and axes"""
        import scipy.ndimage
        
        grid_to_use = self.transformed_grid if self.transformed_grid is not None else self.grid
        self.gridZoom = scipy.ndimage.zoom(grid_to_use, level, order=order)
        self.gridZoom = scipy.ndimage.gaussian_filter(self.gridZoom, sigma*level)
        self.xaxisZoom = scipy.ndimage.zoom(self.xAxis,level,order=order)
        self.yaxisZoom = scipy.ndimage.zoom(self.yAxis,level,order=order)
        # reset so future calls don't use transform unless it is updated 
        self.transformed_grid = None
    
    def log_transform(self, grid, base):
        """
        Apply a logarithmic transform to grid
        """
        grid[grid <= 0] = 0.01 
        if base == 'e':
            grid = np.log(grid)
        elif base == '10':
            grid = np.log10(grid)

        return grid

    def load_style_defaults(self):
        """Some core common styling such as figure dimensions, and rcParams"""
        WIDTH = 454.0
        FACTOR = 1.0 / 2.0
        figwidthpt = WIDTH * FACTOR
        inchesperpt = 1.0 / 72.27
        golden_ratio = (np.sqrt(5) - 1.0) / 2.0

        figwidthin = figwidthpt * inchesperpt  # figure width in inches
        figheightin = figwidthin * golden_ratio + 0.6  # figure height in inches
        self.fig_dims = [figwidthin, figheightin]  # fig dims as a list
        self.fig_dims_hybrid = [figwidthin * 1.8, figheightin]
        self.fig_dims_cls = [figwidthin * 3., 2.1*figheightin]
        self.fig_dims_cbar = [figwidthin * 0.2, figheightin]
        self.fig_dims_overlay = [figwidthin * 1.2, figheightin]
        if self.style == "DRAFT":
            self.fig_dims_dp = [figwidthin * 1.7, figheightin*1.5] 
            self.fig_dims_overlay_and_dp = [figwidthin + self.fig_dims_cbar[0] + self.fig_dims_dp[0], self.fig_dims_dp[1]]
        else:
            self.fig_dims_dp = self.fig_dims
            self.fig_dims_overlay_and_dp = [figwidthin*1.1 + self.fig_dims_dp[0], self.fig_dims_dp[1]]
        


        document_fontsize = 10
        rcParams['font.family'] = 'serif'
        rcParams['font.serif'] = ['Computer Modern Roman']
        rcParams['font.size'] = document_fontsize
        rcParams['axes.titlesize'] = document_fontsize
        rcParams['axes.labelsize'] = document_fontsize
        rcParams['xtick.labelsize'] = document_fontsize
        rcParams['ytick.labelsize'] = document_fontsize
        rcParams['legend.fontsize'] = int(document_fontsize*0.8)
        rcParams['text.usetex'] = bool(shutil.which('tex'))
        rcParams['interactive'] = False
        rcParams['axes.prop_cycle'] = color_config.CONTURCOLORS

    def make_legend(self, ax, contours, alt_details, plot_metric='CLs', levels=None):
        handles, labels = contours.legend_elements()
        
        # plot expected contour for CLs only
        if plot_metric == 'CLs':
            base_label = cfg.stat_to_human[cfg.primary_stat]+" @ "
            labels = [base_label+f"${i+1}"+r"\,\sigma$" for i in range(2)]
            labels += [label for handle, label in alt_details]
            handles += [handle for handle, label in alt_details]
            ax.legend(handles=handles, labels=labels)
        else:
            labels = [level for level in levels]
            ax.legend(handles=handles, labels=labels)
