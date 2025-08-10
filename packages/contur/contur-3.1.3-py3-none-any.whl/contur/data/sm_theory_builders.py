import contur
import yoda
from contur.factories.yoda_factories import mkConturFriendlyScatter
import numpy as np
import scipy.stats
import os, csv
import contur.config.config as cfg
import contur.data.static_db as cdb
import contur.util.utils as cutil
from collections import defaultdict

def write_csv(rawdir,hname,x,y):

    csv_name = os.path.join(rawdir,hname)
    print("Writing to {}".format(csv_name))
    with open(csv_name, 'w', newline='') as csvfile:
        hwriter = csv.writer(csvfile)
        hwriter.writerow(x)
        hwriter.writerow(y)

def read_csv(rawdir,hname):

    lists = []
    csv_name = os.path.join(rawdir,hname)
    cfg.contur_log.debug("Reading from {}".format(csv_name))
    with open(csv_name, 'r', newline='') as csvfile:
        try:
            has_header = csv.Sniffer().has_header(csvfile.read(8192))
        except Exception as ex:
            cfg.contur_log.error("Problem reading {}".format(csvfile))
            cfg.contur_log.error("{}".format(ex))
            raise
        csvfile.seek(0)
        if (has_header):
            # this is vertical x, y listing. skip first column
            next(csvfile)
            lists.append([])
            lists.append([])
        hreader = csv.reader(csvfile,quoting=csv.QUOTE_NONNUMERIC)
        for row in hreader:
            try:
                if not has_header:
                    lists.append(row)
                else:
                    lists[0].append(row[0])
                    lists[1].append(row[1])
            except IndexError:
                print("Error reading file. Maybe a blank line at the end of the file?")
                raise

    return lists[0],lists[1]


def do_ATLAS_2016_I1457605(prediction):
    """
    Photon+jet NNLO Calculation from arXiv:1904.01044
    Xuan Chen, Thomas Gehrmann, Nigel Glover, Marius Hoefer, Alexander Huss
    """

    anaObjects = []
    indir = cfg.input_dir

    a_name = "ATLAS_2016_I1457605"
    yoda_name = a_name+".yoda"

    analysis = cdb.get_analyses(analysisid=a_name,filter=False)[0]

    splitter = " "
    dataFiles = {a_name+"/d01-x01-y01": indir+"/NNLO-Photons/Fig5/NNLO.Et_gam_bin1_ATLAS.dat",
                 a_name+"/d02-x01-y01": indir+"/NNLO-Photons/Fig5/NNLO.Et_gam_bin2_ATLAS.dat",
                 a_name+"/d03-x01-y01": indir+"/NNLO-Photons/Fig5/NNLO.Et_gam_bin3_ATLAS.dat",
                 a_name+"/d04-x01-y01": indir+"/NNLO-Photons/Fig5/NNLO.Et_gam_bin4_ATLAS.dat"
                 }

    f = contur.util.utils.find_ref_file(analysis)
    aos = yoda.read(f)

    for path, orig_ao in aos.items():

        ao = mkConturFriendlyScatter(orig_ao,mkthy=True)
        filename = dataFiles.get(path[5:])
        ao.setPath("/THY/"+path[5:])
        ao.rmAnnotation("ErrorBreakdown")
        cfg.contur_log.debug("Reading {}".format(filename))

        with open(filename, "r+") as f:
            data = f.readlines()  # read the text file
            binNum = 0
            nBins = len(ao.points())
            cfg.contur_log.debug("{} bins".format(nBins))
            for line in data:
                # get a list containing all the entries in a line
                allNums = line.strip().split(splitter)
                # check they're actually numbers
                numberLine = True
                for num in allNums:
                    try:
                        val = float(num)
                    except ValueError:
                        numberLine = False
                        break
                if numberLine:
                    tmplist = [float(allNums[3]), float(allNums[5]), float(allNums[7]), float(
                        allNums[9]), float(allNums[11]), float(allNums[13]), float(allNums[15])]
                    upper = max(tmplist)
                    lower = min(tmplist)
                    uncertainty = (upper - lower)/2000.0
                    mean = (upper + lower)/2000.0
                    if binNum < nBins:
                        point = ao.point(binNum)
                        binNum = binNum + 1
                        point.setY(mean)
                        point.setYErrs(uncertainty, uncertainty)

            ao.setTitle(prediction.short_description)
            #ao.setAnnotation("Title", "NNLO QCD arXiv:1904.01044")
            anaObjects.append(ao)

    yoda.write(anaObjects, a_name+"-Theory.yoda")

def do_ATLAS_2017_I1645627(prediction):

    anaObjects = []
    indir = cfg.input_dir

    # Photon+jet NNLO Calculation from arXiv:1904.01044
    # Xuan Chen, Thomas Gehrmann, Nigel Glover, Marius Hoefer, Alexander Huss
    a_name = "ATLAS_2017_I1645627"
    splitter = " "
    dataFiles = {a_name+"/d01-x01-y01": indir+"/NNLO-Photons/Fig11/NNLO_pt_NNPDF31_hybIso.Et_gam_ATLAS.dat",
                 a_name+"/d02-x01-y01": indir+"/NNLO-Photons/Fig12/NNLO_pt_NNPDF31_hybIso.ptj1_ATLAS.dat",
                 a_name+"/d03-x01-y01": indir+"/NNLO-Photons/Fig14/NNLO_pt_NNPDF31_hybIso.dphi_gam_j1_ATLAS.dat",
                 a_name+"/d04-x01-y01": indir+"/NNLO-Photons/Fig13/NNLO_pt_NNPDF31_hybIso.m_gam_j1_ATLAS.dat",
                 a_name+"/d05-x01-y01": indir+"/NNLO-Photons/Fig15/NNLO_pt_NNPDF31_hybIso.abs_costhetastar_gam_j1_ATLAS.dat"
                 }

    analysis = cdb.get_analyses(analysisid=a_name,filter=False)[0]

    f = contur.util.utils.find_ref_file(analysis)
    aos = yoda.read(f)
    for path, orig_ao in aos.items():
        ao = mkConturFriendlyScatter(orig_ao,mkthy=True)
        filename = dataFiles.get(path[5:])
        ao.setPath("/THY/"+path[5:])
        ao.rmAnnotation("ErrorBreakdown")

        cfg.contur_log.debug("Reading {}".format(filename))

        with open(filename, "r+") as f:
            data = f.readlines()  # read the text file
            binNum = 0
            nBins = len(ao.points())
            cfg.contur_log.debug("nBins= {}".format(nBins))
            for line in data:
                # get a list containing all the entries in a line
                allNums = line.strip().split(splitter)
            # check they're actually numbers
                numberLine = True
                for num in allNums:
                    try:
                        val = float(num)
                    except ValueError:
                        numberLine = False
                        break
                if numberLine:
                    tmplist = [float(allNums[3]), float(allNums[5]), float(allNums[7]), float(
                        allNums[9]), float(allNums[11]), float(allNums[13]), float(allNums[15])]
                    upper = max(tmplist)
                    lower = min(tmplist)
                    uncertainty = (upper - lower)/2000.0
                    mean = (upper + lower)/2000.0
                    if binNum < nBins:
                        point = ao.point(binNum)
                        binNum = binNum + 1
                        point.setY(mean)
                        point.setYErrs(uncertainty, uncertainty)

        ao.setTitle(prediction.short_description)
        anaObjects.append(ao)

    yoda.write(anaObjects, a_name+"-Theory.yoda")


