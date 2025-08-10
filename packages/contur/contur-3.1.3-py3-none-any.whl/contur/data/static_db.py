import re
import sqlite3 as db
import os
from os.path import dirname, join
import fnmatch

import contur
import contur.config.config as cfg
import contur.config.paths
import contur.util.utils as cutil
from .data_objects import *

# TODO: Rewrite using an RAII idiom
# TODO: Explain what that would actually mean.

INIT = False
INVALID = (-1, '', '')
whitelists = {}
blacklists = {}
needtheory = {}
higgsgg = {}
higgsww = {}
bveto = {}
atlaswz = {}
searches = {}
metratio = {}
tracksonly = {}
softphysics ={}
overflows ={}

# lists/dictionaries of data objects
known_beams = []
experiments = []
analyses = {}
pools = {}


class listdict(dict):
    """ Dictionary which returns an empty list if the key is missing. """ 
    def __missing__(self, key):
        self[key] = []
        return self[key]

subpools = listdict()
norms = listdict()
#nxdiffs = listdict()
theory_predictions = listdict()
covariances = listdict()
correlations = listdict()
Lumi_unit = listdict()
            
def init_dbs():
    """ 
    The principle function to read the database and populate dictionaries using the data.
    it is invoked by the first access request. 
    """

    home_dir=os.path.expanduser('~')
    dbfile=contur.config.paths.user_path('analyses.db')

    conn = db.connect(dbfile)
    c = conn.cursor()

    for row in c.execute('SELECT id,collider,particle_a,particle_b,energy_a,energy_b FROM beams GROUP BY id;'):
        this_beam = Beam(row)
        known_beams.append(this_beam)

    for row in c.execute('SELECT id,collider FROM experiments GROUP BY id;'):
        this_expt = Experiment(row)
        experiments.append(this_expt)

    for row in c.execute('SELECT pool,beam,description FROM analysis_pool;'):
        this_pool = Pool(row)
        pools[this_pool.id] = this_pool

    for row in c.execute('SELECT id,pool FROM analysis;'):        
        ana, poolid = row
        beamid = pools[poolid].beamid
        try:
            analyses[ana]=Analysis(row,beamid)
        except cfg.ConturError:
            pass
            
    for row in c.execute('SELECT id,lumi,pattern,intLumi FROM lumi_unit;'):        
        ana, lumi, patterns, intLumi = row
        patterns = patterns.split(',')       
        Lumi_unit[ana].append((lumi, patterns, intLumi))
        
    for row in c.execute('SELECT id,group_concat(pattern) FROM whitelist GROUP BY id;'):
        ana, patterns = row
        patterns = patterns.split(',')
        whitelists[ana] = patterns

    for row in c.execute('SELECT id,group_concat(pattern) FROM blacklist GROUP BY id;'):
        ana, patterns = row
        patterns = patterns.split(',')
        blacklists[ana] = patterns

    for row in c.execute('SELECT id,group_concat(pattern) FROM needtheory GROUP BY id;'):
        ana, patterns = row
        patterns = patterns.split(',')
        needtheory[ana] = patterns

    for row in c.execute('SELECT id,group_concat(pattern) FROM higgsgg GROUP BY id;'):
        ana, patterns = row
        patterns = patterns.split(',')
        higgsgg[ana] = patterns

    for row in c.execute('SELECT id,group_concat(pattern) FROM searches GROUP BY id;'):
        ana, patterns = row
        patterns = patterns.split(',')
        searches[ana] = patterns

    for row in c.execute('SELECT id,group_concat(pattern) FROM higgsww GROUP BY id;'):
        ana, patterns = row
        patterns = patterns.split(',')
        higgsww[ana] = patterns

    for row in c.execute('SELECT id,group_concat(pattern) FROM bveto GROUP BY id;'):
        ana, patterns = row
        patterns = patterns.split(',')
        bveto[ana] = patterns

    for row in c.execute('SELECT id,group_concat(pattern) FROM atlaswz GROUP BY id;'):
        ana, patterns = row
        patterns = patterns.split(',')
        atlaswz[ana] = patterns

    for row in c.execute('SELECT id,group_concat(pattern) FROM metratio GROUP BY id;'):
        ana, patterns = row
        patterns = patterns.split(',')
        metratio[ana] = patterns
        
    for row in c.execute('SELECT id,group_concat(pattern) FROM tracksonly GROUP BY id;'):
        ana, patterns = row
        patterns = patterns.split(',')
        tracksonly[ana] = patterns

    for row in c.execute('SELECT id,group_concat(pattern) FROM softphysics GROUP BY id;'):
        ana, patterns = row
        patterns = patterns.split(',')
        softphysics[ana] = patterns

    for row in c.execute('SELECT id,pattern,subid FROM subpool;'):
        ana, pattern, subid = row
        #        subid = 'R%s' % (subid + 1)
        subpools[ana].append((pattern, subid))

    for row in c.execute('SELECT id,pattern,norm,nxdiff FROM normalization;'):
        ana, patterns, norm, nxdiff = row
        patterns = patterns.split(',')
        for pattern in patterns:
            norms[ana].append((pattern, norm, nxdiff))


    for row in c.execute('SELECT * FROM theory_predictions;'):
        ana = row[1]        
        prediction = SMPrediction(row)
        theory_predictions[ana].append(prediction)

    for row in c.execute('SELECT * FROM covariances;'):        
        if row[2]==0:
            covariances[row[0]] = row[1]
        else:
            correlations[row[0]] = row[1]

    for row in c.execute('SELECT * FROM overflows;'):
        overflows[row[0]] = (row[1],row[2])
            
    conn.close()

    global INIT
    INIT = True


