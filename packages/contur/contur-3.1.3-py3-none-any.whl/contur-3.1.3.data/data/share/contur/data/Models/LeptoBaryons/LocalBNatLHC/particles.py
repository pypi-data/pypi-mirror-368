# This file was automatically created by FeynRules 2.3.49
# Mathematica version: 13.3.1 for Linux x86 (64-bit) (July 24, 2023)
# Date: Mon 24 Mar 2025 18:54:48


from __future__ import division
from .object_library import all_particles, Particle
from . import parameters as Param

from . import propagators as Prop

a = Particle(pdg_code = 22,
             name = 'a',
             antiname = 'a',
             spin = 3,
             color = 1,
             mass = Param.ZERO,
             width = Param.ZERO,
             texname = 'a',
             antitexname = 'a',
             charge = 0,
             BN = 0,
             GhostNumber = 0,
             LeptonNumber = 0,
             Y = 0)

Z = Particle(pdg_code = 23,
             name = 'Z',
             antiname = 'Z',
             spin = 3,
             color = 1,
             mass = Param.MZ,
             width = Param.WZ,
             texname = 'Z',
             antitexname = 'Z',
             charge = 0,
             BN = 0,
             GhostNumber = 0,
             LeptonNumber = 0,
             Y = 0)

W__plus__ = Particle(pdg_code = 24,
                     name = 'W+',
                     antiname = 'W-',
                     spin = 3,
                     color = 1,
                     mass = Param.MW,
                     width = Param.WW,
                     texname = 'W+',
                     antitexname = 'W-',
                     charge = 1,
                     BN = 0,
                     GhostNumber = 0,
                     LeptonNumber = 0,
                     Y = 0)

W__minus__ = W__plus__.anti()

g = Particle(pdg_code = 21,
             name = 'g',
             antiname = 'g',
             spin = 3,
             color = 8,
             mass = Param.ZERO,
             width = Param.ZERO,
             texname = 'g',
             antitexname = 'g',
             charge = 0,
             BN = 0,
             GhostNumber = 0,
             LeptonNumber = 0,
             Y = 0)

ZB = Particle(pdg_code = 32,
              name = 'ZB',
              antiname = 'ZB',
              spin = 3,
              color = 1,
              mass = Param.MZB,
              width = Param.WZB,
              texname = 'ZB',
              antitexname = 'ZB',
              charge = 0,
              BN = 0,
              GhostNumber = 0,
              LeptonNumber = 0,
              Y = 0)

ghA = Particle(pdg_code = 9000001,
               name = 'ghA',
               antiname = 'ghA~',
               spin = -1,
               color = 1,
               mass = Param.ZERO,
               width = Param.ZERO,
               texname = 'ghA',
               antitexname = 'ghA~',
               charge = 0,
               BN = 0,
               GhostNumber = 1,
               LeptonNumber = 0,
               Y = 0)

ghA__tilde__ = ghA.anti()

ghZ = Particle(pdg_code = 9000002,
               name = 'ghZ',
               antiname = 'ghZ~',
               spin = -1,
               color = 1,
               mass = Param.MZ,
               width = Param.WZ,
               texname = 'ghZ',
               antitexname = 'ghZ~',
               charge = 0,
               BN = 0,
               GhostNumber = 1,
               LeptonNumber = 0,
               Y = 0)

ghZ__tilde__ = ghZ.anti()

ghWp = Particle(pdg_code = 9000003,
                name = 'ghWp',
                antiname = 'ghWp~',
                spin = -1,
                color = 1,
                mass = Param.MW,
                width = Param.WW,
                texname = 'ghWp',
                antitexname = 'ghWp~',
                charge = 1,
                BN = 0,
                GhostNumber = 1,
                LeptonNumber = 0,
                Y = 0)

ghWp__tilde__ = ghWp.anti()

ghWm = Particle(pdg_code = 9000004,
                name = 'ghWm',
                antiname = 'ghWm~',
                spin = -1,
                color = 1,
                mass = Param.MW,
                width = Param.WW,
                texname = 'ghWm',
                antitexname = 'ghWm~',
                charge = -1,
                BN = 0,
                GhostNumber = 1,
                LeptonNumber = 0,
                Y = 0)

ghWm__tilde__ = ghWm.anti()

ghG = Particle(pdg_code = 82,
               name = 'ghG',
               antiname = 'ghG~',
               spin = -1,
               color = 8,
               mass = Param.ZERO,
               width = Param.ZERO,
               texname = 'ghG',
               antitexname = 'ghG~',
               charge = 0,
               BN = 0,
               GhostNumber = 1,
               LeptonNumber = 0,
               Y = 0)

ghG__tilde__ = ghG.anti()