def do_ATLAS_2012_I1199269(prediction):
    """
         ATLAS 7TeV diphotons, 2gamma NNLO prediction read from paper
         S. Catani, L. Cieri, D. de Florian, G. Ferrera, and M. Grazzini,
         Diphoton production at hadron colliders: a fully-differential QCD calculation at NNLO,
         Phys. Rev. Lett. 108 (2012) 072001, [arXiv:1110.2375].
    """

    anaObjects = []
    indir = cfg.input_dir

    a_name = "ATLAS_2012_I1199269"
    splitter = ", "
    dataFiles = {a_name+"/d01-x01-y01": indir+"/"+a_name+"/2gammaNNLO-Fig5a.txt",
                 a_name+"/d02-x01-y01": indir+"/"+a_name+"/2gammaNNLO-Fig5b.txt",
                 a_name+"/d03-x01-y01": indir+"/"+a_name+"/2gammaNNLO-Fig5c.txt",
                 a_name+"/d04-x01-y01": indir+"/"+a_name+"/2gammaNNLO-Fig5d.txt"
                 }
    analysis = cdb.get_analyses(analysisid=a_name,filter=False)[0]

    f = contur.util.utils.find_ref_file(analysis)
    aos = yoda.read(f)
    for path, orig_ao in aos.items():
        ao = mkConturFriendlyScatter(orig_ao,mkthy=True)
        filename = dataFiles.get(path[5:])
        if filename:
            ao.setPath("/THY/"+path[5:])
            ao.rmAnnotation("ErrorBreakdown")

            cfg.contur_log.debug("Reading {}".format(filename))

            with open(filename, "r+") as f:
                data = f.readlines()  # read the text file
                binNum = 0
                nBins = len(ao.points())
                for line in data:
                    # get a list containing all the entries in a line
                    allNums = line.strip().split(splitter)
                    # check they're actually numbers
                    numberLine = True
                    for num in allNums:
                        try:
                            val = float(num)
                        except ValueError:
                            numberLine = False
                            break
                    if numberLine:
                        uncertainty = float(allNums[2])
                        mean = float(allNums[1])
                        if binNum < nBins:
                            point = ao.point(binNum)
                            binNum = binNum + 1
                            point.setY(mean)
                            point.setYErrs(
                                uncertainty, uncertainty)

            ao.setTitle(prediction.short_description)
            anaObjects.append(ao)

    yoda.write(anaObjects, a_name+"-Theory.yoda")

def do_ATLAS_2017_I1591327(prediction):
    """
    ATLAS 8TeV diphotons, 

    Matrix prediction prediction read from
    Predictions for the isolated diphoton production through NNLO in QCD and
    comparison to the 8 TeV ATLAS data
    Bouzid Boussaha, Farida Iddir, Lahouari Semlala arXiv:1803.09176

    pT and phi* personal communication from Thomas Neumann:
    The Diphoton qT spectrum at N3LL′+NNLO
    https://arxiv.org/abs/2107.12478

    2gamma from
    S. Catani, L. Cieri, D. de Florian, G. Ferrera, and M. Grazzini,
    Diphoton production at hadron colliders: a fully-differential QCD calculation at NNLO,
    Phys. Rev. Lett. 108 (2012) 072001, [arXiv:1110.2375].
    """
    anaObjects = []
    indir = cfg.input_dir

    a_name = "ATLAS_2017_I1591327"
    splitter = ", "

    if prediction.id == "B":        
        dataFiles = {a_name+"/d02-x01-y01": indir+"/"+a_name+"/Matrix_Mass.txt",
                     a_name+"/d03-x01-y01": indir+"/"+a_name+"/2gammaNNLO_pt.txt"
                     }
        f_stem = "-Theory_B.yoda"
        
    elif prediction.id == "A":
        dataFiles = {a_name+"/d02-x01-y01": indir+"/"+a_name+"/Matrix_Mass.txt",
                     a_name+"/d03-x01-y01": indir+"/"+a_name+"/Neumann/ptgamgam.txt",
                     a_name+"/d05-x01-y01": indir+"/"+a_name+"/Neumann/phistargamgam.txt"
                     }
        f_stem = "-Theory.yoda"

    else:
        cfg.contur_log.error("No info for prediction {} ID {}".format(prediction.short_description,prediction.id))
        return
                
    analysis = cdb.get_analyses(analysisid=a_name,filter=False)[0]

    f = contur.util.utils.find_ref_file(analysis)
    aos = yoda.read(f)
    for path, orig_ao in aos.items():
        ao = mkConturFriendlyScatter(orig_ao,mkthy=True)
        filename = dataFiles.get(path[5:])
        if filename:
            ao.setPath("/THY/"+path[5:])
            ao.rmAnnotation("ErrorBreakdown")

            if "Neumann" in filename:
                splitter = None
                label = "2107.12478 (Neumann)"
                offset = 1
            elif "Matrix" in filename:
                splitter = ", "
                label = "1803.09176 (Matrix)"
                offset = 0
            else:
                splitter = ", "
                label = "2gamma NNLO"
                offset = 0

            with open(filename, "r+") as f:
                data = f.readlines()  # read the text file                
                binNum = 0
                nBins = len(ao.points())
                for line in data:
                    # get a list containing all the entries in a line
                    allNums = line.strip().split(splitter)
                    # check they're actually numbers
                    numberLine = False
                    for num in allNums:
                        try:
                            val = float(num)
                            numberLine = True
                        except ValueError:
#                            if not "N3LLp-mtgg" in num: numberLine = False
                            if not "N3LLp-ptg" in num: numberLine = False
                            break
                    if numberLine:
                        mean = float(allNums[1+offset])
                        if offset==0:
                            uncertainty1 = float(allNums[2+offset])
                            uncertainty2 = uncertainty1
                        else:
                            uncertainty1 = float(allNums[2+offset])-mean
                            uncertainty2 = mean-float(allNums[3+offset])
                            
                        if binNum < nBins:
                            point = ao.point(binNum)
                            binNum = binNum + 1
                            point.setY(mean)
                            point.setYErrs(
                                uncertainty1, uncertainty2)

            ao.setAnnotation("Title", label)

            anaObjects.append(ao)

        yoda.write(anaObjects, a_name+f_stem)


