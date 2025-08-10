import model TypeII_LO_v1_3_UFO
define fermion = e+ e- mu+ mu- ta+ ta- ve vm vt u d c s u~ d~ c~ s~
generate p p > d++ d-- QED=2
add process p p > d++ d- QED=2, d- > d-- fermion fermion
add process p p > d+ d-- QED=2, d+ > d++ fermion fermion
output mgevents --hel_recycling=False
launch
shower=PYTHIA8
set param_card mv1 1.e-11
set param_card mdp {mdp}
set param_card mdpp __mdpp__
set param_card delcp 0.0
set param_card phim1 0.0
set param_card phim2 0.0
set param_card lamhd1 0.1
set param_card lamd1 1.0
set param_card lamd2 0.1
set param_card vevd 1.0
set param_card wdp Auto
set param_card wdpp __wdpp__
set param_card wd0 Auto
set no_parton_cut
set partonlevel:mpi off
