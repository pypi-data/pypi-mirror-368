try:
    import yoda, rivet, contur
except:
    print("Exiting test suite, could not find the dependencies of YODA, Rivet or contur in PYTHONPATH")
    raise

import os
import shutil

import pytest
import yaml

from test_executables import build_executable_cmd
from contur.run.run_batch_submit import batch_submit
from contur.run.run_init import generate_rivet_lists
from contur.run.arg_utils import get_args
import contur.config.config as cfg

test_dir = os.path.dirname(os.path.abspath(__file__))

args_path = os.path.join(test_dir, 'sources/batch_cl_args.yaml')
with open(args_path, 'r') as f:
    arguments_examples = yaml.load(f, yaml.FullLoader)

# define the test sandbox
result_dir = cfg.paths.user_path("tests")

try:
    os.makedirs(result_dir) #, exist_ok=True) #< exist_ok requires Py > 3.2
except:
    pass

@pytest.mark.first
def test_generate_rivet_anas():
    cfg.output_dir = result_dir+"/share"
    # Set up logger
    cfg.setup_logger("contur_mkana.log")
    generate_rivet_lists(False)

main_run_cmds = {}

for k,v in arguments_examples.items():
    cmd = build_executable_cmd(v) 
    cfg.output_dir = result_dir
    cfg.run_info = result_dir+"/RunInfo"
    cfg.batch_output_dir=os.path.join(result_dir,cfg.batch_output_dir)
    parser = get_args(cmd[1:],'batch_submit')
    main_run_cmds[k] = get_args(cmd[1:],'batch_submit')

@pytest.mark.parametrize("fixture", main_run_cmds.values(), ids=main_run_cmds.keys())
def test_run_main(fixture):
    #cfg.output_dir = result_dir
    #cfg.run_info = result_dir+"/RunInfo"
    batch_submit(fixture)


