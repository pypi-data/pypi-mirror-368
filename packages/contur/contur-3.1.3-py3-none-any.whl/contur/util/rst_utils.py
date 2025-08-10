import os, glob
import contur.config.config as cfg
import contur.data as cdb
import contur.util.utils as cutil


"""
Functions for writing put rst files for Sphinx (webpages)

"""

def write_sm_file(ana,out_dir,text_string):
    """
    Write an rst file for the web page describing the theory predictions available for this analysis.

    :param ana:  the analysis object
    :param out_dir: name of the top level directory to write to
    :param text_string: an rst-style link to the generated file, with text, will be appended to this and returned.

    returns text_string with an rst-style link to the new file appended.

    """    
    import contur.factories.yoda_factories as yf

    th_desc = ana.sm()
    ana_file_stem = ana.name
    
    # name of the output directory and rst file
    ana_file_dir = os.path.join(out_dir,"SM",ana.poolid,ana_file_stem)
    ana_file_out = ana_file_dir+".rst"

    # python scripts for make the graphics should be here
    py_script_dir = cfg.paths.user_path(cfg.smdir,ana.poolid,ana.name)
    
    #graphics_root = os.path.join(out_dir,"SM")

    if th_desc:
        text_string += " SM theory predictions are available :doc:`here <SM/{}/{}>`.\n".format(ana.poolid,ana_file_stem)

        # this string is the contents on the RST file for this analysis.
        th_str = ":orphan:\n\nStandard Model Predictions for {}\n{}\n\n".format(ana_file_stem,"="*(31+len(ana_file_stem)))

        cutil.mkoutdir(ana_file_dir)

        # counter to make sure we don't plot the same prediction twice.
        done_ids = []
        for prediction in th_desc:

            if prediction.id in done_ids:
                continue

            done_ids.append(prediction.id)
            
            pvfile = "{}.txt".format(prediction.id)
            try:
                with open(os.path.join(py_script_dir,pvfile)) as f:
                    pvalue = float(f.read())
            except Exception as e:
                print("Problem obtaining p value for {}, prediction {}.".format(ana.name,prediction.id))
                print(e)
                pvalue = None
                
            yf.load_sm_aos(prediction)
            cfg.contur_log.debug("Getting info for theory prediction {} for {}".format(prediction.short_description,ana.shortname))
            insp_ids = prediction.inspids.split(',')
            bibkeys = ""
            for insp_id in insp_ids:
                try:
                    paper_data = cutil.get_inspire(insp_id) 
                    bibkeys+= paper_data['bibkey']
                    bibkeys+=','
                except cfg.ConturError as e:
                    cfg.contur_log.warning("Could not find bibtex key for inspire ID {} in {}: {}".format(insp_id,ana.name,e))
                except url_error:
                    cfg.contur_log.error("Failed to read from server: {}".format(server_error))

            if len(bibkeys)>0 and (not "Failed" in bibkeys[:-1]):
                th_str += "\n {} :cite:`{}`: {}\n".format(prediction.short_description,bibkeys[:-1],prediction.long_description)
            else:
                th_str += "\n {} (Could not find bibtex key) {}\n".format(prediction.short_description,prediction.long_description)

            if pvalue is not None:
                th_str += " Combined p-value for this prediction is {:.2E}.\n".format(pvalue)
                
            plots_file_name = "{}/{}_{}.rst".format(ana_file_dir,ana_file_stem,prediction.id)

            th_str += "\n\n   :doc:`{} prediction {} <{}/{}_{}>`.\n".format(ana.name,prediction.id,ana.name,ana.name,prediction.id)

            plots_str = ":orphan:\n\nStandard Model Predictions for {}\n{}\n\n".format(ana_file_stem,"="*(31+len(ana_file_stem)))

            plots_str += "{} (Prediction ID {})\n\n".format(prediction.long_description,prediction.id)
            plots_str += "\n\nStored in file: {} \n\n".format(prediction.file_name)

            # now make the figures
            for ao in prediction.ao.values():
                
                plots_str += "{}: {}\n".format(ao.title(),ao.name())
                
                plots_str += "\n.. figure:: {}_{}.png\n           :scale: 80%\n\n".format(ao.name(),prediction.id)
                
                cutil.mkoutdir(ana_file_dir)
                plots_file = open(plots_file_name, 'w')
                plots_file.write(plots_str)

        # find Python scripts for SM histogram plotting
        cfg.contur_log.info("Looking for executable Python scripts in {}".format(py_script_dir))
        pyScripts = []
        got_pys=False
        for pyscript in glob.glob(os.path.join(py_script_dir,"*.py")):
            if pyscript.endswith('__data.py'): continue
            pyScripts.append([pyscript, ana_file_dir])
            got_pys=True
        if got_pys:
            ana_file = open(ana_file_out, 'w')
            ana_file.write(th_str)
        else:   
            cfg.contur_log.warning("No py scripts found for {}".format(py_script_dir))
            
    else:
        text_string += ":red:`No SM theory predictions available for this analysis.` \n"
        pyScripts = []

    return text_string, pyScripts


