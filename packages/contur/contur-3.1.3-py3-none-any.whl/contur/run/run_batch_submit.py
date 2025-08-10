"""
Main module for building and submitting event generator jobs to a batch farm based on a parameter grid.

"""

import os, sys
import subprocess
import numpy as np
import argparse
from configobj import ConfigObj
import logging
import shutil

import contur
import contur.config.config as cfg
import contur.util.file_readers as cfr
import contur.scan.os_functions
import contur.scan.scanning_functions
import contur.scan.grid_tools

def gen_batch_command(directory_name, directory_path, args, setup_commands, runbeam):
    """
    Generate the shell commands to write to the batch file for submitting an event generation job

    A script can be invoked to set up the general runtime environment for each job. This may not be necessary, but 
    is taken from the following sources (in order of precedence).
    (1) setup script command line argument
    (2) line from param_file.dat 
    (3) INSTDIR environment variable with a name guess of setupEnv.sh

    The key contur environment variables will be taken from the current runtime environment. (see set_current_env) unless specified in param_file.dat 
    
    :param directory_name: name of the directory (without any path) in the which batch job will run (usual 4 integers eg 0123
    :param directory_path: full, absolute path to the directory in which the batch job will run.
    :param args: command line arugments
    :param setup_commands: the commands read from the param file to set up the genertor. If not present, may be taken from the environment.
    :param runbeam: the collider beam being run.

    :return: batch_command, batch_filename, job_description_content[=None], job_description_filename[=None]

    """

    batch_command = "#! /bin/bash\n"
            
    if cfg.mceg != "madgraph":  # TODO make this work for MG too.
        batch_command += env_setup(args['setup_script'],directory_path)
    
    # TODO: not so nice to have to hard-code specific generators here... can we do it more generically?
    if cfg.mceg == "herwig":

        from contur.scan.herwig_steering import gen_herwig_commands

        # Add Herwig-specific commands
        batch_command += gen_herwig_commands(
            directory_name, args['run_info'], args['pipe_hepmc'], args['seed'], args['num_events'], runbeam)

    elif cfg.mceg == "pbzpwp":

        from contur.scan.powheg_steering import gen_pbzpwp_commands
        from contur.scan.powheg_steering import gen_pbzpwppy8_commands

        # PBZp commands
        batch_command += gen_pbzpwp_commands(directory_name, args['run_info'], args['num_events'], runbeam)

        # Set up the runtime environment
        batch_command += "source {}\n".format(setup_commands['generator'][1])

        # Set up Contur environment
        for l in setup_commands['contur']:
            batch_command += "source {}\n".format(l)

        # Pythia commands
        batch_command += gen_pbzpwppy8_commands(directory_name, args['run_info'], args['num_events'], runbeam)

    elif cfg.mceg == "pythia8":

        from contur.scan.pythia8_steering import gen_pythia8_commands

        # Pythia8 commands
        batch_command += gen_pythia8_commands(directory_name, args['run_info'], args['num_events'], runbeam)

    elif cfg.mceg == "madgraph":

        from contur.scan.madgraph_steering import gen_madgraph_commands

        # Set up the runtime environment, MadGraph needs additional 'environment' setting as well
        for l in setup_commands['generator']:
            batch_command += "export MG_EXEC='{}'\n".format(l) #< TODO: won't this loop just overwrite all but the last iteration?
        for l in setup_commands['environment']:
            batch_command += "source {}\n".format(l)

        # Set up Contur environment
        for l in setup_commands['contur']:
            batch_command += "source {}\n".format(l)

        # Change directory to run-point folder
        batch_command += "cd {}\n".format(directory_path)

        # Madgraph-specific commands
        batch_command += gen_madgraph_commands(
            directory_path, args['run_info'], args['pipe_hepmc'], args['seed'], args['num_events'], runbeam)

    batch_basename = cfg.tag + "_" + directory_name
    batch_filename = batch_basename + '.sh'
    job_description_content = None
    job_description_filename = None

    # If using Condor: generate a job description language file to accompany the script(s):
    # - Generate JDL file, one for each individual job execution
    # - Generate the job execution scripts as usual
    # - Submit the JDL file instead the job script to the hex machine at ppe instead of the qsub systems using any machine
    # In the meantime, need to add a flag to the batch_submit functionality to select which batch system is using HTCondor or qsub
    # return a list of [content,filename] pairs, to support JDL submission systems
    #
    if cfg.using_condor:
        job_description_filename = batch_basename + '.job'
        job_description_content = ""
        job_description_content += "universe = vanilla\n"
        job_description_content += "executable = {}.sh\n".format(batch_basename)
        job_description_content += "log = {}.sh.log\n".format(batch_basename)
        job_description_content += "requirements = OpSysAndVer==\"{}\"\n".format(cfg.condor_os)
        job_description_content += "getenv = True\n"
        job_description_content += "output = {}.sh.out\n".format(batch_basename)
        for jdl in cfg.condor_jdl_extras:
            job_description_content += jdl + "\n"
        if args['walltime'] is not None:
            # convert unit
            hours, minutes = args['walltime'].split(":")
            minutes = 60*int(hours) + int(minutes) # add hours to minutes
            job_description_content += "maxWallTime = {:d} # min\n".format(minutes)
        if args['memory'] is not None:
            # convert unit
            numbermb, unit = args['memory'][0:-1], args['memory'][-1]
            if unit == "G":
              numbermb = int(number)*1000 # convert GB to MB
            job_description_content += "requestMemory = {:d} # MB\n".format(numbermb)
        job_description_content += "queue\n"

    # Return a 4-tuple of run-script & job-description contents and filenames
    return batch_command, batch_filename, job_description_content, job_description_filename

