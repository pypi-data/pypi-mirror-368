import contur.config.config as cfg
import contur.data.static_db as cdb
import contur.factories.likelihood as lh

from contur.factories.likelihood import ts_to_cls
import copy
class LikelihoodPoint(object):
    """
    Save the statistical information about a model parameter point in a run,  which can then be manipulated to sort them,
    calculate a full likelihood result, exclusions result, test b result, test s+b result with related stat_type 
    and a parameter point dictionary

    If instantiated with a valid parameter dictionary this will be added as a property
    If instantiated with a valid YodaFactory, its likelihood blocks will be associated with this likelihood point

    If these are not provided, a blank point will be created which can be populated later (e.g. from a results database)

    Note that in general those likelihood blocks (ie the lists of likelihood objects) will not be present, since a result database does not
    store them. The statistics info can be retrieved from the relevant dictionaries, but not recalculated from scratch since this signal/background
    info won't be available.

    This class corresponds most closely to the run table in the results database, although each row of that
    table has a unique stat_type (which should maybe be changed in future.

    """

    def __init__(self, paramPoint={}, yodaFactory=None):
        """

        :param paramPoint:
            Dictionary of model parameter: value pairs.
        :type paramPoint: ``dict``

        :param yodaFactory:
            String of filesystem location to write out the pickle of this instance to
        :type yodaFactory: ``contur.factories.yoda_factories.YodaFactory``
        """

        self.param_point = paramPoint
        self.pool_exclusion_dict = {}
        self.pool_histos_dict = {}
        self.pool_ts_b = {}
        self.pool_ts_s_b = {}
        self.combined_exclusion_dict = {}
        self.likelihood_blocks = None
        self.obs_excl_dict = {}
        self.run_point = ""
        self._sorted_likelihood_blocks = {}
        self._full_likelihood = {}
        # number of generated event used
        self.num_events = 0
        # any additional arguments
        self.args = None

        # set up four versions of the full likelihood, one for each type of stat calculation.
        for stat_type in cfg.stat_types:
            self._full_likelihood[stat_type] = lh.CombinedLikelihood(stat_type)
        
        if yodaFactory is not None:
            self.num_events = yodaFactory.num_events
            self.likelihood_blocks = yodaFactory._likelihood_blocks            
            for stat_type in cfg.stat_types:

                if self.get_sorted_likelihood_blocks(stat_type) is not None:
                    self.fill_pool_dict(stat_type)
                    
    def fill_pool_dict(self,stat_type):
        pool_dict = {}
        pool_histos = {}
        try:
            self.combined_exclusion_dict[stat_type] = {'CLs':self.get_full_likelihood(stat_type).getCLs(stat_type),
                                                       'mu_lower_limit':self.get_full_likelihood(stat_type).get_mu_lower_limit(stat_type),
                                                       'mu_upper_limit':self.get_full_likelihood(stat_type).get_mu_upper_limit(stat_type),
                                                       'mu_hat':self.get_full_likelihood(stat_type).get_mu_hat(stat_type)}
            for p in self.get_sorted_likelihood_blocks(stat_type):
                pool_dict[p.pools] = {'CLs':p.getCLs(stat_type),
                                      'mu_lower_limit':p.get_mu_lower_limit(stat_type),
                                      'mu_upper_limit':p.get_mu_upper_limit(stat_type),
                                      'mu_upper_limit':p.get_mu_upper_limit(stat_type),
                                      'mu_hat':p.get_mu_hat(stat_type)}
                pool_histos[p.pools] = p.tags 
                
        except AttributeError:
            self.combined_exclusion_dict[stat_type] = None
            
        self.pool_exclusion_dict[stat_type] = pool_dict
        self.pool_histos_dict[stat_type] = pool_histos
                    
    def resort_blocks(self,stat_type,omitted_pools=""):
        """
        Function to sort the :attr:`sorted_likelihood_blocks` list. Used for resorting after a merging exclusively.
        :Keyword Arguments:
        * *stat_type* (``string``) -- which statisic type (default, SM background, expected or hlexpected) is being sorted by.
        """
        cfg.contur_log.debug('Calling resort blocks ({})'.format(stat_type))
        try:
            self._sorted_likelihood_blocks[stat_type] = lh.sort_blocks(self._sorted_likelihood_blocks[stat_type],stat_type,omitted_pools="")
        except ValueError as ve:
            cfg.contur_log.warning("Unable to sort likelihoods for {}. Exception: {}".format(stat_type,ve))

        self._full_likelihood[stat_type] = lh.build_full_likelihood(self.get_sorted_likelihood_blocks(stat_type),stat_type)

        # update the combined exclusion dictionary
        try:
            self.combined_exclusion_dict[stat_type] = self.get_full_likelihood(stat_type).get_stats(stat_type)                
        except AttributeError:
            self.combined_exclusion_dict[stat_type] = None

    
        # cleanup some bulk we don't need  @TODO make this a separate cleanup function.
        if hasattr(self, '_likelihood_blocks'):
            del self._likelihood_blocks
        if hasattr(self, 'yodaFilePath'):
            del self.yodaFilePath
    
    # set runpoint info with beam and scan point, e.g. 13TeV/0003
    def set_run_point(self,run_point):
        self.run_point = run_point
        
    # get runpoint info with beam and scan point, e.g. 13TeV/0003
    def get_run_point(self):
        return self.run_point

    def get_sorted_likelihood_blocks(self,stat_type=None):
        """
        The list of reduced component likelihood blocks extracted from the result file, sorted according
        the test statisitic of type `stat_type`. If stat_type is None, return the whole dictionary.

        **type** ( ``list`` [ :class:`~contur.factories.likelihood.Likelihood` ])

        """

        try:
            if stat_type is None:
                return self._sorted_likelihood_blocks

            if stat_type in self._sorted_likelihood_blocks.keys():
                return self._sorted_likelihood_blocks[stat_type]
            else:
                return None
        except:
            raise cfg.ConturError("Likelihood point has no likelhood blocks.")
        
    def set_sorted_likelihood_blocks(self, value, stat_type):
        self._sorted_likelihood_blocks[stat_type] = value

    def get_dominant_pool(self,stat_type):
        '''
        return the name of the dominant pool for this point
        '''
        pools = self.pool_exclusion_dict[stat_type]
        
        return max(pools, key=lambda pool: pools[pool]['CLs'])


    def get_dominant_analysis(self,stat_type,poolid=None,cls_cut=0.0):
        """
        return the analysis object which has the biggest exclusion for this point.
        """
        analysis = None

        maximum = cls_cut
        maximum_analysis = None
        for histname, stats in self.obs_excl_dict.items():
            if stats[stat_type]['CLs'] is not None:
                analysis, lumi, lumi_fb, this_poolid, subpoolid = cdb.obsFinder(histname)
                if (poolid == this_poolid or poolid is None) and stats[stat_type]['CLs']>maximum:
                    maximum_analysis = analysis
                    maximum = stats[stat_type]['CLs']

        return maximum_analysis

                
    def store_point_info(self, statType, combinedExclusion, combined_mu_low, combined_mu_up, combined_mu_hat,
                         poolExclusion, poolHistos, poolTestb, poolTestsb, obs_excl_dict, yoda_files, num_events):
        """
        :param statType:
            string, represent the point type
        :type combinedExclusion: ``string``
        :param combinedExclusion:
            full likelihood for a parameter point
        :type combinedExclusion: ``float``
        :param poolExclusion:
            **key** ``string`` pool name : **value** ``double``
        :type poolExclusion: ``dict``
        :param poolHistos:
            **key** ``string`` pool name : **value** ``string``
        :type poolHistos: ``dict``
        :param poolTestb:
            **key** ``string`` pool name : **value** ``double``
        :type poolTestb: ``dict``
        :param poolTestsb:
            **key** ``string`` pool name : **value** ``double``
        :type poolTestsb: ``dict``
        """
        self.combined_exclusion_dict[statType] = {'CLs':combinedExclusion,'mu_lower_limit':combined_mu_low,'mu_upper_limit':combined_mu_up,'mu_hat':combined_mu_hat}        
        self.pool_exclusion_dict[statType] = poolExclusion
        self.pool_histos_dict[statType] = poolHistos
        self.pool_ts_b[statType] = poolTestb
        self.pool_ts_s_b[statType] = poolTestsb
        self.obs_excl_dict = obs_excl_dict
        self.yoda_files = yoda_files
        self.num_events = num_events
        
    def store_param_point(self, paramPoint):
        """
        :param paramPoint:
            **key** ``string`` param name : **value** ``float``
        :type paramPoint: ``dict``
        """
        self.param_point = paramPoint

    def recalculate_CLs(self, stat_type, omitted_pools=""):
        """
        recalculate the combined exclusion after excluding the omitted pool in the class
        :param omitted_pools:
            string, the name of the pool to ignore 
        :type omiited_pools: ``string``
        """
    #   if omitted_pools in self.pool_ts_b[stat_type].keys():
    #       self.pool_ts_b[stat_type].pop(omitted_pools)
    #       self.pool_ts_s_b[stat_type].pop(omitted_pools)

    #       sum_ts_b = 0
    #        sum_ts_s_b = 0
    #        for pool in self.pool_ts_b[stat_type]:
    #            sum_ts_b += self.pool_ts_b[stat_type][pool]
    #        for pool in self.pool_ts_s_b[stat_type]:
    #            sum_ts_s_b += self.pool_ts_s_b[stat_type][pool]
    #        cls = ts_to_cls([(sum_ts_b, sum_ts_s_b)])[0]
    #        self.combined_exclusion_dict[stat_type] = cls
    #    return self.combined_exclusion_dict[stat_type]

        # If the user asked us to omit a pool, drop it
        if omitted_pools and omitted_pools in self.pool_ts_b[stat_type]:
            self.pool_ts_b[stat_type].pop(omitted_pools)
            self.pool_ts_s_b[stat_type].pop(omitted_pools)

        # Sum all remaining test statistics in one line each
        sum_ts_b   = sum(self.pool_ts_b[stat_type].values())
        sum_ts_s_b = sum(self.pool_ts_s_b[stat_type].values())

        # Call ts_to_cls with the new required signature (needs a tags list)
        # so we satisfy its signature: ts_to_cls(list_of_(b,s), tags)
        new_cls = ts_to_cls([(sum_ts_b, sum_ts_s_b)], tags=[])[0]

        self.combined_exclusion_dict[stat_type] = new_cls
        return new_cls
    @property
    def likelihood_blocks(self):
        """The list of all component likelihood blocks extracted from the result file

        This attribute is the total information in the result` file, but does not account for potential correlation/
        overlap between the members of the list

        **type** ( ``list`` [ :class:`~contur.factories.likelihood.Likelihood` ])
        """
        return self._likelihood_blocks
    
    @likelihood_blocks.setter
    def likelihood_blocks(self, value):
        self._likelihood_blocks = value

    def get_full_likelihood(self,stat_type=None):
        """The list of all component likelihood blocks extracted from the result file

        This attribute is the total information in the result` file, but does not account for potential correlation/
        overlap between the members of the list

        If stat_type is specified, return to entry for it. Else return the dict of all of them.

        **type** (:class:`~contur.factories.likelihood.CombinedLikelihood`)
        """

        if stat_type is None:
            return self._full_likelihood
        else:
            return self._full_likelihood[stat_type]
            
    def set_full_likelihood(self, stat_type, value):
        self._full_likelihood[stat_type] = value
        
    def __repr__(self):
        try:
            return "%s with %s blocks, holding %s" % (self.__class__.__name__, len(self.likelihood_blocks), self._full_likelihood)
        except:
            return "%s with %s blocks, holding %s" % (self.__class__.__name__, len(self._sorted_likelihood_blocks), self._full_likelihood)