def write_measurement_list():
    """
    Write out the list of measurements used by Contur, with SM predictions where available,
    as rst files for Sphinx.
    """

    pyScripts = []
    
    # make the directory if it doesn't already exist
    output_directory = cfg.output_dir
    cutil.mkoutdir(output_directory)
 
    web_dir = os.getenv('CONTUR_WEBDIR')
    if web_dir == None:
        web_dir = output_directory
    else:
        web_dir = os.path.join(web_dir,"Sphinx","datasets")

    cfg.contur_log.info("Writing graphics output to {}".format(web_dir))

        
    # style stuff
    style_stuff = ".. raw:: html \n \n <style> .red {color:red} </style> \n \n.. role:: red\n\n"

    # open file for the web page list
    data_list_file = open(os.path.join(web_dir,"data-list.rst"), 'w')
    data_list = "Current Data \n------------ \n"

    bvetoissue = "\nb-jet veto issue\n---------------- \n\n *The following measurements apply a detector-level b-jet veto which is not part of the particle-level fiducial definition and therefore not applied in Rivet. Also applies to CMS Higgs-to-WW analysis. Off by default, can be turned on via command-line, but use with care.* \n"

    higgsww = "\nHiggs to WW\n----------- \n\n *Typically involve large data-driven top background subtraction. If your model contributes to the background as well the results maybe unreliable. Off by default, can be turned on via command-line.* \n"

    higgsgg = "\nHiggs to diphotons\n------------------ \n\n *Higgs to two photons use a data-driven background subtraction. If your model predicts non-resonant photon production this may lead to unreliable results. On by default, can be turned off via command-line.* \n"

    ratios = "\nRatio measurements\n------------------ \n\n *These typically use SM theory for the denominator, and may give unreliable results if your model contributes to both numerator and denominator. On by default, can be turned off via command-line.* \n"

    searches = "\nSearches\n-------- \n\n *Detector-level, using Rivet smearing functions. Off by default, can be turned on via command-line.*\n"

    nutrue = "\nNeutrino Truth\n-------------- \n\n *Uses neutrino flavour truth info, may be misleading for BSM. Off by default, can be turned on via command-line.*\n"

    for ana in sorted(cdb.static_db.get_analyses(filter=False), key=lambda ana: ana.poolid):

        pool = ana.get_pool()
        pool_str = "\n Pool: **{}**  *{}* \n\n".format(pool.id,pool.description)
        
        tmp_str = "   * `{} <https://rivet.hepforge.org/analyses/{}.html>`_, ".format(ana.name,ana.shortname)
        tmp_str += "{} :cite:`{}`. ".format(ana.summary(),ana.bibkey())

        tmp_str, scripts = write_sm_file(ana,web_dir,tmp_str)
        pyScripts = pyScripts + scripts

        if cdb.static_db.hasRatio(ana.name):
            if pool.id in ratios:
                ratios += tmp_str
            else:
                ratios += pool_str + tmp_str

        elif cdb.static_db.hasSearches(ana.name):
            if pool.id in searches:
                searches += tmp_str
            else:
                searches += pool_str + tmp_str

        elif cdb.static_db.hasHiggsgg(ana.name):
            if pool.id in higgsgg:
                higgsgg += tmp_str
            else:
                higgsgg += pool_str + tmp_str

        elif cdb.static_db.hasHiggsWW(ana.name):
            if pool.id in higgsww:
                higgsww += tmp_str
            else:
                higgsww += pool_str + tmp_str

        elif cdb.static_db.hasNuTrue(ana.name):
            if pool.id in nutrue:
                nutrue += tmp_str
            else:
                nutrue += pool_str + tmp_str

        else:
            if pool.id in data_list:
                data_list += tmp_str
            else:
                data_list += pool_str + tmp_str

        if cdb.static_db.hasBVeto(ana.name):
            if pool.id in bvetoissue:
                bvetoissue += tmp_str
            else:
                bvetoissue += pool_str + tmp_str


    data_list_file.write(style_stuff)
    data_list_file.write(data_list)
    data_list_file.write(ratios)
    data_list_file.write(higgsgg)
    data_list_file.write(searches)
    data_list_file.write(nutrue)
    data_list_file.write(higgsww)
    data_list_file.write(bvetoissue)

    print("Generating SM histogram plots for all analyses.")

    from contur.run.arg_utils import get_args
    from multiprocessing import cpu_count
    
    try:
        numcores = cpu_count()
    except:
        numcores = 1
 
    cutil.make_mpl_plots(pyScripts,numcores)
    cfg.contur_log.info("Data list written to {}".format(web_dir))

    return
