# -*- python -*-

"""
Miscellaneous helper functions that may be used by more than one contur submodule

"""

import os, glob, subprocess, sys
from builtins import input
import fnmatch

import contur
import contur.config.config as cfg
import contur.config.version
import contur.factories.likelihood as lh
import contur.data as cdb

from rivet import mkStdPlotParser

import importlib

## Import the tqdm progress-bar if possible, otherwise fall back to a safe do-nothing option
def progress_bar(iterable, **kwargs):
    if cfg.multi_p:
        try:
            from tqdm import tqdm
            return tqdm(iterable,**kwargs)
        except ImportError:
            return iterable
    else:
        return iterable

def splitPath(path):
    """
    Take a yoda histogram path and return the analysis name and the histogram name
    :arg path: the full path of a yoda analysis object
    :type: String

    """
    from rivet.aopaths import AOPath

    aop = AOPath(path)
    parts = AOPath.dirnameparts(aop)
    analysis = parts[len(parts)-1]
    h_name = AOPath.basename(aop)
    return analysis, h_name

def mkoutdir(outdir):
    """
    Function to make an output directory if it does not already exist.
    Also tests if an existing directory is write-accessible.
    """
    if not os.path.exists(outdir):
        try:
            os.makedirs(outdir)
        except:
            msg = "Can't make output directory '%s'" % outdir
            raise Exception(msg)
    if not os.access(outdir, os.W_OK):
        msg = "Can't write to output directory '%s'" % outdir
        raise Exception(msg)

def write_banner():
    """
    Write a text banner giving the version and pointing to the documentation
    """
    msgs = ["Contur version {}".format(contur.config.version.version),
            "See https://hepcedar.gitlab.io/contur-webpage/"]
    for m in msgs:
        try:
            cfg.contur_log.info(m)
        except:
            print(m)

def insert_line_break(string, length=25):
    """
    insert a LaTeX newline after <length> characters,
    so that labels stay on the plot canvas
    """

    if len(string) <= length:
        # If the string is 20 characters or less, there is no need to break it up.
        return string

    # Initialize the list of fragments.
    fragments = []

    # Split the string into words using whitespace as the separator.
    words = string.split()

    # Initialize the current fragment with the first word.
    current_fragment = words[0]

    # Iterate over the remaining words.
    for word in words[1:]:
        # If adding the next word to the current fragment would make the fragment longer than 20 characters,
        # add the current fragment to the list of fragments and start a new fragment with the current word.
        if len(current_fragment) + len(word) + 1 > length:
            fragments.append(current_fragment)
            current_fragment = word
        else:
            # Otherwise, add the next word to the current fragment with a space separator.
            current_fragment += ' ' + word

    # Add the final fragment to the list of fragments.
    fragments.append(current_fragment)

    # Join the fragments with line breaks.
    result = r'\newline '.join(fragments)

    return result


def walklevel(some_dir, level=1):
    """
    Like os.walk but can specify a level to walk to
    useful for managing directories a bit better

    https://stackoverflow.com/questions/229186/os-walk-without-digging-into-directories-below
    """
    some_dir = some_dir.rstrip(os.path.sep)
    try:
        assert os.path.isdir(some_dir)
    except AssertionError:
        cfg.contur_log.critical("{} is not a directory".format(some_dir))
        sys.exit(1)
    num_sep = some_dir.count(os.path.sep)
    for root, dirs, files in os.walk(some_dir):
        yield root, dirs, files
        num_sep_this = root.count(os.path.sep)
        if num_sep + level <= num_sep_this:
            del dirs[:]


def newlogspace(start, stop, num=50, endpoint=True, base=10.0, dtype=None):
    """
    Numpy logspace returns base^start to base^stop, we modify this here so it returns logspaced between start and stop
    """
    import numpy
    return numpy.logspace(numpy.log(start)/numpy.log(base), numpy.log(stop)/numpy.log(base), num, endpoint, base, dtype)


