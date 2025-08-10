import sys, os
import contur.data.static_db as cdb
import contur.config.config as cfg
import contur.util.utils as cutil
import yoda, rivet
from configobj import ConfigObj
 
def get_histos(filename):
    """
    Get signal histograms from a generated YODA file.
    Loops over all yoda objects in the input file looking for valid signal histograms.

    Ignores REF and THY (which are read elsewhere) and RAW histograms.

    :Param filename: (```string```) name of yoda input file.

    Returns:

    *   mchistos = dictionary containing {path, ao} pairs for candidate signal histograms.
    *   xsec     = yoda analysis object containing the generated xsec and its uncertainty
    *   Nev      = yoda analysis object containing sum of weights, sum of squared weight, number of events

    """

    mchistos = {}
    xsec = None
    Nev = None

    try:
        analysisobjects = yoda.read(filename)
    except Exception as e:
        cfg.contur_log.error("Failed to read {}. {}".format(filename,e))
        return None, None, None

    cfg.contur_log.debug("Found {} analysisobjects in {}".format(len(analysisobjects),filename))
    for path, ao in analysisobjects.items():

        weight = rivet.extractWeightName(ao.path())
        if weight != cfg.weight:
            continue
        if path.startswith('/RAW/_EVTCOUNT'):
            Nev = ao
        if path.startswith('/_XSEC'):
            xsec = ao
        if os.path.basename(path).startswith("_"):
            continue
        if rivet.isRefPath(path):
            # Reference histograms are read elsewhere.
            continue
        if rivet.isRawPath(path):
            continue
        if rivet.isTheoryPath(path):
            # Theory histograms are read elsewhere.
            continue


        else:
            if path not in mchistos:
                mchistos[path] = ao


    if xsec is not None and Nev is not None:
        try:
            cfg.contur_log.info("Found {} potentially valid histograms in {},".format(len(mchistos),filename))
            cfg.contur_log.info("Cross section {} pb, {} generated events".format(xsec.val(),Nev.numEntries()))
        except AttributeError:
            cfg.contur_log.info("Found {} potentially valid histograms in {},".format(len(mchistos),filename)
                                + " with cross section {} pb".format(xsec.point(0).x()))
            
    else:
        raise cfg.ConturError("Found {} potentially valid histograms in {},".format(len(mchistos),filename)
        + " but number of events or cross section could not be determined.")

    return mchistos, xsec, Nev

def read_slha_file(root,slha_file,block_list):
    """
    read requested blocks from an SLHA1 file (if found)

    returns a dictionary blocks_dict{ block: {name: value} }
    for each block in block_list.

    the name of the block is prepended to each parameter, for disambiguation when
    written to the results file.

    for the MASS block the binwidth and binoffset will be applied, if provided.
    @TODO that would be better handled at the visualisation/plotting step?

    :param root: path to SLHA file
    :param slha_file: name of SLHA file
    :param block_list: list of SLHA blocks to read

    :return: dictionary  (blockname, (name, value))

    """

    import pyslha
    blocks_dict = {}

    shla_file_path = os.path.join(root, slha_file)
    if os.path.exists(shla_file_path):

        slha_file = open(shla_file_path, 'r')
        d = pyslha.read(slha_file)
        for block in block_list:
            tmp_dict = {}
            for k, v in d.blocks[block].items():
                if block == "MASS" and cfg.binwidth > 0:
                    tmp_dict["{}:{}".format(block,k)]=cfg.binoffset+cfg.binwidth*int(abs(v)/cfg.binwidth)
                else:
                    tmp_dict["{}:{}".format(block,k)]=v
            blocks_dict[block]=tmp_dict

    else:
        cfg.contur_log.warning("{} does not exist".format(shla_file_path))


    return blocks_dict



def read_param_point(file_path):
    """
    Read a parameter file and return dictionary of (strings of) contents

    :param file_path: full path the the parameter file
    :type file_path: string

    :return: dictionary of parameter (parameter_name, value) pairs

    """
    with open(file_path, 'r') as param_file:
        raw_params = param_file.read().strip().split('\n')

    param_dict = {}
    for param in raw_params:
        name, value = param.split(' = ')
        param_dict[name] = value

    return param_dict


def get_generator_values(root, files, matrix_elements, particles):
    '''
    read and parse the generator log files to get subprocess cross sections
    and/or particle properties.
    '''

    additional_params = {}

    if matrix_elements == None and particles == None:
        # nothing to see here.
        return additional_params

    if cfg.mceg=="herwig":
        # If requested, get particle info from the generator log files
        if particles is not None:
            particle_list = particles.split(",")
            particle_props = contur.util.read_herwig_log_file(root, files, particle_list)
            additional_params.update(particle_props)

        if matrix_elements is not None:
            me_list = matrix_elements.split(",")
            additional_params.update(contur.util.read_herwig_out_file(
                root, files, me_list, particles, particle_props))

        cfg.contur_log.info("Added this info: {}".format(additional_params))


    else:
        cfg.contur_log.error("Log file parsing is not yet implemented for {}.".format(mceg))
        sys.exit(1)




    return additional_params