def do_ATLAS_2016_I1467454(prediction):

    indir = cfg.input_dir

    anaObjects_el = []
    anaObjects_mu = []


    # ATLAS 8TeV HMDY mass distribution
    # Predictions from the paper, taken from the ll theory ratio plot (Born) but applied
    # to the dressed level ee & mm data as mult. factors.
    a_name_mu  = "ATLAS_2016_I1467454:LMODE=MU"
    a_name_el  = "ATLAS_2016_I1467454:LMODE=EL"
    short_name = "ATLAS_2016_I1467454"

    splitter = ", "
    dataFiles = {"d18-x01-y01": indir+"/"+short_name+"/dy1.txt",
                 "d29-x01-y01": indir+"/"+short_name+"/dy1.txt",
                 }
    analysis_mu = cdb.get_analyses(analysisid=a_name_mu,filter=False)[0]
    analysis_el = cdb.get_analyses(analysisid=a_name_el,filter=False)[0]

    # This finds the REF file, which is common to _mu and _el versions.
    yodaf = contur.util.utils.find_ref_file(analysis=analysis_mu)

    for histo, filename in dataFiles.items():

        aos = yoda.read(yodaf, patterns=histo)
        orig_ao = next(iter(aos.values()))
        ao = mkConturFriendlyScatter(orig_ao,mkthy=True)

        mu = ("d29" in histo)
        el = ("d18" in histo)

        if mu:
            ao.setPath("/THY/{}/{}".format(a_name_mu,histo))
        elif el:
            ao.setPath("/THY/{}/{}".format(a_name_el,histo))

        ao.rmAnnotation("ErrorBreakdown")


        with open(filename, "r+") as f:
            data = f.readlines()  # read the text file
            binNum = 0
            nBins = len(ao.points())
            for line in data:
                # get a list containing all the entries in a line
                allNums = line.strip().split(splitter)
                # check they're actually numbers
                numberLine = True
                for num in allNums:
                    try:
                        val = float(num)
                    except ValueError:
                        numberLine = False
                        break
                if numberLine:
                    uncertainty = float(allNums[2])
                    mean = float(allNums[1])
                    if binNum < nBins:
                        point = ao.point(binNum)
                        uncertainty = uncertainty*point.y()
                        point.setYErrs(
                            uncertainty, uncertainty)
                        point.setY(point.y()*mean)
                        binNum = binNum + 1

        ao.setTitle(prediction.short_description)

        if el:
            anaObjects_el.append(ao)
        elif mu:
            anaObjects_mu.append(ao)

    yoda.write(anaObjects_el, analysis_el.name+"-Theory.yoda")
    yoda.write(anaObjects_mu, analysis_mu.name+"-Theory.yoda")


def do_CMS_2017_I1467451(prediction):
    """
    CMS 8TeV H->WW pT distribution
     Predictions from the paper
    """

    indir = cfg.input_dir
    anaObjects = []

    a_name = "CMS_2017_I1467451"
    splitter = ", "
    dataFiles = {a_name+"/d01-x01-y01": indir +
                 "/"+a_name+"/hpt.txt"}
    analysis = cdb.get_analyses(analysisid=a_name,filter=False)[0]

    f = contur.util.utils.find_ref_file(analysis)
    aos = yoda.read(f)
    for path, orig_ao in aos.items():
        ao = mkConturFriendlyScatter(orig_ao,mkthy=True)

        filename = dataFiles.get(path[5:])
        if filename:
            ao.setPath("/THY/"+path[5:])
            ao.rmAnnotation("ErrorBreakdown")

            with open(filename, "r+") as f:
                data = f.readlines()  # read the text file
                binNum = 0
                nBins = len(ao.points())
                for line in data:
                    # get a list containing all the entries in a line
                    allNums = line.strip().split(splitter)
                    # check they're actually numbers
                    numberLine = True
                    for num in allNums:
                        try:
                            val = float(num)
                        except ValueError:
                            numberLine = False
                            break
                    if numberLine:
                        uncertainty = float(allNums[2])
                        mean = float(allNums[1])
                        if binNum < nBins:
                            point = ao.point(binNum)
                            point.setYErrs(
                                uncertainty, uncertainty)
                            point.setY(mean)
                            binNum = binNum + 1

            ao.setTitle(prediction.short_description)

            anaObjects.append(ao)

    yoda.write(anaObjects, a_name+"-Theory.yoda")

