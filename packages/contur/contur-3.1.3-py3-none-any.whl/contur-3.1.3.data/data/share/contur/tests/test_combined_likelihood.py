import pytest
from pytest import raises
from unittest.mock import MagicMock
import os
import numpy as np
from importlib import reload
import contur
import contur.config.config as cfg

from contur.factories.likelihood import Likelihood, CombinedLikelihood

# some functions require the logger to exist, so set it up here
cfg.setup_logger("{0}.log".format('likelihoods'))

def test_raise_for_invalid_stat_type():
    with raises(ValueError):
        CombinedLikelihood(stat_type='bad stat type')

@pytest.fixture
def mock_likelihood():
    """
    Returns a mock instance of the Likelihood class for use in tests of CombinedLikelihood
    """
    mock_likelihood = MagicMock()

    test_stats = {stat_type:value for stat_type,value in zip(cfg.stat_types,range(1,5))}

    mock_likelihood._ts_s_b = test_stats
    mock_likelihood._ts_b = test_stats
    return mock_likelihood

@pytest.fixture
def one_stat_cl():
    return CombinedLikelihood(stat_type=cfg.smbg)

@pytest.fixture
def all_stats_cl():
    return CombinedLikelihood()

def test_add_likelihood_updates_all_test_stats(mock_likelihood,all_stats_cl):
    """
    In this case, the 'add_likelihood' method should update the test stats for each stat type
    """

    all_stats_cl.add_likelihood(mock_likelihood)

    assert all(all_stats_cl.get_ts_s_b(stat_type) == mock_likelihood.get_ts_s_b(stat_type) for stat_type in all_stats_cl.stat_types)
    assert all(all_stats_cl.get_ts_b(stat_type) == mock_likelihood.get_ts_b(stat_type) for stat_type in all_stats_cl.stat_types)

def test_add_likelihood_only_updates_one_stat_type(mock_likelihood,one_stat_cl):
    """
    In this case, the 'add_likelihood' method should only update the stat type of the CombinedLikelihood
    """
    test_stat = one_stat_cl.stat_types[0]

    other_stat_types = [x for x in cfg.stat_types if x != test_stat]

    one_stat_cl.add_likelihood(mock_likelihood)

    # this one should have updated
    assert one_stat_cl.get_ts_s_b(test_stat) == mock_likelihood.get_ts_s_b(test_stat)
    # these keys should all be None
    assert all([one_stat_cl.results[stat_type].get('ts_s_b') is None for stat_type in other_stat_types])

    # test background stats
    assert one_stat_cl.get_ts_b(test_stat) == mock_likelihood.get_ts_b(test_stat)
    assert all([one_stat_cl.results[stat_type].get('ts_b') is None for stat_type in other_stat_types])

# all the getter methods work in an equivalent way, so want to do the same tests on them
@pytest.mark.parametrize("method", [
    lambda obj: obj.getCLs(),  
    lambda obj: obj.get_ts_b(),  
    lambda obj: obj.get_ts_s_b()  
])
def test_getter_requires_stat_type(method, all_stats_cl):
    with raises(TypeError):
        method(all_stats_cl)

@pytest.mark.parametrize("method", [
    lambda obj: obj.getCLs('bad stat type'),
    lambda obj: obj.get_ts_b('bad stat type'),
    lambda obj: obj.get_ts_s_b('bad stat type')
])
def test_getter_raise_for_bad_stat_type(method, all_stats_cl):
    with raises(KeyError):
        method(all_stats_cl)

@pytest.mark.parametrize("method", [
    lambda obj, stat: obj.getCLs(stat),
    lambda obj, stat: obj.get_ts_b(stat),
    lambda obj, stat: obj.get_ts_s_b(stat)
])
def test_getter_returns_none(method, all_stats_cl):
    assert all(method(all_stats_cl, stat) is None for stat in cfg.stat_types)

# setter tests
@pytest.mark.parametrize("method", [
    lambda obj, stat: obj.set_ts_b(stat),
    lambda obj, stat: obj.set_ts_s_b(stat)
])
def test_stat_setter_raise(method, one_stat_cl):
    """
    If CombinedLikelihood was instantisated with a single stat type, 
    shouldn't be able to modify the test stats for other stat types
    """
    test_stat = one_stat_cl.stat_types[0]
    other_stat_types = [x for x in cfg.stat_types if x != test_stat]

    for stat in other_stat_types:
        with raises(TypeError):
            method(one_stat_cl,stat)
