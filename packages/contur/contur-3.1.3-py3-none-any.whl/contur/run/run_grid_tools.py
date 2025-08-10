"""
Perform various manipulations on an existing contur scan grid or grids, but NOT the actual contur statistical analysis.

"""

import logging
import os
import sys
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

import contur
import contur.data.data_access_db as cdba
import contur.config.config as cfg
from contur.config.config import ConturError
import contur.scan.grid_tools as cgt

def main(args):
    """
    arguments should be passed as a dictionary.

    """

    contur.run.arg_utils.setup_common(args)
    print("Writing log to {}".format(cfg.logfile_name))

    cfg.grid = args['GRID']
    if "RESULTS" in args:
        if cfg.grid is not None:
            cfg.contur_log.critical("Both grid directory and DB specified. You should give only one of these.")
            sys.exit(1)
        cfg.results_dbfile = args['RESULTS']
        
    if args['DO_NOT_CLEAN']:
        cfg.contur_log.info("Not removing unnecessary files from grid")
        Clean = False
    else:
        Clean = True
                
    if args['FINDPARAMS']:

        # find the specified parameter point.
        yoda_files = []
        paramList =  []
        for params in args['FINDPARAMS']:            
            for p in params.split(","):
                paramList.append(p)

        if len(paramList)>0:        

            if args['GRID'] is None:
                try:

                    # try to find an appropriate results database
                    if not os.path.isfile(cfg.results_dbfile):
                        cfg.results_dbfile = os.path.join(cfg.input_dir,cfg.results_dbfile)
                        if not os.path.isfile(cfg.results_dbfile):
                            raise ConturError("Could not find results database")

                    cfg.contur_log.info("Using results file: {}".format(cfg.results_dbfile))

                    if args['PARAM_DETAIL']:
                        yoda_files = cdba.show_param_detail_db(paramList)
                    else:
                        yoda_files = cdba.find_param_point_db(paramList)

                except ConturError as dboe:
                    cfg.contur_log.info(dboe)
                    cfg.contur_log.info("Could not get info from DB {}.".format(cfg.results_dbfile))
                    sys.exit(1)

            # No yodas found so try file system.        
            if len(yoda_files)==0:

                if cfg.grid is None or not os.path.isdir(cfg.grid):
                    cfg.contur_log.critical("Could not find grid with name: {}".format(cfg.grid))
                    sys.exit(1)

                cfg.contur_log.info("Looking for parameter points in {} directory.".format(cfg.grid))
                cfg.contur_log.info("Note that if you have a result database already, using that (with -r) would be quicker.")
                yoda_files = cgt.find_param_point(args['GRID'], cfg.tag, paramList, verbose=True)
      
        return
    else:

        if cfg.grid is None:
            cfg.contur_log.critical("You need to specify a grid directory for these options.")
            sys.exit(1)
        
                    
    if len(args['ANAPATTERNS'])>0 or len(args['ANAUNPATTERNS'])>0:
        cfg.onlyAnalyses = args['ANAPATTERNS']
        cfg.vetoAnalyses = args['ANAUNPATTERNS']
        cfg.contur_log.info("Extracting histograms from particular analyses into a new grid:")
        if len(args['ANAPATTERNS'])>0:
            cfg.contur_log.info("Analyses matching any of {} will be extracted".format(cfg.onlyAnalyses))
        if len(args['ANAUNPATTERNS'])>0:
            cfg.contur_log.info("Analyses matching any of {} will not be extracted (veto takes precedence).".format(cfg.vetoAnalyses))
        cgt.grid_loop(extract=True, clean=Clean)
        
    elif args['RM_MERGED']:
        cgt.grid_loop(unmerge=True, clean=Clean)

    elif args['COMPRESS_GRID']:
        cgt.grid_loop(archive=True,  clean=Clean)

    elif args['CHECK_GRID'] or args['CHECK_ALL'] or args['RESUB']:
        cgt.grid_loop(check=True, resub=args['RESUB'], check_all=args['CHECK_ALL'], queue=args['queue'],  clean=Clean)

    elif Clean:
        cgt.grid_loop(clean=Clean)


    sys.exit(0)


def doc_argparser():
    """ wrap the arg parser for the documentation pages """
    from contur.run.arg_utils import get_argparser
    return get_argparser('grid_tool')