def do_ATLAS_2015_I1408516(prediction):
    """
    ATLAS 8TeV Drell-Yan phi* and pT distributions
    Predictions from Bizon et al arXiv:1805.05916
    """

    indir = cfg.input_dir

    anaObjects_el = []
    anaObjects_mu = []

    a_name_mu = "ATLAS_2015_I1408516:LMODE=MU"
    a_name_el = "ATLAS_2015_I1408516:LMODE=EL"
    short_name = "ATLAS_2015_I1408516"

    analysis_mu = cdb.get_analyses(analysisid=a_name_mu,filter=False)[0]
    analysis_el = cdb.get_analyses(analysisid=a_name_el,filter=False)[0]

    splitter = " "
    dataFiles = {"d02-x01-y04": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_46_66_0.0_0.8.dat",
                 "d03-x01-y04": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_46_66_0.8_1.6.dat",
                 "d04-x01-y04": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_46_66_1.6_2.4.dat",
                 "d05-x01-y04": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_66_116_0.0_0.4.dat",
                 "d06-x01-y04": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_66_116_0.4_0.8.dat",
                 "d07-x01-y04": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_66_116_0.8_1.2.dat",
                 "d08-x01-y04": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_66_116_1.2_1.6.dat",
                 "d09-x01-y04": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_66_116_1.6_2.0.dat",
                 "d10-x01-y04": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_66_116_2.0_2.4.dat",
                 "d11-x01-y04": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_116_150_0.0_0.8.dat",
                 "d12-x01-y04": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_116_150_0.8_1.6.dat",
                 "d13-x01-y04": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_116_150_1.6_2.4.dat",
                 "d14-x01-y04": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_46_66_0.0_2.4.dat",
                 "d15-x01-y04": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_66_116_0.0_2.4.dat",
                 "d16-x01-y04": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_116_150_0.0_2.4.dat",
                 "d17-x01-y04": indir+"/"+short_name+"/ptz/ATLAS_8TeV_ptz_NNLO_N3LL_66_116_0.0_0.4.dat",
                 "d18-x01-y04": indir+"/"+short_name+"/ptz/ATLAS_8TeV_ptz_NNLO_N3LL_66_116_0.4_0.8.dat",
                 "d19-x01-y04": indir+"/"+short_name+"/ptz/ATLAS_8TeV_ptz_NNLO_N3LL_66_116_0.8_1.2.dat",
                 "d20-x01-y04": indir+"/"+short_name+"/ptz/ATLAS_8TeV_ptz_NNLO_N3LL_66_116_1.2_1.6.dat",
                 "d21-x01-y04": indir+"/"+short_name+"/ptz/ATLAS_8TeV_ptz_NNLO_N3LL_66_116_1.6_2.0.dat",
                 "d22-x01-y04": indir+"/"+short_name+"/ptz/ATLAS_8TeV_ptz_NNLO_N3LL_66_116_2.0_2.4.dat",
                 "d26-x01-y04": indir+"/"+short_name+"/ptz/ATLAS_8TeV_ptz_NNLO_N3LL_46_66_0.0_2.4.dat",
                 "d27-x01-y04": indir+"/"+short_name+"/ptz/ATLAS_8TeV_ptz_NNLO_N3LL_66_116_0.0_2.4.dat",
                 "d28-x01-y04": indir+"/"+short_name+"/ptz/ATLAS_8TeV_ptz_NNLO_N3LL_116_150_0.0_2.4.dat",

                 "d02-x01-y01": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_46_66_0.0_0.8.dat",
                 "d03-x01-y01": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_46_66_0.8_1.6.dat",
                 "d04-x01-y01": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_46_66_1.6_2.4.dat",
                 "d05-x01-y01": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_66_116_0.0_0.4.dat",
                 "d06-x01-y01": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_66_116_0.4_0.8.dat",
                 "d07-x01-y01": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_66_116_0.8_1.2.dat",
                 "d08-x01-y01": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_66_116_1.2_1.6.dat",
                 "d09-x01-y01": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_66_116_1.6_2.0.dat",
                 "d10-x01-y01": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_66_116_2.0_2.4.dat",
                 "d11-x01-y01": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_116_150_0.0_0.8.dat",
                 "d12-x01-y01": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_116_150_0.8_1.6.dat",
                 "d13-x01-y01": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_116_150_1.6_2.4.dat",
                 "d14-x01-y01": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_46_66_0.0_2.4.dat",
                 "d15-x01-y01": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_66_116_0.0_2.4.dat",
                 "d16-x01-y01": indir+"/"+short_name+"/phistar/ATLAS_8TeV_phistar_NNLO_N3LL_116_150_0.0_2.4.dat",
                 "d17-x01-y01": indir+"/"+short_name+"/ptz/ATLAS_8TeV_ptz_NNLO_N3LL_66_116_0.0_0.4.dat",
                 "d18-x01-y01": indir+"/"+short_name+"/ptz/ATLAS_8TeV_ptz_NNLO_N3LL_66_116_0.4_0.8.dat",
                 "d19-x01-y01": indir+"/"+short_name+"/ptz/ATLAS_8TeV_ptz_NNLO_N3LL_66_116_0.8_1.2.dat",
                 "d20-x01-y01": indir+"/"+short_name+"/ptz/ATLAS_8TeV_ptz_NNLO_N3LL_66_116_1.2_1.6.dat",
                 "d21-x01-y01": indir+"/"+short_name+"/ptz/ATLAS_8TeV_ptz_NNLO_N3LL_66_116_1.6_2.0.dat",
                 "d22-x01-y01": indir+"/"+short_name+"/ptz/ATLAS_8TeV_ptz_NNLO_N3LL_66_116_2.0_2.4.dat",
                 "d26-x01-y01": indir+"/"+short_name+"/ptz/ATLAS_8TeV_ptz_NNLO_N3LL_46_66_0.0_2.4.dat",
                 "d27-x01-y01": indir+"/"+short_name+"/ptz/ATLAS_8TeV_ptz_NNLO_N3LL_66_116_0.0_2.4.dat",
                 "d28-x01-y01": indir+"/"+short_name+"/ptz/ATLAS_8TeV_ptz_NNLO_N3LL_116_150_0.0_2.4.dat"
                 }

    # This finds the REF file, which is common to _mu and _el versions.
    f = contur.util.utils.find_ref_file(analysis=analysis_mu)
    aos = yoda.read(f)
    for path, orig_ao in aos.items():
        ao = mkConturFriendlyScatter(orig_ao,mkthy=True)
        el = False
        mu = False
        filename = dataFiles.get(ao.name())
        if filename:

            el = ("y01" in path)
            mu = ("y04" in path)

            if mu:
                ao.setPath("/THY/{}/{}".format(a_name_mu,ao.name()))
            elif el:
                ao.setPath("/THY/{}/{}".format(a_name_el,ao.name()))
            ao.rmAnnotation("ErrorBreakdown")

            cfg.contur_log.debug("Reading {}".format(filename))

            with open(filename, "r+") as f:
                data = f.readlines()  # read the text file
                binNum = 0
                nBins = len(ao.points())
                # now we want to get the born-to-dressed corrections
                if "y01" in path:
                    # this is an electron plot
                    dpath = path[:len(path)-1]+"2"
                    dplot = mkConturFriendlyScatter(aos[dpath],mkthy=True)
                elif "y04" in path:
                    # this is a muon plot
                    dpath = path[:len(path)-1]+"5"
                    dplot = mkConturFriendlyScatter(aos[dpath],mkthy=True)

                bornpath = path[:len(path)-1]+"6"
                bornplot = mkConturFriendlyScatter(aos[bornpath],mkthy=True)

                for line in data:
                    # get a list containing all the entries in a line
                    allNums = line.strip().split(splitter)
                    # check they're actually numbers
                    numberLine = True
                    for num in allNums:
                        try:
                            val = float(num)
                        except ValueError:
                            numberLine = False
                            break
                    if numberLine:

                        uncertainty = np.abs(
                            (float(allNums[2])-float(allNums[3]))/2.0)
                        mean = float(allNums[1])
                        if binNum < nBins:
                            corr = dplot.point(binNum).y(
                            )/bornplot.point(binNum).y()
                            point = ao.point(binNum)
                            point.setYErrs(
                                uncertainty*corr, uncertainty*corr)
                            point.setY(mean*corr)
                            binNum = binNum + 1

        ao.setTitle(prediction.short_description)

        if el:
            anaObjects_el.append(ao)
        elif mu:
            anaObjects_mu.append(ao)

    yoda.write(anaObjects_el, analysis_el.name+"-Theory.yoda")
    yoda.write(anaObjects_mu, analysis_mu.name+"-Theory.yoda")



