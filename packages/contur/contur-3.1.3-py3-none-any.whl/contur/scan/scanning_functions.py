# -*- python -*-
import pickle

import numpy as np
import pandas as pd

from .os_functions import *
import contur.util.utils as cutil
import contur.config.config as cfg
import contur.util.utils as cutil

def invalid_params(run_point, param_dict):
    """
    return false is any of the params are invalid for this run_point
    """

    for param, info in sorted(param_dict.items()):

        value = info['values'][run_point]
        try:
            if np.isnan(value):
                cfg.contur_log.warning("Invalid parameter value {} for {}".format(value,param))
                return True
        except:
            # this test is moot
            pass
            
        if info['mode']=='CONDITION' and not bool(value):
            return True
        

    return False
        


def read_template_file(template_file_in):
    """Read in template files and store contents in dictionary"""
    template = {}
    with open(template_file_in, 'r') as f:
        template[cfg.mceg_template] = f.read()
    return template


def check_param_consistency(param_dict):
    """Check that parameters in param file match those in templates."""

    with open(cfg.mceg_template, 'r') as template_file:
        template_text = template_file.read()

    from string import Formatter
    template_param_names = set(
        [fn for _, fn, _, _ in Formatter().parse(template_text) if
         fn is not None])
    param_names = set(param_dict.keys())

    # Check that there aren't unknown params in the template
    if not template_param_names.issubset(param_names):
        unknown = template_param_names - param_names
        cfg.contur_log.critical("Error: unknown parameters {} in template file {}".format(
            list(unknown), cfg.mceg_template))
        # TODO: it'd be better to raise this as an exception, so the calling
        #  code can take evasive action, e.g. cleaning up aborted scan dirs.
        #  Usually a good plan that only top-level code calls exit()
        sys.exit(1)

    # Check that all param names are used: warn but not exit if not
    if template_param_names < param_names:  # < i.e. proper subset
        unused = param_names - template_param_names
        cfg.contur_log.warning("parameters {} unused in template file {}".format(
            list(unused), cfg.mceg_template))


def sample_fromvalues(param_dict, num_points):
    """
    for read mode we return the grid by having already worked out each axis
    (allows us to mix LIN and LOG)
    """

    dimensions = len(param_dict)
    points_per_dim = round(num_points ** (1. / dimensions))
    if not np.isclose(points_per_dim, num_points ** (float(1. / dimensions))):
        permission_message = ("If using uniform mode number of points^"
                              "(1/dimensions) must be an integer!\n"
                              "Do you want to use %i points?"
                              % points_per_dim ** dimensions)
        if not cutil.permission_to_continue(permission_message):
            sys.exit()
    grid = np.meshgrid(*[param["axes"] for param in param_dict.values()])
    coords = [np.reshape(dim, dim.size) for dim in grid]
    return coords

def coords_from_axes(param_dict, param_names=None):
    """
    Read the param_dict that has been dressed with axes values and build a grid
    to return
    """
    if param_names is None:
        axes_list = [v['axes'] for v in param_dict.values()]
    else:
        axes_list = [v['axes']
                     for k, v in param_dict.items()
                     if k in param_names]

    grid = np.meshgrid(*axes_list)
    coords = [np.reshape(dim, dim.size) for dim in grid]
    return coords


