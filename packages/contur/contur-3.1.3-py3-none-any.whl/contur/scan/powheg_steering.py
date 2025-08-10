import contur
import os
import contur.config.config as cfg


def gen_pbzpwp_commands(directory_name, run_info, num_events, beam):
    """
    Generate the (shell) commands needed to run the powheg zpwp event generator.

    :param directory_name: name of the directory (without any path) in the which batch job will run (usual 4 integers eg 0123
    :param run_info: the local runinfo directory name
    :param num_events: number of events to generate
    :param beam: the collider beam being run. (should be in contur.data.static_db.known_beams, though this is not currently checked.)


    """

    run_card_name = cfg.mceg_template
    pbzpwp_commands = ('mkdir output.pbzpwp \n')
    pbzpwp_commands += ('cp ../../../pbzp_input_contur.py . \n')
    pbzpwp_commands += ('./pbzp_input_contur.py \n')
    pbzpwp_commands += ('cd output.pbzpwp \n')
    pbzpwp_commands += ('> Timings.txt \n')
    pbzpwp_commands += ('mv ../powheg.input . \n')
    pbzpwp_commands += 'sed -i "s/.*! The number of events*/numevts {} ! The number of events/" powheg.input \n'.format(num_events)
    pbzpwp_commands += 'sed -i "s/.*! The energy of beam one*/ebeam1 {} ! The energy of beam one/" powheg.input \n'.format(beam.energy_a)
    pbzpwp_commands += 'sed -i "s/.*! The energy of beam two*/ebeam2 {} ! The energy of beam two/" powheg.input \n'.format(beam.energy_b)
    pbzpwp_commands += ('cp ../../../../pwhg_main . \n')
    pbzpwp_commands += ('(echo -n pwhg_main start \' \' ; date ) >> Timings.txt \n')
    pbzpwp_commands += ('./pwhg_main > output-pbzpwp.log \n')
    pbzpwp_commands += ('(echo -n pwhf_main end \' \' ; date ) >> Timings.txt \n')
    return pbzpwp_commands


def gen_pbzpwppy8_commands(directory_name, run_info, num_events, beam):
    """
    Generate the (shell) commands needed to run the powheg zpwp event generator with pythia8

    :param directory_name: name of the directory (without any path) in the which batch job will run (usual 4 integers eg 0123
    :param run_info: the local runinfo directory name
    :param num_events: number of events to generate
    :param beam: the collider beam being run. (should be in contur.data.static_db.known_beams, though this is not currently checked.)


    """

    pbzpwppy8_commands = 'mkfifo my_fifo \n'
    pbzpwppy8_commands += 'cp ../../../main-pythia . \n'
    pbzpwppy8_commands += '(echo -n pythia-rivet start \' \' ; date ) >> Timings.txt \n'
    pbzpwppy8_commands += './main-pythia my_fifo output.pbzpwp/pwgevents.lhe {} & \n'.format(num_events)
    if cfg.databg in cfg.stat_types:
        pbzpwppy8_commands += 'rivet -a $CONTUR_RA{}_ALL -o {}.yoda my_fifo \n'.format(beam.id,cfg.tag+"_"+directory_name)
    else:
        pbzpwppy8_commands += 'rivet -a $CONTUR_RA{} -o {}.yoda my_fifo \n'.format(beam.id,cfg.tag+"_"+directory_name)
    pbzpwppy8_commands += '(echo -n pythia-rivet end  \' \' ; date ) >> Timings.txt \n'
    return pbzpwppy8_commands

