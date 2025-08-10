try:
    import yoda, rivet, contur
except:
    print("Exiting test suite, could not find the dependencies of YODA, Rivet or contur in PYTHONPATH")
    raise
    
import os
import shutil

import pytest
import yaml

import pickle as pkl
from pandas._testing import assert_frame_equal

import contur.config.config as cfg

test_dir = os.path.join(os.getenv("PWD"))
# define the test sandbox
result_dir = cfg.paths.user_path("tests")

from contur.run.run_analysis import main as main_ana
from contur.run.run_smtest import main as main_sm
from contur.run.run_extract_xs_bf import main as main_xsbf
from contur.run.run_plot import main as main_mapplot
from contur.run.run_mkplots import main as main_rivetplots
from contur.run.arg_utils import get_args
from contur.export.contur_export import export
from contur.oracle.cli import start_oracle
import numpy as np

from importlib import reload 

args_path = os.path.join(test_dir, 'sources/grid_cl_args.yaml')
with open(args_path, 'r') as f:
    arguments_examples = yaml.load(f, yaml.FullLoader)


def build_executable_cmd(cl_args_dict):
    cl_string=[cl_args_dict["command"]]
    try:
        for v in cl_args_dict["args"]:
            #load the optional args to a string
            cl_string.append("{}".format(v))
    except:
        pass
    try:
        for k,v in cl_args_dict["options"].items():
            #load the optional args to a string
            cl_string.append("--%s=%s" % (k,v))
    except:
        pass
    try:
        for v in cl_args_dict["switches"]:
            #load the optional switches to the string
            cl_string.append("-%s" % v)
    except:
        pass

    return cl_string


main_run_cmds={}

for k,v in arguments_examples.items():
    cmd=build_executable_cmd(v)
    cfg.output_dir=result_dir
    cfg.input_dir=result_dir
    if "contur-smtest" in cmd:
        cfg.smdir=result_dir+"/sm_plots"
        main_run_cmds[k]=get_args(cmd[1:],'smtest')
    elif "contur-extract-xs-bf" in cmd:
        main_run_cmds[k]=get_args(cmd[1:],'extract_xs_bf')
    elif "contur-plot" in cmd:
        main_run_cmds[k]=get_args(cmd[1:],'plot')
    elif "contur-oracle" in cmd:
        v1=v
        v1['oracle_test']=None
        main_run_cmds[k]=v1
    elif "contur-rivetplots" in cmd:
        main_run_cmds[k]=get_args(cmd[1:],'mkhtml')
    else:
        main_run_cmds[k]=get_args(cmd[1:],'analysis')


#@pytest.mark.first
@pytest.mark.parametrize("fixture", main_run_cmds.values(), ids=main_run_cmds.keys())
def test_run_main(fixture):
    contur.config.config = reload(contur.config.config)
    cfg.output_dir=result_dir
    cfg.input_dir=result_dir
    if "yodafiles" in fixture.keys():
        if 'contur_run.db' in fixture.values():
            cfg.output_dir=result_dir+"/DEFAULT"
        elif 'spey_results.db' in fixture.values():
            cfg.output_dir=result_dir+"/SPEY"
        elif 'single_results.db' in fixture.values():
            cfg.output_dir=result_dir+"/SINGLE"
        elif 'contur_databg.db' in fixture.values():
            cfg.output_dir=result_dir+"/DATABG"
        elif 'single_results_noExp.db' in fixture.values():
            cfg.output_dir=result_dir+"/NOEXP"
        main_ana(fixture)
    elif "foldBRs" in fixture.keys():
        main_xsbf(fixture)
    elif "variables" in fixture.keys():
        cfg.output_dir=result_dir+"/conturPlot"
        cfg.input_dir=result_dir+"/DEFAULT/ANALYSIS"
        main_mapplot(fixture)
    elif "oracle_test" in fixture.keys():
        oracle_dir = os.path.join(result_dir,"oracle")
        os.system("cp -r sources/oracle {}".format(result_dir))
        # if you have set your $CONTUR_DATA_PATH to be not writeable by you (permissions testing) this may be needed.
        #os.system("chmod -R ou+w {}/oracle".format(result_dir))
        os.system("cp {}/oracle.config.0.yaml {}/oracle.config.yaml".format(oracle_dir,oracle_dir))
        start_oracle(oracle_dir)
    elif "RUNPOINT" in fixture.keys():
        if fixture['NO_EXP']:
            # no exp
            cfg.input_dir=result_dir+"/NOEXP/ANALYSIS"
            cfg.output_dir=result_dir+"/NOEXP/plots"
        elif fixture['DATABG']:
            # databg