def do_ATLAS_2019_I1725190(prediction):
    """
    ATLAS 13 TeV DY Run 2 search
    Fit to SM from the paper.
    """
    anaObjects = []

    a_name = "ATLAS_2019_I1725190"
    analysis = cdb.get_analyses(analysisid=a_name,filter=False)[0]

    def atlas_fit(mass,muon):

        # return the result of the ATLAS fit to dilepton mass, 13 TeV
        # electron if not muon

        rootS = 13000.0
        mZ = 91.1876
        gammaZ = 2.4952

        x = mass/rootS

        if muon:
            # dimuon channel:
            c = 1.0/3.0
            b = 11.8
            p0 = -7.38
            p1 = -4.132
            p2 = -1.0637
            p3 = -0.1022
        else:
            # electron
            c = 1.0
            b = 1.5
            p0 = -12.38
            p1 = -4.295
            p2 = -0.9191
            p3 = -0.0845

        val = scipy.stats.cauchy.pdf(mass, mZ, gammaZ) * np.power((1-np.power(x,c)),b) * np.power(x, p0 + p1*np.log(x) + p2*np.log(x)**2 + p3*np.log(x)**3)
        return val


    a_muon = 138700
    a_elec = 178000

    f = contur.util.utils.find_ref_file(analysis)
    aos = yoda.read(f)
    for path, orig_ao in aos.items():

        ao = mkConturFriendlyScatter(orig_ao,mkthy=True)

        if "d01-x01-y01" in path:
            muon = False
            norm = 178000.0
        elif "d02-x01-y01" in path:
            muon = True
            norm = 138700.0
        else:
            continue

        ao.setPath("/THY/"+path[5:])
        ao.rmAnnotation("ErrorBreakdown")

        sum_n = 0
        for point in ao.points():
            mass = point.x()
            point.setY(atlas_fit(mass,muon))
            bw=point.xErrs()[0]*2.0
            sum_n+=point.y()*bw


        norm = 10.*norm/sum_n
        # now another loop to set the normalisation.
        for point in ao.points():
            point.setY(point.y()*norm)
            bw=point.xErrs()[0]*2.0
            # uncertainty set to root of the number of events, then scaled to error on events per ten GeV ie sqrt(n=y*10)/10
            num_events = point.y()*bw/10.0
            uncertainty = 10.0*np.sqrt(num_events)/bw
            point.setYErrs(uncertainty,uncertainty)



        ao.setAnnotation("Title", "fit to data")
        anaObjects.append(ao)

    yoda.write(anaObjects, a_name+"-Theory.yoda")

def do_ATLAS_2021_I1852328(prediction):
    """
    ATLAS 13 TeV WW+jet
    the prediction is for the b-veto, so we need to scale it for the difference (taken from the difference in the data)
    y05 multiplied by the ratio y02/y01
    """

    anaObjects = []
    indir = cfg.input_dir

    a_name = "ATLAS_2021_I1852328"
    yoda_name = a_name+".yoda"

    analysis = cdb.get_analyses(analysisid=a_name,filter=False)[0]

    f = contur.util.utils.find_ref_file(analysis)
    aos = yoda.read(f)

    for path, orig_ao in aos.items():

        ao = mkConturFriendlyScatter(orig_ao,mkthy=True)
        if "y05" in path:
            aob = mkConturFriendlyScatter(aos[path[:-1]+"2"],mkthy=True)
            aoi = mkConturFriendlyScatter(aos[path[:-1]+"1"],mkthy=True)
            for points in zip(ao.points(),aob.points(),aoi.points()):
                points[0].setY(points[0].y()*points[1].y()/points[2].y())

            ao.setTitle(prediction.short_description)
            ao.setPath(ao.path()[:-1]+"2")
            ao.setPath("/THY/"+ao.path()[5:])
            ao.rmAnnotation("ErrorBreakdown")
            anaObjects.append(ao)


    yoda.write(anaObjects, a_name+"-Theory.yoda")

def do_ATLAS_2019_I1764342(prediction):
    """
    ATLAS 13 TeV ll+photons
    There's a version of this in HEPData with no uncertainties. Rerun by Xilin Wang to include scale uncertainties, which
    are calculated here from the RAW rivet weights output.
    """

    a_name = "ATLAS_2019_I1764342"

    if prediction.id != "A":
        cfg.contur_log.error("Do not know how to make file for {}, prediction ID {}".format(a_name, prediction.id))
        return

    # input raw file.
    relpath = "data/TheoryRaw/{}/{}.yoda".format(a_name,a_name)
    f = cfg.paths.data_path(relpath)
    # output file
    f_out = prediction.file_name

    SCALES = [
      'MUR0.5_MUF0.5_PDF261000',
      'MUR0.5_MUF1_PDF261000',
      'MUR1_MUF0.5_PDF261000',
      'MUR1_MUF1_PDF261000',
      'MUR1_MUF2_PDF261000',
      'MUR2_MUF1_PDF261000',
      'MUR2_MUF2_PDF261000',
    ]

    #EW_CORRS = [
    #  'MUR1_MUF1_PDF261000_MULTIASSEW',
    #  'MUR1_MUF1_PDF261000_EXPASSEW',
    #  'MUR1_MUF1_PDF261000_ASSEW',
    #]


    OUT = { }
    aos = yoda.read(f)
    for path, ao in aos.items():
        if ao.dim() != 2: # Scatter1D object does not have y value
           continue
        if 'RAW' in path or path.endswith(']'):
            continue
        hname = '/THY' + path
        OUT[hname] = mkConturFriendlyScatter(ao,mkthy=True)
        OUT[hname].setPath(hname)
        OUT[hname].setTitle(prediction.short_description)

        nominal = np.array([ b.sumW()   for b in ao.bins() ])
        statsSq = np.array([ b.sumW2()  for b in ao.bins() ])
        bwidth  = np.array([ b.xMax() - b.xMin()  for b in ao.bins() ])

        scaleup = np.array(nominal)
        scaledn = np.array(nominal)
        for scale in SCALES:
          temp = np.array([ b.sumW() for b in aos['%s[%s]' % (path, scale) ].bins() ])
          scaleup = np.array(list(map(max, zip(scaleup, temp))))
          scaledn = np.array(list(map(min, zip(scaledn, temp))))
        delta_qcd = 0.5 * (scaleup - scaledn)

        delta_total = np.sqrt(statsSq + delta_qcd ** 2) / bwidth

        for i in range(OUT[hname].numPoints()):
          cval = OUT[hname].point(i).y()
          olderr = OUT[hname].point(i).yErrs()[0]
          cfg.contur_log.debug('old: %.1f%%, new: %.1f%%' % (100.*olderr/cval, 100.*delta_total[i]/cval))
          OUT[hname].point(i).setYErrs(delta_total[i])

#    yoda.write(OUT, f.replace('.yoda', '_B.yoda'))
    yoda.write(OUT, f_out)

