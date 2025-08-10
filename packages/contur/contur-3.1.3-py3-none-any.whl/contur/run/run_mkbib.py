
import contur
from contur.run.arg_utils import setup_common, valid_beam_arg
from contur.util.utils import hack_journal, mkoutdir, get_inspire
import contur.config.config as cfg
import contur.data as cdb
import contur.plot.color_config as color_config
import rivet
import os

def sanitise_pool_description(text):
    text = text.replace("e+", r"$e^+$")
    if not "same-" in text:
        text = text.replace("e-", r" $e^-$")
    text = text.replace("l+", r"$l^+$")
    text = text.replace("l-", r"$l^-$")
    text = text.replace("mu+", r"$\mu^+$")
    text = text.replace("mu-", r"$\mu^-$")
    text = text.replace("(e/mu)", r"($e/\mu$)")
    text = text.replace("e mu plus b", r"$e\mu+b$")
    text = text.replace("ttbar", r"$t\bar{t}$")
    if not "WW" in text:
        text = text.replace("W", r"$W$")
    text = text.replace("WW", r"$W^+W^-$")
    text = text.replace("Z", r"$Z$")
    text = text.replace("$$", "")
    return text

def main(args):
    """
    Main programme to build the bibliography for the web pages.
    args should be a dictionary
    """

    # Set up / respond to the common argument flags and logger config
    setup_common(args) 
    print("Writing log to {}".format(cfg.logfile_name))

    if cfg.offline:
        cfg.contur_log.info("Running in offline mode. Bibliography will not be updated from inspire.")
        return
        
    if args["OUTPUTDIR"] is not None:
        web_dir = args["OUTPUTDIR"]
        mkoutdir(web_dir)
    else:
        web_dir = os.getenv('CONTUR_WEBDIR')
        if web_dir == None:
            web_dir = ""
        else:
            web_dir = os.path.join(web_dir,"Sphinx")

    cfg.contur_log.info("Writing bibliography to {}".format(web_dir))
        
    # get the analyses. Unless --all is set, the default filters will be applied for analysis types.
    if  args["USEALL"]:
        anas = cdb.static_db.get_analyses(filter=False)
    else:
        anas = []
        beams = valid_beam_arg(args)
        for beam in beams:
            anas.extend(cdb.static_db.get_analyses(beam=beam))
            
    found_keys=[]
    found_texs=[]
    summed_info_anas = []
    missing_either=[]
    th_info = []
    pools = {}
        
    cite_file = "contur-bib-cite.tex"
    bib_file = os.path.join(web_dir,"contur-anas.bib")
    missing_file = "contur-bib-missing.txt"
    contur_anas_table_file = "contur_anas_table.tex"
    contur_pools_table_file = "contur_pools_table.tex"

    # =================================================
    # get analysis info
    # =================================================
    for a in anas:
        sm_theory=a.sm()
        cfg.contur_log.info("Updating bibtex info for {}".format(a.name))
        try:
            bibkey = a.bibkey()
            if not bibkey in found_keys:
                found_keys.append(bibkey)
                found_texs.append(a.bibtex())
                summed_info_anas.append((rivet.stripOptions(a.name), bibkey, sm_theory is not None))
            if not a.poolid in pools:
                pools[a.poolid] = []
            pools[a.poolid].append(bibkey)
        except:
            missing_either.append(a.name)

        if sm_theory:
            for sm in sm_theory:
                for inspid in sm.inspids.split(','):
                    try:
                        pub_info=get_inspire(inspid)
                    except cfg.ConturError as e:
                        cfg.contur_log.warning("Could not find bibtex key for inspire ID {} in {}: {}".format(insp_id,ana.name,e))
                    if (pub_info is not None) and not (pub_info['bibtex'] in th_info) and not inspid in a.name:
                        th_info.append((hack_journal(pub_info['bibtex'])))

    # ======================================================================================
    # get pool info
    # ======================================================================================
    pool_dic = {}

    for poolid, ana_keys in pools.items():
        pool = cdb.static_db.get_pool(poolid=poolid)
        split = pool.id.split("_")
        experiment, physics = split[0], "_".join(split[2:])
        physics = physics.replace("HMDY_EL", "HMDY").replace("HMDY_MU", "HMDY") # only a single HMDY pool
        if physics not in pool_dic:
            pool_dic[physics] = {
                "description": sanitise_pool_description(pool.description),
                "experiments" : [],
                "latexName" : color_config.sanitise_poolName(pool.id).replace(experiment+" ", ""),
                "ana_keys" : set(ana_keys)
            }
        experiment = experiment.replace("LHCB", "LHCb")
        if not experiment in pool_dic[physics]["experiments"]:
            pool_dic[physics]["experiments"].append(experiment)
            pool_dic[physics]["experiments"].sort() # sort in alphabetical order
        
    sorted_keys = sorted(pool_dic.keys())

    # ======================================================================================
    # get analysis reference key
    # ======================================================================================
    # retrieve keys from pools_dic so pool table can group keys
    for physics in sorted_keys:
        for key in pool_dic[physics]["ana_keys"]:
            if key not in found_keys:
                found_keys.append(key)

    # ======================================================================================
    # bibliography keys
    # ======================================================================================
    keystr='\cite{'
    for s in set(found_keys):
        keystr+=s+","
    keystr=keystr[:-1]+'}'


    # =================================================
    # bibliography entries
    # =================================================
    texstr=''
    for t in set(found_texs+th_info):
        # replace unicode and problematic characters
        t = t.replace(u"\u2212", r"\ensuremath{-}")
        t = t.replace(r"\text {", r"\text{")
        t = t.replace(r"\text{", r"\textrm{")
        texstr+=t+"\n"

    # =================================================
    # table for analyses
    # =================================================
    contur_anas_table = r"\documentclass{standalone}"+"\n"
    contur_anas_table += r"\usepackage{biblatex} "+"\n"
    contur_anas_table += r"\addbibresource{"+bib_file+"}\n"
    contur_anas_table += r"\begin{document}"+"\n"
    contur_anas_table += "\t"+r"\begin{tabular}{lcc}"+"\n"
    contur_anas_table += "\t\t"+r"Analysis name & Reference & SM prediction available\\"+"\n"
    for entry in summed_info_anas:
        ana_name = entry[0].replace("_", "\_")
        contur_anas_table += f"\t\t{ana_name} & \cite{{{entry[1]}}} & {'yes' if entry[2] else 'no'}\\\\\n"
    contur_anas_table += "\t"+r"\end{tabular}"+"\n"
    contur_anas_table += r"\end{document}"+"\n"

    # =================================================
    # table for pools
    # =================================================
    contur_pools_table = r"\documentclass{standalone}"+"\n"
    contur_pools_table += r"\usepackage[sorting=none,citestyle=numeric-comp]{biblatex} "+"\n" # sorting: sort keys by appearance in document, citestyle: compress [1,2,3] to [1-3]
    contur_pools_table += r"\addbibresource{"+bib_file+"}\n"
    contur_pools_table += r"\begin{document}"+"\n"
    contur_pools_table += "\t"+r"\begin{tabular}{llll}"+"\n"
    contur_pools_table += "\t\t"+r"Pool name & Experiments & Description & References\\"+"\n"
    for physics in sorted_keys:
        pool = pool_dic[physics]
        experiments = ", ".join(pool["experiments"])
        pool_keys = r"\cite{"+",".join(pool["ana_keys"])+r"}"
        contur_pools_table += "\t\t"+f"{pool['latexName']} & {experiments} & {pool['description']} & {pool_keys}\\\\"+"\n"
    contur_pools_table += "\t"+r"\end{tabular}"+"\n"
    contur_pools_table += r"\end{document}"+"\n"

    # =================================================
    # write to files
    # =================================================
    with open(cite_file,"w") as f:
        f.write(keystr)
    with open(bib_file,"w") as f:
        f.write(texstr)
    with open(missing_file, "w") as f:
        f.write(str(missing_either))
    with open(contur_anas_table_file, "w") as f:
        f.write(contur_anas_table)
    with open(contur_pools_table_file, "w") as f:
        f.write(contur_pools_table)

    log_info = "Wrote\n"
    log_info += "* {} for cite command\n".format(cite_file)
    log_info += "* {} for bibtex entries\n".format(bib_file)
    log_info += "* {} for a summary table of the analyses\n".format(contur_anas_table_file)
    log_info += "* {} for a summary table of the pools\n".format(contur_pools_table_file)
    log_info += "* {} for RivetIDs that could not be matched\n".format(missing_file)
    cfg.contur_log.info(log_info)

