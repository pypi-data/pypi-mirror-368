
# functions build theory reference yodas from various raw inputs.

import contur
import re      
import sys
import os
import rivet
import yoda
from contur.data.sm_theory_builders import *
import contur.config.config as cfg
import contur.data.static_db as cdb
import contur.util.utils as cutil
from contur.run.arg_utils import setup_common
from contur.factories.yoda_factories import mkConturFriendlyScatter


def make_sm_yoda(analysis):
    '''
    Make the SM yoda file for analysis

    This is a pretty clunky and bespoke set of scripts because it has to handle data from a very varied set of sources.
    From these sources it produces standard SM prediction files to be stored in data/Theory

    If source == "REF", will look for additonal y axes on the REF plots (labelled y02 by default, others from axis parameter)
                        and replace them to convert into y01 /THY versions.
                        Filters out analysis objects which are not assigned to an analysis pool.

    if source == "RAW" will look in the TheoryRaw areas for /THY/ yodas and just filter them.

    if source == "HEPDATA" will look in the TheoryRaw area for a (possibly modified) HEPDATA download where the y-axis name
                                  should be replace y-axis of the REF histogram name

    if source == "HEPDATA_APPEND" will look in the TheoryRaw area for a (possibly modified) HEPDATA download where the y-axis name
                                  should be appended to the REF histogram name

    if source == "SPECIAL" invoke a special routine for this analysis (usually reading from
                           text files supplied by theorists).

    the above will only be applied to histograms with a regexp match to the pattern.

    '''

    ao_out = []
    a_name = analysis.shortname
    if analysis.sm() is None:
        return


    output_aos = {}

    # counter to make sure we only take the first prediction
    got_pred = {}

    for prediction in analysis.sm():

        # only take the first prediction with this ID
        if not prediction.id in got_pred.keys():
            got_pred[prediction.id] = []

        # only read each prediction file once
        if prediction.file_name not in output_aos:
            output_aos[prediction.file_name] = []

        if prediction.origin == "RAW":

            cfg.contur_log.info("Making SM theory for {}, prediction {}".format(analysis.name,prediction.id))
            f = os.path.join(os.getenv("CONTUR_ROOT"),"data","TheoryRaw",a_name,a_name)
            if prediction.axis is not None:
                f = f+"-Theory"+prediction.axis+".yoda"
            else:
                f = f+"-Theory.yoda"
            if  os.path.isfile(f):
                cfg.contur_log.debug("Reading from {}".format(f))
                aos = yoda.read(f)
                for path, ao in aos.items():

                    if path in got_pred[prediction.id]:
                        continue

                    if rivet.isTheoryPath(path) and analysis.name in path:
                        pool = cdb.get_pool(path=path)
                        if pool is not None:
                            ao = mkConturFriendlyScatter(ao,mkthy=True)
                            ao.setTitle(prediction.short_description)
                            output_aos[prediction.file_name].append(ao)
                        else:
                            cfg.contur_log.debug("No pool for {}".format(path))

            else:
                cfg.contur_log.critical("File {} does not exist.".format(f))

        elif prediction.origin == "REF":
            # from the installed ref data 
            cfg.contur_log.info("Making SM theory for {}, prediction {}".format(analysis.name,prediction.id))

            f = contur.util.utils.find_ref_file(analysis)
            aos = yoda.read(f)

            for short_path, ao in aos.items():
                opt_path = "/"+analysis.name+"/"+ao.name()
                if opt_path in got_pred[prediction.id]:
                    continue
                pool = cdb.get_pool(path=opt_path)
                if pool is not None:
                    