def cast_arguments(section, key):
    """Walks through the config file, casting optional spey arguments to the correct type."""

    # list of keys to convert from strings (note we can leave arguments expected as strings as they are)
    key2list = ["theory_predictions", "spey"]
    key2float = ["poi_test", "poi_test_denominator", "confidence_level", "low_init", "hig_init"]
    key2int = ["size"]
    key2bool = ["allow_negative_signal"]
    key2list_of_float = ["init_pars"]
    key2list_of_tuple_of_float = ["par_bounds"]
    if key in key2list:
        # function to make single entries in otherwise csv lists into a list
        # for easier processing
        if not type(section[key]) == list:
            section[key] = [section[key]]
    elif key in key2float:
        section[key] = float(section[key])
    elif key in key2int:
        section[key] = int(section[key])

    elif key in key2bool:
        if section[key] == "False":
            section[key] = False
        elif section[key] == "True":
            section[key] = True
        else:
            raise ValueError('Argument {} should be True or False, not {}'.format(section[key], key))
        
    elif key in key2list_of_float:
        if not type(section[key]) == list:
            section[key] = [section[key]]
        
        section[key] = [float(i) for i in section[key]]
    
    elif key in key2list_of_tuple_of_float:
        if not type(section[key]) == list:
            section[key] = [section[key]]
        
        section[key] = [tuple(float(i) for i in item.split(",")) for item in section[key]]


def safe_walk(section):
    """
    Recursively apply cast_arguments to sections,
    safely handling lists created by wildcard sections like [[*]].
    """
    if isinstance(section, list):
        for item in section:
            safe_walk(item)  # recurse into each list item
    elif isinstance(section, dict):  # ConfigObj section
        # apply cast_arguments to each key in the current section
        for key in list(section.keys()):
            if isinstance(section[key], (dict, list)):
                safe_walk(section[key])  # go deeper
            else:
                cast_arguments(section, key)  # apply type casting here

def read_config_file(filename, histos=['*'], configure_theory=True, configure_calculation=True, configure_generator=False):
    """
    Read in the configuration file and convert to a python dict.
    Falls back to default config if the file is empty.

    :param filename: (```string```) name of the config file to read.
    :param histos: (```list```) pattern of analyses to match against (default: all)
    :param read_MCgenerator: (```bool```) for `contur-batch` we want to read this block, but for `contur` we don't (default: False)
    """
    if not os.path.exists(filename):
        cfg.contur_log.info("Config file {} not found. Falling back to default from {}".format(filename,cfg.default_config_path))
        filename = cfg.default_config_path

    config = ConfigObj(filename)
    
    # cast inputs to correct types
    safe_walk(config)

    if configure_generator:
        configure_MCEG(config)
    
    if configure_theory:
        configure_theory_predictions(config)

    if configure_calculation:

        # no --spey flag
        if not cfg.use_spey:
            cfg.contur_log.info("Using default calculation.")

        # have --spey flag
        else:
            # 1. no config file, use the default to configure spey
            if filename == cfg.default_config_path:
                cfg.contur_log.info(f"Using spey calculation, configured by {filename}.")
                configure_spey(config, histos)

            # 2. have a config file, but no spey blocks, so use spey setup from default_config.dat
            elif (not config.get("models")) or (not config.get("calculations")):
                cfg.contur_log.warning(f"Config file {filename} missing 'models' or calculations' block. Fall back to spey configuration from {cfg.default_config_path}.")
                default_spey_config = ConfigObj(cfg.default_config_path)
                configure_spey(default_spey_config, histos)

            # 3. have a config file with spey blocks, so use it
            else:
                cfg.contur_log.info(f"Using spey configuration from {filename}.")
                configure_spey(config, histos)
                

