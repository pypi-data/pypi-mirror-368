"""Global configuration class setting default behaviour. Importing contur loads all of the following

:Module members:

Where these are setable from the command line of a given script, see ``` --help``` for documentation.

    * **spey_models_config** (``dict``) each key is an analysis, the value is a dictionary with a 'name key containing the name of the spey model to use
     * **spey_calculation_config** (``dict``) each key is the name of a computation, the value is a dictionary with the spey function name and any options passed to it

Default file names

    * mceg_template (default "herwig.in")
    * paramfile (default "params.dat")
    * tag (default "runpoint")
    * param_steering_file (default "param_file.dat")
    * output_dir (default ANALYSIS)
    * batch_output_dir (default myscan00)
    * **config_file** (default "config.dat")

    * unneeded_files (default ["herwig.run","Looptools.log", "py.py", "mgevents"])
      These files will be removed when runing ```contur-gridtool```

These are used internally, set from other conditions.

    * **silenceWriter** (``bool``) --
      Disables a lot of plotting output, for when it is not needed (eg in grid mode).

    * **contur_log** (``logging.logger``) logger object

    * **stat_types** ["DATABG","SMBG","EXP","HLEXP"] This indexes different ways of evaluating a likelihood.
       DATABG: using the data as the background. Off by default.
       SMBG: if we have the Standard Model prediction, we evaluate the exclusion using this as the background too.
       EXP: this is the expected limit. Evaluated by moving the data central value to the SM prediction (when we have one) 
       HLEXP: this is the expected limit. Evaluated as above, but reducing the uncertainties by sqrt of lumi ratio to the projected HL-LHC

"""
import os
contur_log=None

logfile_name="contur.log"

# this will make numpy raise exceptions instead of printing warnings
import numpy
numpy.seterr(all="raise")

