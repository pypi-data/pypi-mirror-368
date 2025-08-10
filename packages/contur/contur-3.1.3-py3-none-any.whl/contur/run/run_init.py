# make the shared area of a common contur install

from genericpath import exists
import os, glob

import contur.config.config as cfg
from contur.run.arg_utils import setup_common, setup_mysql
from contur.data.data_objects import Beam
import contur.data as cdb

import contur.util.utils as cutil
import contur.util.rst_utils as rst_utils

from contur.data import build_database

home_dir=os.path.expanduser('~')
VERBOSITY = 1
def log(msg, v):
    if v >= VERBOSITY:
        print(msg)
def debug(msg):
    log(msg, 0)
def warning(msg):
    log(msg, 2)

def generate_rivet_lists(webpages):
    """
    Generate various rivet analysis listings from the Contur database.
    Called on initialisation only.

    - the .ana files for Herwig running

    - the script to set the analysis list environment variables

    - (optionally) the contur webpage listings.

    :param webpages: if true, also write out the contur webpage listings.
    
    """
    # statics
    rivettxt = "insert Rivet:Analyses 0 "
    
    # make the directory if it doesn't already exist
    output_directory = cfg.output_dir
    cutil.mkoutdir(output_directory)

    # open file for the environment setters
    fl = open(output_directory + "/analysis-list", 'w')

    known_beams = cdb.static_db.get_beams()
    known_pools = cdb.static_db.get_pools()
    envStrings = {}
    envStrings_all = {}

    # build the .ana and env variable setters
    for beam in known_beams:
        analysis_list = cdb.static_db.get_analyses(beam=beam,filter=False) 
        f = open(os.path.join(output_directory, beam.id + ".ana"), 'w')
        f_all = open(os.path.join(output_directory, beam.id + ".ana_all"), 'w')
        envStrings[beam.id] = "export CONTUR_RA{}=\"".format(beam.id)
        envStrings_all[beam.id] = "export CONTUR_RA{}_ALL=\"".format(beam.id)
        for analysis in analysis_list:
            f_all.write(rivettxt + analysis.name + " # " + analysis.summary() + "\n")
            envStrings_all[beam.id] = envStrings_all.get(beam.id) + analysis.name + ","
            if analysis.hasPrediction():
                f.write(rivettxt + analysis.name + " # " + analysis.summary() + "\n")
                envStrings[beam.id] = envStrings.get(beam.id) + analysis.name + ","

        f.close()
        f_all.close()

    for pool in known_pools:
        analysis_list =cdb.static_db.get_analyses(poolid=pool,filter=False)

        if not analysis_list:
            continue

        f = open(os.path.join(output_directory, pool + ".ana"), 'w')
        envStrings[pool] = "export CONTUR_RA_{}=\"".format(pool)
        for analysis in analysis_list:
            f.write(rivettxt + analysis.name + " # " + analysis.summary() + "\n")
            envStrings[pool] = envStrings.get(pool) + analysis.name + ","
    
        f.close()	

    # write environment setter file        
    for estr in envStrings.values():
        if estr.endswith(","):
            estr = estr[:len(estr) - 1]
        estr += "\""
        fl.write(estr + "\n \n")
    for estr in envStrings_all.values():
        if estr.endswith(","):
            estr = estr[:len(estr) - 1]
        estr += "\""
        fl.write(estr + "\n \n")
        
    fl.close()
        
    cfg.contur_log.info("Analysis and environment files written to {}".format(output_directory))

    if not webpages:
        return
    else:
        rst_utils.write_measurement_list()
    
def main(args):
    """
    Main programme to run over the known analysis and build SM theory yodas from the TheoryRaw or REF areas.
    """
    setup_common(args)
    print("Writing log to {}".format(cfg.logfile_name))
    setup_mysql(args)

    cfg.contur_log.info("Making shared area in {}".format(cfg.output_dir))

    # build DB
    DB = build_database.BuildDB('analyses.db')
    DB.build_db()

    cfg.results_dbfile = os.path.join(cfg.output_dir,cfg.results_dbfile)
    cfg.models_dbfile = os.path.join(cfg.output_dir,cfg.models_dbfile)

     

    try:
        import yoda
        import rivet
        import contur.data.data_access_db
        if cfg.use_mysql:
            cdb.data_access_db.generate_mysql_model_db()
        else:
            cdb.data_access_db.generate_model_and_parameter(model_db=True)
        generate_rivet_lists(args['WEBPAGES'])
        debug('Successfully found RIVET and YODA Python module')
    except ImportError as ie:
        if cfg.use_mysql:
            cdb.data_access_db.generate_mysql_model_db()
        else:
            cdb.data_access_db.generate_model_and_parameter(model_db=True)
        warning('Warning: modules (maybe rivet and yoda?) not found, contur functionality will be limited')
        warning(ie)
        