def do_ATLAS_2016_I1494075(prediction, mode_flag):
    """
    ATLAS 8 TeV 4l/2l2nu
    Newly written rivet routine, verified with events generated by Powheg+Pythia 8
    """

    #Two separate files generated but with all histograms on it
    #so for mode 4L, graphs of 2L2NU will be empty and need to be excluded, vice versa.

    a_name = "ATLAS_2016_I1494075"
    mode_analysis = ["_MODE:4L", "_MODE:2L2NU"]

    # input raw file.
    relpath = "data/TheoryRaw/{}/{}-Theory.yoda".format(a_name,a_name + mode_analysis[mode_flag-1])

    f = cfg.paths.data_path(relpath)
    # output file
    f_out = prediction.file_name

    #Include 62 weights > <
    SCALES = [
        "_muR5000000E-01_muF5000000E-01_",
        "_muR1000000E+00_muF5000000E-01_",
        "_muR2000000E+00_muF5000000E-01_",
        "_muR5000000E-01_muF1000000E+00_",
        "_muR2000000E+00_muF1000000E+00_",
        "_muR5000000E-01_muF2000000E+00_",
        "_muR1000000E+00_muF2000000E+00_",
        "_muR2000000E+00_muF2000000E+00_",
        "_pdfset_21100_",
        "_pdfset_260000_"
    ]
    pdf_range = list(np.linspace(11001,11052,52,dtype=int))
    pdf_list = ["_pdfset_"+str(i)+"_" for i in pdf_range]
    SCALES = SCALES + pdf_list

    OUT = { }
    histo_4l = ['d02', 'd03' ,'d04', 'd05']
    histo_2l2nu = ['d06', 'd07', 'd08']
    aos = yoda.read(f)
    for path, ao in aos.items():
        #READING only Nominal data
        if ao.dim() != 2: # Scatter1D object does not have y value
            continue
        if 'RAW' in path or path.endswith(']'):
            continue
        if mode_flag == 1:
            if any(histo in path for histo in histo_2l2nu):
                continue
        if mode_flag == 2:
            if any(histo in path for histo in histo_4l):
                continue
        hname = '/THY' + path
        OUT[hname] = mkConturFriendlyScatter(ao,mkthy=True)
        OUT[hname].setPath(hname)
        OUT[hname].setTitle(prediction.short_description)

        #Uncertainty calculation
        nominal = np.array([ b.sumW()   for b in ao.bins() ])
        statsSq = np.array([ b.sumW2()  for b in ao.bins() ])
        bwidth  = np.array([ b.xMax() - b.xMin()  for b in ao.bins() ])

        scaleup = np.array(nominal)
        scaledn = np.array(nominal)
        #For selected ones, calculate uncertainties from the weighted histograms.
        for scale in SCALES:
            temp = np.array([ b.sumW() for b in aos['%s[%s]' % (path, scale) ].bins() ])
            scaleup = np.array(list(map(max, zip(scaleup, temp))))
            scaledn = np.array(list(map(min, zip(scaledn, temp))))
        delta_qcd = 0.5 * (scaleup - scaledn)

        delta_total = np.sqrt(statsSq + delta_qcd ** 2) / bwidth
        #Writing uncertainties
        for i in range(OUT[hname].numPoints()):
            cval = OUT[hname].point(i).y()
            olderr = OUT[hname].point(i).yErrs()[0]
            cfg.contur_log.debug('old: %.1f%%, new: %.1f%%' % (100.*olderr/cval, 100.*delta_total[i]/cval))
            OUT[hname].point(i).setYErrs(delta_total[i])
    yoda.write(OUT, f_out)


def read_from_csv_files(analysis,histo_list,prediction,err_in_aux=False):
    '''
    Generic function to read SM prediction from a set of CSV files 

    it is assumed the values are given as the ratio to the data (usually digitised from a ratio plot in the paper)
    so they are multiplied by the data valie.

    if err_in_aux is True, it is assumed the central value (or the ratio) are in the main file, and the fractional 
    uncertainties on those values are in files with __uncertainty_ appended.

    '''

    anaObjects = []
    yoda_name = analysis.name+".yoda"

    rawdir = os.path.join(cfg.input_dir,analysis.name)
    
    # make directory if not already present.
    #cutil.mkoutdir(rawdir)

    f = contur.util.utils.find_ref_file(analysis)
    aos = yoda.read(f)
    for path, ao in aos.items():
        ao = mkConturFriendlyScatter(ao, mkthy=True)
        for histo in histo_list:
            if histo in path:
                if prediction.id=="A":
                    x, y = read_csv(rawdir,histo+".csv")
                    if err_in_aux:
                        # uncertainties in a seperate file.
                        xe, ye = read_csv(rawdir,histo+"__uncertainty_.csv")
                else:
                    x, y = read_csv(rawdir,"{}_{}.csv".format(histo,prediction.id))
                    if err_in_aux:
                        # uncertainties in a seperate file.
                        xe, ye = read_csv(rawdir,"{}_{}__uncertainty_.csv".format(histo,prediction.id))
                ao.rmAnnotation("ErrorBreakdown")
                ao.setPath("/THY/"+analysis.name+"/"+histo)

                if err_in_aux:

                    # labourious procedure to obtain the uncertainties
                    
                    # sort them by x value to get bins aligned
                    errs = sorted(zip(xe, ye))
                    vals = sorted(zip(x, y))
                    
                    x_val = []
                    y_val = []
                    for i in range(len(vals)):
                        # build the xvalues (three per point)
                        x_val.append(vals[i][0])
                        x_val.append(errs[2*i][0])
                        x_val.append(errs[2*i+1][0])

                        # build the xvalues (three per point)
                        # central value
                        y_val.append(vals[i][1])
                        # multiply by the y ratio to get abs unc on ratio
                        y_val.append(errs[2*i+1][1]*vals[i][1])
                        y_val.append(errs[2*i+1][1]*vals[i][1])
                        
                    x = x_val
                    y = y_val
                
                # get rid of some of the spurious precision
                x = list(np.around(np.array(x),4))
                y = list(np.around(np.array(y),4))

                # list of pairs
                points = sorted(zip(x, y))

                # check we have the right number of points"
                nBins = len(ao.points())
                if not nBins == len(points)/3.0:
                    cfg.contur_log.error("Mismatched number of points in {}, {} vs {}".format(path,nBins,len(points)/3.0))
                    continue

                counter=0
                for point in ao.points():

                    # for each x value we have an upper, central and lower value. Get them and order them.
                    yvals = sorted([points[counter][1],points[counter+1][1],points[counter+2][1]])

                    # central value
                    point.setY(point.y()*yvals[1])

                    # uncertainty
                    uncertainty_up   = (yvals[2]-yvals[1])*point.y()
                    uncertainty_down = (yvals[1]-yvals[0])*point.y()                
                    point.setYErrs(uncertainty_down, uncertainty_up)

                    counter=counter+3

                ao.setTitle(prediction.short_description)
                anaObjects.append(ao)

    if prediction.id=="A":
        yoda.write(anaObjects, analysis.name+"-Theory.yoda")
    else:
        yoda.write(anaObjects,"{}-Theory_{}.yoda".format(analysis.name,prediction.id))


