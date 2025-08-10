set automatic_html_opening False
set run_mode 0
set nb_core 1
set low_mem_multicore_nlo_generation

# IMPORTANT 
# make sure to point this to the correct relative path
# where the DMSimp_t directory is located
import model ./DMSimp_t-S3D_uni --modelname 

# dark matter particles in S3D_uni model
define dm = xd xd~
# mediators in S3D_uni model
define med = ys3qd1 ys3qu1 ys3qd2 ys3qu2 ys3qd3 ys3qu3 ys3d1 ys3u1 ys3d2 ys3u2 ys3d3 ys3u3 ys3qd1~ ys3qu1~ ys3qd2~ ys3qu2~ ys3qd3~ ys3qu3~ ys3d1~ ys3u1~ ys3d2~ ys3u2~ ys3d3~ ys3u3~

# add processes
# - t-channel diagram of p p > dm dm + radiated gluon
# - this line also includes p p > dm mediator diagrams because of the extra j requirement
# - exclude the YF mediators (with different spin) and the other DM particles Xs-Xw
generate p p > dm dm j / YF3d1 YF3u1 YF3d2 YF3u2 YF3d3 YF3u3 YF3Qd1 YF3Qu1 YF3Qd2 YF3Qu2 YF3Qd3 YF3Qu3 Xs Xm Xv Xc Xw
# - QCD p p > med med, where mediator decays into DM + quark/gluon
add process p p > med med, med > dm j
add process p p > med med, med > dm t

# - t-channel p p > mediator mediator, mediator decays into quark+gluon
add process p p > med med DMT=2 QCD=0 QED=0 / Xs Xm Xv Xc Xw, med > dm j

# configure MG5 run
output dm_combined_uni
launch
madspin=OFF
shower=pythia8

# set model parameters
set MXd     {DMMass} 
set MYS3Qd1 {MediatorMass}
set MYS3Qu1 {MediatorMass}
set MYS3Qd2 {MediatorMass}
set MYS3Qu2 {MediatorMass}
set MYS3Qd3 {MediatorMass}
set MYS3Qu3 {MediatorMass}
set MYS3d1  {MediatorMass}
set MYS3u1  {MediatorMass}
set MYS3d2  {MediatorMass}
set MYS3u2  {MediatorMass}
set MYS3d3  {MediatorMass}
set MYS3u3  {MediatorMass}
set lamS3d1x1 1.0 
set lamS3d2x2 1.0 
set lamS3d3x3 1.0 
set lamS3Q1x1 1.0 
set lamS3Q2x2 1.0 
set lamS3Q3x3 1.0 
set lamS3u1x1 1.0 
set lamS3u2x2 1.0 
set lamS3u3x3 1.0
set wys3u1 Auto
set wys3u2 Auto
set wys3u3 Auto
set wys3d1 Auto
set wys3d2 Auto
set wys3d3 Auto
set wys3Qu1 Auto
set wys3Qu2 Auto
set wys3Qu3 Auto
set wys3Qd1 Auto
set wys3Qd2 Auto
set wys3Qd3 Auto

# cut on jet pt (100 GeV)
set ptj 100

# configure MG5 settings
set partonlevel:mpi off
set use_syst False