class InvalidPath(Exception):
    pass



def validHisto(h,filter=True):
    """
    Tests a histogram path to see if it is a valid contur histogram for this run (taking into account
    the run time flags).
    :arg h: the full path of a yoda analysis object
    :type: String

    if invalid, return False. Otherwise return the full name of the analysis object the histogram belongs to.
    """

    import rivet.aopaths

    if rivet.aopaths.isTmpPath(h):
        return False

    if rivet.aopaths.isRawPath(h):
        return False

    try:
        ana, tag = cutil.splitPath(h)
    except InvalidPath:
        return False

    if not INIT:
        init_dbs()

    if not cutil.analysis_select(ana):
        return False
        
    if filter:
        
        if ana in searches and cfg.exclude_searches:
            for pattern in searches[ana]:
                if pattern in tag:
                    return False

        if ana in higgsgg and cfg.exclude_hgg:
            for pattern in higgsgg[ana]:
                if pattern in tag:
                    return False

        if ana in higgsww and cfg.exclude_hww:
            for pattern in higgsww[ana]:
                if pattern in tag:
                    return False

        if ana in bveto and cfg.exclude_b_veto:
            for pattern in bveto[ana]:
                if pattern in tag:
                    return False

        if ana in atlaswz and cfg.exclude_awz:
            for pattern in atlaswz[ana]:
                if pattern in tag:
                    return False

        if isRatio(h) and cfg.exclude_met_ratio:
            return False

        if not is_tracks_only(h) and cfg.tracks_only:
            return False

        if is_soft(h) and cfg.exclude_soft_physics:
            return False

    return passes_lists(ana,tag)

def passes_lists(ana,tag):
    """ 
    Check the blacklist/whitelist status of the histogram name tag within analysis name ana.
    Only works if ana is the full analysis name, including options.
    """
    if ana in analyses.keys():

        if ana not in whitelists.keys():
            if ana not in blacklists:
                return True
            elif ana in blacklists:
                for pattern in blacklists[ana]:
                    if re.compile(pattern).search(tag) is not None:
                        return False
                return True
        elif ana in whitelists:
            for pattern in whitelists[ana]:
                if re.compile(pattern).search(tag) is not None:
                    return True
            return False
    else:
        return False