#            cfg.input_dir=result_dir+"/DATABG/ANALYSIS"
#            cfg.output_dir=result_dir+"/DATABG/plots"
            cfg.input_dir=result_dir+"/SINGLE/ANALYSIS"
            cfg.output_dir=result_dir+"/SINGLE/plots"
        elif ['ATLAS_2024_I2765017'] in fixture.values():
            cfg.input_dir=result_dir+"/SINGLE/ANALYSIS"
            cfg.output_dir=result_dir+"/SINGLE/plots"
            
        main_rivetplots(fixture)
    else:
        cfg.smdir=result_dir+"/sm_plots"
        main_sm(fixture)


def test_regression_single_yoda_run():
    """
    Regression test of current contur output on single yoda file against base 
    output given by live version of contur code run on same yoda file.
    
    Test will fail if an update to contur code changes output from
    a single contur run
    
    """

    args_path = os.path.join(test_dir, 'sources/single_results.db')
    base_depot = contur.factories.depot.Depot()
    base_depot.add_points_from_db(args_path)
    base = base_depot._build_frame(include_dominant_pools=True,include_per_pool_cls=True)
        
    args_path = os.path.join(result_dir, 'SINGLE/ANALYSIS', 'single_results.db')
    target_depot = contur.factories.depot.Depot()
    target_depot.add_points_from_db(args_path)
    target = target_depot._build_frame(include_dominant_pools=True,include_per_pool_cls=True)

    assert_frame_equal(base, target, check_like=True) # ignore column order

def test_regression_grid_run():
    """
    Regression test of current contur output on grid against base 
    output given by live version of contur code run on same the same grid.
    
    Test will fail if an update to contur code changes the map file (read with pickle
    to get the Depot contur object) output from a grid run
    
    """

    args_path = os.path.join(test_dir, 'sources/contur_run.db')
    base_depot = contur.factories.depot.Depot()
    base_depot.add_points_from_db(args_path)
    base = base_depot._build_frame(include_dominant_pools=True,include_per_pool_cls=False)
        
    args_path = os.path.join(result_dir, 'DEFAULT/ANALYSIS', 'contur_run.db')
    target_depot = contur.factories.depot.Depot()
    target_depot.add_points_from_db(args_path)
    target = target_depot._build_frame(include_dominant_pools=True,include_per_pool_cls=False)

    assert_frame_equal(base, target, check_like=True) # ignore column order
    
def test_spey_regression_grid_run():
    """
    Regression test of current contur output on grid against base 
    output given by live version of contur code run on same the same grid.
    
    Test will fail if an update to contur code changes the map file (read with pickle
    to get the Depot contur object) output from a grid run
    
    """

    args_path = os.path.join(test_dir, 'sources/spey_results.db')
    base_depot = contur.factories.depot.Depot()
    base_depot.add_points_from_db(args_path)
    base = base_depot._build_frame(include_dominant_pools=True,include_per_pool_cls=False)
        
    args_path = os.path.join(result_dir, 'SPEY/ANALYSIS', 'spey_results.db')
    target_depot = contur.factories.depot.Depot()
    target_depot.add_points_from_db(args_path)
    target = target_depot._build_frame(include_dominant_pools=True,include_per_pool_cls=False)

    assert_frame_equal(base, target, check_like=True) # ignore column order   

def test_export():
    """
    Regression test of exporting a map to csv 
    
    Test will fail if an update to contur-export code changes the format of the resulting csv.
    
    """
    
    args_path = os.path.join(test_dir, 'sources/contur.csv')
    with open(args_path) as sf:
        base = sf.read().splitlines(True)
    args_path = os.path.join(result_dir, 'DEFAULT/ANALYSIS','contur.csv')
    with open(args_path) as sf:
        target = sf.read().splitlines(True)

    #assert base == pytest.approx(target):
    
    # some bs because python 3.10/pytest is bust
    # use the above line if it gets fixed...    
    base_float = []
    target_float = []
    for val in base:
        try:
            val = float(val)
            base_float.append(val)                
        except:
            pass
    for val in target:
        try:
            val = float(val)
            target_float.append(val)                
        except:
            pass

    if not np.allclose(np.array(base_float,dtype=float),np.array(target_float,dtype=float)):
        assert(False)

    
    

