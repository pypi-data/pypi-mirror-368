"""

The Depot module contains the Depot class. This is intended to be the high level analysis control, 
most user access methods should be implemented at this level

"""

import os
import pickle
import numpy as np
import sqlite3 as db 
import scipy.stats as spstat
import contur
import contur.factories.likelihood as lh
import contur.config.config as cfg
import contur.util.utils as cutil
from contur.factories.yoda_factories import YodaFactory
from contur.factories.likelihood_point import LikelihoodPoint
from contur.data.data_access_db import write_grid_data
from contur.data.data_access_db import open_for_reading
import contur.plot.yoda_plotting as cplot
from yoda.plotting import script_generator




class Depot(object):
    """ Parent analysis class to initialise

    This can be initialised as a blank canvas, then the desired workflow is to add parameter space points to the Depot using
    the :func:`add_point` method. This appends each considered point to the objects internal :attr:`points`. To get the point 
    from a database to the Depot use the :func:`add_points_from_db` method. 

    Path for writing out objects is determined by cfg.plot_dir

    """

    def __init__(self):

        self._point_list = []

    def write(self, outDir, args, yodafile=None, include_dominant_pools=True, include_per_pool_cls=True):
        """Function to write depot information to disk
        
        write a results db files to outDir
        if cfg.csvfile is not None, also write out a csv file containing the data

        :param outDir:
            String of filesystem location to write out the pickle of this instance to
        :type outDir: ``string``

        """
        cutil.mkoutdir(outDir)

        # populate the local database for this grid
        if args is not None:
            try:
                write_grid_data(self,args,yodafile)
            except cfg.ConturError as ce:
                cfg.contur_log.error("Failed to write results database. Error was: {}".format(ce))

        if cfg.csvfile is not None:
            path_out = os.path.join(outDir,cfg.csvfile)
            cfg.contur_log.info("Writing output csv to : " + path_out)
            self.export(path_out, include_dominant_pools=include_dominant_pools, include_per_pool_cls=include_per_pool_cls)

    def add_point(self, yodafile, param_dict):
        """
        Add yoda file and the corresponding parameter point into the depot
        """

        try:
            yFact = YodaFactory(yodaFilePath=yodafile)
            lh_point = LikelihoodPoint(yodaFactory=yFact, paramPoint=param_dict)
            lh_point.set_run_point(cfg.runpoint)

        except cfg.ConturError as ce:
            cfg.contur_log.warning(ce)
            cfg.contur_log.warning("Skipping file.")
            return
        
        for likehd in lh_point.likelihood_blocks:
            # set the model to the dominant bin for cases where we have no covariance matrix
            for stat_type in cfg.stat_types:
                likehd.find_dominant_bin(stat_type)

            if cfg.use_spey:
                # cleanup after we've found the dominant bin
                likehd.cleanup_model_list()

            for stat_type in cfg.stat_types:
                # get CLs for each block
                likehd.calculate(stat_type)
        obs_excl_dict = {}
        cfg.contur_log.debug('Writing plotting scripts')
        for observable in yFact.observables:
            
            exclusions = {}
            for stat_type in cfg.stat_types:
                exclusions[stat_type] = observable.likelihood.get_results(stat_type)
            obs_excl_dict[observable.signal.path()] = exclusions

            # write out the plotting scripts here, now CLs have been calculated
            if not cfg.silenceWriter:
                        
                # create output dir for each analysis
                if not cfg.gridMode :
                    scriptsOutdir = os.path.join(cfg.script_dir, observable.pool, observable.analysis.name)
                    # plotsOutdir = os.path.join(cfg.plot_dir, observable.pool, observable.analysis.name)
                else:
                    scriptsOutdir = os.path.join(cfg.script_dir, cfg.runpoint, observable.pool, observable.analysis.name)
                cutil.mkoutdir(scriptsOutdir)
                # cutil.mkoutdir(plotsOutdir)
                
                # get YODA objects for BSM + SM, theory and data + BG
                thisPathYodaFiles = cplot.createYODAPlotObjects(observable, nostack=cfg.nostack)

                # get plot contents, pass YODA dict and reference data YODA object.
                plotContents = cplot.assemble_plotting_data(observable, thisPathYodaFiles)

                # create scripts
                pyScript = script_generator.process(plotContents, observable.signal.path(), scriptsOutdir.rsplit('/',1)[0], ["PDF", "PNG"])

                if cfg.use_spey and observable.likelihood.getCLs(cfg.smbg) is not None:
                    observable.likelihood.make_chi2_script(output_dir=scriptsOutdir)
                            

        # combine subpools (does it for all test stats, but has to be done after we have found the dominant bin for each test stat (above)
        subpool_lh = lh.combine_subpool_likelihoods(lh_point.likelihood_blocks)
        cfg.contur_log.debug('Finished building subpool likelihoods')
        # update histogram exclusions to reflect the exclusion of the subpool they are in, if any.
        for observable_path, exclusions in obs_excl_dict.items():
            for sp_lh in subpool_lh:
                if observable_path in sp_lh.tags:
                    for stat_type in cfg.stat_types:
                        exclusions[stat_type]['CLs'] = sp_lh.getCLs(stat_type)
                        exclusions[stat_type]['mu_lower_limit'] = sp_lh.get_mu_lower_limit(stat_type)
                        exclusions[stat_type]['mu_upper_limit'] = sp_lh.get_mu_upper_limit(stat_type)
                        exclusions[stat_type]['mu_hat'] = sp_lh.get_mu_hat(stat_type)

        lh_point.likelihood_blocks = lh_point.likelihood_blocks+subpool_lh
        lh_point.obs_excl_dict = obs_excl_dict

        msg = "Added yodafile {} with exclusions: ".format(yodafile)

        for stat_type in cfg.stat_types:


            try:

                #print(lh_point.likelihood_blocks,stat_type)
                # sort the blocks according to this test statistic
                lh_point.set_sorted_likelihood_blocks(lh.sort_blocks(lh_point.likelihood_blocks,stat_type),stat_type)
                lh_point.set_full_likelihood(stat_type,lh.build_full_likelihood(lh_point.get_sorted_likelihood_blocks(stat_type),stat_type))
                
                if lh_point.get_full_likelihood(stat_type) is not None:
                    msg+="\n     - {}={} ".format(stat_type,str(lh_point.get_full_likelihood(stat_type).getCLs(stat_type)))
                    lh_point.fill_pool_dict(stat_type)
                
                else:
                    msg+="\n     - {}=Not evaluated".format(stat_type)
        
            except ValueError:
                cfg.contur_log.warn("Not adding likelihood for {}".format(stat_type))

        cfg.contur_log.info(msg+"\n")
                
        try:
            lh_point.set_run_point(cfg.runpoint.split('/')[-1])
        except:
            lh_point.set_run_point(cfg.runpoint)
        cfg.contur_log.debug("adding point {}".format(lh_point))
        self._point_list.append(lh_point)

        
    def add_points_from_db(self, file_path, runpoint=None):
        """
        Get the info of model points from the result database into the depot class


        @TODO write a "get from DB" method for likelihood_point?
        """

        cfg.results_dbfile = os.path.join(os.getcwd(), file_path)
        conn = open_for_reading(cfg.results_dbfile)
        conn.row_factory = db.Row # read in rows as dicts
        c = conn.cursor()
        # start with map_id to select all related data info in a run
        id = c.execute("select id from map").fetchall()

        for map_id in id:
            map_id = map_id['id']

            # model point maybe should have a map id?            
            #  model_point_list = c.execute("select id from model_point where map_id = {};".format(map_id)).fetchall()
            model_point_list = c.execute("select id, yoda_files, run_point from model_point;").fetchall()

            for model_point in model_point_list:
            
                # if single runpoint is specified, no need to load the entire
                # grid into the depot
                if runpoint:
                    try:
                        # try parsing the runpoint for a model point ID
                        if runpoint.split('/')[1] != model_point['run_point']: continue
                    except:
                        cfg.contur_log.error("Could not parse the runpoint requested ({}).")
                        raise
                        
                # set a flag to avoid reading param_point repeatedly in the same point
                likelihood_point = LikelihoodPoint()
                param_point = {}
                search_sql1 = "select name, value from parameter_value where model_point_id =" + str(model_point['id']) + ";"
                param_names_values = c.execute(search_sql1).fetchall()
                # store parameter name and value in a dicionary
                for row in param_names_values:
                    param_point[row['name']] = row['value']

                # select all run_id which map_id and model_point_id are current
                try:
                    run_list = c.execute("select id,stat_type,combined_exclusion, mu_lower_limit, mu_upper_limit, mu_hat, events_num from run where model_point_id = {} and map_id = {};".format(model_point['id'],map_id)).fetchall()
                except db.OperationalError:
                    run_list = c.execute("select id,stat_type,combined_exclusion, events_num from run where model_point_id = {} and map_id = {};".format(model_point['id'],map_id)).fetchall()

                # get the per-histo exclusions
                # obs_exclusions can be large, so get info for all stat types in one pass
                obs_excl_dict = {}
                num_stat_types = len(run_list)
                if num_stat_types > 1:
                    run_ids = tuple([run[0] for run in run_list])
                else:
                    run_ids = "(1)"
                try:
                    rows = c.execute("select histo, stat_type, exclusion, mu_lower_limit, mu_upper_limit, mu_hat from obs_exclusions where run_id in {};".format(run_ids)).fetchall()
                except db.OperationalError: # backwards compatibility
                    rows = c.execute("select histo, stat_type, exclusion from obs_exclusions where run_id in {};".format(run_ids)).fetchall()
                
                for row in rows:
                    histo = row['histo']
                    stat_type = row['stat_type']
                    exclusion = row['exclusion']
                    if 'mu_lower_limit' in row.keys():
                        mu_lower_limit = row['mu_lower_limit']
                    else:
                        mu_lower_limit = None
                    if 'mu_upper_limit' in row.keys():
                        mu_upper_limit = row['mu_upper_limit']
                    else:
                        mu_upper_limit = None
                    if 'mu_hat' in row.keys():
                        mu_hat = row['mu_hat']
                    else:    
                        mu_hat = None

                    if not histo in obs_excl_dict.keys():
                        obs_excl_dict[histo] = {}

                    obs_excl_dict[histo][stat_type] = {'CLs':exclusion,  'mu_lower_limit':mu_lower_limit,'mu_upper_limit':mu_upper_limit, 'mu_hat':mu_hat}

                # not ideal that each stat_type is its own run...
                for run in run_list:
                    run_id = run['id']
                    num_events = run['events_num']
                    stat_type = run['stat_type']
                    combined_exclusion = run['combined_exclusion']
                    try:
                        combined_mu_low    = run['mu_lower_limit']
                        combined_mu_up     = run['mu_upper_limit']
                        combined_mu_hat    = run['mu_hat']
                    except IndexError:
                        # backward compatibility for dbs without these.
                        combined_mu_low    = None
                        combined_mu_up     = None
                        combined_mu_hat    = None
                        

                        
                    if "mu_lower_limit" and "mu_upper_limit" and "mu_hat" in c.execute("PRAGMA table_info(exclusions);").fetchall():
                        pool_exclusion_histos = c.execute("select pool_name, exclusion, mu_lower_limit, mu_upper_limit, mu_hat, histos from exclusions where run_id =" + str(run_id) + ";").fetchall()
                    else:
                        pool_exclusion_histos = c.execute("select pool_name, exclusion, histos from exclusions where run_id =" + str(run_id) + ";").fetchall()
                    # use dictionaries to store exclusion and histos for each pool, in each run
                    pool_exclusion = {}
                    pool_histos = {}
                    for row in pool_exclusion_histos:
                        pool = row['pool_name']
                        exclusion = row['exclusion']

                        if 'mu_lower_limit' in row.keys():
                            mu_lower_limit = row['mu_lower_limit']
                        else:
                            mu_lower_limit = None

                        if 'mu_upper_limit' in row.keys():
                            mu_upper_limit = row['mu_upper_limit']
                        else:
                            mu_upper_limit = None
                        if 'mu_hat' in row.keys():
                            mu_hat = row['mu_hat']
                        else:
                            mu_hat = None

                        histos = row['histos']
                        pool_exclusion[pool] = {'CLs':exclusion, 'mu_lower_limit':mu_lower_limit, 'mu_upper_limit':mu_upper_limit, 'mu_hat':mu_hat}
                        pool_histos[pool] = histos

                    pool_test_stats = c.execute("select pool_name, ts_b, ts_s_b from intermediate_result where run_id =" + str(run_id) + ";").fetchall()
                    # use the dictionaries to store pool name and ts_b/ts_s_b result in each run
                    pool_ts_b = {}
                    pool_ts_s_b = {}
                    for pool, ts_b, ts_s_b in pool_test_stats:
                        pool_ts_b[pool] = ts_b
                        pool_ts_s_b[pool] = ts_s_b
      
                    # use a list to store each data type in a map
                    likelihood_point.store_point_info(stat_type, combined_exclusion, combined_mu_low, combined_mu_up, combined_mu_hat,
                                                      pool_exclusion, pool_histos, pool_ts_b, pool_ts_s_b, obs_excl_dict, model_point['yoda_files'], num_events)

                # add the runpoint info ("BEAM/POINT") into the individual points (if present)
                try:
                    runpoint_id = c.execute("select run_point from model_point;").fetchall()
                    likelihood_point.set_run_point(runpoint_id[int(model_point['id']) - 1])
                except:
                    cfg.contur_log.warn("Problem reading runpoint attribute from DB. This may be an old (<2.5) results file.")
                    pass
                    
                likelihood_point.store_param_point(param_point)

                # add the likelihood point into the point list
                self._point_list.append(likelihood_point)
                
        conn.commit()
        conn.close()

    def resort_points(self):
        """Function to trigger rerunning of the sorting algorithm on all items in the depot, 
        typically if this list has been affected by a merge by a call to :func:`contur.depot.merge`
        """
        cfg.contur_log.debug('Calling resort_points')
        for i, p in enumerate(self.points):
            cfg.contur_log.debug('Resorting points ({}), point is {}'.format(i,p))
            for stat_type in cfg.stat_types:
                p.resort_blocks(stat_type)

    def merge(self, depot):
        """
        Function to merge this conturDepot instance with another.
        
        Points with identical parameters will be combined. If point from the input Depot is not present in this Depot,
        it will be added.

        :param depot:
            Additional instance to conturDepot to merge with this one
        :type depot: :class:`contur.conturDepot`


        """
        new_points = []
        for point in depot.points:

            merged = False

            # look through the points to see if this matches any.
            for p in self.points:

                if not merged:
                    same = True
                    valid = True
                    for parameter_name, value in p.param_point.items():
                        try:
                            # we don't demand the auxilliary parameters match, since they can be things like
                            # cross sections, which will depend on the beam as well as the model point.
                            if point.param_point[parameter_name] != value and not parameter_name.startswith("AUX:"):
                                same = False
                                break
                        except KeyError:
                            cfg.contur_log.warning("Not merging. Parameter name not found:" + parameter_name)
                            valid = False

                    # merge this point with an existing one
                    if same and valid:
                        cfg.contur_log.debug("Merging {} with {}".format(point.param_point,p.param_point))
                        p.pool_exclusion_dict.update(point.pool_exclusion_dict)
                        p.pool_histos_dict.update(point.pool_histos_dict)
                        p.pool_ts_b.update(point.pool_ts_b)
                        p.pool_ts_s_b.update(point.pool_ts_s_b)
                        p.obs_excl_dict.update(point.obs_excl_dict)
                        #print("point",p.pool_exclusion_dict)
                        p.combined_exclusion_dict.update(point.combined_exclusion_dict)
                        #print("CED:{}",p.combined_exclusion_dict)
                        #       self.combined_exclusion_dict = {} (does this get updated?)

                        for stat_type in cfg.stat_types:
                            try:
                                blocks = p.get_sorted_likelihood_blocks(stat_type)
                                
                                blocks.extend(point.get_sorted_likelihood_blocks(stat_type))
       
                                cfg.contur_log.debug("Previous CLs: {} , {}".format(point.get_full_likelihood(stat_type).getCLs(stat_type),p.get_full_likelihood(stat_type).getCLs(stat_type)))
                            except (AttributeError, TypeError) as e:
                                # This happens when no likelihood was evaluated for a particular block, so
                                # we can't query it for a CLs...
                                cfg.contur_log.warn("No likelihood evaluated for {}, {}".format(stat_type,p.get_run_point()))
                                cfg.contur_log.warn(" {} ".format(e))
                                pass

                        merged = True

            # this is a new point
            if not merged:
                new_points.append(point)
                cfg.contur_log.debug("Adding new point {} with dominant.".format(point.param_point))
                

        if len(new_points)>0:
            cfg.contur_log.debug("Adding {} new points to {}".format(len(new_points),len(self.points)))
            self.points.extend(new_points)


    def _build_frame(self, include_dominant_pools=False, include_per_pool_cls=False):
        """
        Note: mu values rounded to 3dp to avoid scipy version artefacts (and save time).
        :return pandas.DataFrame of the depot points
        """
        try:
            import pandas as pd
        except ImportError:
            cfg.contur_log.error("Pandas module not available. Please, ensure it is installed and available in your PYTHONPATH.")

        try:
            frame = pd.DataFrame(
                [likelihood_point.param_point for likelihood_point in self.points])
            
            for stat_type in cfg.stat_types:

                frame['CL{}'.format(stat_type)] = [
                    likelihood_point.combined_exclusion_dict[stat_type]['CLs'] for likelihood_point in self.points]                
                frame['MULO{}'.format(stat_type)] = [
                    None if likelihood_point.combined_exclusion_dict[stat_type]['mu_lower_limit'] is None else
                    round(likelihood_point.combined_exclusion_dict[stat_type]['mu_lower_limit'],2)
                    for likelihood_point in self.points
                ]
                frame['MUUP{}'.format(stat_type)] = [
                    None if likelihood_point.combined_exclusion_dict[stat_type]['mu_upper_limit'] is None else
                    round(likelihood_point.combined_exclusion_dict[stat_type]['mu_upper_limit'],2)
                    for likelihood_point in self.points
                ]                    
                frame['MUHAT{}'.format(stat_type)] = [
                    None if likelihood_point.combined_exclusion_dict[stat_type]['mu_hat'] is None else
                    round(likelihood_point.combined_exclusion_dict[stat_type]['mu_hat'],2)
                    for likelihood_point in self.points
                ]                    
                
                if include_dominant_pools:
                    frame['dominant-pool{}'.format(stat_type)] = [
                        likelihood_point.get_dominant_pool(stat_type)
                        for likelihood_point in self.points
                    ]
                    frame['dominant-pool-tag{}'.format(stat_type)] = [
                        likelihood_point.pool_histos_dict[stat_type][likelihood_point.get_dominant_pool(stat_type)]
                        for likelihood_point in self.points
                    ]

                if include_per_pool_cls:
                    for likelihood_point in self.points:
                        for pool in likelihood_point.pool_exclusion_dict[stat_type]:
                            frame['{}{}'.format(pool,stat_type)] = likelihood_point.pool_exclusion_dict[stat_type][pool]

            return frame
        except:
            raise
            
    def export(self, path, include_dominant_pools=True, include_per_pool_cls=False):
        self._build_frame(include_dominant_pools, include_per_pool_cls).to_csv(path, index=False)
    
    def write_summary_dict(self, output_opts):
        """
        Write a brief text summary of a conturDepot to a (returned) dictionary,
        intended for use with yoda stream input.

        :param output_opts: list of requested outputs to put in the summary dict
        """  
        summary_dict = {}
        for stat_type in cfg.stat_types:
            summary_dict[stat_type] = {}

            if len(self.points) < 1:
                continue

            # summary function will just read the first entry in the depot.
            #full_like = self.points[0].combined_exclusion_dict[stat_type]
            full_like = self.points[0].get_full_likelihood(stat_type)
            like_blocks = self.points[0].get_sorted_likelihood_blocks(stat_type)

            if "LLR" in output_opts:
                if (full_like.get_ts_s_b(stat_type) is not None and full_like.get_ts_b(stat_type) is not None):
                    summary_dict[stat_type]["LLR"] = full_like.get_ts_s_b(stat_type) - full_like.get_ts_b(stat_type)
                else:
                    summary_dict[stat_type]["LLR"] = 0.0

            if "CLs" in output_opts:
                summary_dict[stat_type]["CLs"] = full_like.getCLs(stat_type)

            if "Pool_LLR" in output_opts:
                summary_dict[stat_type]["Pool_LLR"] = {}
                for block in like_blocks:
                    if ((block.get_ts_s_b(stat_type) is not None)
                    and (block.get_ts_b(stat_type) is not None)):
                        summary_dict[stat_type]["Pool_LLR"][block.pools] = (
                            block.get_ts_s_b(stat_type) - block.get_ts_b(stat_type))
                    else:
                        summary_dict[stat_type]["Pool_LLR"][block.pools] = 0.0

            if "Pool_CLs" in output_opts:
                summary_dict[stat_type]["Pool_CLs"] = {}
                for block in like_blocks:
                    summary_dict[stat_type]["Pool_CLs"][block.pools] = block.getCLs(stat_type)

            if "Pool_tags" in output_opts:
                summary_dict[stat_type]["Pool_tags"] = {}
                for block in like_blocks:
                    summary_dict[stat_type]["Pool_tags"][block.pools] = block.tags

        return summary_dict

    def is_plot_metric_valid(self, plot_metric, file):
        """
        Checks if the plot metric is in the database, if contur-plot run without spey
        function returns False
        """
        primary_stat_type = cfg.primary_stat
        if self.points[0].combined_exclusion_dict[primary_stat_type][plot_metric] is None:
            cfg.contur_log.info(f"{plot_metric} is not in {file}")
            return False
        else:
            cfg.contur_log.info(f"{plot_metric} is in {file}")
            return True

       
    @property
    def points(self):
        """
        The master list of :class:`~contur.factories.depot.LikelihoodPoint` instances added to the Depot instance

        **type** ( ``list`` [ :class:`~contur.factories.depot.LikelihoodPoint` ])
        """
        return self._point_list
    
    @property
    def frame(self):
        """
        A ``pandas.DataFrame`` representing the CLs interval for each point in :attr:`points`

        **type** (``pandas.DataFrame``)
        """
        return self._build_frame()

    def __repr__(self):
        return "%s with %s added points" % (self.__class__.__name__, len(self.points))


    
def ts_to_cls(ts_tuple_list):
    """
    calculate the final cls value
    """
    if type(ts_tuple_list) == tuple:
        ts_tuple_list = [ts_tuple_list] #place in list

    log_p_vals = spstat.norm.logsf(np.sqrt(np.array(ts_tuple_list)))
    cls = []

    for ts_index in range(len(log_p_vals)):
        log_pval_b = log_p_vals[ts_index][1]
        log_pval_sb = log_p_vals[ts_index][0]

        try:
            # have stayed with logs for as long as possible for numerical stability
            cls_ts_index = 1 - np.exp(log_pval_sb - log_pval_b)
        except FloatingPointError:
            cls_ts_index = 1

        if (cls_ts_index is not None and cls_ts_index < 0):
            cls_ts_index = 0

        cls.append(cls_ts_index)
    
    return cls  
