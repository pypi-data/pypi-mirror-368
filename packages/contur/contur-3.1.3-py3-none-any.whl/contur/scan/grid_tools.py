import os
import sys
import shutil
import subprocess

import contur
import rivet
import yoda
import contur.run.run_batch_submit
import contur.config.config as cfg
import contur.data.static_db as cdb
import contur.util.file_readers as cfr
import contur.util.utils as cutil
import contur.scan.os_functions

def grid_loop(extract=False,clean=True,unmerge=False,archive=False,check=False,check_all=False,resub=False,queue=""):
    """
    General purpose function for looking through all the files below scan_path and performing various operations.
    Unless told otherwise (by setting ``unmerge=True``) it will always merge any unmerged yodas and zip the result.

    the top directory to start from is taken from config.grid

    :arg extract: extract analyses with names in the strong config.onlyAnalyses into new directory

    :arg clean: remove unnecessary files

    :arg unmerge: remove the merged yoda files and decompress the raw yoda files

    :arg archive: if true, remove unnecessary files (unless told not to) and compress the rest

    :arg check: look for batch jobs that ran and failed

    :arg check_all: look for batch jobs that either ran and failed, or were never run

    :arg resub: resubmit any jobs identified by check ot check_all

    :arg queue: queue to resubmit them to

    :return: return a list of all the directories containing valid yoda files.

    """

    valid_yoda_dirs = []

    scan_path = cfg.grid
    
    if not os.path.isdir(scan_path):
        raise cfg.ConturError("grid_loop expected a directory containing a contur grid. Got {}. Terminating.".format(scan_path))

    if archive:
        cfg.contur_log.info("Archiving this grid")
        extract=False
        unmerge=False

    if clean:
        cfg.contur_log.info("Removing unnecessary files from {}.".format(scan_path))

    if unmerge:
        cfg.contur_log.info("If unmerged yodas exist, unzipping them, and removing merged yodas.")
    
    if extract:
        new_dir = scan_path+"_new"
        cutil.mkoutdir(new_dir)
        cfg.contur_log.info("Extracting selected analyses to {}".format(new_dir))

    if check or check_all or resub:
        cfg.contur_log.info("Checking directory tree")
        if check_all:
            cfg.contur_log.info("Also counting jobs without batch logs as failed")
        if resub:
            cfg.contur_log.info("Resubmitting failed jobs")

    for root, dirs, files in sorted(os.walk(scan_path)):

        if hide_directory(root):
            continue
            
        run_point_num = os.path.basename(root)
        
        got_valid_yoda = False
        got_batch_logs = False
        batch_script = False

        # removing unnecessary files
        if clean:
            contur.scan.os_functions.delete_files(root)

        got_merged_yoda_file = False
        merged_yoda_file = os.path.join(root, cfg.tag +"_" + run_point_num + '.yoda')
        merged_yoda_file_gz = merged_yoda_file+'.gz'
        if not unmerge:
            # gzipping merged yoda file if unzipped file exists
            if os.path.exists(merged_yoda_file):
                if os.path.exists(merged_yoda_file_gz):
                    os.remove(merged_yoda_file_gz)
                command = 'gzip {}'.format(merged_yoda_file)
                cfg.contur_log.debug(command)
                os.system(command)

            elif not os.path.exists(merged_yoda_file_gz):
                # the merged yoda is not there in either gzipped or unzipped form
                # try making it.
                merged_yoda_file_gz = merge_yodas(root,files,len(dirs)>0)


        got_merged_yoda_file = os.path.exists(merged_yoda_file_gz)



        if got_merged_yoda_file:
            param_file_path = os.path.join(root, cfg.paramfile)
            params = cfr.read_param_point(param_file_path)
            cfg.contur_log.debug('\nFound valid yoda file ' + merged_yoda_file_gz.strip('./'))
            sample_str = 'Sampled at:'
            for param, val in params.items():
                sample_str += ('\n'+param + ': ' + str(val))
                cfg.contur_log.debug(sample_str)

            if extract:
                # Here we are pulling out the histograms for a specific analysis
                # make the new directory if needed
                new_one = os.path.join(new_dir,root[len(scan_path)+1:])
                if not os.path.exists(new_one):
                    os.makedirs(new_one)
                # copy over the param file.
                shutil.copy(param_file_path,new_one)
                # do the extraction
                aos = yoda.read(merged_yoda_file_gz)
                for analysis in cdb.get_analyses():
                    if cutil.analysis_select(analysis.name):
                        aos_new = []
                        for path, ao in aos.items():
                            if not rivet.isRawPath(path) and analysis.name in path:
                                aos_new.append(ao)
                        yoda.write(aos_new, os.path.join(new_one, analysis.name+".yoda"))

        if unmerge or archive or check or check_all or resub:
            # for all these options we need to interrogate the file system

            # get {generator}-*.yoda(.gz) files
            file_list = []
            file_list_gz = []
            for name in files:

                if is_unmerged_yoda(name):
                    file_list.append(os.path.join(root, name))
                if is_unmerged_yoda_gz(name):
                    file_list_gz.append(os.path.join(root, name))

                if name.startswith(cfg.tag+"_"+run_point_num+".sh.e"):
                    got_batch_logs = True
                if name==cfg.tag+"_"+run_point_num+".sh":
                    batch_script = name

            if file_list_gz and unmerge:

                # decompress {generator}-*.yoda.gz files if necessary and remove any merged ones
                command = ' '.join(['gzip -d']+file_list_gz)
                cfg.contur_log.debug(command)
                os.system(command)
                # remove any merged files
                if os.path.exists(merged_yoda_file):
                    # remove merged file
                    os.remove(merged_yoda_file)
                if os.path.exists(merged_yoda_file_gz):
                    # remove merged file
                    os.remove(merged_yoda_file_gz)

            if archive:
                if got_merged_yoda_file:

                    # also removing the pre-merged yodas.
                    if file_list_gz:
                        for yfile_gz in file_list_gz:
                            os.remove(yfile_gz)
                    if file_list:
                        for yfile in file_list:
                            os.remove(yfile)

                # compress everything that isn't compressed, except the params.dat file
                for fname in files:
                    if not fname.endswith('.gz') and not fname==cfg.paramfile:
                        # (need to check they weren't already deleted or zipped.)
                        name = os.path.join(root,fname)
                        if os.path.isfile(name) and not os.path.islink(name):
                            command = 'gzip {}'.format(name)
                            cfg.contur_log.debug(command)
                            os.system(command)

            got_valid_yoda = file_list_gz or file_list or got_merged_yoda_file
            if got_valid_yoda:
                valid_yoda_dirs.append(root)

            if (check or check_all or resub) and not got_valid_yoda:
                # if there are batch job outputs, this is a failed job
                # otherwise it might still be running; if check_all is set, assume it failed to submit
                if got_batch_logs or (check_all and batch_script):
                    cfg.contur_log.warn("Found a failed job: {}".format(root))
                    if resub and batch_script and not cfg.using_condor:
                        # if there is a script and the flag is setup, resubmit
                        with contur.scan.os_functions.WorkingDirectory(root):
                            cfg.contur_log.info("Resubmitting {}".format(batch_script))
                            qsub = contur.run.run_batch_submit.gen_submit_command(queue)

                            subprocess.call([qsub + " " +batch_script],
                                            shell=True)
    return valid_yoda_dirs

