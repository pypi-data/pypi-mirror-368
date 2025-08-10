import sqlite3 as db
import contur
import contur.config.config as cfg
import contur.scan.grid_tools as cgt
from contur.scan.os_functions import read_param_steering_file
import os
import re

if cfg.use_mysql:
    try:
        import pymysql
    except ImportError:
        cfg.contur_log.error("Failed to import pymysql package.")
        raise cfg.ConturError("Failed to import pymysql package when enable use-mysql.")

INIT_MDB  = False
INIT_DADB = False
GENERATE_MODEL_DATA = False
EXCLUSION_THRESHOLD = 0.2


def init_mdb():
    """
    Initialise the model database
    """
    
    try:
        conn = db.connect(cfg.models_dbfile)
    except db.OperationalError:
        cfg.contur_log.error("Failed to open result DB file: {}".format(cfg.models_dbfile))
        raise
                
    c = conn.cursor()

    _create_model_and_parameter_tables(c)
    _create_model_and_parameter_indexes(c)
        
    conn.commit()
    conn.close()

    global INIT_MBD
    INIT_MDB = True

    return

def open_for_reading(file):

    if not os.path.isfile(file):
        raise cfg.ConturError("Tried to read points from {}, which does not exist.".format(file))
    try:
        conn = db.connect(file)
    except db.OperationalError:
        cfg.contur_log.error("Failed to open result DB file: {}".format(cfg.results_dbfile))
        raise

    return conn
    
def init_dadb():
    """
    initialise the local results database
    """

    try:
        conn = db.connect(cfg.results_dbfile)
    except db.OperationalError:
        cfg.contur_log.error("Failed to open result DB file: {}".format(cfg.results_dbfile))
        raise
        
        
    c = conn.cursor()

    _create_model_and_parameter_tables(c)
    
    c.execute('''create table if not exists model_point
                   (id integer primary key AUTOINCREMENT,
                   model_id  integer     not null,
                   yoda_files text,
                   run_point text,
                   foreign key(model_id) references model(id) on delete cascade on update cascade);''')

    # parameter_value with the same model_point_id is in the same parameter_point
    c.execute('''create table if not exists parameter_value
                   (id integer primary key AUTOINCREMENT,
                   model_point_id  integer     not null,
                   parameter_id  integer,
                   name varchar(255) not null,
                   value  double    not null,
                   foreign key(model_point_id) references model_point(id) on delete cascade on update cascade,
                   foreign key(parameter_id) references parameter(id) on delete cascade on update cascade);''')

    # run contur command multiple times, then we'll have multiple heatmap data
    c.execute('''create table if not exists map
                    (id integer primary key AUTOINCREMENT,
                    name varchar(255));''')
    
    # record scan modes used for each parameter (for slice plotting)
    c.execute('''create table if not exists scan_mode
                   (id integer primary key AUTOINCREMENT,
                   model_id  integer     not null,
                   map_id integer not null,
                   parameter_id integer,
                   parameter_name varchar(255), 
                   mode varchar(255),
                   foreign key(model_id) references model(id) on delete cascade on update cascade,
                   foreign key(map_id) references map(id) on delete cascade on update cascade,
                   foreign key(parameter_id) references parameter(id) on delete cascade on update cascade);''')

    # different run with different model_point will produce different exclusion results
    c.execute('''create table if not exists run
               (id integer primary key AUTOINCREMENT,
               map_id integer     not null,
               model_point_id  integer  not null,
               events_num   integer  not null,
               stat_type varchar(255) not null,
               combined_exclusion double not null,
               mu_lower_limit double,
               mu_upper_limit double,
               mu_hat double,
               addition_argument varchar(255),
               foreign key(model_point_id) references model_point(id) on delete cascade on update cascade,
               foreign key(map_id) references map(id) on delete cascade on update cascade);''')

    # store the intermediate result to recalculate the exclusion if a pool name is omiited
    c.execute('''create table if not exists intermediate_result
                (id integer primary key AUTOINCREMENT,
                run_id  integer     not null,
                pool_name  varchar(255)   not null,
                stat_type varchar(255) not null,
                ts_b double not null,
                ts_s_b double not null,
                foreign key(run_id) references run(id) on delete cascade on update cascade);''')


    c.execute('''create table if not exists exclusions
                   (id integer primary key AUTOINCREMENT,
                   run_id  integer     not null,
                   pool_name  varchar(255)   not null,
                   stat_type varchar(255) not null,
                   exclusion  double not null,
                   mu_lower_limit double,
                   mu_upper_limit double,
                   mu_hat double,
                   histos  text not null,
                   foreign key(run_id) references run(id) on delete cascade on update cascade);''')

    c.execute('''create table if not exists obs_exclusions
                   (id integer primary key AUTOINCREMENT,
                   run_id  integer     not null,
                   stat_type varchar(255) not null,
                   exclusion  double,
                   ts_s_b double,
                   ts_b double,
                   mu_lower_limit double,
                   mu_upper_limit double,
                   mu_hat double,
                   histo  text not null,
                   foreign key(run_id) references run(id) on delete cascade on update cascade);''')

    # create indexes for the tables
    _create_model_and_parameter_indexes(c)
    _create_additional_indexes(c)

    conn.commit()
    conn.close()

    global INIT_DABD
    INIT_DADB = True