#serialise the current LikelihoodPoint into a plain‑Python dict.
    # Captures every attribute needed to rebuild the point later.
    # Uses copy.deepcopy so the caller can mutate the returned
    # structure without affecting the original object.
    def as_dict(self):
        """Return a dict snapshot of all serializable fields of this point."""
        return {
            "param_point": copy.deepcopy(self.param_point),
            "pool_exclusion_dict": copy.deepcopy(self.pool_exclusion_dict),
            "pool_histos_dict": copy.deepcopy(self.pool_histos_dict),
            "pool_ts_b": copy.deepcopy(self.pool_ts_b),
            "pool_ts_s_b": copy.deepcopy(self.pool_ts_s_b),
            "combined_exclusion_dict": copy.deepcopy(self.combined_exclusion_dict),
            "obs_excl_dict": copy.deepcopy(self.obs_excl_dict),
            "run_point": self.run_point,
            "num_events": self.num_events,
            "args": copy.deepcopy(self.args),
        }
        
    # alternative constructor
    # Re‑create a fresh LikelihoodPoint from a dict produced by as_dict.
    # Declared as @classmethod so it receives the *class* (cls) instead
    # of an instance—this lets the method call cls() and therefore works
    # automatically for subclasses too.
    @classmethod
    def from_dict(cls, data):
        """Create a new instance from a dict snapshot."""
        obj = cls()
        obj.param_point = dict(data["param_point"])
        obj.pool_exclusion_dict = dict(data["pool_exclusion_dict"])
        obj.pool_histos_dict = dict(data["pool_histos_dict"])
        obj.pool_ts_b = dict(data["pool_ts_b"])
        obj.pool_ts_s_b = dict(data["pool_ts_s_b"])
        obj.combined_exclusion_dict = dict(data["combined_exclusion_dict"])
        obj.obs_excl_dict = dict(data["obs_excl_dict"])
        obj.run_point = data["run_point"]
        obj.num_events = data["num_events"]
        obj.args = data["args"]
        return obj