def get_pool(path=None,poolid=None):
    """ 
    Given a pool id only, return the pool object.

    Given only the yoda path of a histogram, return the pool object it belongs to.
    Should work whether the analysis part of the path contains the option or not,
    since any given histo has a specific pool.

    Given both, check for consistency and return the pool object or None, depending

    Given neither, return None
    """
    
    if not INIT:
        init_dbs()

    if path is None:
        if poolid is None: 
            return None
        else:
            return pools[poolid]
    
    try:
        ana, histo_name = cutil.splitPath(path)
    except InvalidPath:
        return False

    # can't just grab the pool from the ana and return it, because sometimes the path doesn't
    # contain the full analysis name including options string.
        
    analysis = None
    has_whitelists = False
    for full_ana, patterns in whitelists.items():
        if ana in full_ana:
            if passes_lists(full_ana,histo_name):
                analysis = analyses[full_ana]
                if poolid is not None and poolid != analysis.poolid:
                    return None
                else:
                    return pools[analysis.poolid]
            else:
                return None
    
    for full_ana, patterns in blacklists.items():
        analysis = analyses[full_ana]
        if ana in full_ana:
            if not passes_lists(full_ana,histo_name):
                return None
        
    try:
        analysis = analyses[ana]
    except:
        cfg.contur_log.warning("Could not find {} in analysis list. Maybe you need to specify the options?".format(ana))
        return None
    
    if poolid is not None and poolid != analysis.poolid:
        return None
    else:
        return pools[analysis.poolid]
        
def obsFinder(h):
    """
    Get meta dat (analysis, integrated luminosity, poolid, subpoolid) for a valid contur histogram. Else return INVALID.

    :param h: (``string``) yoda histogram path

    """
    if not INIT:
        init_dbs()

    try:
        ana, tag = cutil.splitPath(h)
    except InvalidPath:
        return INVALID

    if cfg.splitAnalysis:
        poolid = tag
    else:
        try:
            poolid = analyses[ana].poolid
        except:
            print(analyses)
            
    if not passes_lists(ana,tag):
        return INVALID
    
    lumi = None 
    try:
        for lumi_text, patterns, intlumi in Lumi_unit[ana]:
            for p in patterns:
                if re.compile(p).search(tag) is not None:
                    if intlumi is None:
                        lumi_fb = analyses[ana].rivet_analysis.luminosityfb()
                        #Normal case, take int lumi from rivet info file.
                        if analyses[ana].rivet_analysis.luminosityfb()<0:
                            raise cfg.ConturError("No integrated luminosity in rivet or contur for {} {}.".format(analyses[ana].name,analyses[ana].rivet_analysis.luminosityfb())) from None
                        elif lumi_text == "fb":
                            lumi = lumi_fb
                        elif lumi_text == "pb":
                            lumi = lumi_fb*1000.
                        elif lumi_text == "nb":
                            lumi = lumi_fb*1000000.
                        elif lumi_text == "ub":
                            lumi = lumi_fb*1000000000.
                        elif lumi_text == "eventcount":
                            lumi = 1.0
                        else:
                            cfg.contur_log.error("Unrecognised instruction in contur DB lumi field: {}.".format(lumi_text))
                            raise cfg.ConturError("Unrecognised instruction in contur DB lumi field: {}.".format(lumi_text)) from None

                    else:
                        try:
                            #Overwrite rivet lumi info for this histogram
                            lumi = intlumi
                            if lumi_text == "fb":
                                lumi_fb = intlumi
                            elif lumi_text == "pb":
                                lumi_fb = intlumi/1000.
                            elif lumi_text == "nb":
                                lumi_fb = intlumi/1000000.
                            elif lumi_text == "ub":
                                lumi_fb = intlumi/1000000000.
                            elif lumi_text == "eventcount":
                                lumi_fb = 140.0
                                
                        except ValueError:
                            raise cfg.ConturError("{} is not a float, please correct the format of input.".format(intlumi)) from None
                    # No need to carry on looping, we found it.
                    break

    except KeyError: 
        pass
                    
    if lumi is None:
       raise cfg.ConturError("Luminosity for analysis: {} , Histogram: {} is not defined properly , please make sure it's inserted in analyses.sql".format(ana,tag)) from None 
        
    subpoolid = None
    if ana in subpools:

        for p, subid in subpools[ana]:
            if re.search(p, tag):
                subpoolid = subid
                if cfg.splitAnalysis:
                    poolid = subid
                break

    return analyses[ana], lumi, lumi_fb, poolid, subpoolid