def generate_model_and_parameter(model_db=False):
    """
    Create the model and parameter tables and populate them

    if model_db is True, they are written to the central model database, otherwise they are written to the local 
    results db (and the other tables will also be created, empty)

    """
    if model_db:
        if not INIT_MDB:
            init_mdb()
        conn = db.connect(cfg.models_dbfile)
    else:
        if not INIT_DADB:
            init_dadb()
        conn = db.connect(cfg.results_dbfile)

    c = conn.cursor()

    default_contur_url = "https://gitlab.com/hepcedar/contur/-/tree/master/data/Models"
    default_version = "0"

    croot = os.getenv("CONTUR_DATA_PATH")

    models_path = os.path.join(croot, "data", "Models")
    if models_path is None:
        raise Exception("CONTUR_DATA_PATH not defined")

    for root, dirs, files in sorted(os.walk(models_path)):
        # reach the bottom most directory
        if len(dirs) == 0:
            model_dir_name = os.path.basename(root)
            location = root[re.search("Models", root).end():]

            exist_log_file = False
            exist_source_file = False

            # first search for source.txt files
            for file in files:
                if file == "source.txt":
                    exist_source_file = True
                    with open(os.path.join(root, file), 'r') as f:
                        content = f.read()
                        name = re.findall(r"name=(.*)\n", content)[0]
                        if name != model_dir_name:
                            cfg.contur_log.warning(
                                "Model name in the source.txt should be the same as the model's directory name!")
                        version = re.findall(r"version=(.*)\n", content)[0] if re.findall(r"version=(.*)\n",
                                                                                          content) else "0"
                        url = re.findall(r"url=(.*)\n", content)[0] if re.findall(r"url=(.*)\n", content) else None
                        contur_url = re.findall(r"contur_url=(.*)\n", content)[0] if re.findall(r"contur_url=(.*)\n",
                                                                                                content) else None
                        author = re.findall(r"author=(.*)\n", content)[0] if re.findall(r"author=(.*)\n",
                                                                                        content) else None
                        reference = re.findall(r"reference=(.*)\n", content)[0] if re.findall(r"reference=(.*)\n",
                                                                                              content) else None
                        if contur_url is not None:
                            contur_web_url = contur_url[:re.search("/data/Models", contur_url).end()]
                            location = contur_url[re.search("/data/Models", contur_url).end():]

                    c.execute("insert into  model (id,name,version,author,original_source,contur_url,location,reference) \
                                              values (?,?,?,?,?,?,?,?);",
                              (None, name, version, author, url, contur_web_url, location, reference))
                    break

            # source.txt file not exists, search for log file
            if not exist_source_file:
                for file in files:
                    # store model data if log file exists
                    if file.endswith(".log") and model_dir_name in file:
                        exist_log_file = True
                        with open(os.path.join(root, file), 'r') as f:
                            content = f.read()
                            version = re.findall(r"\d+\.(?:\d+\.)*\d+", content)[0]
                        c.execute("insert into  model (id,name,version,contur_url,location) \
                          values (?,?,?,?,?);", (None, model_dir_name, version, default_contur_url, location))
                        break

            if not exist_log_file and not exist_source_file:
                c.execute("insert into  model (id,name,version,contur_url,location) \
                    values (?,?,?,?,?);", (None, model_dir_name, default_version, default_contur_url, location))

            model_id = c.execute("select id from model order by id desc").fetchone()[0]

            # after store model data, search for parameter data
            for file in files:
                # store parameter data
                if file == "parameters.py":
                    with open(os.path.join(root, file), 'r') as f:
                        parameters = f.read().split("Parameter")[2:]
                        for parameter in parameters:
                            parameter_name = re.findall(r"name = \'(\w+)*\'", parameter)[0]
                            parameter_type = re.findall(r"type = \'(\w+)*\'", parameter)[0]
                            parameter_value = re.findall(r"value = \'?([^\',]+)\'?", parameter)[0]
                            parameter_texname = re.findall(r"texname = \'?([^\']+)\'?", parameter)[0]

                            c.execute("insert into  parameter (id,model_id,name,texname,type,value) \
                                values (?,?,?,?,?,?);", (
                                None, model_id, parameter_name, parameter_texname, parameter_type, parameter_value))
    conn.commit()
    conn.close()

    global GENERATE_MODEL_DATA
    GENERATE_MODEL_DATA = True