def generate_points(param_dict):
    """
    Generate points to sample using given mode.

    parameters:
        param_dict: Dictionary with parameter names as keys each containing another
        dictionary with keys 'range' and 'values'.

    returns: 
        - param_dict: Same param_dict as was passed in to the function but now filled
          with points.
        - num_points: The number of points generated.

    """

    # We use a dictionary to group the param names to reduce the number of
    # iterations and avoid duplicating the dictionary.
    # Currently, we classify them only for DATAFRAME and REL categories, as these
    # modes require special action. DATAFRAME requires loading a dataframe and merging
    # the data points back into the grid separately. REL requires filling in all
    # points first to then determine its value relative to another parameter.
    # CONDITION requires filling all point first then using them to see
    # whether the condition is satisfied.
    grouped_param_names = {
        'df': [],
        'non-df': [],
        'condition': [],
        'rel': [],
        'non-rel': []
    }

    # This dictionary will hold three dataframes: one for the data loaded
    # from the Pickle file, another for the axes generated programmatically,
    # and a final dataframe that will contain both.
    points = {
        'df': None,
        'non-df': None,
        'final': None
    }


    def replace_and_eval_rel(series):
        """
        evaluate the expressions for relative parameters and replece them in ``series``.
        """
        # initially, this holds values of the non-rel params
        # when each series is calculated, it can be added to this to calculate other rel series
        established_values = {param: series[param] for param in
                                  grouped_param_names['non-rel']}
        

        for rel_param in grouped_param_names['rel']:
            # cfg.contur_log.debug('calculating values for REL param {}'.format(rel_param))
            conditions = {param: series[param] for param in
                              grouped_param_names['condition']}
            
            # cfg.contur_log.debug('conditions = {}'.format(conditions))
            if all(conditions.values()):            
                try:
                    formatted_expr = param_dict[rel_param]['form'].format(**established_values)
                except KeyError:
                    cfg.contur_log.critical("KeyError on {}. Does this depends on another REL parameter beneath this in the param file?".format(rel_param))
                    sys.exit(1)
                try:
                    series[rel_param] = eval(formatted_expr)
                except:
                    cfg.contur_log.error("Error evaluating one of your relative parameters.")
                    cfg.contur_log.error("Could not evaluate {}. Check your values?".format(formatted_expr))
                    raise
                val = float(series[rel_param])

                # successfully calculated values for this REL param, so can use it to calculate others
                established_values[rel_param] = val
            else:
                val = float("NaN")
        return series

    def replace_and_eval_conditions(series):
        """
        evaluate the expressions for relative parameters and replece them in ``series``.
        """
        for condition in grouped_param_names['condition']:
            non_rel_values = {param: series[param] for param in
                              grouped_param_names['non-rel']}
            rel_values = {param: series[param] for param in
                              grouped_param_names['rel']}
            try:
                formatted_expr = param_dict[condition]['form'].format(**non_rel_values,**rel_values)
            except KeyError:
                cfg.contur_log.critical("KeyError on {}. This may mean you have tried to specify a condition using REL parameters.".format(condition))
                sys.exit(1)

            series[condition] = float(eval(formatted_expr))  # cast to avoid dtype incompatibility
            val = bool(series[condition])

        return series

    
    def append_param(param_name, mode):
        """
        This function classifies a given param name according to its mode for
        efficient iteration in other parts of the code.
        """
        if mode == 'DATAFRAME':
            grouped_param_names['df'].append(param_name)
        else:
            grouped_param_names['non-df'].append(param_name)
        if mode == 'REL':
            grouped_param_names['rel'].append(param_name)
        elif not mode == 'CONDITION':
            grouped_param_names['non-rel'].append(param_name)
        if mode == 'CONDITION':
            grouped_param_names['condition'].append(param_name)
            
    for param_name, param_config_dict in param_dict.items():
        create_axes(param_config_dict)
        append_param(param_name, param_config_dict['mode'])
            
    if len(grouped_param_names['df']) > 0:
        points['df'] = load_df_points(param_dict)

    if len(grouped_param_names['non-df']) > 0:
        # If there are params that do not have the DATAFRAME mode, we create the
        # grid independently for those.
        points['non-df'] = coords_from_axes(param_dict,
                                            grouped_param_names['non-df'])
        # Non-df refers to the fact that the points are not loaded from a
        # dataframe. However, we do use a pandas DataFrame to manipulate the
        # data.
        points['non-df'] = pd.DataFrame(
            np.array(points['non-df']).T, columns=grouped_param_names['non-df'])

    # Merge the non-df and df param grids, creating a new grid will all
    # possible combinations. It is important to preserve the fixed
    # combinations provided in the Pickle Dataframe file, i.e. treat
    # every row as a fixed object and not combine the pickle dataframe
    # columns separately.
    if points['df'] is None:
        points['final'] = points['non-df']
    elif points['non-df'] is None:
        points['final'] = points['df']
    else:
        points['final'] = (pd
                           .merge(points['non-df'].assign(key=0),
                                  points['df'].assign(key=0),
                                  on='key')
                           .drop('key', axis=1))

    
    # and for the conditions
    points['final']=points['final'].apply(replace_and_eval_conditions, axis=1)

    # Now we have merged the two separate grids, we will do the required
    # substitutions for the REL params.
    points['final']=points['final'].apply(replace_and_eval_rel, axis=1)

    for param in param_dict.keys():
        # Now, copy the coordinates into the param dictionary.
        param_dict[param]['values'] = np.array(points['final'][param])

    num_points = len(points['final'].index)
    return param_dict, num_points


