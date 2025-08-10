import pytest
import os
import pickle
from importlib import reload
import contur
from contur.run.arg_utils import get_argparser
from contur.run.arg_utils import get_args
from contur.run.run_analysis import main
import contur.config.config as cfg
import contur.util.utils as cutil
import gzip
from io import StringIO
import numpy as np
import sqlite3
import pandas as pd
from pandas.testing import assert_frame_equal

def reload_contur():
    reload(contur)
    reload(contur.config.config)
    reload(contur.run.arg_utils)
    reload(contur.run.run_analysis)

@pytest.fixture(autouse=True)
def setup_and_reload():
    # Reload contur to reset any shared state before each test
    reload_contur()
    # Cleanup previous test results if necessary
    yield
    
    # can add cleanup here


test_dir = os.path.join(os.getenv("PWD"))
# define the test sandbox
result_dir = cfg.paths.user_path("tests")

def test_yodastream(setup_and_reload):

    sourcepath = os.path.join(test_dir, "sources/myscan00/13TeV/0003/runpoint_0003.yoda.gz")

    with gzip.open(sourcepath, 'rt') as f:
        yodastream = StringIO(f.read())

    yodastream.seek(0)
    args = get_args("", "analysis")

    args["YODASTREAM"] = yodastream
    #Ask for all output types to test fully.
    args['YODASTREAM_API_OUTPUT_OPTIONS'] = ["LLR", "Pool_LLR", "Pool_tags", "CLs", "Pool_CLs"]

    #TODO @TP: copied this from the other tests. Is it needed?
    #    contur.config = reload(contur.config)

    summaryDict = main(args)
    stat_types = summaryDict.keys()
    #print("STAT",stat_types)
    
    comparisonpath = os.path.join(test_dir, "sources/yodastream_results_dict.pkl")
    with open(comparisonpath, 'rb') as f:
        compareDict = pickle.load(f)
    
    #Check consistency

    pkl_out = os.path.join(result_dir,"yodastream_results.pkl")

    try:

        #Dump a copy of the results dict for debugging if something is wrong
        #Or as a replacement version if e.g. new analyses/theory available. 
        cutil.mkoutdir(result_dir)
        with open(pkl_out, "wb") as f:
            pickle.dump(summaryDict, f)

        if not (
                #LLR Values must be consistent -> this should mean CLs is also fine.
                (np.allclose(np.array([compareDict[i]["LLR"] for i in stat_types], dtype=float),
                             np.array([summaryDict[i]["LLR"] for i in stat_types], dtype=float))) and
                #Pool-by-pool LLR values must also be consistent
                (np.allclose(np.concatenate([np.array(list(compareDict[i]["Pool_LLR"].values())) for i in stat_types]),
                             np.concatenate([np.array(list(summaryDict[i]["Pool_LLR"].values())) for i in stat_types])))
                ):

            print("TOTALS")
            for i in stat_types:
                if not np.isclose(compareDict[i]["LLR"],summaryDict[i]["LLR"]):
                    print(compareDict[i]["LLR"],summaryDict[i]["LLR"])
            
            print("POOLS")
            print(np.concatenate([np.array(list(compareDict[i]["Pool_LLR"].values())) for i in stat_types]))
            print(np.concatenate([np.array(list(summaryDict[i]["Pool_LLR"].values())) for i in stat_types]))

            print("Results do not match expected values - has an analysis been added?")
            assert(False)

            
    except Exception as ex:
        #Dump a copy of the results dict for debugging if something is wrong
        #Or as a replacement version if e.g. new analyses/theory available.
        cutil.mkoutdir(result_dir)
        with open(pkl_out, "wb") as f:
            pickle.dump(summaryDict, f)
        print("Results do not match expected values - has an analysis been added?")
        assert(False)
        raise
    
def test_yodastream_consistent_with_single_default(setup_and_reload):
    """
    Checks that running on a single file produces the same results when run on a yodastream vs not
    """
    sourcepath = os.path.join(test_dir, "sources/myscan00/13TeV/0003/runpoint_0003.yoda.gz")

    with gzip.open(sourcepath, 'rt') as f:
        yodastream = StringIO(f.read())

    yodastream.seek(0)
    args = get_args("", "analysis")

    args["YODASTREAM"] = yodastream
    #Ask for all output types to test fully.
    args['YODASTREAM_API_OUTPUT_OPTIONS'] = ["LLR", "Pool_LLR", "Pool_tags", "CLs", "Pool_CLs"]

    # apply the same switches as for the single test
    # -s -u --whw --wbv --awz
    args["USESEARCHES"] = args["UNCORR"] = args["DATABG"] = True
    #args["USESEARCHES"] = args["UNCORR"] = args["USEHWW"] = args["USEBV"] = args["USEAWZ"] = True

    summaryDict = main(args)
    stat_types = summaryDict.keys()

    # load output from single_default
    db_path = os.path.join(test_dir,'sources','single_results.db')
    query = 'SELECT * from exclusions'
    print(f'reading single_default results from {db_path}')

    with sqlite3.connect(db_path) as conn:
        single_results = pd.read_sql_query(query, conn)

    # convert yodastream dict to match db format
    yodastream_list_of_dicts = []
    for stat_type in stat_types:
        pools = summaryDict[stat_type]['Pool_CLs'].keys()

        for pool in pools:
            exclusion = summaryDict[stat_type]['Pool_CLs'][pool]
            histos = summaryDict[stat_type]['Pool_tags'][pool]

            yodastream_list_of_dicts.append({'pool_name':pool, 'stat_type':stat_type, 'exclusion':exclusion, 'histos':histos})
    
    yodastream_df = pd.DataFrame(yodastream_list_of_dicts)
    single_results = single_results[['pool_name','stat_type','exclusion','histos']]

    # write to csv for debugging
    cutil.mkoutdir(result_dir)
    yodastream_out_path = os.path.join(result_dir,'yodastream_compare_to_single.csv')
    print(f'writing results from yodastream to: {yodastream_out_path}')
    yodastream_df.to_csv(yodastream_out_path)

    # order them the same
    single_results = single_results.sort_values(by=['pool_name','stat_type'], ignore_index=True)
    yodastream_df = yodastream_df.sort_values(by=['pool_name','stat_type'], ignore_index=True)

    assert_frame_equal(single_results,yodastream_df,check_like=True)
