import pytest
from pytest import raises
import os
import numpy as np
from importlib import reload
import contextlib
import contur
import contur.factories.likelihood as lh
from contur.factories.test_observable import ObservableValues
import contur.config.config as cfg

# some functions require the logger to exist, so set it up here
cfg.setup_logger("{0}.log".format('likelihoods'))

@contextlib.contextmanager
def temporary_config(**kwargs):
    # Store original values
    original_values = {key: getattr(cfg, key) for key in kwargs.keys()}
    
    # Update config with temporary values
    for key, value in kwargs.items():
        setattr(cfg, key, value)
    
    try:
        yield
    finally:
        # Restore original values
        for key, value in original_values.items():
            setattr(cfg, key, value)

# tests of Likelihood.__init__ 
@pytest.fixture
def empty_likelihood():
    return lh.Likelihood()

def test_covariances_not_built_when_likelihood_empty(empty_likelihood):
    assert not empty_likelihood._covariances
def test_test_stats_not_built_when_likelihood_empty(empty_likelihood):
    assert all(not empty_likelihood.results[key] for key in cfg.stat_types), "Results dict should be empty when likelihood is empty"

# each of the below fixtures return an ObservableValues object, with default values that can be overridden
# they also have a switch to return None, for testing cases where some None values are passed tom Likelihood
@pytest.fixture
def bsm_values():
    def _bsm_values(make_bsm_none=False,
                    bsm_vals=np.ones(5), 
                    bsm_errs=np.full(5, 0.1), 
                    bsm_diag=np.eye(5), 
                    bsm_cov=np.zeros((5, 5))):
        if make_bsm_none:
            return None
        return ObservableValues(central_values=bsm_vals, err_breakdown=bsm_errs, covariance_matrix=bsm_cov, diagonal_matrix=bsm_diag)
    return _bsm_values

@pytest.fixture
def sm_values():
    def _sm_values(make_sm_none=False,
                   sm_vals=np.full(5, 4.), 
                   sm_errs=np.full(5, 0.8), 
                   sm_diag=np.diag(np.full(5, np.sqrt(0.8))), 
                   sm_cov=np.array([[5, 2, 3, 4, 1], [1, 6, 2, 1, 3], [2, 3, 7, 1, 0], [4, 2, 1, 8, 5], [3, 1, 4, 2, 9]])):
        if make_sm_none:
            return None
        return ObservableValues(central_values=sm_vals, err_breakdown=sm_errs, covariance_matrix=sm_cov, diagonal_matrix=sm_diag)
    return _sm_values

@pytest.fixture
def data_values():
    def _data_values(make_data_none=False,
                     data_vals=np.full(5, 4.), 
                     data_errs=np.full(5, 0.4), 
                     data_diag=np.diag(np.full(5, np.sqrt(0.4))), 
                     data_cov=np.array([[5, 2, 3, 4, 1], [1, 6, 2, 1, 3], [2, 3, 7, 1, 0], [4, 2, 1, 8, 5], [3, 1, 4, 2, 9]])):
        if make_data_none:
            return None
        return ObservableValues(central_values=data_vals, err_breakdown=data_errs, covariance_matrix=data_cov, diagonal_matrix=data_diag)
    return _data_values

@pytest.fixture
def exp_values():
    def _exp_values(make_exp_none=False,
                    exp_vals=np.full(5, 4.), 
                    exp_errs=np.full(5, 0.4), 
                    exp_diag=np.diag(np.full(5, np.sqrt(0.4))), 
                    exp_cov=np.array([[5, 2, 3, 4, 1], [1, 6, 2, 1, 3], [2, 3, 7, 1, 0], [4, 2, 1, 8, 5], [3, 1, 4, 2, 9]])):
        if make_exp_none:
            return None
        return ObservableValues(central_values=exp_vals, err_breakdown=exp_errs, covariance_matrix=exp_cov, diagonal_matrix=exp_diag)
    return _exp_values

# Helper function to filter kwargs for a specific function
def filter_kwargs(func, kwargs):
    # Get the argument names for the function
    arg_names = func.__code__.co_varnames[:func.__code__.co_argcount]
    # Return the subset of kwargs that match the function's arguments
    return {k: v for k, v in kwargs.items() if k in arg_names}

