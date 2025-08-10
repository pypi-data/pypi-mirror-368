import os
import contur
import contur.config.config as cfg

def gen_pythia8_commands(directory_name, run_info, num_events, beam):
    """
    Generate the (shell) commands needed to run the pythia 8 standalone event generator.

    :param directory_name: name of the directory (without any path) in the which batch job will run (usual 4 integers eg 0123
    :param run_info: the local runinfo directory name 
    :param num_events: number of events to generate
    :param beam: the collider beam being run. (should be in contur.data.static_db.known_beams, though this is not currently checked.)
    :param main_program: Specify whether to use the main93 or main89 program for pythia8. Number of events for main89 presently have to be specified within your command file.

    """
    run_card_name = cfg.mceg_template
    pythia8_commands = ""
    
    if cfg.main_program == "main93":	
	
        pythia8_commands += ('pythia8-main93 -c {} -o  LHC-{}_{} -n {}\n').format(run_card_name,cfg.tag,directory_name,num_events)

    elif cfg.main_program == "main89":
    	
    	pythia8_main89_commands += ('pythia8-main89R {} \n').format(run_card_name)
    	pythia8_main89_commands += ('mv Rivet.yoda LHC-{}{}').format(cfg.tag,directory_name)

    return pythia8_commands