def read_mysql_config_file(filename):
    """
    Read in the MySQL configuration file and set MySQL parameters in cfg.

    :param filename: path to the MySQL configuration file
    :type filename: string

    The configuration file should contain MySQL connection parameters in the format:
    [mysql]
    host = localhost
    port = 3306
    user = your_user
    passwd = your_password
    """
    if not os.path.exists(filename):
        cfg.contur_log.error("MySQL config file {} not found.".format(filename))
        return False

    try:
        config = ConfigObj(filename)

        # Check if mysql section exists
        if not config.get("mysql"):
            cfg.contur_log.error("No 'mysql' section found in config file: {}".format(filename))
            return False

        mysql_config = config["mysql"]

        # Read MySQL parameters and set them in cfg
        if mysql_config.get("host"):
            cfg.mysql_host = mysql_config["host"]
        if mysql_config.get("port"):
            cfg.mysql_port = int(mysql_config["port"])
        if mysql_config.get("user"):
            cfg.mysql_user = mysql_config["user"]
        if mysql_config.get("passwd"):
            cfg.mysql_passwd = mysql_config["passwd"]

        # Check if any MySQL parameter is provided
        if cfg.mysql_host or cfg.mysql_port or cfg.mysql_user or cfg.mysql_passwd:
            cfg.use_mysql = True
            cfg.contur_log.info("MySQL database configuration loaded from: {}".format(filename))
            if cfg.mysql_host:
                cfg.contur_log.info("MySQL host: {}".format(cfg.mysql_host))
            if cfg.mysql_port:
                cfg.contur_log.info("MySQL port: {}".format(cfg.mysql_port))
            if cfg.mysql_user:
                cfg.contur_log.info("MySQL user: {}".format(cfg.mysql_user))
            if cfg.mysql_passwd:
                cfg.contur_log.info("MySQL password: [HIDDEN]")
            return True
        else:
            cfg.contur_log.warning("No MySQL parameters found in config file: {}".format(filename))
            cfg.use_mysql = False
            return False

    except Exception as e:
        cfg.contur_log.error("Failed to read MySQL config file {}: {}".format(filename, e))
        return False


def configure_MCEG(config):
    """
    Update the event generator configuration in the central config.
    """
    
    if not config.get("MCgenerator"):
        raise cfg.ConturError("No 'MCgenerator' block found in config file. ")

    # use wildcards to assign default predictions, and overwrite for specific analyses
    for pattern, config_dict in config['MCgenerator'].items():
        if cfg.mceg!=pattern:
            raise cfg.ConturError("Found {} config but generator is {}".format(pattern,cfg.mceg))
        if pattern == 'herwig':
            cfg.herwig_hp = config_dict['hpconstructor']
            cfg.mceg_template = config_dict['steering_template']
        elif pattern == 'madgraph':
            cfg.mceg_template = config_dict['steering_template']
        elif pattern == 'pbzpwp':
            pass
        elif pattern == 'pythia8':
            cfg.main_program = config_dict['main_program']

def configure_theory_predictions(config):
    """
    Configure the theory predictions for the analysis.
    """
    
    theory_predictions = {}
    if config.get("theory_predictions"):

        # use wildcards to assign default predictions, and overwrite for specific analyses
        for pattern, config_dict in config['theory_predictions'].items():
            if pattern=="*":
                cfg.contur_log.info("Using predicton {} as default".format(config_dict['id']))
            matches = cdb.match_analyses(pattern)
            for ana in matches:
                if pattern!="*":
                    cfg.contur_log.info("Using predicton {} for {}".format(config_dict['id'],ana))
                theory_predictions[ana] = config_dict['id']
        
    else:
        cfg.contur_log.info("No 'theory_predictions' block in config file. Using prediction A.")
        all_anas = matches = cdb.match_analyses("*")

        for ana in all_anas:
            theory_predictions[ana] = "A"

    # update the central config
    cfg.sm_prediction_choices = theory_predictions

def configure_spey(config, histos):
    """
    Configure the spey statistical model and calculations to use
    """
    cfg.contur_log.debug("Building spey config")
    cfg.use_spey = True # have spey blocks, no need to additionally pass --spey flag

    from spey import AvailableBackends
    from spey.interface.statistical_model import StatisticalModel
    
    spey_model_config = {}
    spey_calculation_config = {}

    special_overrides = ["single_bin","combined_likelihood"]

    # configure which spey models to use
    for pattern, config_dict in config['models'].items():
        # check the model name is valid
        if not config_dict.get("name"):
            raise ValueError("'name' key missing from 'model' block for analysis {}".format(pattern))
        
        if not config_dict.get("name") in AvailableBackends():
            raise ValueError("model {} not available in spey".format(config_dict["name"]))
        
        # these aren't analysis patterns, but control predefined groups of analyses
        if pattern in special_overrides:
            spey_model_config[pattern] = config_dict

        # config for this pattern is ok, assign to the matching analyses
        else:
            matches = cutil.match_analysis_objects(pattern, histos)

            for ana in matches:
                spey_model_config[ana] = config_dict

    # configure the calculations to perform
    optimizer_args = {}
    for stat_name, stat_options in config['calculations'].items():
            
        # this block isn't a calculation
        if stat_name == "optimizer_arguments":
            optimizer_args = stat_options
            continue
        
        # need to specify a function to use for this calculation
        if not stat_options.get("function"):
            raise ValueError("'function' key missing from computation block {}".format(stat_name))
        
        # check function is available in spey
        elif not hasattr(StatisticalModel, stat_options["function"]):
            raise ValueError("function {} not available in spey".format(stat_options["function"]))
            
        spey_calculation_config[stat_name] = stat_options
        spey_calculation_config["optimizer_arguments"] = optimizer_args

    # update the central config
    cfg.spey_model_config = spey_model_config
    cfg.spey_calculation_config = spey_calculation_config
