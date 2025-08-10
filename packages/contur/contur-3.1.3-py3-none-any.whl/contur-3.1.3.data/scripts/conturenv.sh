# -*- bash -*-

mydir="$( dirname "${BASH_SOURCE[0]}" )"
python_root="$( which contur )"
python_bin_root="${python_root%/*}"
python_bin_root="${python_bin_root%/*}"
data_file_pre="$(find ${python_bin_root} -name DB)"
data_file_pre="${python_bin_root}/share/contur"

export CONTUR_DATA_PATH="${data_file_pre}" 
if [[ -z "${CONTUR_USER_DIR}" ]]; then
    export CONTUR_USER_DIR="$HOME/contur_users"
fi
export PYTHONWARNINGS='ignore:resource_tracker:UserWarning'

# ------------------
# Add the local rivet area to the rivet data and analysis paths.
export RIVET_DATA_PATH=$(echo $CONTUR_DATA_PATH/data/Rivet:$CONTUR_DATA_PATH/data/Theory:$RIVET_DATA_PATH | awk -v RS=':' '!a[$1]++ { if (NR > 1) printf RS; printf $1 }')
export RIVET_ANALYSIS_PATH=$(echo $CONTUR_DATA_PATH/data/Rivet:$CONTUR_USER_DIR:$RIVET_ANALYSIS_PATH | awk -v RS=':' '!a[$1]++ { if (NR > 1) printf RS; printf $1 }')


# This file won't exist until make has been run
ALIST=$CONTUR_USER_DIR/analysis-list
test -f $ALIST && source $ALIST

echo "-------------------------------------------------------------------------------------------"
echo "Contur data files and Makefile should be in \$CONTUR_DATA_PATH"
echo "Derived files will be installed in $CONTUR_USER_DIR when make is run."
echo "You may change this location by setting \$CONTUR_USER_DIR to the desired path."
echo "\$CONTUR_DATA_PATH/data/Rivet has been added to \$RIVET_DATA_PATH and \$RIVET_ANALYSIS_PATH"
echo "-------------------------------------------------------------------------------------------"
