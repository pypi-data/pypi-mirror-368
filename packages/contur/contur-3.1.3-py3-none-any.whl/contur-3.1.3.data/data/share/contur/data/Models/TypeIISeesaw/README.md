There is some known limitations in madgraph width computations for 1->3 body resonance decays (related to link https://answers.launchpad.net/mg5amcnlo/+question/696360). Thus instead of relying on the automatic width calculation that occurs during event generation, instead one needs to compute the widths of d++ particle using command below :
```
define ff = u d c s u~ c~ d~ s~ e+ mu+ ta+ e- mu- ta- v1 v2 v3
generate d++ > ff ff ff ff
```
Computed width values are stored in `width/width.dat` file in mass and width order.