def isNorm(h):
    """
    :param h: (``string``) histogram path.

    Returns:

    * **isScaled** - does this histogram need to be scaled to turn it into a differential cross section?

    * **scaleFactor** - the scale factor, if so (=1 otherwise)

    * **nev_differential** - factor for converting "number of events per something" plots (searches) into number of events. See ``analysis.sql`` for detailed description.

    """
    if not INIT:
        init_dbs()

    ana, tag = cutil.splitPath(h)

    isNorm = False
    normFac = 1.0
    nx_diff = 0

    # need to do it this way because for ref data ana does not have the MODE attached.
    for s in norms:
        if ana in s:
            for p, norm, nxdiff in norms[s]:
                if re.search(p, tag):
                    if norm > 0:
                        isNorm = True
                        normFac = norm
                    nx_diff = nxdiff
                    break

    return isNorm, normFac, nx_diff

# Better-named alias, since this isn't just a boolean-test function
getNormInfo = isNorm


def isRatio(h):
    """
    Is this a ratio plot?
    :param h: (``string``) yoda histogram path
    
    """

    if not INIT:
        init_dbs()

    try:
        ana, tag = cutil.splitPath(h)
    except InvalidPath:
        return False

    if ana in metratio:
        for pattern in metratio[ana]:
            if pattern in tag:
                return True

    return False

# More-specific alias
isMETRatio = isRatio
" Is this a missing energy ratio plot? "

def hasRatio(ana):
    "Does this analysis have ratio measurements?"
    if not INIT:
        init_dbs()

    # Hard-coded!
    if ana in metratio:
        return True

    return False

# More-specific alias
hasMETRatio = hasRatio
"Does this analysis have missing-energy ratio measurements?"


def hasSearches(ana):
    "Does this analysis have search measurements?"
    if not INIT:
        init_dbs()

    if ana in searches:
        return True

    return False

def isSearch(h):
    """

    Is this a search event-count plot?

    :param h: (``string``) yoda histogram path

    """
    if not INIT:
        init_dbs()

    try:
        ana, tag = cutil.splitPath(h)
    except InvalidPath:
        return False

    if ana in searches:
        for pattern in searches[ana]:
            if pattern in tag:
                return True

    return False


def hasBVeto(ana):
    "Does this analysis have measurements with a b-jet-veto problem?"
    if not INIT:
        init_dbs()

    if ana in bveto:
        return True

    return False

def hasNuTrue(ana):
    "Does this analysis have measurements with a truth-neutrino problem?"
    if not INIT:
        init_dbs()

    if ana in atlaswz:
        return True

    return False


def hasHiggsgg(ana):
    "Does this analysis have Higgs -> photons measurements?"
    if not INIT:
        init_dbs()

    if ana in higgsgg:
        return True

    return False


def hasHiggsWW(ana):
    "Does this analysis have Higgs -> WW measurements?"
    if not INIT:
        init_dbs()

    if ana in higgsww:
        return True

    return False
    
    
def is_tracks_only(h):
    """
    Is this a plot which only uses tracks?
    :param h: (``string``) yoda histogram path
    
    """

    if not INIT:
        init_dbs()

    try:
        ana, tag = cutil.splitPath(h)
    except InvalidPath:
        return False

    if ana in tracksonly:
        for pattern in tracksonly[ana]:
            if pattern in tag:
                return True

    return False

def is_soft(h):
    """
    Is this a soft QCD plot 
    :param h: (``string``) yoda histogram path
    
    """

    if not INIT:
        init_dbs()

    try:
        ana, tag = cutil.splitPath(h)
    except InvalidPath:
        return False

    if ana in softphysics:
        for pattern in softphysics[ana]:
            if pattern in tag:
                return True

    return False



def theoryComp(h):
    """
    If this histogram **always** requires a SM theory comparison, return True.

    :param h: (``string``) yoda histogram path

    """
    if not INIT:
        init_dbs()

    ana, tag = cutil.splitPath(h)

    if ana in needtheory:
        for pattern in needtheory[ana]:
            if pattern in tag:
                return True

    return False