ghZB = Particle(pdg_code = 9000005,
                name = 'ghZB',
                antiname = 'ghZB~',
                spin = -1,
                color = 1,
                mass = Param.MZB,
                width = Param.WZB,
                texname = 'ghZB',
                antitexname = 'ghZB~',
                charge = 0,
                BN = 0,
                GhostNumber = 1,
                LeptonNumber = 0,
                Y = 0)

ghZB__tilde__ = ghZB.anti()

ve = Particle(pdg_code = 12,
              name = 've',
              antiname = 've~',
              spin = 2,
              color = 1,
              mass = Param.ZERO,
              width = Param.ZERO,
              texname = 've',
              antitexname = 've~',
              charge = 0,
              BN = 0,
              GhostNumber = 0,
              LeptonNumber = 1,
              Y = 0)

ve__tilde__ = ve.anti()

vm = Particle(pdg_code = 14,
              name = 'vm',
              antiname = 'vm~',
              spin = 2,
              color = 1,
              mass = Param.ZERO,
              width = Param.ZERO,
              texname = 'vm',
              antitexname = 'vm~',
              charge = 0,
              BN = 0,
              GhostNumber = 0,
              LeptonNumber = 1,
              Y = 0)

vm__tilde__ = vm.anti()

vt = Particle(pdg_code = 16,
              name = 'vt',
              antiname = 'vt~',
              spin = 2,
              color = 1,
              mass = Param.ZERO,
              width = Param.ZERO,
              texname = 'vt',
              antitexname = 'vt~',
              charge = 0,
              BN = 0,
              GhostNumber = 0,
              LeptonNumber = 1,
              Y = 0)

vt__tilde__ = vt.anti()

e__minus__ = Particle(pdg_code = 11,
                      name = 'e-',
                      antiname = 'e+',
                      spin = 2,
                      color = 1,
                      mass = Param.Me,
                      width = Param.ZERO,
                      texname = 'e-',
                      antitexname = 'e+',
                      charge = -1,
                      BN = 0,
                      GhostNumber = 0,
                      LeptonNumber = 1,
                      Y = 0)

e__plus__ = e__minus__.anti()

mu__minus__ = Particle(pdg_code = 13,
                       name = 'mu-',
                       antiname = 'mu+',
                       spin = 2,
                       color = 1,
                       mass = Param.MMU,
                       width = Param.ZERO,
                       texname = 'mu-',
                       antitexname = 'mu+',
                       charge = -1,
                       BN = 0,
                       GhostNumber = 0,
                       LeptonNumber = 1,
                       Y = 0)

mu__plus__ = mu__minus__.anti()

ta__minus__ = Particle(pdg_code = 15,
                       name = 'ta-',
                       antiname = 'ta+',
                       spin = 2,
                       color = 1,
                       mass = Param.MTA,
                       width = Param.ZERO,
                       texname = 'ta-',
                       antitexname = 'ta+',
                       charge = -1,
                       BN = 0,
                       GhostNumber = 0,
                       LeptonNumber = 1,
                       Y = 0)

ta__plus__ = ta__minus__.anti()

u = Particle(pdg_code = 2,
             name = 'u',
             antiname = 'u~',
             spin = 2,
             color = 3,
             mass = Param.MU,
             width = Param.ZERO,
             texname = 'u',
             antitexname = 'u~',
             charge = 2/3,
             BN = 0,
             GhostNumber = 0,
             LeptonNumber = 0,
             Y = 0)

u__tilde__ = u.anti()

c = Particle(pdg_code = 4,
             name = 'c',
             antiname = 'c~',
             spin = 2,
             color = 3,
             mass = Param.MC,
             width = Param.ZERO,
             texname = 'c',
             antitexname = 'c~',
             charge = 2/3,
             BN = 0,
             GhostNumber = 0,
             LeptonNumber = 0,
             Y = 0)

c__tilde__ = c.anti()

t = Particle(pdg_code = 6,
             name = 't',
             antiname = 't~',
             spin = 2,
             color = 3,
             mass = Param.MT,
             width = Param.WT,
             texname = 't',
             antitexname = 't~',
             charge = 2/3,
             BN = 0,
             GhostNumber = 0,
             LeptonNumber = 0,
             Y = 0)

t__tilde__ = t.anti()

d = Particle(pdg_code = 1,
             name = 'd',
             antiname = 'd~',
             spin = 2,
             color = 3,
             mass = Param.MD,
             width = Param.ZERO,
             texname = 'd',
             antitexname = 'd~',
             charge = -1/3,
             BN = 0,
             GhostNumber = 0,
             LeptonNumber = 0,
             Y = 0)

d__tilde__ = d.anti()