def hide_directory(dirname):
    """
    return true or false depending on if the input directory name is in 
    the list of directories that should be hidden/ignored when looking 
    for yoda files.
    """
    for hdir in cfg.hidden_directories:
        if hdir in dirname:
            return True

    return False

def merge_yodas(root,files,has_subdir):
    """
    make a zipped, merged yoda file from any unmerged ones in the file list

    :param root: absolute path to the directory the files are in

    :param files: list of filenames to check for merging.

    """

    file_list = []
    file_list_to_zip = []  # separate list to prevent zipping already zipped files again
    run_point_num = os.path.basename(root)
    out_file = os.path.join(root, cfg.tag +"_"+ run_point_num + '.yoda')
    out_file_gz = out_file+'.gz'

    for name in files:
        
        if is_unmerged_yoda(name) or is_unmerged_yoda_gz(name):

            yodafile = os.path.join(root, name)
            file_list.append(yodafile)
            if name.endswith('.yoda'):
                file_list_to_zip.append(yodafile)
            
    if file_list:
        file_string = ' '.join(file_list)
        if len(file_list) > 1:
            command = ' '.join(['yodamerge -o', out_file, file_string])
        else:
            command = ' '.join(['cp', file_string, out_file])
        cfg.contur_log.debug(command)
        os.system(command)

        command = ' '.join(['gzip -f', out_file]+file_list_to_zip)
        cfg.contur_log.debug(command)
        os.system(command)

    elif not has_subdir:
        cfg.contur_log.warning('NO YODA FILES FOUND IN DIRECTORY {} '.format(root))

    return out_file_gz

