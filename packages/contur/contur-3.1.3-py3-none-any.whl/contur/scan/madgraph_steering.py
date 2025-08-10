"""
Madgraph specific scipt and steering generators.

"""
import os
import contur
import contur.config.config as cfg

def madgraph_check_config(template_text):
    
    # null lines only with '\n' in the madgraph command can cause errors
    replace_template_text = ""    
    for line in template_text.split("\n"):
        if line and (not "exit" in line):
            replace_template_text += "{}\n".format(line)

    return replace_template_text

def madgraph_template_beam_config(template_text, pipe_hepmc, beam):

    ## beam dependency (more conditionals for each beam type added)
    if beam.collider == "LHC":
        # TODO: could move these to the Beam class?
        template_text += "set run_card lpp1 1\n"
        template_text += "set run_card lpp2 1\n" 

        template_text += "set run_card ebeam1 {}\n".format(beam.energy_a)
        template_text += "set run_card ebeam2 {}\n".format(beam.energy_b)

    elif beam.collider == "LEP":
        template_text += "set run_card lpp1 0\n"
        template_text += "set run_card lpp2 0\n"

        template_text += "set run_card ebeam1 {}\n".format(beam.energy_a)
        template_text += "set run_card ebeam2 {}\n".format(beam.energy_b)

    if pipe_hepmc:
        template_text += "set HEPMCoutput:file fifo\n"
    else:
        template_text += "set HEPMCoutput:file auto\n"

    return template_text

def madgraph_template_run_config(template_text, seed, num_events):

    replace_template_text = ""
    ## add the lines to start from ./bin/madevent
    ## first two lines necessary to prevent madgraph from using all the cores
    ## next two lines necessary to run the ME and PS steps
    replace_template_text += "set run_mode 0\n"
    replace_template_text += "set nb_core 1\n"
    replace_template_text += "launch\n"
    replace_template_text += "shower=PYTHIA8\n"

    ## remove the lines that were used for initialisation
    dummyrun = False
    for line in template_text.split("\n"):
        if not dummyrun:
            if "output" in line:
                dummyrun = True
        else:
            if not ("launch" in line or "exit" in line):
                replace_template_text += "{}\n".format(line)

    ## number of events and seed settings in the run card
    replace_template_text += "set run_card iseed {}\n".format(seed)
    replace_template_text += "set run_card nevents {}\n".format(num_events)
    replace_template_text += "set run_card run_tag tag_1\n"
    replace_template_text += "set run_card use_syst False\n"

    return replace_template_text

def write_madgraph_initialise_config(run_info, run_card_name):

    ## write the dummy run file (only collect the available feynman diagrams)
    initialise_text = ""

    for line in open(run_card_name).readlines():
        if "output" in line: # need to 'exit' after the directory is created otherwise it will run everything up to PS
            initialise_text += "output mgevents\n"
            initialise_text += "exit\n"
            break
        else: # ignore the other lines (not needed when collecting feynman diagrams)
            initialise_text += "{}\n".format(line)

    with open("{}/initialise_{}".format(run_info, run_card_name), 'w') as f:
        f.write(initialise_text)