def generate_mysql_model_db():
    """
    Create a MySQL database schema named 'model_db' and populate it with model and parameter data.
    This method mirrors the functionality of generate_model_and_parameter but uses MySQL instead of SQLite.
    """

    # MySQL connection parameters from environment variables
    mysql_host = cfg.mysql_host
    mysql_port = cfg.mysql_port
    mysql_user = cfg.mysql_user
    mysql_password = cfg.mysql_passwd

    # Validate required environment variables
    if not mysql_host:
        raise Exception("MySQL host is not configured in config")
    if not mysql_port:
        raise Exception("MySQL port is not configured in config")
    if not mysql_user:
        raise Exception("MySQL user is not configured in config")
    if not mysql_password:
        raise Exception("MySQL passwd is not configured in config")

    try:
        # Connect to MySQL server
        connection = pymysql.connect(
            host=mysql_host,
            port=mysql_port,
            user=mysql_user,
            password=mysql_password,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

        with connection.cursor() as cursor:
            # Create the model_db schema if it doesn't exist
            cursor.execute("CREATE DATABASE IF NOT EXISTS model_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            cursor.execute("USE model_db")

            # Create model table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS model (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    version VARCHAR(255) NOT NULL,
                    author VARCHAR(255),
                    original_source VARCHAR(255),
                    contur_url VARCHAR(255),
                    location VARCHAR(255),
                    reference VARCHAR(255),
                    INDEX idx_model_name_version (name, version)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            ''')

            # Create parameter table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS parameter (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    model_id INT NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    texname VARCHAR(255) NOT NULL,
                    type VARCHAR(50) NOT NULL,
                    value TEXT NOT NULL,
                    FOREIGN KEY (model_id) REFERENCES model(id) ON DELETE CASCADE ON UPDATE CASCADE,
                    INDEX idx_parameter_model_id_name (model_id, name)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            ''')

            # Clear existing data (optional - remove if you want to keep existing data)
            cursor.execute("DELETE FROM parameter")
            cursor.execute("DELETE FROM model")

            # Default values
            default_contur_url = "https://gitlab.com/hepcedar/contur/-/tree/master/data/Models"
            default_version = "0"

            croot = os.getenv("CONTUR_DATA_PATH")
            if croot is None:
                raise Exception("CONTUR_DATA_PATH not defined")

            models_path = os.path.join(croot, "data", "Models")

            # Walk through the models directory
            for root, dirs, files in sorted(os.walk(models_path)):
                # Process bottom-most directories only
                if len(dirs) == 0:
                    model_dir_name = os.path.basename(root)
                    location = root[re.search("Models", root).end():]

                    exist_log_file = False
                    exist_source_file = False

                    # Look for source.txt file first
                    for file in files:
                        if file == "source.txt":
                            exist_source_file = True
                            with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                                content = f.read()

                                # Extract information from source.txt
                                name_match = re.findall(r"name=(.*)\n", content)
                                name = name_match[0] if name_match else model_dir_name

                                if name != model_dir_name:
                                    cfg.contur_log.warning(
                                        "Model name in the source.txt should be the same as the model's directory name!")

                                version_match = re.findall(r"version=(.*)\n", content)
                                version = version_match[0] if version_match else "0"

                                url_match = re.findall(r"url=(.*)\n", content)
                                url = url_match[0] if url_match else None

                                contur_url_match = re.findall(r"contur_url=(.*)\n", content)
                                contur_url = contur_url_match[0] if contur_url_match else None

                                author_match = re.findall(r"author=(.*)\n", content)
                                author = author_match[0] if author_match else None

                                reference_match = re.findall(r"reference=(.*)\n", content)
                                reference = reference_match[0] if reference_match else None

                                if contur_url is not None:
                                    contur_web_url = contur_url[:re.search("/data/Models", contur_url).end()]
                                    location = contur_url[re.search("/data/Models", contur_url).end():]
                                else:
                                    contur_web_url = default_contur_url

                            cursor.execute('''
                                INSERT INTO model (name, version, author, original_source, contur_url, location, reference)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                            ''', (name, version, author, url, contur_web_url, location, reference))
                            break

                    # If source.txt doesn't exist, look for log file
                    if not exist_source_file:
                        for file in files:
                            if file.endswith(".log") and model_dir_name in file:
                                exist_log_file = True
                                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                                    content = f.read()
                                    version_match = re.findall(r"\d+\.(?:\d+\.)*\d+", content)
                                    version = version_match[0] if version_match else default_version

                                cursor.execute('''
                                    INSERT INTO model (name, version, contur_url, location)
                                    VALUES (%s, %s, %s, %s)
                                ''', (model_dir_name, version, default_contur_url, location))
                                break

                    # If neither source.txt nor log file exists
                    if not exist_log_file and not exist_source_file:
                        cursor.execute('''
                            INSERT INTO model (name, version, contur_url, location)
                            VALUES (%s, %s, %s, %s)
                        ''', (model_dir_name, default_version, default_contur_url, location))

                    # Get the last inserted model ID
                    cursor.execute("SELECT LAST_INSERT_ID()")
                    model_id = cursor.fetchone()['LAST_INSERT_ID()']

                    # Process parameters.py file
                    for file in files:
                        if file == "parameters.py":
                            with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                                content = f.read()
                                parameters = content.split("Parameter")[2:]  # Skip first two parts

                                for parameter in parameters:
                                    try:
                                        # Extract parameter information
                                        name_match = re.findall(r"name = \'(\w+)*\'", parameter)
                                        parameter_name = name_match[0] if name_match else None

                                        type_match = re.findall(r"type = \'(\w+)*\'", parameter)
                                        parameter_type = type_match[0] if type_match else None

                                        value_match = re.findall(r"value = \'?([^\',]+)\'?", parameter)
                                        parameter_value = value_match[0] if value_match else None

                                        texname_match = re.findall(r"texname = \'?([^\']+)\'?", parameter)
                                        parameter_texname = texname_match[0] if texname_match else None

                                        # Only insert if all required fields are found
                                        if all([parameter_name, parameter_type, parameter_value, parameter_texname]):
                                            cursor.execute('''
                                                INSERT INTO parameter (model_id, name, texname, type, value)
                                                VALUES (%s, %s, %s, %s, %s)
                                            ''', (model_id, parameter_name, parameter_texname, parameter_type,
                                                  parameter_value))
                                        else:
                                            cfg.contur_log.warning(f"Incomplete parameter data in {file}: {parameter}")

                                    except Exception as e:
                                        cfg.contur_log.error(f"Error processing parameter in {file}: {e}")
                                        continue
                            break

        # Commit all changes
        connection.commit()
        cfg.contur_log.info("Successfully created and populated MySQL model_db schema")

    except pymysql.Error as e:
        cfg.contur_log.error(f"MySQL error: {e}")
        raise
    except Exception as e:
        cfg.contur_log.error(f"Error in generate_mysql_model_db: {e}")
        raise
    finally:
        if 'connection' in locals():
            connection.close()


def get_model_version(dir):
    """
    for a model somewhere in the tree below dir, get its version
    """
    exist_log_file = False
    exist_source_file = False
    for root, _, files in sorted(os.walk(dir, topdown=False)):
        for file in files:
            if file == "source.txt":
                exist_source_file = True
                with open(os.path.join(root, file), 'r') as f:
                    content = f.read()
                    version = re.findall(r"version=(.*)\n", content)[0]

        if not exist_source_file:
            for file in files:
                if file.endswith(".log") and os.path.basename(dir) in file:
                    exist_log_file = True
                    with open(os.path.join(root, file), 'r') as f:
                        content = f.read()
                        version = re.findall(r"\d+\.(?:\d+\.)*\d+", content)[0]
        if not exist_source_file and not exist_log_file:
            version = "0"
    return version


def get_mysql_model_id(run_info_path):
    """
    Check the MySQL model database to see if the model in run_info_path is present.
    If so, return its id (-1 if not found).
    This is the MySQL version of get_model_id function.
    """
    mysql_host = cfg.mysql_host
    mysql_port = cfg.mysql_port
    mysql_user = cfg.mysql_user
    mysql_password = cfg.mysql_passwd

    # Validate required environment variables
    if not mysql_host:
        raise Exception("MySQL host is not configured in config")
    if not mysql_port:
        raise Exception("MySQL port is not configured in config")
    if not mysql_user:
        raise Exception("MySQL user is not configured in config")
    if not mysql_password:
        raise Exception("MySQL passwd is not configured in config")

    model_id = -1

    try:
        # Connect to MySQL server
        connection = pymysql.connect(
            host=mysql_host,
            port=mysql_port,
            user=mysql_user,
            password=mysql_password,
            database='model_db',  # Connect directly to model_db schema
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

        with connection.cursor() as cursor:
            # Walk through the run_info_path to find model directories
            for root, dirs, _ in sorted(os.walk(run_info_path)):
                for dir in dirs:
                    # Search for model's name and version
                    version = get_model_version(os.path.join(root, dir))

                    # Query MySQL database for matching model
                    cursor.execute(
                        "SELECT id FROM model WHERE name = %s AND version = %s",
                        (dir, version)
                    )
                    result = cursor.fetchone()

                    if result is not None:
                        model_id = result['id']
                        cfg.contur_log.info("Found matching model with ID {}".format(model_id))
                        break

                # Break outer loop if model found
                if model_id != -1:
                    break

        if model_id == -1:
            msg = "No match found in the MySQL Model database for the model in {}.\n".format(run_info_path)
            msg += "       If you want this to be added, copy the source files into the contur Models area and remake."
            cfg.contur_log.info(msg)

    except pymysql.Error as e:
        cfg.contur_log.error(f"MySQL error in get_mysql_model_id: {e}")
        raise cfg.ConturError(f"MySQL database error: {e}")
    except Exception as e:
        cfg.contur_log.error(f"Error in get_mysql_model_id: {e}")
        raise cfg.ConturError(f"Error accessing MySQL model database: {e}")
    finally:
        if 'connection' in locals():
            connection.close()

    return model_id


def get_model_id(run_info_path):
    """
    check the model database to see if the model in run_info_path is present.
    if so, return its id (-1 if not found).
    """

    conn = open_for_reading(cfg.models_dbfile)
    c = conn.cursor()

    model_id = -1
    for root, dirs, _ in sorted(os.walk(run_info_path)):
        for dir in dirs:
            # search for model's name and version
            version = get_model_version(os.path.join(root,dir))
            res = c.execute("select id from  model where name = ? and version = ?;", (dir, version)).fetchone()

            if res is None:
                continue
            else:
                model_id = res[0]
                cfg.contur_log.info("Found matching mode with ID {}".format(model_id))
                break
    if model_id == -1:
        msg = "No match found in the Contur Model database for the model in {}.\n".format(run_info_path)
        msg += "       If you want this to be added, copy the sources files into the contur Models area and remake."
        cfg.contur_log.info(msg)

    # do we want to write this model and parameters to the local db too? probs not.
    conn.close()
    return model_id


def write_grid_data(conturDepot, args, yodafile=None):
    """
    populate the local database with information about this run.

    """
    
    # see if this model is in the DB already 
    run_info_path = os.path.join(os.path.abspath("."), cfg.run_info)
    try:
        if cfg.use_mysql:
            model_id = get_mysql_model_id(run_info_path)
        else:
            model_id = get_model_id(run_info_path)
    except db.OperationalError as dboe:
        raise cfg.ConturError(dboe)
        
    if conturDepot.points is None:
        return False

    # now open the local results file for writing.
    if not INIT_DADB:
        init_dadb()
    conn = db.connect(cfg.results_dbfile)
    c = conn.cursor()

    default_list = ['LOG','OUTPUTDIR','GRID','TAG','MAPFILE','RUNNAME','INIT_DB','PARAM_FILE','SLHA','BEAMS','THCORR','MIN_SYST','ERR_PREC','LL_PREC','N_ITER','MNS']
    # record the additional arguments 
    addition_argument_list = []
    for i in args:
        if args[i] and i not in default_list:
            addition_argument_list.append(i)
    # list to string
    addition_argument = "/".join(addition_argument_list)

    runname = args['RUNNAME']
    c.execute("insert into  map (id,name) \
         values (?,?);", (None, runname))

    # each run will have the same heatmap (ie same map id) and the same events_num
    map_id = c.execute("select id from map order by id desc;").fetchone()[0]

    # look for the param steering file in the input dir. add it to the db if found
    param_dict = None
    if (cfg.grid is not None):
        for file in os.listdir(cfg.grid):
            if file.endswith('.dat'):
                try:
                    param_dict, run_dict = read_param_steering_file(os.path.join(os.path.abspath(cfg.grid), file))
                    break # if found the param file
                except KeyError:
                    continue # keep looking if we find the wrong .dat file

        if param_dict is None:
            cfg.contur_log.warning("No param file in {}, unable to write scan modes to database".format(cfg.grid))
        else:
              for param, values in param_dict.items():
                res = c.execute("select id from parameter where model_id = ? and name = ?;",
                                        (str(model_id), param,)).fetchone()

                # can't find parameter id so insert as null
                if res is None:
                    c.execute("insert into scan_mode (id, model_id, map_id, parameter_name, mode)\
                                            values (?,?,?,?,?);", (None, model_id, map_id, param, values['mode']))
                else:
                    parameter_id = res[0]
                    c.execute("insert into scan_mode (id, model_id, map_id, parameter_id, parameter_name, mode) \
                        values (?,?,?,?,?,?)", (None, model_id, map_id, param, values['mode']))

    for likelihood_point in conturDepot.points:

        # store all stat types to database. 
        if yodafile is None:
            grid_name = os.path.abspath(cfg.grid)
            yoda_files_list = cgt.find_param_point(grid_name, cfg.tag, likelihood_point.param_point)
            yodaFiles = ",".join(yoda_files_list)            
        else:
            yodaFiles = yodafile

        current_run_point = likelihood_point.get_run_point()

        # generate model_point data
        c.execute("insert into model_point (id, model_id, yoda_files, run_point) values (?,?,?,?);", (None, model_id, str(yodaFiles), str(current_run_point)))
        model_point_id = c.execute("select id from model_point order by id desc").fetchone()[0]
            
        for stat_type in cfg.stat_types:   
            # write information for parameter points
            if likelihood_point.get_full_likelihood(stat_type) is not None and likelihood_point.get_full_likelihood(stat_type).getCLs(stat_type) is not None:
                # match parameter point with yoda files TODO I suspect we can do this more efficiently
                # by using info from the map file?

                for param, val in likelihood_point.param_point.items():
                    res = c.execute("select id from parameter where model_id = ? and name = ?;",
                                    (str(model_id), param,)).fetchone()

                    # this parameter is not original from contur model
                    if res is None:
                        c.execute("insert into parameter_value (id,model_point_id,name,value)\
                                                values (?,?,?,?);", (None, model_point_id, param, val))
                    else:
                        parameter_id = res[0]
                        c.execute("insert into parameter_value (id,model_point_id,parameter_id,name,value)\
                            values (?,?,?,?,?);", (None, model_point_id, parameter_id, param, val))

                c.execute("insert into run (id,map_id,model_point_id,events_num,stat_type,combined_exclusion,mu_lower_limit,mu_upper_limit,mu_hat,addition_argument) \
                    values (?,?,?,?,?,?,?,?,?,? )",
                        (None, map_id, model_point_id, likelihood_point.num_events, stat_type, likelihood_point.get_full_likelihood(stat_type).getCLs(stat_type),likelihood_point.get_full_likelihood(stat_type).get_mu_lower_limit(stat_type),likelihood_point.get_full_likelihood(stat_type).get_mu_upper_limit(stat_type),likelihood_point.get_full_likelihood(stat_type).get_mu_hat(stat_type), addition_argument))

                run_id = c.execute("select id from run order by id desc;").fetchone()[0]

                for x in likelihood_point.get_sorted_likelihood_blocks(stat_type):
                    c.execute("insert into exclusions (id, run_id, pool_name, stat_type, exclusion, mu_lower_limit,mu_upper_limit, mu_hat, histos) \
                            values (?,?,?,?,?,?,?,?,?);", (None, run_id, x.pools, stat_type, x.getCLs(stat_type), x.get_mu_lower_limit(stat_type), x.get_mu_upper_limit(stat_type),x.get_mu_hat(stat_type), x.tags))
                    # skip the None value 
                    if x.get_ts_b(stat_type) is None:
                        continue
                    c.execute("insert into intermediate_result (id,run_id,pool_name,stat_type,ts_b,ts_s_b) \
                            values (?,?,?,?,?,?);", (None, run_id, x.pools, stat_type, x.get_ts_b(stat_type), x.get_ts_s_b(stat_type)))
                    
                for obs, exc in likelihood_point.obs_excl_dict.items():
                    c.execute("insert into obs_exclusions (id, run_id, stat_type, exclusion, ts_s_b, ts_b, mu_lower_limit, mu_upper_limit, mu_hat, histo) \
                            values (?,?,?,?,?,?,?,?,?,?);", (None, run_id, stat_type, exc[stat_type].get('CLs'), exc[stat_type].get('ts_s_b'), exc[stat_type].get('ts_b'), exc[stat_type].get('mu_lower_limit'), exc[stat_type].get('mu_upper_limit'),exc[stat_type].get('mu_hat'), obs))

                    
    conn.commit()
    conn.close()
    cfg.contur_log.info("Writing summary for grid mode into database: {}".format(cfg.results_dbfile))


def find_model_point_by_params(paramList):
    """
    Send a list of parameters **paramList**, this will return the closest model point for which results are available in the results database.

    """    
    params = {}
    model_points = {}

    # parse the parameter list
    # turn the values into floats if possible
    for pair in paramList:
        temp = pair.split('=')
        try:
            params[temp[0]] = float(temp[1])
        except ValueError:
            params[temp[0]] = temp[1]
        model_points[temp[0]] = []

    cfg.contur_log.info('Looking for the closest match to these parameter values: {}'.format(params))

    try:
        conn = open_for_reading(cfg.results_dbfile)
        c = conn.cursor()
    except db.OperationalError as dboe:
        raise cfg.ConturError(dboe)
   
    for param, val in params.items():
 
        search_sql = "select min(value) from parameter_value where value >= {} and name=\'{}\';".format(val,param)
        near_val = c.execute(search_sql).fetchone()[0]
        if near_val is None:
            raise db.OperationalError("No values found in DB for parameter {}".format(param))
        
        search_sql = "select model_point_id from parameter_value where name = \'{}\' and value ={}".format(param,near_val)
        model_point_ids = c.execute(search_sql).fetchall()

        # TODO: this might not actually be closest, since we only look from below.
        
        for model_point_id in model_point_ids:
            model_points[param].append(model_point_id[0])

    # now look for a model point which is in the "closest" list for all parameters
    new_model_points = []

    iterP = next(iter(params))
    for model_point in model_points[iterP]:
        inAll = True
        for points in model_points.values():
            if model_point not in points:
                inAll = False

        if inAll:
            new_model_points.append(model_point)

    return new_model_points

def search_yoda_file(model_points):
    """
    Sent a list of **model_points**, will return a list of corresponding yoda filenames.
    """
    conn = open_for_reading(cfg.results_dbfile) 
    c = conn.cursor()

    search_yoda_sql = "select yoda_files from model_point where id in (" + ','.join(map(str, model_points)) + ");"
    yoda_file_res = c.execute(search_yoda_sql).fetchall()
    yoda_file_list = []
    for yoda_file_str in yoda_file_res:
        yoda_files=yoda_file_str[0].split(",")
        for file in yoda_files:
            yoda_file_list.append(file.strip("[").strip("]").replace("'","").strip())

    conn.commit()
    conn.close()
    return yoda_file_list

def find_param_point_db(paramList):
    """
    Given a list of model parameters, search the results DB for the closest match, and return the associated yoda file names.
    """    

    try:
        model_points = find_model_point_by_params(paramList)
        yoda_files = search_yoda_file(model_points)
    except db.OperationalError as dboe:
        raise cfg.ConturError(dboe)
        
    cfg.contur_log.info('These files have been identified as the nearest match: {}'.format(yoda_files))

    return yoda_files


def show_param_detail_db(paramList):

    """
    Given a list of models parameters, search the results DB for the closest match, print some detailed info, and return the associated yoda file names.
    """    

    conn = open_for_reading(cfg.results_dbfile) 

    model_points = find_model_point_by_params(paramList)
    yoda_files = search_yoda_file(model_points)

    for model_point_id in model_points:
        search_sql = "select name,value from parameter_value where model_point_id = " + str(model_point_id) + ";"
        res = c.execute(search_sql).fetchall()
        cfg.contur_log.info("********************************")
        cfg.contur_log.info("Parameters for this run are:")
        for params in res:
            cfg.contur_log.info("{}: {}".format(params[0], params[1]))

        search_sql = "select yoda_files from model_point where id =" + str(model_point_id) + ";"
        yoda_file = c.execute(search_sql).fetchone()[0]
        cfg.contur_log.info("Files identified as the nearest match: {}".format(yoda_file))

        search_sql = "select id,events_num,combined_exclusion from run where model_point_id = " + str(
            model_point_id) + ";"
        run_res = c.execute(search_sql).fetchone()
        run_id = run_res[0]
        events_num = run_res[1]
        combined_exclusion = run_res[2]
        cfg.contur_log.info(
            "Combined exclusion and number of events: {}, {}".format(combined_exclusion, events_num))

        cfg.contur_log.info("Histograms contributed to the combined exclusion (exclusion>0.5):")
        search_sql = "select pool_name,exclusion,histos from exclusions where run_id = " + str(
            run_id) + " and exclusion > " + str(EXCLUSION_THRESHOLD) + ";"
        exclusion_res = c.execute(search_sql).fetchall()
        for exclusion in exclusion_res:
            cfg.contur_log.info(
                "pool:{}, exclusion:{}, histograms:{}".format(exclusion[0], exclusion[1], exclusion[2]))

    return yoda_files



def _create_model_and_parameter_tables(c):
    """
    Make the model table and the parameter table on connection c.
    """

    c.execute('''create table if not exists model
                   (id integer primary key AUTOINCREMENT,
                   name  varchar(255)    not null,
                   version  varchar(255)   not null,
                   author  varchar(255),
                   original_source   varchar(255),
                   contur_url  varchar(255),
                   location  varchar(255),
                   reference  varchar(255));''')

    # TODO: Comment it out temporarily to avoid exceptions
    # c.execute('''create unique index if not exists model_version on model (name, version);''')

    c.execute('''create table if not exists parameter
                   (id integer primary key AUTOINCREMENT,
                   model_id  integer     not null,
                   name  varchar(255)    not null,
                   texname varchar(255)    not null,
                   type  varchar(50)    not null,
                   value  varchar(50)    not null,
                   foreign key(model_id) references model(id) on delete cascade on update cascade);''')

    return


def _create_model_and_parameter_indexes(c):
    """
    Create indexes for model and parameter tables on connection c.
    """
    c.execute('''CREATE INDEX IF NOT EXISTS idx_model_name_version ON model(name, version);''')
    c.execute('''CREATE INDEX IF NOT EXISTS idx_parameter_model_id_name ON parameter(model_id, name);''')

    return


def _create_additional_indexes(c):
    """
    Create additional indexes for database tables on connection c.
    """
    c.execute('''CREATE INDEX IF NOT EXISTS idx_run_model_point_id ON run(model_point_id);''')

    c.execute('''CREATE INDEX IF NOT EXISTS idx_parameter_value_name_value ON parameter_value(name, value);''')
    c.execute('''CREATE INDEX IF NOT EXISTS idx_parameter_value_model_point_id ON parameter_value(model_point_id);''')

    c.execute('''CREATE INDEX IF NOT EXISTS idx_exclusions_run_id_exclusion ON exclusions(run_id, exclusion);''')

    return

