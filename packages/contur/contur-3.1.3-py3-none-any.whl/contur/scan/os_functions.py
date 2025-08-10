#!/usr/bin/env python

"""
Functions that operate directly on the operating/file system in a contur grid.

"""

import os
import shutil
import sys
from builtins import input
import textwrap

import contur
from configobj import ConfigObj
import contur.config.config as cfg
import contur.util.utils as cutil
import contur.util.file_readers as cfr



run_key_list = ["generator", "contur", "environment"]

def write_sampled_map(output_dir, param_dict):
    """
    write a config object of the sampled points to a text file (sampled_points.dat) in the output_dir containing
    parameters and values scanned in a grid beneath output_dir.

    :param output_dir: directory to write the file to

    :param param_dict: dictionary of 

    """

    sampled_points = ConfigObj()
    sampled_points["keys"] = param_dict.keys()
    sampled_points["values"] = {}
    for k, v in param_dict.items():
        sampled_points["values"][k] = list(v["values"])
    sampled_points["points"] = {}

    for root, _, files in os.walk(output_dir):
        for file_name in files:
            if file_name == cfg.paramfile:
                run_point = os.path.basename(root)
                param_file_dict = cfr.read_param_point(os.path.join(root, file_name))
                sampled_points["points"][run_point] = param_file_dict
    sampled_points.filename = os.path.join(output_dir, 'sampled_points.dat')
    sampled_points.write()


def read_sampled_map(input_dir):
    """
    read the sampled_points.dat file

    :return: sampled_points: the sampled points as a ConfigObj
    
    """
    
    sampled_points = ConfigObj(os.path.join(input_dir, "sampled_points.dat"))
    # sampled_points.walk(sanitise_inputs_map, call_on_sections=True)
    return sampled_points


def sanitise_inputs(section, key):
    """Function specific to config obj to walk and convert key values."""

    # list of keys to convert from strings to ints/floats
    key2float = ["start", "stop", "value"]
    key2int = ["number"]
    key2list = run_key_list
    if key in key2list:
        # function to make single entries in otherwise csv lists into a list
        # for easier processing
        if not type(section[key]) == list:
            section[key] = [section[key]]
    if key in key2float:
        section[key] = float(section[key])
    if key in key2int:
        section[key] = int(section[key])


def get_exclusions(filename=""):
    """
    Get points that we will exclude from param file

    :param filename: name of the parameter file to read. If empty, the value from cfg is used.

    """

    if filename == "":
        filename = cfg.param_steering_file
        
    config = ConfigObj(filename)
    if 'SkippedPoints' in config.keys():
        return [int(i) for i in str.split(config['SkippedPoints']['points'])]
    else:
        return []


def read_param_steering_file(filename=""):
    """
    Read in the parameter card and convert to a python dict

    :param filename: name of the steering file. If empty, the value from cfg is used

    """

    if filename == "":
        filename = cfg.param_steering_file

    
    config = ConfigObj(filename)
    config.walk(sanitise_inputs, call_on_sections=True)
 
    try:
        param_dict = config["Parameters"]
    except:
        cfg.contur_log.error("Error reading {}".format(filename))
        raise KeyError("Input parameter file must contain Parameters block")

    try:        
        run_dict = config["Run"]
        run_args = run_key_list
        for run_arg in run_args:
            if run_arg in run_dict.keys():
                for path in run_dict[run_arg]:
                    if not os.path.exists(path):
                        print("Warning: For %s setup,  %s does not exist!\n" %
                              (run_arg, path))
                        if not cutil.permission_to_continue("Do you wish to continue?"):
                            sys.exit()
    except KeyError:
       cfg.contur_log.info("No run block in {}. Will use environment variables".format(filename))
       run_dict = None



    for param_name, param_config_dict in param_dict.items():
        # apart from "block" (which is used with SLHA files), these are actually required, not just allowed.
        allowed_modes = {
            "LOG": {"start", "stop", "number","block"},
            "LIN": {"start", "stop", "number","block"},
            "CONST": {"value","block"},
            "REL": {"form","block"},
            "DIR": {"name"},
            "SINGLE": {"name"},
            "SCALED": {"name"},
            "DATAFRAME": {"name"},
            "CONDITION": {"form"}
        }

        def fmt_iter(iterable):
            if len(iterable) == 0:
                return "(None)"
            return ", ".join(iterable)

        try:
            param_mode = param_config_dict["mode"]
        except KeyError:
            error_message = """
            All parameters in {param_steering_file} must have a mode assigned.
            Choose from either: {options}
            """.format(param_steering_file=filename, options=fmt_iter(allowed_modes.keys()))
            raise ValueError(textwrap.dedent(error_message))
        try:
            required_param_keys = allowed_modes[param_mode]
        except KeyError:
            raise ValueError("Param mode \"{param_mode}\" not allowed. Please, "
                             "choose from {options}".format(
                param_mode=param_mode, options=fmt_iter(allowed_modes.keys())))

        param_keys = set(param_config_dict.keys())

        # We spare from including "mode" in every entry in the dict
        # `allowed_modes`, as it is obvious that each mode must include the
        # mode key. However, when checking its presence, we need to include it.
        complete_req_param_keys = required_param_keys | {"mode"}
        missing_keys=fmt_iter(complete_req_param_keys - param_keys)
        
        if param_keys != complete_req_param_keys and not missing_keys=="block":
            error_message = """
            In parameter file "{param_steering_file}", parameter block "{param_name}", 
            mode "{param_mode}" requires keys: {required_keys}.
                Missing keys: {missing_keys}.
                Disallowed keys: {disallowed_keys}.
            """.format(
                param_steering_file=filename,
                param_name=param_name,
                param_mode=param_mode,
                required_keys=fmt_iter(complete_req_param_keys),
                missing_keys=fmt_iter(complete_req_param_keys - param_keys),
                disallowed_keys=fmt_iter(param_keys - complete_req_param_keys),

            )
            raise ValueError(textwrap.dedent(error_message))

    return param_dict, run_dict