s = Particle(pdg_code = 3,
             name = 's',
             antiname = 's~',
             spin = 2,
             color = 3,
             mass = Param.MS,
             width = Param.ZERO,
             texname = 's',
             antitexname = 's~',
             charge = -1/3,
             BN = 0,
             GhostNumber = 0,
             LeptonNumber = 0,
             Y = 0)

s__tilde__ = s.anti()

b = Particle(pdg_code = 5,
             name = 'b',
             antiname = 'b~',
             spin = 2,
             color = 3,
             mass = Param.MB,
             width = Param.ZERO,
             texname = 'b',
             antitexname = 'b~',
             charge = -1/3,
             BN = 0,
             GhostNumber = 0,
             LeptonNumber = 0,
             Y = 0)

b__tilde__ = b.anti()

chi = Particle(pdg_code = 52,
               name = 'chi',
               antiname = 'chi',
               spin = 2,
               color = 1,
               mass = Param.Mchi,
               width = Param.ZERO,
               texname = 'chi',
               antitexname = 'chi',
               charge = 0,
               BN = 0,
               GhostNumber = 0,
               LeptonNumber = 0,
               Y = 0)

rhoM = Particle(pdg_code = 71,
                name = 'rhoM',
                antiname = 'rhoM~',
                spin = 2,
                color = 1,
                mass = Param.Mrhom,
                width = Param.WrhoM,
                texname = 'rhoM',
                antitexname = 'rhoM~',
                charge = -1,
                BN = 0,
                GhostNumber = 0,
                LeptonNumber = 0,
                Y = 0)

rhoM__tilde__ = rhoM.anti()

rhoZ = Particle(pdg_code = 72,
                name = 'rhoZ',
                antiname = 'rhoZ',
                spin = 2,
                color = 1,
                mass = Param.MrhoZ,
                width = Param.WrhoZ,
                texname = 'rhoZ',
                antitexname = 'rhoZ',
                charge = 0,
                BN = 0,
                GhostNumber = 0,
                LeptonNumber = 0,
                Y = 0)

psi = Particle(pdg_code = 73,
               name = 'psi',
               antiname = 'psi~',
               spin = 2,
               color = 1,
               mass = Param.Mpsi,
               width = Param.Wpsi,
               texname = 'psi',
               antitexname = 'psi~',
               charge = -1,
               BN = 0,
               GhostNumber = 0,
               LeptonNumber = 0,
               Y = 0)

psi__tilde__ = psi.anti()

h = Particle(pdg_code = 25,
             name = 'h',
             antiname = 'h',
             spin = 1,
             color = 1,
             mass = Param.mh,
             width = Param.Wh,
             texname = 'h',
             antitexname = 'h',
             charge = 0,
             BN = 0,
             GhostNumber = 0,
             LeptonNumber = 0,
             Y = 0)

G0 = Particle(pdg_code = 250,
              name = 'G0',
              antiname = 'G0',
              spin = 1,
              color = 1,
              mass = Param.MZ,
              width = Param.WZ,
              texname = 'G0',
              antitexname = 'G0',
              goldstone = True,
              charge = 0,
              BN = 0,
              GhostNumber = 0,
              LeptonNumber = 0,
              Y = 0)

G__plus__ = Particle(pdg_code = 251,
                     name = 'G+',
                     antiname = 'G-',
                     spin = 1,
                     color = 1,
                     mass = Param.MW,
                     width = Param.WW,
                     texname = 'G+',
                     antitexname = 'G-',
                     goldstone = True,
                     charge = 1,
                     BN = 0,
                     GhostNumber = 0,
                     LeptonNumber = 0,
                     Y = 0)

G__minus__ = G__plus__.anti()

hB = Particle(pdg_code = 35,
              name = 'hB',
              antiname = 'hB',
              spin = 1,
              color = 1,
              mass = Param.mhB,
              width = Param.WhB,
              texname = 'hB',
              antitexname = 'hB',
              charge = 0,
              BN = 0,
              GhostNumber = 0,
              LeptonNumber = 0,
              Y = 0)

GZB = Particle(pdg_code = 9000006,
               name = 'GZB',
               antiname = 'GZB',
               spin = 1,
               color = 1,
               mass = Param.MZB,
               width = Param.WZB,
               texname = 'GZB',
               antitexname = 'GZB',
               goldstone = True,
               charge = 0,
               BN = 0,
               GhostNumber = 0,
               LeptonNumber = 0,
               Y = 0)

sphi = Particle(pdg_code = 51,
                name = 'sphi',
                antiname = 'sphi~',
                spin = 1,
                color = 1,
                mass = Param.Msphi,
                width = Param.Wsphi,
                texname = 'sphi',
                antitexname = 'sphi~',
                charge = 0,
                BN = 0,
                GhostNumber = 0,
                LeptonNumber = -1,
                Y = 0)

sphi__tilde__ = sphi.anti()