def do_ATLAS_2024_I2809112(analysis,prediction): #takes in arbitrary nr of theory predictions
    '''
    Reads arbitrary nr of SM predictions and computes the error. 
    '''
    
    anaObjects = []
   # yoda_name = analysis.name+".yoda"

    rawdir = os.path.join(cfg.input_dir,analysis.name)
            
    #ttbar to lepton and bjets (DB)
    histo_list = ['d101-x01-y01','d129-x01-y01','d131-x01-y01','d72-x01-y01','d76-x01-y01','d78-x01-y01','d80-x01-y01',
                   'd88-x01-y01','d90-x01-y01','d95-x01-y01','d98-x01-y01','d128-x01-y01','d130-x01-y01',
                   'd74-x01-y01','d77-x01-y01','d79-x01-y01','d81-x01-y01','d89-x01-y01','d91-x01-y01','d97-x01-y01','d99-x01-y01']

    f = contur.util.utils.find_ref_file(analysis)
    aos = yoda.read(f)
    for path, ao in aos.items():
        ao = mkConturFriendlyScatter(ao, mkthy=True)
        for histo in histo_list:
            if histo in path:
                if prediction.id=='A': #Sherpa predictions
                    x, y = read_csv(rawdir,histo+"_A.csv")
                    
                if prediction.id=='B': #Powheg+Pythia/Powheg+Herwig predictions
                    x, y = read_csv(rawdir, histo+'_B.csv')

                ao.rmAnnotation("ErrorBreakdown")
                ao.setPath("/THY/"+analysis.name+"/"+histo)
                
                # get rid of some of the spurious precision
                x = list(np.around(np.array(x),4))
                y = list(np.around(np.array(y),4))
                
                values = defaultdict(list)

                for xval, yval in zip(x, y):
                    values[xval].append(yval)

                   # sort by x to match YODA bin order
                sorted_xvals = sorted(values.keys())
                   
                nBins = len(ao.points()) #nr of predictions per measurement
                if len(sorted_xvals) != nBins:
                    cfg.contur_log.error("Mismatched number of points in {}, {} vs {}".format(path, nBins, len(sorted_xvals)))
                    continue
                    
                    
                test_vals = []
                #calculate average theory prediction and errors
                for i, point in enumerate(ao.points()):
                    xval = sorted_xvals[i]
                    yvals = values[xval]

                    if not yvals:
                        cfg.contur_log.warning(f"No y-values found for x = {xval}")
                        continue
                  
                    y_avg = np.mean(yvals)
                    y_error = (max(yvals) - min(yvals))/2

                    point.setY(point.y() * y_avg)
                    point.setYErrs(y_error * point.y(),y_error * point.y())

                ao.setTitle(prediction.short_description)
                anaObjects.append(ao)

    if prediction.id=="A":
        yoda.write(anaObjects, analysis.name+"-Theory_Powheg.yoda")

    if prediction.id=="B":
        yoda.write(anaObjects, analysis.name+"-Theory_Sherpa.yoda")
   


def do_ATLAS_2019_I1718132(prediction,mode_flag):
    '''
    ATLAS dilepton–dijet events in proton–proton collisions at COM energy of 13TeV.
    3 modes: electron-electron, muon-muon and electron-muon
    '''

    mode_analysis = [":LMODE=ELEL", ":LMODE=MUMU", ":LMODE=ELMU"]

    a_name = "ATLAS_2019_I1718132" + mode_analysis[mode_flag-1]

    anaObjects = []

    # get the analysis
    analysis = cdb.get_analyses(analysisid=a_name,filter=False)[0]

    # get the REF analysis objects.
    f = contur.util.utils.find_ref_file(analysis)
    aos = yoda.read(f)

    rawdir = os.path.join(cfg.input_dir,analysis.name)

    # output file
    f_out = prediction.file_name

    for path, orig_ao in aos.items():
        ao = mkConturFriendlyScatter(orig_ao,mkthy=True)
        histo = ao.name()
        #print(histo)

        # MG is for all, B
        # Powheg is for EM, C
        # Sherpa is for EE, MM and is D
        # should be either a C or a D
        readB = False
        readC = False
        readD = False

        try:
            xB, yB = read_csv(rawdir,"{}_B.csv".format(histo))
            readB = True
        except FileNotFoundError:
            # not all files are in the directories for ELEL, MUMU and ELMU, so this could be ok
            continue

        try:
            xX, yX = read_csv(rawdir,"{}_C.csv".format(histo))
            readC = True
        except FileNotFoundError:
            xX, yX = read_csv(rawdir,"{}_D.csv".format(histo))
            readD = True

        if readB and (readC or readD):
            cfg.contur_log.debug("Valid input found for {}, {}".format(histo,analysis.name))
        else:
            continue

        y_mid = []

        if not len(xX) == len(xB):
            cfg.contur_log.error("Mismatched number of points between SM predictions for {}, {} vs {}".format(path,len(xB),len(xX)))
            continue

        for i in range(len(xB)):
            # generating new central data points using the mean of the two theories
            # at i = 0, the column headings are x and y, so we start at i+1
            y_data = (yB[i] + yX[i])/2
            y_mid.append(y_data)

        ao.rmAnnotation("ErrorBreakdown")
        ao.setPath("/THY/"+analysis.name+"/"+histo)

        # check we have the right number of points
        nBins = len(ao.points())
        if not nBins == len(xX):
            cfg.contur_log.error("Mismatched number of points in {}, {} vs {}".format(path,nBins,len(xX)))
            continue


        counter=0
        for point in ao.points():

            # for each x value we have an upper, central and lower value. Get them and order them.
            yvals = sorted([yB[counter],y_mid[counter],yX[counter]])

            # central value
            point.setY(point.y()*yvals[1])

            # uncertainty
            uncertainty_up   = (yvals[2]-yvals[1])*point.y()
            uncertainty_down = (yvals[1]-yvals[0])*point.y()                
            point.setYErrs(uncertainty_down, uncertainty_up)

            counter=counter+1

        cfg.contur_log.info("Creating SM for {}, {}".format(histo,analysis.name))
        ao.setTitle(prediction.short_description)
        anaObjects.append(ao)

    # there are two analyses used to generate the centre points, B and T
    yoda.write(anaObjects, analysis.name+"-Theory.yoda")
        