def gen_submit_command(queue, walltime=None, memory=None):
    """
    Generate the appropriate batch submission command.
    :param queue: the queue or partition name to submit to.

    """

    if cfg.using_slurm:
        qsub = "sbatch"
        if queue != "":
            qsub += " -p "+queue
        else:
            qsub += " -p RCIF"
        qsub += " -e {} -o {}".format(cfg.logfile_name,cfg.logfile_name)
        if walltime is not None:
            qsub += " -t %s" % walltime
        if memory is not None:
            # convert unit
            number, unit = memory[0:-1], memory[-1]
            if unit == "G":
              number = int(number)*1000 # convert GB to MB
            qsub += " --mem=%s" % number
    elif cfg.using_qsub:
        qsub = "qsub"
        if queue != "":
            qsub = qsub + " -q "+queue
        if walltime is not None:
            # make h_rt slightly longer than s_rt to allow job to react to soft kill
            #qsub += " -l h_rt="+walltime+":10 -l s_rt="+walltime+":00"
            qsub += " -l walltime="+walltime+":10"
        if memory is not None:
            qsub += " -l h_rss=%s" % memory
    elif cfg.using_condor:
        qsub = "condor_submit"

    return qsub


def batch_submit(args):
    """
    Build event generator jobs for a parameter scan and submit shell scripts to batch
    args should be a dictionary

    if "--single" is set, just make one directory with the required files, using the 
    first parameter point in param_file.dat
    """

    # Set the config file
    cfg.config_file = args['CONFIG']

    contur.run.arg_utils.setup_common(args)
    contur.run.arg_utils.setup_batch(args)
    cfg.mceg = args['mceg']
    cfg.write_hepmc_to_tmp = args['write_hepmc_to_tmp']

    # read in the config file.
    cfr.read_config_file(cfg.config_file, configure_theory=False, configure_calculation=False, configure_generator=True)
    
    print("Writing log to {}".format(cfg.logfile_name))
    cfg.contur_log.info("Generated num of events: " + str(args['num_events']))

    valid, beams = contur.run.arg_utils.valid_batch_arguments(args)
    if not valid:
        cfg.contur_log.critical("There is a fatal problem with your setup. See ERROR message(s) above. Aborting run")
        sys.exit(1)

    cfg.contur_log.info("Contur will prepare jobs for these beams:")
    for beam in beams:
        cfg.contur_log.info("- {}".format(beam.id))


    # Make sure scan is not overwriting previous scans
    if os.path.isdir(cfg.output_dir):
        out_dir_basename = cfg.output_dir[:-2]
        counter = 1
        while os.path.isdir(cfg.output_dir):
            cfg.output_dir = out_dir_basename + "%02i" % counter
            counter += 1

    np.random.seed(args['seed'])

    qsub = gen_submit_command(args['queue'], args['walltime'], args['memory'])

    # Param dict has parameter names as keys and then each item is a
    # dictionary with keys 'range' and 'values'
    param_dict, run_dict = contur.scan.os_functions.read_param_steering_file()

    contur.scan.scanning_functions.check_param_consistency(param_dict)

    # Generate parameter values depending on sampling mode
    param_dict, num_points = contur.scan.scanning_functions.generate_points(param_dict)

    # Get exceptions from based on low-movement points
    exclusions = contur.scan.scanning_functions.get_exclusions()

    # Create run point directories
    contur.scan.scanning_functions.run_scan(param_dict, beams, num_points,
                                            args['pipe_hepmc'], args['seed'], args['num_events'], args['SINGLE'],exclusions)

    # Get variable scale for number of events for each point
    if args['variable_precision']:
        scales_str = ConfigObj(cfg.param_steering_file)['NEventScalings']['points']
        scales = [float(i) for i in scales_str.split()]
        num_events_orig = args['num_events']

    for beam in beams:
        beam_directory = os.path.join(cfg.output_dir, beam.id)
        for directory_name in os.listdir(beam_directory):

            # If event numbers are variable, scale by values in param file
            if args['variable_precision']:
                # This will locate correct point index based on directory name
                try:
                    scale = scales[int(directory_name)]
                # This is to handle non-number directory or other file
                except:
                    scale = 1.0
                args['num_events'] = int(num_events_orig * scale)


            directory_path = os.path.abspath(
                os.path.join(beam_directory, directory_name))
            # there can be other (non-directory) files in here too
            if os.path.isdir(directory_path):
                sh, sh_filename, jd, jd_filename \
                    = gen_batch_command(directory_name, directory_path, args, run_dict, runbeam=beam)

                sh_path = os.path.join(directory_path, sh_filename)
                jd_path = os.path.join(directory_path, jd_filename) if jd_filename else None

                # Write files
                with open(sh_path, 'w') as batch_file:
                    batch_file.write(sh)
                if jd_path:
                    with open(jd_path, 'w') as jd_file:
                        jd_file.write(jd)

                if args['scan_only'] is False and args['SINGLE'] is False:
                    print("Submitting: " + sh_path)
                    with contur.scan.os_functions.WorkingDirectory(directory_path):
                        # Changing working directory is necessary here since
                        # qsub reports are outputted to current working directory
                        if cfg.using_condor:
                            # Note: this needs to be submitted using the 'job submit' machine only
                            subprocess.call(["chmod a+x " + sh_path], shell=True)
                            subprocess.call([qsub + " " + jd_path], shell=True)
                        else:
                            subprocess.call([qsub + " " + sh_path], shell=True)
                else:
                    if args['SINGLE']:
                        cfg.contur_log.info("Examples made in: {} ".format(sh_path))
                    else:
                        cfg.contur_log.info("Not Submitting: {} {} ".format(qsub,sh_path))

    # copy param file to output dir
    shutil.copy(cfg.param_steering_file,cfg.output_dir)                    