def is_unmerged_yoda(filename):
    """ 
    return true if the the file name is consistent with being a raw (ie unmerged)
    yoda file output from a job
    """
    return (filename.endswith('yoda') and not filename.startswith(cfg.tag))
            
def is_unmerged_yoda_gz(filename):
    """ 
    return true if the the file name is consistent with being a gzipped raw (ie unmerged)
    yoda file output from a job
    """
    return (filename.endswith('yoda.gz') and not filename.startswith(cfg.tag))

def is_valid_yoda_filename(filename):
    """ 
    return true if the the file name is consistent with being a merged
    yoda file 
    """
    valid = ((filename.endswith('.yoda') or filename.endswith('.yoda.gz'))
             and filename.startswith(cfg.tag))
    return valid

def find_param_point(grid_name,tag,paramList,verbose=False):
    """
    Given a list of parameters and values, find the appropriate yoda file in a tree and return it.
    If no params given, just return the existing list
    """

    
    if len(paramList)==0:
        return grid_name

    params = {}
    testValues = {}
    fileNames = {}

    # parse the parameter list
    # turn the values into floats if possible
    if type(paramList) == list:
        for pair in paramList:
            temp = pair.split('=')
            try:
                params[temp[0]]=float(temp[1])
            except ValueError:
                params[temp[0]]=temp[1]
            testValues[temp[0]]=None
            fileNames[temp[0]]=[]

    # type(parameterList) == dict
    else:
        for key in paramList.keys():
            testValues[key] = None
            fileNames[key] = []
        params=paramList

    cfg.contur_log.debug('Looking for the closest match to these parameter values: {}'.format(params))

    # scan directory tree(s) looking in the param.dat files for closest values.
    cfg.contur_log.debug('Looking in {}'.format(grid_name))
    for root, dirs, files in sorted(os.walk(grid_name)):
        for file_name in files:
            if file_name == cfg.paramfile:
                param_dict = cfr.read_param_point(os.path.join(root,file_name))
                run_point_num = os.path.basename(root)
                yoda_file = os.path.join(root, tag + "_" + run_point_num + '.yoda.gz')
                if not os.path.exists(yoda_file):
                    yoda_file = os.path.join(root, tag + "_" + run_point_num + '.yoda')
                    if not os.path.exists(yoda_file):
                        cfg.contur_log.warn("No yoda file found in "+root)

                for key in params.keys():
                    if key in param_dict.keys():
                        value = param_dict[key]
                        if type(params[key]) is float:
                            # float comparisons
                            try:
                                value = float(value)
                                testValue = abs(value-params[key])
                                # Add the yoda files for nearest values to file list.
                                if testValues[key] is None or testValue < testValues[key]:
                                    testValues[key] = testValue
                                    fileNames[key] = [yoda_file]
                                elif testValue == testValues[key]:
                                    fileNames[key].append(yoda_file)
                            except ValueError:
                                cfg.contur_log.warn("Cannot compare {} and {}".format(value,params[key]))
                        else:
                            # string comparisons
                            if value==params[key]:
                                # Add the yoda file which matches to file list.
                                if testValues[key] is None:
                                    testValues[key] = value
                                    fileNames[key] = [yoda_file]
                                else:
                                    fileNames[key].append(yoda_file)

                    else:
                        cfg.contur_log.error("Parameter {} is not present in this grid file".format(key))
                        cfg.contur_log.error("Known parameters are: {}".format(param_dict.keys()))
                        sys.exit(1)


    # now look for a yoda file which is in the "closest" list for all parameters.
    newList = []
    testP = next(iter(params))
    for fileN in fileNames[testP]:
        inAll = True
        for names in fileNames.values():
            if fileN not in names:
                inAll = False

        if inAll:
            newList.append(fileN)

    if verbose:
        cfg.contur_log.info('These files have been identified as the nearest match: {}'.format(newList))
    return newList