def get_inspire(inspire_id):
    """
    Function to query InspireHEP database and return a dictionary containing the metadata

    extracted/adapted from rivet-findid

    if contur.config.config.offline is True, no web query is made and returned variables are set to "Offline"
    if contur.config.config.offline is False, but web query fails, returned variables are set to "Failed"


    :arg inspire_id: the ID of the publication on Inspire
    :type inspire_id: ``string``

    :return: pub_data ``dictionary`` -- selected metadata as a dictionary of strings
    """
    
    if not cfg.offline:
        # Get the necessary packages.
        try:
            from urllib.request import urlopen
            import json
        except ImportError:
            from urllib2 import urlopen
            import json
        except  Exception as e:
            cfg.ConturError("Error importing URL modules: {}".format(e))
            cfg.ConturError("Switching to offline mode")
            cfg.offline=True

    pub_data = {}
        
    if cfg.offline:
        pub_data['bibkey']="Offline"
        pub_data['bibtex']="Offline"
    else:
            
        url = "https://inspirehep.net/api/literature/{}".format(inspire_id)

        ## Get and test JSON
        try:
            cfg.contur_log.debug("Querying inspire: {}".format(inspire_id))
            response = urlopen(url)
            cfg.contur_log.debug("Success")
        except Exception as e:
            pub_data['bibkey']="Failed"
            pub_data['bibtex']="Failed"
            cfg.contur_log.error("Error opening URL {}: {}".format(url,e))
            return pub_data

        metadata = json.loads(response.read().decode("utf-8"))
        if metadata.get("status", "") == 404:
            raise cfg.ConturError('ERROR: id {} not found in the InspireHEP database\n'.format(inspire_id))

        try:
            md=metadata["metadata"]
        except KeyError as ke:
            cfg.contur_log.error("Could not find metadata for inspire ID {}".format(inspire_id))
            pub_data['bibkey']="Failed"
            pub_data['bibtex']="Failed"
            return pub_data

        pub_data['bibkey']=str(md["texkeys"][0])
        biburl = metadata["links"]["bibtex"]

        cfg.contur_log.debug("Querying inspire: {}".format(biburl))
        try:
            pub_data['bibtex']=urlopen(biburl).read().decode()
        except Exception as e:
            cfg.contur_log.error("Failed to read bibtex from {} for inspire ID {}".format(biburl,inspire_id))
            pub_data['bibtex']="Failed"
            return pub_data
            
        cfg.contur_log.debug("Success")

    return pub_data

def permission_to_continue(message):
    """Get permission to continue program"""
    permission = ""
    while permission.lower() not in ['no', 'yes', 'n', 'y']:
        permission = str(input("{}\n [y/N]: ".format(message)))
        if len(permission)==0:
            permission = 'N'

    if permission.lower() in ['y', 'yes']:
        return True
    else:
        return False


class Plot(dict):
    ''' A tiny Plot object to help writing out the head in the .dat file '''

    def __repr__(self):
        return "# BEGIN PLOT\n" + "\n".join("%s=%s" % (k, v) for k, v in self.items()) + "\n# END PLOT\n\n"


def cleanupCommas(text):
    '''
    Replace commas and multiple spaces in text by single spaces
    '''
    text=text.replace(","," ")
    
    while "  " in text:
        text=text.replace("  ", " ")
    
    return text.strip()

def remove_brackets(text):
    '''
    remove any brackets from text, and try to turn it into a float.
    return None if not possible.
    '''
    res = text.split("(")[0]+text.split(")")[-1]
    try:
        res = float(res)
    except:
        res = None
        
    return res

def compress_particle_info(name,info):
    ''' 
    Turns a dictionary of properties of the particle <name> into simple string-formatted
    dictionary suitable for storing as parameters: 
    (removes commas, backslashes and spaces and puts <particlename>_<property>)

    '''

    info_dict = {}

    info_dict["{}_mass".format(name)]=info["mass"]
    info_dict["{}_width".format(name)]=info["width"]

    for decay, bf in info.items():
        if not (decay=="mass" or decay=="width"):
            decay = decay.replace(",","")
            decay = decay.replace(" ","")
            decay = decay.replace("\\","")
            info_dict["{}_{}".format(name,decay)]=bf

    return info_dict
    

def compress_xsec_info(info,matrix_elements):
    '''
    compresses a dict of subprocess cross sections into a format they can be stored as AUX params
    (removes commas, backslashes and spaces and puts AUX:<name>_<property>)
    Also, if matrix_elements is not None, then remove any which are not in it.

    '''

    info_dict = {}
    for name, value in info.items():
        name = name.replace(",","")
        name = name.replace(" ","")
        name = name.replace("\\rightarrow","_")
        name = name.replace("\\","")
        if matrix_elements is None or name in matrix_elements:
            name = "AUX:{}".format(name)
            info_dict[name]=value
        
    return info_dict

def hack_journal(bibtex):
    ''' 
    Add a dummy journal field if absent, to stop sphinx barfing.
    '''
    if "journal" in bibtex:
        return bibtex
    else:
        newbibtex = bibtex[:-3]+',journal = "no journal"\n}\n'
        return newbibtex

def find_ref_file(analysis):
    '''
    return the REF data file name and path for analysis with name a_name
    if not found, return an empty string.
    '''
    import rivet
    yoda_name = analysis.shortname+".yoda.gz"
    f = rivet.findAnalysisRefFile(yoda_name)
    return f

def find_thy_predictions(analysis,prediction_id=None):
    '''
    return the THY data file name and path for analysis with name a_name
    and chosen ID.
    if not found, return an empty string.
    '''
    import rivet
    
    predictions = cdb.static_db.get_sm_theory(analysis.name)

    if prediction_id is None:
        return predictions
    
    if predictions is not None:
        for sm in predictions:
            if sm.id == prediction_id:
                return sm
            
    return None, None