def get_valid_job_lists(grid_name,num_points):
    """
    find the valid yoda files in a given grid and return the as a List strings,
    with each string contain up to num_points file names of the same beam type.
    """
    import re
    valid_dirs = contur.scan.grid_tools.grid_loop(scan_path=grid_name,clean=False,check=True)
    jlists = []
    counter = 0
    sublist = ""

    known_beams = contur.data.get_beams()
    current_beam = ""
    beam = "Not known"

    for dir in valid_dirs:

        for b in known_beams:
            if b in dir:
                beam = b

        if counter < num_points and beam == current_beam:
            sublist = sublist+" {}".format(dir)
            counter += 1
        else:
            if not sublist == "":
                jlists.append(re.sub(r'\s+', ',',sublist.strip()))
            counter = 1
            current_beam = beam
            sublist = " {}".format(dir)

    if counter > 0:
        jlists.append(re.sub(r'\s+', ',',sublist.strip()))

    return jlists

def set_current_env():
    """ 
    return a script (string) which set the important environment variable from the current setup.

    """
    setup_string  = "export CONTUR_DATA_PATH={}\n".format(os.getenv('CONTUR_DATA_PATH'))
    setup_string += "export CONTUR_USER_DIR={}\n".format(os.getenv('CONTUR_USER_DIR'))
    setup_string += "export RIVET_ANALYSIS_PATH={}\n".format(os.getenv('RIVET_ANALYSIS_PATH'))
    setup_string += "export RIVET_DATA_PATH={}\n".format(os.getenv('RIVET_DATA_PATH'))
    if os.getenv('CONTUR_ROOT') != "":
        setup_string  += "export CONTUR_ROOT={}\n".format(os.getenv('CONTUR_ROOT'))
    setup_string += "source $CONTUR_USER_DIR/analysis-list\n"

    return setup_string

def env_setup(setup_script,directory_path):
    """
    return the command need to setup the generic (ie not generator specific) runtime environment.

    """

    batch_command = "" 

    if cfg.using_qsub:
        batch_command += "#$ -j y # Merge the error and output streams into a single file\n"
        batch_command += "#$ -o {} # Output file path\n".format(os.path.join(directory_path, cfg.logfile_name))

    # Setup the general runtime environment. 
    # If a script is given on the command line, this takes precedence.
    if setup_script is None:

        # If a script is given in the param_file.dat, use this next.
        try:
            for l in setup_commands['generator']:
                batch_command += 'source {};\n'.format(l)
        except:

            # If no script is given in the param_file.dat or on the command line, look for a sensible default.
            # Try the user's contur area.
            setup_script = contur.config.paths.user_path("setupEnv.sh")
            if setup_script is None or not os.path.exists(setup_script):
                if os.getenv("CEDARINSTDIR") is not None: 
                    setup_script = os.path.join(os.getenv("CEDARINSTDIR"), "setupEnv.sh")

    # Set up Contur environment. Use param_file entry if it exists, otherwise use current contur settings.
    try:
        for l in setup_commands['contur']:
            batch_command += "source {}\n".format(l)
    except:
        batch_command += set_current_env()

    # now check we have a setup script and warn user if not.
    if setup_script is None or not os.path.exists(setup_script):
        cfg.contur_log.warning("No setup script found. Tried {}. You may specify a script with --setup ".format(setup_script))
    else:
        batch_command += 'source {};\n'.format(setup_script)

    # Change directory to run point folder
    batch_command += "cd {}\n".format(directory_path)

    return batch_command

def doc_argparser():
    """ wrap the arg parser for the documentation pages """
    from contur.run.arg_utils import get_argparser
    return get_argparser('batch_submit')