def do_ATLAS_2022_I2037744(prediction):
    a_name = "ATLAS_2022_I2037744" 
    anaObjects = []    
    yoda_name = a_name + "-Theory.yoda"

    rawdir = os.path.join(cfg.input_dir,a_name)

    aos = yoda.read(rawdir + "/" + yoda_name)
    f_out = prediction.file_name
  
    for path, ao in aos.items():
        histo = ao.name()
        csv_data = []
        cfg.contur_log.debug(rawdir + "/{}.csv".format(histo))

        #Reading csv files
        with open(rawdir + "/{}.csv".format(histo), 'r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)
            for row in csv_reader:
                csv_data.append(row[1:])
        #cfg.contur_log.info(csv_data)
        
        #Finding the max distance dn and up from central values PWG+Py8
        data_arr = np.array(csv_data, dtype=float)
        diff = np.transpose(data_arr[1:] - data_arr[0])
        downErr = np.min(np.where(diff < 0, diff, 1), axis=1)
        upErr = np.max(np.where(diff > 0, diff, -1), axis=1)

        #When all predictions are above/below the PWG+Py8 and giving 0 up or down error: set up error = down error
        downErr[downErr == 1] = 0
        upErr[upErr == -1] = 0
        up_indices, down_indices = np.where(upErr == 0)[0], np.where(downErr == 0)[0]
        upErr[up_indices] = downErr[up_indices] * -1
        downErr[down_indices] = upErr[down_indices] * -1

        upErr.tolist()
        downErr.tolist()

        ao.rmAnnotation("ErrorBreakdown")
        ao.setPath("/THY/"+a_name+"/"+histo)

        #Writing uncertainties to Yoda files
        counter = 0
        for point in ao.points():
            #print(point)
            #print(upErr[counter]*point.y(), downErr[counter]*point.y())
            point.setYErrs(downErr[counter]*point.y()*-1, upErr[counter]*point.y())
            counter = counter + 1 
        
        ao.setTitle(prediction.short_description)            
        anaObjects.append(ao)
    yoda.write(anaObjects, a_name+"-Theory.yoda")

def do_ATLAS_2024_I2768921(prediction,analysis,scale_errors=2.0):
    """
    Two theory predictions in Hepdata, but no uncertainties.
    Estimate uncertainty as +- difference between the two predictions
    """

    # to output
    file_name = prediction.a_name+"-Theory"+'_'+prediction.id+".yoda"
    anaObjects = []

    compare_axis = 'y02' if prediction.axis == 'y03' else 'y03'

    f = contur.util.utils.find_ref_file(analysis)
    aos = yoda.read(f)
    # filter to the histos that match the pattern, keeping only the two relevant axes
    filtered_aos = {d: {} for d in prediction.pattern.split(',')}
    for short_path, ao in aos.items():
        d, x, y = ao.name().split('-')
        
        if not d in prediction.pattern:
            continue

        if y in [prediction.axis, compare_axis]:
            filtered_aos[d][y] = ao

    for d, aos in filtered_aos.items():
        central_ao = mkConturFriendlyScatter(aos[prediction.axis],mkthy=True)
        compare_ao = mkConturFriendlyScatter(aos[compare_axis],mkthy=True) 

        for central_point, compare_point in zip(central_ao.points(), compare_ao.points()):
            difference = abs(compare_point.y() - central_point.y())
            central_point.setYErrs(difference*scale_errors, difference*scale_errors)

        central_ao.setTitle(prediction.short_description)
        central_ao.setPath("/THY/"+analysis.name+"/"+d+'-x01-y01')

        anaObjects.append(central_ao)

    yoda.write(anaObjects, file_name)


def do_ATLAS_2024_I2765017(prediction,analysis,output_aos,got_pred):
    """
    Special fix for rmiss
    """
    # from the installed ref data 
    cfg.contur_log.info("Making SM theory for {}, RMISS prediction {}".format(analysis.name,prediction.id))
    import re

    # define the theory paths used to calculate rmiss
    aux_bits = {"cr1ie_", "cr1im_", "cr2ie_", "cr2im_"}
    obs_names   = {"met_mono", "met_vbf", "mjj_vbf", "dphijj_vbf"}


    thy_paths={}
    for obs in obs_names:
        for auxil in aux_bits:
            rmiss_name = "rmiss_"+auxil+obs             
            numer =  "/REF/"+analysis.shortname+"/"+"sr0l_"+obs             
            denom =  "/REF/"+analysis.shortname+"/"+"sr0l_"+auxil+"0v_"+obs
            thy_paths[rmiss_name]=(numer,denom)
                   
                   
    f = contur.util.utils.find_ref_file(analysis)
    aos = yoda.read(f)

#    print(aos)
    
    for short_path, ao in aos.items():        
        opt_path = "/"+analysis.name+"/"+ao.name()
        if opt_path in got_pred[prediction.id]:
            continue
        pool = cdb.get_pool(path=opt_path)
        if pool is not None:

            if re.search(prediction.pattern, opt_path) and cdb.validHisto(opt_path,filter=False):

                cfg.contur_log.debug("Found a prediction for {}. Axis is {}.".format(opt_path,prediction.axis))
                # get the appropriate theory axis for this plot 

                numer, denom = thy_paths[ao.name()]
                
                try:
                    numer_ao = aos[numer+prediction.axis]
                    denom_ao = aos[denom+prediction.axis]
                    cfg.contur_log.debug("FOUND! {}".format(ao.name()))

                except:
                    cfg.contur_log.debug("not found {}".format(thypath))
                    continue

                got_pred[prediction.id].append(opt_path)


                #print("dividing",numer_ao.path()," by ",denom_ao.path())
                if "_mjj_vbf" in ao.name():

                    thy_ao = None
                    if numer_ao.numBins() != denom_ao.numBins():
                        try:
                            numer_ao.rebinXTo(denom_ao.xEdges()) 
                        except Exception as e:
                            print(e)
                            thy_ao = aos["/REF/"+analysis.shortname+"/"+ao.name()+prediction.axis]

                    rmiss = aos["/REF/"+analysis.shortname+"/"+ao.name()+prediction.axis]        
                    if thy_ao is None:
                        thy_ao = numer_ao/denom_ao
                        idx=1
                        for bin in thy_ao.bins():
                            for source in bin.sources():
                                if source in rmiss.bin(idx).sources():
                                    bin.setErr(rmiss.bin(idx).err(source),source)
                            idx=idx+1
                            
                else:
                    thy_ao = aos["/REF/"+analysis.shortname+"/"+ao.name()+prediction.axis]
                        
                thy_ao.setPath("/THY"+opt_path)

                thy_ao = mkConturFriendlyScatter(thy_ao,mkthy=True)

                thy_ao.setTitle(prediction.short_description)
                output_aos[prediction.file_name].append(thy_ao)



def do_ATLAS_2024_I2765017_photon(prediction,analysis):
    """
    Read Jeppe's yoda file.
    """

    import re
    import rivet
    from rivet.aopaths import AOPath

    # file to output
    file_name = prediction.a_name+"-Theory"+'_'+prediction.id+".yoda"
    anaObjects = []

    # input file.
    relpath = "data/TheoryRaw/{}/HEJ-NLL-NLO-EWKNLO-Enveloped.yoda".format(prediction.a_name)
    f = cfg.paths.data_path(relpath)
    aos = yoda.read(f)

    # match the relevant histo
    filtered_aos = {d: {} for d in prediction.pattern.split(',')}
    for short_path, ao in aos.items():

        if rivet.isRawAO(ao): continue

        if len(rivet.extractWeightName(ao.path())) > 0: continue

        #print(ao.name(),short_path)

        if re.search(prediction.pattern, short_path):

            ao.setTitle(prediction.short_description)

            aop = AOPath(ao.path())
            h_name = AOPath.basename(aop)

            pathname = "/THY/"+ prediction.a_name + "/" +h_name 
            print(pathname)
            ao.setPath(pathname)

            if prediction.id == "C":
                ao.scale(1,0.683)

            anaObjects.append(ao)
            print("ADDED ",pathname)

    yoda.write(anaObjects, file_name)

def do_CMS_2020_I1814328(prediction,analysis):
    """
    CMS WW which had theory errors on the data
    """

    print("Called do_CMS_2020_I1814328")

    # list the histogram names we want to read here.
    histo_list = ['d02-x01-y01','d04-x01-y01','d05-x01-y01','d06-x01-y01','d07-x01-y01']

    read_from_csv_files(analysis,histo_list,prediction,err_in_aux=True)    

