import pytest
from pytest import raises
import pickle
import os
import numpy as np
from importlib import reload
import contur
import contur.data.static_db as cdb

test_dir = os.path.dirname(os.path.abspath(__file__))
args_path = os.path.join(test_dir, 'sources/likelihood_data.p')
with open(args_path, 'rb') as f:
    master_data_dic = pickle.load(f)

contur.config = reload(contur.config)

# tests for building objects
def test_data_objects():
    analyses = cdb.get_analyses(filter=False)

    for analysis in analyses:
        pool = analysis.get_pool()
        beams = cdb.get_beams(pool.id)
        for beam in beams:
            assert beam.id == analysis.beamid
        
    

