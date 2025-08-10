#! /bin/bash
#$ -j y # Merge the error and output streams into a single file
#$ -o /unix/cedar/jmb/Work/Regression_Rebuild/myscan00/13TeV/0003/contur.log # Output file path
export CONTUR_DATA_PATH=/home/jmb/gitstuff/contur-dev
export CONTUR_USER_DIR=/home/jmb/gitstuff/contur-dev/contur_user
export RIVET_ANALYSIS_PATH=/home/jmb/gitstuff/contur-dev/contur_user:/home/jmb/gitstuff/contur-dev/data/Rivet
export RIVET_DATA_PATH=/home/jmb/gitstuff/contur-dev/contur_user:/home/jmb/gitstuff/contur-dev/data/Rivet:/home/jmb/gitstuff/contur-dev/data/Theory
export CONTUR_ROOT=/home/jmb/gitstuff/contur-dev
source $CONTUR_USER_DIR/analysis-list
source /unix/cedar/software/cos7/Dev/setupEnv.sh;
cd /unix/cedar/jmb/Work/Regression_Rebuild/myscan00/13TeV/0003
Herwig read herwig.in -I /unix/cedar/jmb/Work/Regression_Rebuild/RunInfo -L /unix/cedar/jmb/Work/Regression_Rebuild/RunInfo;
Herwig run herwig.run --seed=101  --tag=runpoint_0003  --numevents=30000 ;