# pytest factory
@pytest.fixture
def filled_likelihood(bsm_values, sm_values, data_values, exp_values):
    def _filled_likelihood(calculate=True, 
                           tags='/ATLAS_2022_I2023464/d02-x01-y01', 
                           **kwargs):
        

        bsm_args = filter_kwargs(bsm_values, kwargs)
        sm_args = filter_kwargs(sm_values, kwargs)
        data_args = filter_kwargs(data_values, kwargs)
        exp_args = filter_kwargs(exp_values, kwargs)

        print(bsm_args,sm_args,data_args,exp_args)

        print(data_values(**data_args).covariance_matrix)
        print(data_values(**data_args).diagonal_matrix)
        print(data_values(**data_args).err_breakdown)

        return lh.Likelihood(
            calculate=calculate,
            sm_values=sm_values(**sm_args),
            bsm_values=bsm_values(**bsm_args),
            measured_values=data_values(**data_args),
            expected_values=exp_values(**exp_args),
            tags=tags
        )
    return _filled_likelihood

# some tests with default values
def test_covariances_not_built_when_calculate_false(filled_likelihood):
    assert not filled_likelihood(calculate=False)._covariances, "Covariance matrices shouldn't build unless calculate=True"

def test_signal_stats_constructed(filled_likelihood):

    assert all('ts_s_b' in filled_likelihood().results[key] for key in cfg.stat_types), "Not all signal test stats were constructed"

def test_signal_test_stats_not_none(filled_likelihood):
    assert all(filled_likelihood().results[key]['ts_s_b'] is not None for key in cfg.stat_types), "Some signal test stats are None"

def test_background_test_stats_constructed(filled_likelihood):
    assert all('ts_b' in filled_likelihood().results[key] for key in cfg.stat_types), "Not all background test stats were constructed"

def test_background_test_stats_not_none(filled_likelihood):
    assert all(filled_likelihood().results[key]['ts_b'] is not None for key in cfg.stat_types), "Some background test stats are None"

# tests for non-default values
def test_likelihood_with_none_bsm(filled_likelihood):
    likelihood = filled_likelihood(make_bsm_none=True)
    
    assert np.allclose(likelihood._statCov,np.zeros(5)), "BSM statistical error assigned nonzero when BSM signal is zero"

def test_likelihood_raise_when_no_measurement_errors(filled_likelihood):
    with raises(cfg.ConturError):
        filled_likelihood(data_diag=None,data_cov=None,data_errs=None)

def test_single_bin_method(filled_likelihood):
    with temporary_config(diag=True,min_num_sys=100):
        likelihood = filled_likelihood(data_cov=None)
        assert likelihood._singleBin 

# tests for ts_to_pval method
def test_ts_to_pval_monotonic():
    assert lh.ts_to_pval(0) > lh.ts_to_pval(1)    

def test_ts_to_pval_pass_numpy_array():  
    numpy_array = np.array([[1,2], [3,4]])
    assert lh.ts_to_pval(numpy_array).shape == (2,2)

# tests for ts_to_cls method
def test_ts_to_cls_passing_a_single_tuple_in_list_return_single_cls():
    test_stats = [(1,1)]
    print(test_stats)
    assert len(lh.ts_to_cls(test_stats,"test")) == 1

def test_ts_to_cls_signal_equals_background_cls_zero():
    test_stats = [(1,1)]
    assert lh.ts_to_cls(test_stats,"test")[0] == 0

def test_ts_to_cls_signal_greater_than_background_cls_between_0_1():
    test_stats = [(1,0)]
    assert (lh.ts_to_cls(test_stats,"test")[0] < 1) and (lh.ts_to_cls(test_stats,"test")[0] > 0)

def test_ts_to_cls_signal_less_background_set_to_zero():
    test_stats = [(0,1)]
    assert lh.ts_to_cls(test_stats,"test")[0] == 0

def test_ts_to_cls_passed_tuple_same_as_list(): 
    test_stats = (1,1)
    test_stats_list = [test_stats]
    assert lh.ts_to_cls(test_stats,"test") == lh.ts_to_cls(test_stats_list,"test")

def test_sort_blocks_throws_exception_if_passed_empty_list(): 
    with raises(ValueError) as exception:
        lh.sort_blocks([],cfg.databg)

def test_build_full_likelihood_throws_exception_if_passed_empty_list(): 
    with raises(ValueError) as exception:
        lh.build_full_likelihood([],cfg.databg)
        
def test_like_block_ts_to_cls_throws_exception_if_passed_empty_list(): 
    with raises(ValueError) as exception:
        lh.likelihood_blocks_ts_to_cls([],cfg.databg)

def test_find_dominant_ts_throws_exception_if_passed_empty_list(): 
    with raises(ValueError) as exception:
        lh.likelihood_blocks_find_dominant_ts([],cfg.databg)
