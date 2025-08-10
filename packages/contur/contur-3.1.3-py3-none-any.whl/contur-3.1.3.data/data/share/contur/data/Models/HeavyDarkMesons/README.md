# Heavy Dark Mesons

## Useful references

* [New sensitivity of LHC measurements to composite dark matter models](https://arxiv.org/abs/2105.08494) by J. M. Butterworth, L. Corpe, X. Kong, S. Kulkarni, M. Thomas
* [Dark Mesons in the LHC](https://arxiv.org/abs/1809.10184) by Graham D. Kribs, Adam Martin, Bryan Ostdiek, Tom Tong
* [Composite bosonic baryon dark matter on the lattice: SU(4) baryon spectrum and the effective Higgs interaction](https://arxiv.org/abs/1402.6656)
* [Stealth Dark Matter: Dark scalar baryons through the Higgs portal](https://arxiv.org/abs/1503.04203)
* [Effective Theories of Dark Mesons with Custodial Symmetry](https://arxiv.org/abs/1809.10183)
* [Stealth Dark Matter: Dark scalar baryons through the Higgs portal](https://arxiv.org/abs/1503.04203)

* There are several UFO directories in that paper, some of which you can see listed above. The authors github repository is [here](https://github.com/bostdiek/HeavyDarkMesons/tree/master/UFO_Files/FromPaper)

* These model files and some example .in and parameter files are also available in the ["Models" area of the Contur repository](https://gitlab.com/hepcedar/contur/-/tree/master/Models/HeavyDarkMesons)

* Need to run ufo2herwig with the  `--forbidden-particle-name FORBIDDEN_PARTICLE_NAME`
option for rho0, rho+, rho-, to avoid name clashes with the SM rho meson.

* The parameter Xi is only defined for the gaugephobic models (see the first reference above, p7).

* The charged rhos are not defined for the SU2R model.