def create_axes(param_config_dict):
    """
    this is a bit of hybrid mess, should just make the grid directly
    out of these axes and attach to object I think?....
    """
    
    mode = param_config_dict["mode"]

    if mode in ("LOG", "LIN"):
        start = param_config_dict["start"]
        stop = param_config_dict["stop"]
        number = param_config_dict["number"]
        if mode == "LOG":
            # quick work to make the file read log spacing
            logspace = cutil.newlogspace
            param_config_dict["axes"] = logspace(start, stop, number)
        else:
            param_config_dict["axes"] = np.linspace(start, stop, num=number)
    elif mode == "CONST":
        param_config_dict["axes"] = param_config_dict["value"]
    elif mode == "REL":
        # for now just give REL a dummy 0 axis
        param_config_dict["axes"] = 0.0
    elif mode == "DIR":
        param_config_dict["axes"] = 0.0
        scan_dir = param_config_dict["name"]
        if os.path.isdir(scan_dir):
            param_config_dict["axes"] = os.listdir(scan_dir)
        else:
            cfg.contur_log.critical("{} is not a directory".format(scan_dir))
            sys.exit(1)
    elif mode == "SINGLE" or mode == "SCALED":
        # single string, usually an SLHA file name
        param_config_dict["axes"] = param_config_dict["name"]
    elif mode == "DATAFRAME":
        param_config_dict["axes"] = 0
    elif mode == "CONDITION":
        param_config_dict["axes"] = 0
    else:
        raise ValueError(
            "Unrecognised mode parameter %s in param_card.dat " % mode)


def filter_param_dict_by_key(param_dict, expr):
    """
    filter the parameter dictionary based on the key

    :param param_dict: dictionary containing the model parameters.

    :param expr: expression which, if true, means the parameter passes

    """
    return {
        param_name: param_config_dict
        for (param_name, param_config_dict)
        in param_dict.items()
        if expr(param_config_dict['mode'])
    }


def load_df_points(param_dict):
    """
    Loads the parameter points for DATAFRAME mode from the given Pickle file(s).
    """

    # These are the dataframe parameters.
    df_params = filter_param_dict_by_key(param_dict, lambda mode: mode == 'DATAFRAME')
    # We have to load the pickle file, verify its a valid file, and load the
    # values in the dataframe into the grid.

    files = list(set(param_config_dict['name'] for param_config_dict in
                     df_params.values()))

    # For now, we will enforce that only one file can be loaded at a time.
    # If not, it is ambiguous in what way we should combine the values
    # (element-wise or an outer product, i.e. forming a mesh-grid?)
    # This can be easily extended if a clear implementation is set out.

    if len(files) > 1:
        raise ValueError('At the moment, only one Pickle file can be used for '
                         'the same param file, for parameters in DATAFRAME mode.')
    filename = files[0]
    cwd = os.getcwd()
    if os.path.isabs(filename):
        file_path = filename
    else:
        file_path = os.path.join(cwd, filename)

    if not os.path.exists(file_path):
        raise ValueError('File {filename} does not exist (cwd {cwd})'.format(
            filename=filename, cwd=cwd))

    df = pd.read_pickle(file_path)
    if not isinstance(df, pd.DataFrame):
        raise ValueError('{filename} does not contain a valid pandas '
                         'DataFrame.'.format(filename=filename))

    provided_params = set(df.columns)
    required_params = df_params.keys()
    missing_params = set(required_params) - provided_params

    if len(missing_params) > 0:
        raise ValueError('Parameters {missing_params} specified as DATAFRAME mode '
                         'in param file but not found in Pickle '
                         'file.'.format(missing_params=missing_params))

    return df[required_params]