def get_analyses(analysisid=None, poolid=None, beam=None, filter=True):
    """ 
    Return a list of analysis objects

    If no pool, beam or id supplied, return all valid analyses in the current config.

    If analysisid is supplied, return only analyses with an id containing it

    If poolid supplied, return only analyses associated with that pool

    If beamid supplied, return only analyses associated with that beam

    If more than one of the above supplied, they are ANDed.

    Depending on the filter flag, the analyses will be filtered according to
    the current configuation or not.

    Optional inputs: analysisid string, Beam object, poolid string, filter boolean.
    """

    if not INIT:
        init_dbs()

    if poolid is None and beam is None and analysisid is None and not filter:
        return analyses.values()

    analysis_selection = []
    
    if poolid is not None:
        pool = pools[poolid]
        if beam is not None and beam.id != poolid:
            cfg.contur_log.warning("Requested incompatible pool ({}) and beam {}".format(poolid,beam.id))
            return None

    for analysis in analyses.values():
        
        ana = analysis.name
        condition = False
        if filter:
            condition =  ((hasSearches(ana) and cfg.exclude_searches) or
                          (hasHiggsgg(ana) and cfg.exclude_hgg) or
                          (hasHiggsWW(ana) and cfg.exclude_hww) or
                          (hasNuTrue(ana) and cfg.exclude_awz) or
                          (hasBVeto(ana) and cfg.exclude_b_veto))
            if condition:
                continue

        if poolid is not None and analysis.poolid != poolid:
            continue

        if beam is not None and analysis.beamid != beam.id:
            continue

        if analysisid is not None and not analysisid in analysis.name:
            continue
                
        analysis_selection.append(analysis)

    if len(analysis_selection)==0:
        cfg.contur_log.warning("Warning: No analyses found for analysis {}, beam {}, pool,{}. Returning empty list".format(analysisid,beam,poolid))
            
    return analysis_selection

def get_analysis(ana_id):
    ''' 
    returns the analysis with this id
    '''
    return analyses[ana_id]


def match_analyses(pattern):
    '''
    Returns the analyses which match a glob-style pattern.
    '''
    if not INIT:
        init_dbs()

    matches = fnmatch.filter(analyses, pattern)

    return matches

def get_beams(poolid=None):
    '''
    Get the list of known beam configurations, specific to the named pool if given
    '''
    if not INIT:
        init_dbs()

    if not poolid: 
        return known_beams
    
    for beam in known_beams:
        if pools[poolid].beamid==beam.id:
            return [beam]

    cfg.contur_log.error("No beam found for pool {}".format(pool))
    return None

def get_beam_names(poolid=None, allow_all=False):
    '''
    Get the list of known beam names, specific to the named pool if given
    '''
    beams = get_beams(poolid)
    beam_names = [beam.id for beam in beams]
    if allow_all:
        beam_names += ["all"]
    return beam_names

def get_pools(beamid=None):
    '''
    Get the list of known pool names, specific to a beam id (7/8/13TeV) if given
    '''
    if not INIT:
        init_dbs()

    if not beamid: 
        return pools
    
    filtered_pools = []
    for pool in pools:
        if pool.beam.id==beamid:
            filtered_pools.append(pool)

    return filtered_pools

def get_experiments(collider=None,beam=None):
    '''
    Get the list of known pool names, specific to a beam id (7/8/13TeV) if given
    '''
    if not INIT:
        init_dbs()

    if collider is None and beam is None:
        return experiments
    
    filtered_experiments = []

    if collider is not None and beam is not None:
        if beam.collider != collider:
            cfg.contur_log.warning("Beam {} is not valid for collider {}.".format(beam.id, collider))
            return filtered_experiments
            
    for experiment in experiments:
        if experiment.collider==collider or (beam is not None and beam.collider==experiment.collider):
            filtered_experiments.append(experiment)
    
    return filtered_experiments

def get_sm_theory(ana=None):
    """
    Return a list of the SM theory predictions, if any, for the input analysis name.
    Otherwise return ``False``.
    """
    if not INIT:
        init_dbs()

    if ana is None:
        return theory_predictions

    if ana in theory_predictions:
        return theory_predictions[ana]
    else:
        return None

def get_covariance_name(path):
    try:
        return covariances[path]
    except KeyError:
        return False

def get_correlation_name(path):
    try:
        return correlations[path]
    except KeyError:
        return False

def use_overflow(path):
    try:
        return bool(overflows[path][0])
    except KeyError:
        return False


def use_underflow(path):
    try:
        return bool(overflows[path][1])
    except KeyError:
        return False
