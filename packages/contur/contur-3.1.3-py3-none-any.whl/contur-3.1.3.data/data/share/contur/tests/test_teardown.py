try:
    import yoda, rivet, contur
except:
    print("Exiting test suite, could not find the dependencies of YODA, Rivet or contur in PYTHONPATH")
    raise
    
import os
import shutil

import pytest

import contur.config.config as cfg

test_dir = os.path.join(os.getenv("PWD"))
# define the test sandbox
result_dir = cfg.paths.user_path("tests")

@pytest.mark.last
def test_teardown_module():
    """Clean up test area"""

    if os.path.exists(result_dir):
        shutil.rmtree(result_dir)
