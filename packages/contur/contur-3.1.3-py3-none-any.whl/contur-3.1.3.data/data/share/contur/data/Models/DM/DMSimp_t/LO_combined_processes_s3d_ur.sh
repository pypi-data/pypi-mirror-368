set automatic_html_opening False
set run_mode 0
set nb_core 1
set low_mem_multicore_nlo_generation

# IMPORTANT 
# make sure to point this to the correct relative path
# where the DMSimp_t directory is located
import model ./DMSimp_t-S3D_uR --modelname

# dark matter particles in S3D_uR model
define dm = xd xd~

# mediator in S3D_uR model
define med = ys3u1 ys3u1~ 

# add processes
# - t-channel diagram of p p > dm dm + radiated gluon
# - this line also includes p p > dm mediator diagrams because of the extra j requirement
# - exclude the YF mediators (with different spin) and the other DM particles Xs-Xw
generate p p > dm dm j / YS3Qd1 YS3Qu1 YS3Qd2 YS3Qu2 YS3Qd3 YS3Qu3 YS3d1 YS3d2 YS3u2 YS3d3 YS3u3 YF3Qd1 YF3Qu1 YF3Qd2 YF3Qu2 YF3Qd3 YF3Qu3 YF3d1 YF3u1 YF3d2 YF3u2 YF3d3 YF3u3 Xs Xm Xv Xc Xw

# - QCD p p > med med, where mediator decays into DM + quark/gluon
add process p p > med med, med > dm j

# - t-channel p p > mediator mediator, mediator decays into quark+gluon
add process p p > med med DMT=2 QCD=0 QED=0 / Xs Xm Xv Xc Xw, med > dm j 

# configure MG5 run
output dmdmj_combined
launch
madspin=OFF
shower=pythia8

# set model parameters
set MXd    {DMMass}
set MYS3u1 {MediatorMass}
set lamS3u1x1 1.0
set wys3u1 Auto

# cut on jet pt (100 GeV)
set ptj 100

# configure MG5 settings
set partonlevel:mpi off
set use_syst False