def make_run_point_directory(run_point, output_dir):
    """
    If run point directories don't exist, make them and return path
    """

    run_point_dir_name = "%04i" % run_point
    run_point_path = os.path.join(output_dir, run_point_dir_name)
    cutil.mkoutdir(run_point_path)
    return run_point_path

def write_param_dat(param_dict, run_point_path, run_point):
    """
    Write param file containing parameter values for given run point.
    """
    config = ConfigObj()
    for param, info in sorted(param_dict.items()):

        value = info['values'][run_point]
        config[param] = info["values"][run_point]

    config.filename = os.path.join(run_point_path, cfg.paramfile)
    config.write()



def gen_format_dict(parameters, idx):
    """
    Create dictionary to use in formatting template run card.

    :param parameters: (parameter, value) pairs
    :type parameters: dict
    :param idx: numerical ID (nnnn) of the paramter point

    """
    format_dict = {}
    for param, info in sorted(parameters.items()):
        format_dict[param] = info['values'][idx]
    return format_dict


def write_generator_files(templates, param_dict, run_point, run_point_path, pipe_hepmc, seed, num_events, beam):
    """
    Write the generator steering files, based on templates, formatted with parameter values.
    Generator is determined by cfg.mceg

    :param templates: list of template files
    :param param_dict: dictionary of event generator parameters
    :param run_point: the numeric id of the run point 
    :param run_point_path: the full path of the run point directory
    :param pipe_hepmc: run the hepmc events from the generator through a unix pipe to rivet
    :type pipe_hepmc: bool
    :param seed: random number seed for the event generator
    :param num_events: number of MC event generator events per parameter point
    :param beam: collider beam being generated

    """

    for template_name in templates:
        raw_template_text = templates[template_name]
        format_dict = gen_format_dict(param_dict, run_point)
        try:
            template_text = raw_template_text.format(**format_dict)
        except KeyError:
            cfg.contur_log.critical("Error: Parameters in {} do not match the parameters in {}.".format(cfg.param_steering_file, template_name))
            sys.exit(1)
        except IndexError:
            cfg.contur_log.critical("IndexError: Have you used an integer parameter name in {}?".format(template_name))
            sys.exit(1)

        # Commands for specific generators added here with conditionals on
        # the config.
        if cfg.mceg == "herwig":

            from .herwig_steering import herwig_template_beam_config
            template_text = herwig_template_beam_config(template_text, pipe_hepmc, beam)

        elif cfg.mceg == "madgraph":

            from .madgraph_steering import madgraph_check_config,\
                                           madgraph_template_beam_config,\
                                           madgraph_template_run_config
            template_text = madgraph_template_beam_config(template_text, pipe_hepmc, beam)
            template_text = madgraph_template_run_config(template_text, seed, num_events)
            template_text = madgraph_check_config(template_text)

        template_path = os.path.join(run_point_path, template_name)
        with open(template_path, 'w') as f:
            f.write(template_text)

class WorkingDirectory:
    """Context manager to temporarily change working directory"""

    def __init__(self, temp_working_directory):
        self.temp_working_directory = os.path.abspath(temp_working_directory)

    def __enter__(self):
        self.working_directory = os.getcwd()
        os.chdir(self.temp_working_directory)

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.working_directory)


def delete_files(root):
    """
    delete all the superfluous files in root

    the superfluous files are defined in cfg.unneeded_files

    """
    for delete_file in cfg.unneeded_files:
        try:
            file_path = os.path.join(root, delete_file)
            if os.path.isdir(file_path):
                shutil.rmtree(file_path)
            else:
                os.remove(os.path.join(root, delete_file))
        except OSError:
            cfg.contur_log.debug(' {} not found'.format(
                os.path.join(root, delete_file)))