def run_scan(param_dict, beams, num_points, pipe_hepmc, seed, num_events, single, exclusions=[]):
    """
    Given points defined in param_dict, create run point directories
    and populate with MCEG template file and parameter file.

    :param param_dict: 
        Dictionary with parameter names as keys each containing another
        dictionary with keys 'range' and 'values'.

    :param pipe_hepmc: is True, running hepmc events to a pipe for rivet to read. otherwise using a native generator rivet interface. 

    :param seed: random number seed

    :param num_events: number of events to generate
    :param exclusions: list of run points to be excluded
 
    :returns: None

    """

    # Read in run card template files
    template = read_template_file(cfg.mceg_template)

    cutil.mkoutdir(cfg.output_dir)
        
    for beam in beams:

        if single:
            msg_string = "Building example for {}".format(beam.id)
        else:
            msg_string = "Building scripts for {}".format(beam.id)

        directory = os.path.join(cfg.output_dir,beam.id)
        cutil.mkoutdir(directory)

        for run_point in cutil.progress_bar(range(num_points), desc=msg_string):
            # Skip this point if it is excluded in param file
            if run_point in exclusions:
                continue

            if invalid_params(run_point, param_dict):
                continue
            
            # Run point directories are inside the output directory and hold
            # the necessary files to run the generator with the param_dict
            # associated with that point
            run_point_path = make_run_point_directory(run_point, directory)

            # Write generator run card files formatted with parameter values
            write_generator_files(template, param_dict, run_point,
                                  run_point_path, pipe_hepmc, seed, num_events, beam)

            # Write all sampled points and their run points to a .dat file
            write_map = True
            if "slha_file" in param_dict.keys():

                import pyslha
                slha_mode = param_dict['slha_file']['mode']

                if slha_mode == "DIR":
                    # copy the SLHA file over
                    info = param_dict['slha_file']
                    f_source = os.path.join(
                        param_dict['slha_file']['name'],
                        info['values'][run_point])
                    f_dest = os.path.join(
                        os.getcwd(), run_point_path, info['values'][run_point])
                    shutil.copyfile(f_source, f_dest)
                    write_map = False

                elif slha_mode == "SINGLE" or slha_mode == 'SCALED':

                    # need to add any modified parameters to the dict for writing out.


                    # Read the SLHA, modify it and write it out.
                    slha_name = param_dict['slha_file']['name']
                    susy = pyslha.read(slha_name)

                    for param, info in sorted(param_dict.items()):

                        # looks at all the other params now.
                        if param != 'slha_file':

                            if slha_mode == 'SCALED':
                                # they should all be blocks that exist in the file
                                try:
                                    for ident in susy.blocks[param].keys():
                                        slha_val = susy.blocks[param][ident]
                                        susy.blocks[param][ident] = slha_val * float(info['values'][run_point])
                                except KeyError:
                                    cfg.contur_log.critical("SLHA BLOCK not found:{}".format(param))
                                    sys.exit(1)

                            elif slha_mode == 'SINGLE':
                                try:
                                    block = param_dict[param]['block']
                                except KeyError:
                                    cfg.contur_log.critical("Missing SLHA Block Name:{}".format(param))
                                    sys.exit(1)
                                for ident in susy.blocks[block].keys():
                                    try:
                                        if ident == int(param[1:]):
                                            susy.blocks[block][ident] = float(info['values'][run_point])
                                    except ValueError:
                                        cfg.contur_log.critical("Malformed SLHA ident:{}".format(param))
                                        sys.exit(1)


                    f_dest = open(os.path.join(
                        os.getcwd(), run_point_path, slha_name), "w")
                    pyslha.write(f_dest, susy)


            # Write parameter file inside run point directory. This is purely to
            # record what the param_dict are at this run pointg
            write_param_dat(param_dict, run_point_path, run_point)

            if single:
                break
        if write_map:
            write_sampled_map(directory, param_dict)
