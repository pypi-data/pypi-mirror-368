import pickle
import os
import contur.config.config as cfg
import contur.factories.depot
import contur.util.utils as cutil

def export(in_path, out_path, include_dominant_pools=False, include_per_pool_cls=False):

    cfg.setup_logger(filename="contur-export.log")
    cutil.mkoutdir(os.path.dirname(out_path))
    
    # First try reading as a database
    try:

        # Run the conturPlot processing, should allow to read the input db file from command line
        contur_depot = contur.factories.depot.Depot()
        # read the result database into Depot class
        contur_depot.add_points_from_db(in_path)
        cfg.contur_log.info("Read DB file {}".format(in_path))

    except Exception as ex:

        cfg.contur_log.info("Could not read {} as db file.".format(in_path))
        cfg.contur_log.info("Caught exception:{}".format(ex))
        raise

    cfg.csvfile = out_path
    contur_depot.write(".", None, include_dominant_pools=include_dominant_pools, include_per_pool_cls=include_per_pool_cls)