#                    print(prediction.pattern, opt_path)
                    if re.search(prediction.pattern, opt_path) and cdb.validHisto(opt_path,filter=False):
                        cfg.contur_log.debug("Found a prediction for {}. Axis is {}.".format(opt_path,prediction.axis))
                        # get the appropriate theory axis for this plot 

                        if re.search("y[0-9]{2}",prediction.axis):
                            # if it's of the form yNN, remove the old one before adding the new one
                            thypath = short_path[:-len(prediction.axis)]+prediction.axis
                        else:
                            # otherwise just append it.
                            thypath = short_path+prediction.axis
                        try:
                            thy_ao = aos[thypath]
                            cfg.contur_log.debug("FOUND! {}".format(thypath))

                        except:
                            cfg.contur_log.debug("not found {}".format(thypath))
                            continue
                        
                        got_pred[prediction.id].append(opt_path)
                        thy_ao = mkConturFriendlyScatter(thy_ao,mkthy=True)
                        thy_ao.setPath("/THY"+opt_path)
                        thy_ao.setTitle(prediction.short_description)
                        output_aos[prediction.file_name].append(thy_ao)


                        
        elif prediction.origin.startswith("HEPDATA"):

            # from specially downloaded HEPData
            cfg.contur_log.info("Making SM theory for {}, prediction {}".format(analysis.name,prediction.id))
            f = os.path.join(os.getenv("CONTUR_ROOT"),"data","TheoryRaw",a_name,a_name)
            f = f+".yoda.gz"

            aos = yoda.read(f)
            cfg.contur_log.debug("Reading from {}".format(f))
            for path, ao in aos.items():
                if path in got_pred[prediction.id]:
                    continue
                pool = cdb.get_pool(path=path)
                cfg.contur_log.debug("Pool is {} for {}".format(pool.id,path))
                if pool is not None:
                    if re.search(prediction.pattern, path) and cdb.validHisto(path,filter=False):
                        cfg.contur_log.debug("Getting a prediction for {}. Axis is {}.".format(path,prediction.axis))
                        if prediction.origin.endswith("APPEND"):
                            thypath = path+prediction.axis
                        else:
                            thypath = path[:-len(prediction.axis)]+prediction.axis
                        try:
                            thy_ao = aos[thypath]
                            cfg.contur_log.debug("Found a prediction for {} at {}.".format(path,thypath))
                        except:
                            cfg.contur_log.debug("not found")
                            continue

                        thy_ao = mkConturFriendlyScatter(thy_ao,mkthy=True)
                        thy_ao.setPath("/THY"+path[4:])
                        thy_ao.setTitle(prediction.short_description)
                        output_aos[prediction.file_name].append(thy_ao)

        elif prediction.origin == "SPECIAL":

            histo_lists= {}
            # Z + Jets run 2 CMS
            histo_lists['CMS_2018_I1667854:LMODE=EMU'] = ['d01-x01-y01','d02-x01-y01','d03-x01-y01','d04-x01-y01','d05-x01-y01','d06-x01-y01',
                                                          'd07-x01-y01','d08-x01-y01','d09-x01-y01','d10-x01-y01','d11-x01-y01','d12-x01-y01',
                                                          'd13-x01-y01','d14-x01-y01','d15-x01-y01','d16-x01-y01','d17-x01-y01','d18-x01-y01']
            #    Z + high transverse momentum jets at ATLAS

            histo_lists['CMS_2018_I1711625'] = ['d05-x01-y01','d06-x01-y01']

            histo_lists['ATLAS_2022_I2077570'] = ['d01-x01-y01','d02-x01-y01','d03-x01-y01','d04-x01-y01','d05-x01-y01','d06-x01-y01']
            histo_lists['CMS_2021_I1866118'] = ['d01-x01-y01','d02-x01-y01','d03-x01-y01','d04-x01-y01','d05-x01-y01']
            histo_lists['CMS_2019_I1753680:LMODE=EMU'] = ['d26-x01-y01','d27-x01-y01','d28-x01-y01','d26-x01-y02','d27-x01-y02','d28-x01-y02']
            histo_lists['CMS_2020_I1794169'] = ['d09-x01-y01','d11-x01-y01','d13-x01-y01','d15-x01-y01']
            #  Measurement of four-jet differential cross sections in √s = 8 TeV proton–proton collisions using the ATLAS detector
            histo_lists['ATLAS_2015_I1394679'] = ['d01-x01-y01','d02-x01-y01','d03-x01-y01','d04-x01-y01','d05-x01-y01','d06-x01-y01',
                                                  'd07-x01-y01','d08-x01-y01','d09-x01-y01','d10-x01-y01','d11-x01-y01','d12-x01-y01',
                                                  'd13-x01-y01','d14-x01-y01','d15-x01-y01','d16-x01-y01','d17-x01-y01','d18-x01-y01',
                                                  'd19-x01-y01','d20-x01-y01','d21-x01-y01','d22-x01-y01','d23-x01-y01','d24-x01-y01',
                                                  'd25-x01-y01','d26-x01-y01']
            # Measurement of the Zγ → ννγ¯ production cross section in pp collisions at √s = 13 TeV NB d06 not used, not enough bins.
            histo_lists['ATLAS_2018_I1698006:LVETO=ON'] = ['d02-x01-y01','d03-x01-y01','d04-x01-y01','d05-x01-y01']
            # WZ and same-sign WW boson pairs in association with two jets in proton-proton collisions at √s= 13 TeV
            histo_lists['ATLAS_2018_I1635273:LMODE=EL'] = ['d01-x01-y01','d06-x01-y01','d11-x01-y01','d16-x01-y01','d21-x01-y01',
                                                           'd26-x01-y01','d28-x01-y01','d30-x01-y01','d32-x01-y01']
            histo_lists['ATLAS_2016_I1448301:LMODE=LL'] = ['d05-x01-y01','d06-x01-y01','d09-x01-y01','d10-x01-y01']
            # Z + high transverse momentum jets at ATLAS
            histo_lists['ATLAS_2019_I1744201'] = ['d02-x01-y01','d03-x01-y01','d04-x01-y01','d05-x01-y01','d06-x01-y01','d07-x01-y01']
            # WW production at 13 TeV
            histo_lists['ATLAS_2019_I1734263'] = ['d04-x01-y01','d07-x01-y01','d10-x01-y01','d13-x01-y01','d16-x01-y01','d19-x01-y01']
            # Triphoton 8 TeV
            histo_lists['ATLAS_2017_I1644367'] = ['d01-x01-y01','d01-x01-y02','d02-x01-y01','d02-x01-y02','d03-x01-y01','d03-x01-y02',
                                                  'd04-x01-y01','d04-x01-y02','d05-x01-y01','d05-x01-y02','d06-x01-y01','d06-x01-y02',
                                                  'd07-x01-y01','d07-x01-y02','d08-x01-y01','d08-x01-y02','d09-x01-y01','d09-x01-y02',
                                                  'd10-x01-y01','d10-x01-y02','d11-x01-y01','d11-x01-y02','d12-x01-y01','d12-x01-y02',
                                                  'd13-x01-y01','d13-x01-y02']
            # Z & W bosons produced in proton-proton collisions at 8 TeV
            histo_lists['CMS_2016_I1471281:VMODE=W'] = ['d01-x01-y01','d02-x01-y01']
            histo_lists['CMS_2016_I1471281:VMODE=Z'] = ['d03-x01-y01']

            # ttbb produced in proton-proton collisions with additional heavy-flavour jets at 13 TeV
            histo_lists['ATLAS_2018_I1705857'] = ['d01-x02-y01','d04-x01-y01','d06-x01-y01','d08-x01-y01','d10-x01-y01','d12-x01-y01',
                                                  'd14-x01-y01','d16-x01-y01','d18-x01-y01','d20-x01-y01','d22-x01-y01','d24-x01-y01',
                                                  'd26-x01-y01','d28-x01-y01','d30-x01-y01','d32-x01-y01','d34-x01-y01','d36-x01-y01',
                                                  'd38-x01-y01','d40-x01-y01','d42-x01-y01','d44-x01-y01','d46-x01-y01','d48-x01-y01',
                                                  'd50-x01-y01']
            
            # H to diphoton
            histo_lists['ATLAS_2022_I2023464'] = ['d02-x01-y01','d03-x01-y01','d04-x01-y01','d05-x01-y01','d06-x01-y01','d07-x01-y01',
                                                  'd08-x01-y01','d09-x01-y01','d10-x01-y01','d21-x01-y01','d23-x01-y01','d25-x01-y01',
                                                  'd27-x01-y01','d29-x01-y01','d31-x01-y01','d33-x01-y01','d35-x01-y01','d37-x01-y01',
                                                  'd39-x01-y01','d41-x01-y01','d43-x01-y01','d45-x01-y01','d47-x01-y01','d49-x01-y01',
                                                  'd51-x01-y01','d53-x01-y01', 'd57-x01-y01', 'd59-x01-y01']
            histo_lists['ATLAS_2018_I1707015:LMODE=SINGLE'] = ['d03-x01-y01','d04-x01-y01','d05-x01-y01']
            histo_lists['ATLAS_2018_I1707015:LMODE=DILEPTON']=['d06-x01-y01','d07-x01-y01','d08-x01-y01','d09-x01-y01','d10-x01-y01']

            # ttbar to hadrons
            histo_lists['ATLAS_2022_I2077575'] = ['d02-x01-y01','d75-x01-y01','d76-x01-y01','d77-x01-y01','d78-x01-y01','d79-x01-y01',
                                                  'd80-x01-y01','d81-x01-y01','d82-x01-y01','d83-x01-y01','d84-x01-y01','d85-x01-y01',
                                                  'd86-x01-y01','d87-x01-y01','d88-x01-y01','d89-x01-y01','d90-x01-y01','d91-x01-y01',
                                                  'd92-x01-y01','d93-x01-y01','d94-x01-y01','d95-x01-y01','d96-x01-y01','d97-x01-y01',
                                                  'd98-x01-y01','d99-x01-y01','d100-x01-y01','d101-x01-y01','d102-x01-y01','d103-x01-y01',
                                                  'd104-x01-y01','d105-x01-y01','d106-x01-y01','d107-x01-y01','d108-x01-y01','d109-x01-y01',
                                                  'd110-x01-y01','d111-x01-y01','d112-x01-y01','d113-x01-y01','d114-x01-y01','d115-x01-y01',
                                                  'd116-x01-y01','d117-x01-y01','d118-x01-y01','d119-x01-y01','d120-x01-y01','d121-x01-y01',
                                                  'd122-x01-y01','d123-x01-y01','d124-x01-y01','d125-x01-y01','d126-x01-y01','d127-x01-y01',
                                                  'd128-x01-y01','d129-x01-y01','d130-x01-y01','d131-x01-y01','d132-x01-y01','d133-x01-y01',
                                                  'd134-x01-y01','d135-x01-y01','d136-x01-y01','d137-x01-y01','d138-x01-y01','d139-x01-y01',
                                                  'd140-x01-y01','d141-x01-y01','d142-x01-y01','d143-x01-y01','d144-x01-y01','d145-x01-y01',
                                                  'd146-x01-y01']
            histo_lists['ATLAS_2020_I1801434'] = ['d04-x01-y01','d08-x01-y01','d12-x01-y01','d16-x01-y01','d20-x01-y01','d24-x01-y01','d28-x01-y01',
                                                  'd32-x01-y01','d36-x01-y01','d40-x01-y01','d44-x01-y01','d48-x01-y01','d52-x01-y01','d56-x01-y01',
                                                  'd60-x01-y01','d64-x01-y01','d68-x01-y01','d72-x01-y01','d76-x01-y01','d80-x01-y01','d84-x01-y01',
                                                  'd88-x01-y01','d92-x01-y01','d96-x01-y01','d100-x01-y01','d104-x01-y01','d108-x01-y01','d112-x01-y01',
                                                  'd116-x01-y01','d120-x01-y01','d124-x01-y01','d128-x01-y01','d132-x01-y01','d136-x01-y01']
            
            # mass dependence of pT of Drell-Yan lepton pairs
            histo_lists['CMS_2022_I2079374'] = ['d01-x01-y01','d03-x01-y01','d05-x01-y01','d07-x01-y01','d09-x01-y01','d11-x01-y01',
                                                'd13-x01-y01','d15-x01-y01','d17-x01-y01','d19-x01-y01','d21-x01-y01','d23-x01-y01',
                                                'd25-x01-y01','d27-x01-y01']
            
            # dileptonic ttbar
            histo_lists['ATLAS_2023_I2648096'] = ['d06-x01-y01','d09-x01-y01','d12-x01-y01','d15-x01-y01','d18-x01-y01','d21-x01-y01',
                                                  'd24-x01-y01','d27-x01-y01']
            # ttbar to lepton, jets and MET
            histo_lists['CMS_2021_I1901295'] = ['d159-x01-y01','d163-x01-y01','d167-x01-y01','d171-x01-y01','d175-x01-y01','d179-x01-y01',
                                                'd183-x01-y01','d187-x01-y01','d191-x01-y01','d195-x01-y01','d199-x01-y01','d203-x01-y01',
                                                'd207-x01-y01','d211-x01-y01','d317-x01-y01','d321-x01-y01','d325-x01-y01','d329-x01-y01']


            if analysis.name in histo_lists.keys():
                cfg.contur_log.info("Making SM theory for {} prediction {}".format(analysis.name,prediction.id))
                read_from_csv_files(analysis,histo_lists[analysis.name],prediction)
                
            if analysis.name == "ATLAS_2016_I1457605":
                cfg.contur_log.info("Making SM theory for {}, prediction {}".format(analysis.name,prediction.id))
                do_ATLAS_2016_I1457605(prediction)

            if analysis.name == "ATLAS_2017_I1645627":
                cfg.contur_log.info("Making SM theory for {}, prediction {}".format(analysis.name,prediction.id))
                do_ATLAS_2017_I1645627(prediction)

            if analysis.name == "ATLAS_2012_I1199269":
                cfg.contur_log.info("Making SM theory for {}, prediction {}".format(analysis.name,prediction.id))
                do_ATLAS_2012_I1199269(prediction)

            if analysis.name == "ATLAS_2017_I1591327":
                cfg.contur_log.info("Making SM theory for {}, prediction {}".format(analysis.name,prediction.id))
                do_ATLAS_2017_I1591327(prediction)

            if analysis.name == "ATLAS_2016_I1467454:LMODE=MU":
                cfg.contur_log.info("Making SM theory for {}, prediction {}".format(analysis.name,prediction.id))
                # this actually does both EL and MU
                do_ATLAS_2016_I1467454(prediction)

            if analysis.name == "CMS_2017_I1467451":
                cfg.contur_log.info("Making SM theory for {}, prediction {}".format(analysis.name,prediction.id))
                do_CMS_2017_I1467451(prediction)

            if analysis.name == "ATLAS_2015_I1408516:LMODE=MU":
                cfg.contur_log.info("Making SM theory for {}, prediction {}".format(analysis.name,prediction.id))
                # this actually does both EL and MU
                do_ATLAS_2015_I1408516(prediction)

            if analysis.name == "ATLAS_2019_I1725190":
                cfg.contur_log.info("Making SM theory for {}, prediction {}".format(analysis.name,prediction.id))
                do_ATLAS_2019_I1725190(prediction)

            if analysis.name == "ATLAS_2021_I1852328":
                cfg.contur_log.info("Making SM theory for {}, prediction {}".format(analysis.name,prediction.id))
                do_ATLAS_2021_I1852328(prediction)

            if analysis.name == "ATLAS_2019_I1764342":
                cfg.contur_log.info("Making SM theory for {} prediction {}".format(analysis.name,prediction.id))
                do_ATLAS_2019_I1764342(prediction)

            if analysis.name == 'ATLAS_2016_I1494075:LMODE=4L':
                cfg.contur_log.info("Making SM theory for {} prediction {}".format(analysis.name,prediction.id))
                do_ATLAS_2016_I1494075(prediction,1)

            if analysis.name == 'ATLAS_2016_I1494075:LMODE=2L2NU':
                cfg.contur_log.info("Making SM theory for {} prediction {}".format(analysis.name,prediction.id))
                do_ATLAS_2016_I1494075(prediction,2)

            if analysis.name == 'ATLAS_2019_I1718132:LMODE=ELEL':
            	cfg.contur_log.info("Making SM theory for {} prediction {}".format(analysis.name,prediction.id))
            	do_ATLAS_2019_I1718132(prediction,1)

            if analysis.name == 'ATLAS_2019_I1718132:LMODE=MUMU':
            	cfg.contur_log.info("Making SM theory for {} prediction {}".format(analysis.name,prediction.id))
            	do_ATLAS_2019_I1718132(prediction,2)

            if analysis.name == 'ATLAS_2019_I1718132:LMODE=ELMU':
            	cfg.contur_log.info("Making SM theory for {} prediction {}".format(analysis.name,prediction.id))
            	do_ATLAS_2019_I1718132(prediction,3)    

            if analysis.name == "ATLAS_2022_I2037744":
                cfg.contur_log.info("Making SM theory for {} prediction {}".format(analysis.name,prediction.id))
                do_ATLAS_2022_I2037744(prediction)  

            if "ATLAS_2024_I2768921" in analysis.name:
                # makes both SINGLE and DILEPTON files
                cfg.contur_log.info("Making SM theory for {} prediction {}".format(analysis.name,prediction.id))
                do_ATLAS_2024_I2768921(prediction,analysis)

            if "ATLAS_2024_I2765017:MODE=EXTRAPOLATED:TYPE=BSM" == analysis.name:
                # Photon xsec from Jeppe/HEJ
                cfg.contur_log.info("Making SM photon+jet theory for {} prediction {}".format(analysis.name,prediction.id))
                do_ATLAS_2024_I2765017_photon(prediction,analysis)

            if "ATLAS_2024_I2765017:TYPE=BSM" == analysis.name:
                # special hack for rmiss to make sure the ratio is exactly the ratio of the xsecs
                cfg.contur_log.info("Making SM RMISS theory for {} prediction {}".format(analysis.name,prediction.id))
                do_ATLAS_2024_I2765017(prediction,analysis,output_aos,got_pred)

            if "CMS_2020_I1814328" == analysis.name:
                # special treat because the MC errors were shown on the data for some reason.
                cfg.contur_log.info("Making SM theory for {} prediction {}".format(analysis.name,prediction.id))
                do_CMS_2020_I1814328(prediction,analysis)
  
            if 'ATLAS_2024_I2809112' == analysis.name:                                                                                                                                          
                cfg.contur_log.info("Making SM theory for {} prediction {}".format(analysis.name,prediction.id))
                do_ATLAS_2024_I2809112(analysis, prediction)

        else:
            cfg.contur_log.critical("Unknown source {}".format(source))
            sys.exit(1)

    for fname, ao_out in output_aos.items():
        if len(ao_out)>0:
            yoda.write(ao_out, fname)

    return


def main(args):
    """
    Main programme to run over the known analysis and build SM theory yodas from the TheoryRaw or REF areas.
    """
#    cfg.setup_logger(filename="contur_mkthy.log")
    setup_common(args)
    print("Writing log to {}".format(cfg.logfile_name))

    if args['ANAUNPATTERNS']:
        cfg.vetoAnalyses = args['ANAUNPATTERNS']
    if args['ANAPATTERNS']:
        cfg.onlyAnalyses = args['ANAPATTERNS']

    cfg.input_dir = args["INPUTDIR"]
    cfg.contur_log.info("Looking for raw theory files in {}".format(cfg.input_dir))

#    do_all = (args['ANALYSIS'] == "all")

    # -------------------------------------
    for analysis in cdb.get_analyses(filter=False):
        if cutil.analysis_select(analysis.name):
            make_sm_yoda(analysis)