def setup_logger(filename=logfile_name, logstream=None, level="ERROR"):
    """
    set up the logger object

    :param filename: name of log file
    """

    import logging, sys
    import contur.config.config as cfg
    cfg.logfile_name=filename

    level = getattr(logging, level)

    #for some reason we can't supply a formatter to the basic config: https://stackoverflow.com/questions/34319521/python-logging-module-having-a-formatter-causes-attributeerror
    if logstream is None:
        try:
            logging.basicConfig(
                level=level,
                format='%(name)s - %(levelname)s - %(message)s',
                filemode="w",
                filename=cfg.logfile_name,
            )
        except:
            print("Can not write your logfile to {}. Writing to $CONTUR_USER_DIR instead".format(os.path.join(os.getcwd(),cfg.logfile_name)))
            cfg.logfile_name = os.path.join(paths.user_path(),cfg.logfile_name)
            logging.basicConfig(
                level=level,
                format='%(name)s - %(levelname)s - %(message)s',
                filemode="w",
                filename=cfg.logfile_name,
            )

    else:
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            stream=logstream
        )

    stream = (logging.StreamHandler(sys.stdout) if logstream is None else
         logging.StreamHandler(logstream))
    FMT = (logging.Formatter('%(levelname)s - %(message)s') if logstream is None
            else logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    stream.setFormatter(FMT)

    if logstream is None:
        file_handler = logging.FileHandler(cfg.logfile_name)
        file_handler.setFormatter(FMT)

    cfg.contur_log=logging.getLogger("contur")
    cfg.contur_log.addHandler(stream)
    if logstream is None:
        cfg.contur_log.addHandler(file_handler)
    cfg.contur_log.propagate=False

# Setup some module level variable defaults
multi_p = True
graphics = True

# switch for input type. default is signal only, but can be switched to signal+SM combined
sig_plus_bg = False

# if true, only use the diagonal elements of the covariance matrices
diag=False
# treat theory systematics as correlated within a plot
useTheoryCorr=True

# run offline (dont query inspire db)
offline=False

vetoAnalyses=[]
onlyAnalyses=[]
exclude_met_ratio=False
exclude_hgg=False
exclude_hww=True
exclude_b_veto=True
exclude_awz=True
exclude_searches=True
exclude_soft_physics=True
tracks_only=False
splitAnalysis=False

weight=""

# minimum number of systematic uncertainty contributions before they will be treated as correlated via NPs
min_num_sys=5
# only treat theory uncertainties as correlated if we have at least stat+4 scale variations for example.
min_num_sys_sm=5
# include null results in ll ratio
look_elsewhere=False
# use spey for test stat calculations
use_spey = False
# steer which spey backends to use for calculations
spey_model_config = {}
# steer which calculations to perform with spey, and any options
spey_calculation_config = {}
# read in the config once per beam
config_read_for_beams = []

found_ref = []
found_thy = []
silenceWriter=False #For API mode: disable file output

binwidth=-100.
binoffset=0.

using_condor=False
using_qsub  =True
using_slurm =False
seed = 101

condor_os = "CentOS7"
condor_jdl_extras = ["+JobFlavour = 'testmatch'"] #< needed for CERN lxbatch

mceg="herwig"
known_mcegs = ["herwig",  "madgraph","pbzpwp", "pythia8" ]
default_nev=30000
mceg_template=mceg+".in"
keep_hepmc=False
# pythia main default
main_program="main93"

# herwig specific
herwig_hp = "SingleParticleInclusive"

# madgraph specific
write_hepmc_to_tmp = False

# Some default filenames
conturenv="conturenv.sh"
paramfile="params.dat"
tag="runpoint"
unneeded_files=["herwig.run","Looptools.log", "py.py", "mgevents"]
blocklist={"MASS","STOPMIX"}
csvfile=None
param_steering_file="param_file.dat"
summary_file="Summary.txt"
config_file="config.dat"
smtest_config=os.path.join(os.getenv("CONTUR_ROOT"),"contur","config","default_config_smtest.dat")
default_config_path=os.path.join(os.getenv("CONTUR_ROOT"),"contur","config","default_config.dat")

# current runpoint (the beam and the number identifying the param point, eg 13TeV/0001)
runpoint="" 

#####################
# Various directories
#####################
import os
import contur.config.paths as paths

# These directories are operational and can generally be changed from the command line
######################################################################################
# Top level directory where output of a contur run will be written
output_dir="."
# Top level directory where output of a contur run will be read from
input_dir="."
# Location of UFO file and analysis list (*.ana) input for contur-batch
run_info = "RunInfo"
# Top level directory containing a grid being processed.
grid=None

# These directories are operational but will be configured internally
#####################################################################
# Directory to write all plots and html to
plot_dir=os.path.join(output_dir,"plots")
# Directory to write plotting scripts to
script_dir=os.path.join(output_dir,"scripts")
# Configured from user environment. Location of analysis db and default analysis lists
share = paths.user_path()

# These directories are default values. They can't be changed but may be overridden
###################################################################################
# default directory to write all the SM plots to.
smdir = "sm_plots"
# directories to ignore when looking for yoda files.
hidden_directories=["mgevents","ANALYSIS"]
# Directory where the batch scripts will be written by contur-batch
batch_output_dir="myscan00"

# switch to tell contur whether it is running on a grid or on a single yoda file
gridMode=False

add_to_results_db=False
results_dbfile="contur_run.db"
models_dbfile="models.db"

import re
# This allows for the form EXPERIMENT_YEAR_INSPIRENUMBER or EXPERIMENT_PHYSICSGROUP_YEAR_ID
APATT=r'(([A-Z0-9]+_\d{4}_[IS]\d{5,8})|([A-Z0-9]+_[A-Z]{4}_\d{4}_[A-Z0-9]+)'
ANALYSISPATTERN = re.compile(APATT+r')')
ANALYSIS        = re.compile(r'('+APATT+r')[^/]*)')
ANALYSISHISTO   = ANALYSISHISTO   = re.compile(r'('+APATT+r')[^/]*)/((d\d+-x\d+-y\d+)|\w+)')

# reference data indexed by the yoda object path
refObj = {}
refCorr = {}
refUncorr = {}
refErrors = {}
# SM theory predictions indexed by analysis name
sm_prediction = {}
sm_prediction_choices = {} # from config file
prediction_choice = "A" # used only by SM test

# A one-off to hold objects that have been scaled in an unscaled form for plotting
plotObj = {}

# various types of statistic evaluations
databg = "DATABG"
smbg = "SMBG"
expected = "EXP"
hlexpected = "HLEXP"
ctzero = "ctzero"
#default
stat_types = [smbg,expected,hlexpected]
stat_to_human = {
    databg : "bkg=data",
    smbg : "bkg=SM",
    expected : "exp.",
    hlexpected : "exp. (HL-LHC)",
#    ctzero : "ct=0"
}
primary_stat = smbg
hllhc_intl_fb = 3000.0
scale_signal_evtcount = True # scale signal evnt count by root(n)
flat_uncertainty = None # flat uncertainty to add to data

# plotting heatmaps with spey
plot_metrics = {
    'CLs' : r"CL$_{s}$",
    'mu_upper_limit' : r"$\mu_{max}$",
    'mu_lower_limit' : r"$\mu_{min}$",
    'mu_hat' : r"$\hat{\mu}$"
}

# rivet histo display
nostack = False

# plotting config
contour_colour = {}
contour_colour[databg]="white"
contour_colour[smbg]="black"
contour_colour[expected]="black"
contour_colour[hlexpected]="red"
contour_style = {}
contour_style[databg]="solid"
contour_style[smbg]="solid"
contour_style[expected]="dotted"
contour_style[hlexpected]="dotted"
map_colorCycle=None
plot_format="pdf"

# mysql config
mysql_host = ""
mysql_port = 3306
mysql_user = ""
mysql_passwd = ""
use_mysql = False

class _DuplicateFilter(object):
    """
    Private class to filter log messages so only one instance shows once, from:
    from https://stackoverflow.com/questions/31953272/python-logging-print-message-only-once
    """
    def __init__(self):
        self.msgs = set()

    def filter(self, record):
        rv = record.msg not in self.msgs
        self.msgs.add(record.msg)
        return rv

class ConturError(Exception):
    pass
