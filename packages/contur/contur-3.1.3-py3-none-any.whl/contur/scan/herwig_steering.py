"""
Herwig specific scipt and steering generators.

"""
import os
import contur
import contur.config.config as cfg


def herwig_template_beam_config(template_text, pipe_hepmc, beam):
    """
    configure herwig input file text for each beam type

    :param template_text: the template file text formatted with its parameters
    :param pipe_hepmc: run the hepmc events from the generator through a unix pipe to rivet
    :type pipe_hepmc: bool
    :param beam: collider beam being generated
    """

    sm_particles = ['u', 'ubar', 'd', 'dbar', 'c', 'cbar', 's', 'sbar', 'b', 'bbar', 't', 'tbar', 'g',
                    'e+', 'e-', 'mu+','mu-', 'tau+','tau-', 'nu_e','nu_ebar','nu_mu','nu_mubar','nu_tau','nu_taubar',
                    'W+','W-','Z0','gamma','h0']
    if cfg.herwig_hp != "Exclusive":
        template_text += "## all SM particles are possible outgoing from resonance\n"
        for sm_particle in sm_particles:
            template_text += "insert ResConstructor:Outgoing 0 /Herwig/Particles/{}\n".format(sm_particle)
        template_text += "\n"
    
    template_text += "## generic parameters (valid for all beams)\n"
    template_text += "cd /Herwig/Generators\n"
    template_text += "set EventGenerator:NumberOfEvents 10000000\n"
    template_text += "set EventGenerator:RandomNumberGenerator:Seed 31122001\n"
    template_text += "set EventGenerator:DebugLevel 0\n"
    template_text += "set EventGenerator:EventHandler:StatLevel Full\n"
    template_text += "set EventGenerator:PrintEvent 100\n"
    template_text += "set EventGenerator:MaxErrors 10000\n\n"
    template_text += "\n"
    
    ## beam dependency (more conditionals for each beam type added)
    if beam.collider == "LHC":
        # TODO: could move these to the Beam class?
        beam_partons = ['u', 'ubar', 'd', 'dbar', 'c', 'cbar', 's', 'sbar', 'b', 'bbar', 'g']
        template_text += "## proton collider setup\n"
        template_text += "read snippets/PPCollider.in \n"
        template_text += "set /Herwig/Shower/ShowerHandler:IntrinsicPtGaussian 2.2*GeV \n"
        ## add the beam energy (note that for HERA this will need to be set beam-by-beam)
        template_text += "set  /Herwig/Generators/EventGenerator:EventHandler:LuminosityFunction:Energy {}\n".format(beam.root_s)

    elif beam.collider == "LEP":
        beam_partons = ['e+','e-']
        template_text += "## e+e- collider setup\n"
        template_text += "read snippets/EECollider.in \n"
        ## add the beam energy (note that for HERA this will need to be set beam-by-beam)
        template_text += "set /Herwig/Generators/EventGenerator:EventHandler:LuminosityFunction:Energy {}\n".format(beam.root_s)

    template_text += "cd /Herwig/NewPhysics\n"
    template_text += "set HPConstructor:Processes {}\n".format(cfg.herwig_hp)

    ## add the beam partons
    for beam_parton in beam_partons:
        template_text += "insert HPConstructor:Incoming 0 /Herwig/Particles/{}\n".format(beam_parton)
        if cfg.herwig_hp != "Exclusive":
            template_text += "insert ResConstructor:Incoming 0 /Herwig/Particles/{}\n".format(beam_parton)
    
    template_text += "\n"
    template_text += "cd /Herwig/Generators \n"
    
    if pipe_hepmc:
        template_text += "## rivet via HepMC pipe\n"
        template_text += "read snippets/HepMC.in \n"
        template_text += "set /Herwig/Analysis/HepMC:PrintEvent 10000000 \n"
    else:
        template_text += "## rivet via interface\n"
        template_text += "create ThePEG::RivetAnalysis Rivet RivetAnalysis.so \n"
        template_text += "insert EventGenerator:AnalysisHandlers 0 Rivet \n"
        template_text += "read {}.ana \n".format(beam.id)
    
    template_text += "saverun {} EventGenerator \n".format(cfg.mceg)
    
    return template_text


def gen_herwig_commands(directory_name, run_info, pipe_hepmc, seed, num_events, runbeam):
    """
    Generate the (shell) commands needed to run the herwig event generator.

    :param directory_name: name of the directory (without any path) in the which batch job will run (usual 4 integers eg 0123
    :param run_info: the local runinfo directory name
    :param pipe_hepmc: if True pipe the hepmc events to rivet. Otherwise use the native Herwig interface.
    :param seed: random number seed for Herwig
    :param num_events: number of events to generate
    :param runbeam: the collider beam being run. (should be in contur.data.static_db.known_beams, though this is not currently checked.)


    """

    herwig_commands = 'Herwig read {} -I {} -L {};\n'.format(cfg.mceg_template, run_info, run_info)

    if pipe_hepmc:
        filestem = cfg.mceg + '-S' + str(seed) + "-" + cfg.tag + "_" + directory_name
        herwig_commands += ('mkfifo '+filestem+'.hepmc; \n')
        
    herwig_commands += 'Herwig run {}.run --seed={}  --tag={}_{}  --numevents={} '.format(cfg.mceg,seed,cfg.tag,directory_name,num_events)

    if pipe_hepmc:
        if cfg.databg in cfg.stat_types:
            herwig_commands += '&\nrivet -a $CONTUR_RA{}_ALL -n {} -o {}.yoda {}.hepmc \n'.format(runbeam.id,num_events,filestem,filestem)
        else:
            herwig_commands += '&\nrivet -a $CONTUR_RA{} -n {} -o {}.yoda {}.hepmc \n'.format(runbeam.id,num_events,filestem,filestem)
    else:
        herwig_commands += ';\n'

    return herwig_commands