def gen_madgraph_commands(directory_path, run_info, pipe_hepmc, seed, num_events, beam):
    """
    Generate the (shell) commands needed to run the madgraph event generator.

    :param directory_path: name of the directory path
    :param run_info: the local runinfo directory name
    :param pipe_hepmc: if True pipe the hepmc events to rivet.
    :param seed: random number seed for Herwig
    :param num_events: number of events to generate
    :param beam: the collider beam being run. (should be in contur.data.static_db.known_beams, though this is not currently checked.)


    """
    directory_name = directory_path.split("/")[-1]

    run_card_name = cfg.mceg_template
    madgraph_commands = ""

    output_directory = "mgevents/Events/run_01/"
    cards_directory = "mgevents/Cards/"

    write_madgraph_initialise_config(run_info, run_card_name)

    initialise_script = "{}/initialise_{}".format(run_info, run_card_name)

    if cfg.write_hepmc_to_tmp:
        madgraph_commands += 'export TMP_RUN_DIR="/tmp/${{USER}}{}"\n'.format(directory_path)
        madgraph_commands += 'mkdir -p "$TMP_RUN_DIR"\n'
        madgraph_commands += 'cp {} "$TMP_RUN_DIR"/\n'.format(run_card_name)
        madgraph_commands += 'cd "$TMP_RUN_DIR"\n'
        # mgevents will be written to TMP_RUN_DIR

    # run the initialise script
    madgraph_commands += '$MG_EXEC {}\n'.format(initialise_script)

    ## check if the card exists in the run_info, and replace it if exists
    replace_card_candidates = ["run", "madspin", "pythia8"]
    for replace_card in replace_card_candidates:
        if os.path.exists('{}/{}_card.dat'.format(run_info, replace_card)):
            madgraph_commands += 'cp {}/{}_card.dat {}\n'.format(run_info, replace_card, cards_directory)
            if replace_card == "madspin":
                output_directory = output_directory.replace("run_01", "run_01_decayed_1")

    madgraph_commands += 'cd mgevents\n'
    # Run madevent with the template
    madgraph_commands += 'if [ -e ./bin/madevent ]\n'
    madgraph_commands += 'then\n'
    madgraph_commands += '    ./bin/madevent ../{}\n'.format(run_card_name)
    madgraph_commands += 'else\n'
    madgraph_commands += '    ./bin/aMCatNLO ../{}\n'.format(run_card_name)
    madgraph_commands += 'fi\n'
    madgraph_commands += 'cd -\n'

    filestem = cfg.mceg + '-S' + str(seed) + "-" + cfg.tag + "_" + directory_name

    if pipe_hepmc:
        hepmc_file_name = os.path.join(output_directory, "PY8.hepmc.fifo")
        madgraph_commands += 'while [[ ! -p {} ]]; do sleep 1; done # wait for creation of fifo\n'.format(hepmc_file_name)
    
    else:
        '''
        This is a bit hardcoded but checking if '*.hepmc.gz' exists with wildcard in directory
        seems to be a bit long. Hence force all the outputs to have the same name.
        Default names are
        NLO : events_PYTHIA8_0.hepmc.gz
        LO : tag_1_pythia8_events.hepmc.gz (but also can be tag_1_pythia8_events.hepmc... ignore this for now)
        '''
        hepmc_file_name = filestem + ".hepmc.gz"
        pythia_log_name = "tag_1_pythia8.log"

        madgraph_commands += 'mv {} {}\n'.format(os.path.join(output_directory, '*.hepmc.gz'), hepmc_file_name)
        madgraph_commands += 'mv {} {}\n'.format(os.path.join(output_directory, pythia_log_name), pythia_log_name)

    if cfg.databg in cfg.stat_types:
        madgraph_commands += 'rivet --skip-weights -a $CONTUR_RA{}_ALL -n {} -o {}.yoda {}\n'.format(
            beam.id, num_events, filestem, hepmc_file_name)
    else:
        madgraph_commands += 'rivet --skip-weights -a $CONTUR_RA{} -n {} -o {}.yoda {}\n'.format(
            beam.id, num_events, filestem, hepmc_file_name)
        
    if cfg.write_hepmc_to_tmp:
        madgraph_commands += 'mv {}.yoda {}/\n'.format(filestem, directory_path)
        madgraph_commands += 'mv {} {}/\n'.format(pythia_log_name, directory_path)
        madgraph_commands += 'cd {}\n'.format(directory_path)
        madgraph_commands += 'rm -rf "$TMP_RUN_DIR"\n'

    elif (not cfg.keep_hepmc) or pipe_hepmc:
        madgraph_commands += 'rm {}\n'.format(hepmc_file_name)

    if not cfg.write_hepmc_to_tmp:
        madgraph_commands += 'rm -r mgevents\n'

    return madgraph_commands