def get_beam_dirs(beams):
    """
    return a dict of the paths (under cfg.grid) containing the name of each beam, keyed on beam 
    beams = a list of beams to look for.
    """
    scan_dirs = {}

    for root, dirnames, files in sorted(walklevel(cfg.grid,1)):

        for beam in beams:
            for dir in dirnames:
                if beam.id in dir:                    
                    dir_path = os.path.join(cfg.grid,dir)
                    try:
                        if not dir_path in scan_dirs:
                            scan_dirs[beam.id].append(dir_path)
                        else:
                            cfg.contur_log.warning("Directory name {} is ambiguous as to what beam is belongs to.".format(dir_path))
                    except KeyError:
                        scan_dirs[beam] = [os.path.join(cfg.grid,dir)]
                        

    return scan_dirs
    
def analysis_select(name, veto_only=False):
    """ 
    return true if the analysis passes the select/veto conditions, false otherwise
    """
    import re
    
    for pattern in cfg.vetoAnalyses:
        if re.compile(pattern).search(name):
            return False

    if veto_only:
        return True
        
    if len(cfg.onlyAnalyses)>0:
        for pattern in cfg.onlyAnalyses:
            if re.compile(pattern).search(name):
                return True
        return False
        
    return True

def executeScript(script, plot_dir = "", multiprocess=False, shared_modules_list=[], print_script=True):
    """
    execute a single Python script, with argument string arg
    """
    

    if not os.path.isfile(script):
        if "chi2" in script:
            if  print_script:
                try:
                    cfg.contur_log.warning("No chi2 plot for {}. Likely no signal.".format(script))
                except:
                    print("No chi2 plot for {}. Likely no signal.".format(script))
            return
        else:
            raise FileNotFoundError("Python script {} not found!".format(script))

    
    if print_script:
        try:
            cfg.contur_log.info("Executing {}".format(script))
        except:
            print("Executing {}".format(script))

    try:
        if multiprocess:
            
            # load shared imports
            mpl = importlib.import_module(shared_modules_list[0])
            np  = importlib.import_module(shared_modules_list[1])
            sys_lib = importlib.import_module(shared_modules_list[2])
            os_lib  = importlib.import_module(shared_modules_list[3])

            # global variables (including imports) that are passed to subprocesses
            if plot_dir != "":
                script_globals = {'mpl': mpl, 'np': np, 'sys' : sys_lib, 'os' : os_lib,
                                  '__file__': script, 'YODA_USER_PLOT_PATH' : plot_dir}
            else:
                script_globals = {'mpl': mpl, 'np': np, 'sys' : sys_lib, 'os' : os_lib,
                                  '__file__': script}
                
            # execute script and pass it the dict. of global variables
            exec(open(script).read(), script_globals)
            
        else:
            subprocess.check_call([script + " " + plot_dir], shell=True)

    except Exception as ex:
        print("Unexpected error when executing ", script)
        print(ex)
        
def make_mpl_plots(pyScripts,numcores=1):

    # make the necessary plot directories
    for script, dir in pyScripts:
        if len(dir)>0: mkoutdir(dir)
    
    cfg.contur_log.info("Executing {} plotting scripts.".format(len(pyScripts)))

    if cfg.multi_p:

        # manage matplotlib and numpy processes centrally,
        # so that they are not imported for each individual script
        from multiprocessing import Pool, Manager
        manager = Manager()
        manager_module = manager.Namespace()
        manager_module.shared_modules = ["matplotlib", "numpy", "sys", "os"]

        # Call multiprocessing pool to generate plots
        p = Pool(processes=numcores)

        try:
            # show progress bar only
            import tqdm
            jobs = [p.apply_async(func=executeScript, 
                                  args=(pyScript[0], pyScript[1], True, manager_module.shared_modules, False)) 
                                  for pyScript in pyScripts]
            p.close()
        
            for job in tqdm.tqdm(jobs):
                job.get()

        except ImportError:
            # execute without progress bar but print path to executed python scripts to screen
            p.starmap(func=executeScript, 
                      iterable=[(pyScript[0], pyScript[1], True, manager_module.shared_modules) 
                                for pyScript in pyScripts])
    
    # submit scripts serially
    else:
        for script in pyScripts:
            executeScript(script[0], script[1], False)

def get_numcores(nreq):

    from multiprocessing import cpu_count

    if nreq == 0:
        try:
            numcores = cpu_count()
        except:
            numcores = 1
    # user-specified number
    else:
        numcores = nreq
    return numcores

def pairwise(iterable):
    """
    Iterates pairwise over a list.
    Example: s -> (s0, s1), (s2, s3), (s4, s5), ..
    """
    a = iter(iterable)
    return zip(a, a)

def match_analysis_objects(pattern, ana_objects):
    '''
    Returns the analysis_objects which match a glob-style pattern.
    If the pattern is the form EXPT_YEAR_INSPIRE, will match all histos in that analysis
    '''

    # if passing an analysis pattern, match all histos in the analysis
    if cfg.ANALYSISPATTERN.match(pattern):
        pattern += "*"

    matches = fnmatch.filter(ana_objects, pattern)

    return matches
