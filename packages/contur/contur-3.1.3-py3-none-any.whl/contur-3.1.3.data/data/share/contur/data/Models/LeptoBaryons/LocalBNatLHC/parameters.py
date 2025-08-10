# This file was automatically created by FeynRules 2.3.49
# Mathematica version: 13.3.1 for Linux x86 (64-bit) (July 24, 2023)
# Date: Mon 24 Mar 2025 18:54:48



from .object_library import all_parameters, Parameter


from .function_library import complexconjugate, re, im, csc, sec, acsc, asec, cot

# This is a default parameter object representing 0.
ZERO = Parameter(name = 'ZERO',
                 nature = 'internal',
                 type = 'real',
                 value = '0.0',
                 texname = '0')

# User-defined parameters.
cabi = Parameter(name = 'cabi',
                 nature = 'external',
                 type = 'real',
                 value = 0.227736,
                 texname = '\\theta _c',
                 lhablock = 'CKMBLOCK',
                 lhacode = [ 1 ])

gB = Parameter(name = 'gB',
               nature = 'external',
               type = 'real',
               value = 0.25,
               texname = 'g_B',
               lhablock = 'GaugeCoupling',
               lhacode = [ 1 ])

sth = Parameter(name = 'sth',
                nature = 'external',
                type = 'real',
                value = 0.01,
                texname = 's_B',
                lhablock = 'mixing',
                lhacode = [ 2 ])

aEWM1 = Parameter(name = 'aEWM1',
                  nature = 'external',
                  type = 'real',
                  value = 127.9,
                  texname = '\\text{aEWM1}',
                  lhablock = 'SMINPUTS',
                  lhacode = [ 1 ])

Gf = Parameter(name = 'Gf',
               nature = 'external',
               type = 'real',
               value = 0.0000116637,
               texname = 'G_f',
               lhablock = 'SMINPUTS',
               lhacode = [ 2 ])

aS = Parameter(name = 'aS',
               nature = 'external',
               type = 'real',
               value = 0.1184,
               texname = '\\alpha _s',
               lhablock = 'SMINPUTS',
               lhacode = [ 3 ])

ymdo = Parameter(name = 'ymdo',
                 nature = 'external',
                 type = 'real',
                 value = 0.00504,
                 texname = '\\text{ymdo}',
                 lhablock = 'YUKAWA',
                 lhacode = [ 1 ])

ymup = Parameter(name = 'ymup',
                 nature = 'external',
                 type = 'real',
                 value = 0.00255,
                 texname = '\\text{ymup}',
                 lhablock = 'YUKAWA',
                 lhacode = [ 2 ])

yms = Parameter(name = 'yms',
                nature = 'external',
                type = 'real',
                value = 0.101,
                texname = '\\text{yms}',
                lhablock = 'YUKAWA',
                lhacode = [ 3 ])

ymc = Parameter(name = 'ymc',
                nature = 'external',
                type = 'real',
                value = 1.27,
                texname = '\\text{ymc}',
                lhablock = 'YUKAWA',
                lhacode = [ 4 ])

ymb = Parameter(name = 'ymb',
                nature = 'external',
                type = 'real',
                value = 4.7,
                texname = '\\text{ymb}',
                lhablock = 'YUKAWA',
                lhacode = [ 5 ])

ymt = Parameter(name = 'ymt',
                nature = 'external',
                type = 'real',
                value = 172,
                texname = '\\text{ymt}',
                lhablock = 'YUKAWA',
                lhacode = [ 6 ])

yme = Parameter(name = 'yme',
                nature = 'external',
                type = 'real',
                value = 0.000511,
                texname = '\\text{yme}',
                lhablock = 'YUKAWA',
                lhacode = [ 11 ])

ymm = Parameter(name = 'ymm',
                nature = 'external',
                type = 'real',
                value = 0.10566,
                texname = '\\text{ymm}',
                lhablock = 'YUKAWA',
                lhacode = [ 13 ])

ymtau = Parameter(name = 'ymtau',
                  nature = 'external',
                  type = 'real',
                  value = 1.777,
                  texname = '\\text{ymtau}',
                  lhablock = 'YUKAWA',
                  lhacode = [ 15 ])

lame = Parameter(name = 'lame',
                 nature = 'external',
                 type = 'real',
                 value = 0.1,
                 texname = '\\text{lame}',
                 lhablock = 'Yuke3',
                 lhacode = [ 1 ])

lammu = Parameter(name = 'lammu',
                  nature = 'external',
                  type = 'real',
                  value = 0.1,
                  texname = '\\text{lammu}',
                  lhablock = 'Yuke3',
                  lhacode = [ 2 ])

lamtau = Parameter(name = 'lamtau',
                   nature = 'external',
                   type = 'real',
                   value = 0.1,
                   texname = '\\text{lamtau}',
                   lhablock = 'Yuke3',
                   lhacode = [ 3 ])

MZ = Parameter(name = 'MZ',
               nature = 'external',
               type = 'real',
               value = 91.1876,
               texname = '\\text{MZ}',
               lhablock = 'MASS',
               lhacode = [ 23 ])

MW = Parameter(name = 'MW',
               nature = 'external',
               type = 'real',
               value = 80.379,
               texname = '\\text{MW}',
               lhablock = 'MASS',
               lhacode = [ 24 ])

MZB = Parameter(name = 'MZB',
                nature = 'external',
                type = 'real',
                value = 1000,
                texname = '\\text{MZB}',
                lhablock = 'MASS',
                lhacode = [ 32 ])

Me = Parameter(name = 'Me',
               nature = 'external',
               type = 'real',
               value = 0.000511,
               texname = '\\text{Me}',
               lhablock = 'MASS',
               lhacode = [ 11 ])

MMU = Parameter(name = 'MMU',
                nature = 'external',
                type = 'real',
                value = 0.10566,
                texname = '\\text{MMU}',
                lhablock = 'MASS',
                lhacode = [ 13 ])

MTA = Parameter(name = 'MTA',
                nature = 'external',
                type = 'real',
                value = 1.777,
                texname = '\\text{MTA}',
                lhablock = 'MASS',
                lhacode = [ 15 ])

MU = Parameter(name = 'MU',
               nature = 'external',
               type = 'real',
               value = 0.00255,
               texname = 'M',
               lhablock = 'MASS',
               lhacode = [ 2 ])

MC = Parameter(name = 'MC',
               nature = 'external',
               type = 'real',
               value = 1.27,
               texname = '\\text{MC}',
               lhablock = 'MASS',
               lhacode = [ 4 ])

MT = Parameter(name = 'MT',
               nature = 'external',
               type = 'real',
               value = 172,
               texname = '\\text{MT}',
               lhablock = 'MASS',
               lhacode = [ 6 ])

MD = Parameter(name = 'MD',
               nature = 'external',
               type = 'real',
               value = 0.00504,
               texname = '\\text{MD}',
               lhablock = 'MASS',
               lhacode = [ 1 ])

MS = Parameter(name = 'MS',
               nature = 'external',
               type = 'real',
               value = 0.101,
               texname = '\\text{MS}',
               lhablock = 'MASS',
               lhacode = [ 3 ])

MB = Parameter(name = 'MB',
               nature = 'external',
               type = 'real',
               value = 4.7,
               texname = '\\text{MB}',
               lhablock = 'MASS',
               lhacode = [ 5 ])

Mchi = Parameter(name = 'Mchi',
                 nature = 'external',
                 type = 'real',
                 value = 500,
                 texname = '\\text{Mchi}',
                 lhablock = 'MASS',
                 lhacode = [ 52 ])

Mrhom = Parameter(name = 'Mrhom',
                  nature = 'external',
                  type = 'real',
                  value = 2999,
                  texname = '\\text{Mrhom}',
                  lhablock = 'MASS',
                  lhacode = [ 71 ])

MrhoZ = Parameter(name = 'MrhoZ',
                  nature = 'external',
                  type = 'real',
                  value = 2999,
                  texname = '\\text{MrhoZ}',
                  lhablock = 'MASS',
                  lhacode = [ 72 ])

Mpsi = Parameter(name = 'Mpsi',
                 nature = 'external',
                 type = 'real',
                 value = 3000,
                 texname = '\\text{Mpsi}',
                 lhablock = 'MASS',
                 lhacode = [ 73 ])

mh = Parameter(name = 'mh',
               nature = 'external',
               type = 'real',
               value = 125,
               texname = '\\text{mh}',
               lhablock = 'MASS',
               lhacode = [ 25 ])

mhB = Parameter(name = 'mhB',
                nature = 'external',
                type = 'real',
                value = 500,
                texname = '\\text{mhB}',
                lhablock = 'MASS',
                lhacode = [ 35 ])

Msphi = Parameter(name = 'Msphi',
                  nature = 'external',
                  type = 'real',
                  value = 3000,
                  texname = '\\text{Msphi}',
                  lhablock = 'MASS',
                  lhacode = [ 51 ])

WZ = Parameter(name = 'WZ',
               nature = 'external',
               type = 'real',
               value = 2.4952,
               texname = '\\text{WZ}',
               lhablock = 'DECAY',
               lhacode = [ 23 ])

WW = Parameter(name = 'WW',
               nature = 'external',
               type = 'real',
               value = 2.085,
               texname = '\\text{WW}',
               lhablock = 'DECAY',
               lhacode = [ 24 ])

WZB = Parameter(name = 'WZB',
                nature = 'external',
                type = 'real',
                value = 1.,
                texname = '\\text{WZB}',
                lhablock = 'DECAY',
                lhacode = [ 32 ])

WT = Parameter(name = 'WT',
               nature = 'external',
               type = 'real',
               value = 1.50833649,
               texname = '\\text{WT}',
               lhablock = 'DECAY',
               lhacode = [ 6 ])

WrhoM = Parameter(name = 'WrhoM',
                  nature = 'external',
                  type = 'real',
                  value = 1,
                  texname = '\\text{WrhoM}',
                  lhablock = 'DECAY',
                  lhacode = [ 71 ])

WrhoZ = Parameter(name = 'WrhoZ',
                  nature = 'external',
                  type = 'real',
                  value = 1,
                  texname = '\\text{WrhoZ}',
                  lhablock = 'DECAY',
                  lhacode = [ 72 ])

Wpsi = Parameter(name = 'Wpsi',
                 nature = 'external',
                 type = 'real',
                 value = 1,
                 texname = '\\text{Wpsi}',
                 lhablock = 'DECAY',
                 lhacode = [ 73 ])

Wh = Parameter(name = 'Wh',
               nature = 'external',
               type = 'real',
               value = 0.00407,
               texname = '\\text{Wh}',
               lhablock = 'DECAY',
               lhacode = [ 25 ])

WhB = Parameter(name = 'WhB',
                nature = 'external',
                type = 'real',
                value = 1,
                texname = '\\text{WhB}',
                lhablock = 'DECAY',
                lhacode = [ 35 ])

Wsphi = Parameter(name = 'Wsphi',
                  nature = 'external',
                  type = 'real',
                  value = 1,
                  texname = '\\text{Wsphi}',
                  lhablock = 'DECAY',
                  lhacode = [ 51 ])

cth = Parameter(name = 'cth',
                nature = 'internal',
                type = 'real',
                value = 'cmath.sqrt(1 - sth**2)',
                texname = 'c_B')

aEW = Parameter(name = 'aEW',
                nature = 'internal',
                type = 'real',
                value = '1/aEWM1',
                texname = '\\alpha _{\\text{EW}}')

sw2 = Parameter(name = 'sw2',
                nature = 'internal',
                type = 'real',
                value = '1 - MW**2/MZ**2',
                texname = '\\text{sw2}')

G = Parameter(name = 'G',
              nature = 'internal',
              type = 'real',
              value = '2*cmath.sqrt(aS)*cmath.sqrt(cmath.pi)',
              texname = 'G')

CKM1x1 = Parameter(name = 'CKM1x1',
                   nature = 'internal',
                   type = 'complex',
                   value = 'cmath.cos(cabi)',
                   texname = '\\text{CKM1x1}')

CKM1x2 = Parameter(name = 'CKM1x2',
                   nature = 'internal',
                   type = 'complex',
                   value = 'cmath.sin(cabi)',
                   texname = '\\text{CKM1x2}')

CKM1x3 = Parameter(name = 'CKM1x3',
                   nature = 'internal',
                   type = 'complex',
                   value = '0',
                   texname = '\\text{CKM1x3}')

CKM2x1 = Parameter(name = 'CKM2x1',
                   nature = 'internal',
                   type = 'complex',
                   value = '-cmath.sin(cabi)',
                   texname = '\\text{CKM2x1}')

CKM2x2 = Parameter(name = 'CKM2x2',
                   nature = 'internal',
                   type = 'complex',
                   value = 'cmath.cos(cabi)',
                   texname = '\\text{CKM2x2}')

CKM2x3 = Parameter(name = 'CKM2x3',
                   nature = 'internal',
                   type = 'complex',
                   value = '0',
                   texname = '\\text{CKM2x3}')

CKM3x1 = Parameter(name = 'CKM3x1',
                   nature = 'internal',
                   type = 'complex',
                   value = '0',
                   texname = '\\text{CKM3x1}')

CKM3x2 = Parameter(name = 'CKM3x2',
                   nature = 'internal',
                   type = 'complex',
                   value = '0',
                   texname = '\\text{CKM3x2}')

CKM3x3 = Parameter(name = 'CKM3x3',
                   nature = 'internal',
                   type = 'complex',
                   value = '1',
                   texname = '\\text{CKM3x3}')

vB = Parameter(name = 'vB',
               nature = 'internal',
               type = 'real',
               value = '(2*MZB)/(3.*gB)',
               texname = 'v_B')

cw = Parameter(name = 'cw',
               nature = 'internal',
               type = 'real',
               value = 'cmath.sqrt(1 - sw2)',
               texname = 'c_w')

sw = Parameter(name = 'sw',
               nature = 'internal',
               type = 'real',
               value = 'cmath.sqrt(sw2)',
               texname = 's_w')

ee = Parameter(name = 'ee',
               nature = 'internal',
               type = 'real',
               value = '2*cmath.sqrt(aEW)*cmath.sqrt(cmath.pi)',
               texname = 'e')

lamS = Parameter(name = 'lamS',
                 nature = 'internal',
                 type = 'real',
                 value = '(cth**2*mhB**2)/(2.*vB**2) + (mh**2*sth**2)/(2.*vB**2)',
                 texname = '\\text{lamS}')

ychi = Parameter(name = 'ychi',
                 nature = 'internal',
                 type = 'real',
                 value = 'Mchi/(vB*cmath.sqrt(2))',
                 texname = 'y_{\\chi }')

ypsi = Parameter(name = 'ypsi',
                 nature = 'internal',
                 type = 'real',
                 value = '(Mpsi*cmath.sqrt(2))/vB',
                 texname = 'y_{\\psi }')

yrho = Parameter(name = 'yrho',
                 nature = 'internal',
                 type = 'real',
                 value = 'MrhoZ/(vB*cmath.sqrt(2))',
                 texname = 'y_{\\rho }')

g1 = Parameter(name = 'g1',
               nature = 'internal',
               type = 'real',
               value = 'ee/cw',
               texname = 'g_1')

gw = Parameter(name = 'gw',
               nature = 'internal',
               type = 'real',
               value = 'ee/sw',
               texname = 'g_w')

vev = Parameter(name = 'vev',
                nature = 'internal',
                type = 'real',
                value = '(2*MW*sw)/ee',
                texname = 'v_0')

lam1 = Parameter(name = 'lam1',
                 nature = 'internal',
                 type = 'real',
                 value = '(cth*(-mh**2 + mhB**2)*sth)/(vB*vev)',
                 texname = '\\text{lam1}')

lamH = Parameter(name = 'lamH',
                 nature = 'internal',
                 type = 'real',
                 value = '(cth**2*mh**2)/(2.*vev**2) + (mhB**2*sth**2)/(2.*vev**2)',
                 texname = '\\text{lamH}')

yb = Parameter(name = 'yb',
               nature = 'internal',
               type = 'real',
               value = '(ymb*cmath.sqrt(2))/vev',
               texname = '\\text{yb}')

yc = Parameter(name = 'yc',
               nature = 'internal',
               type = 'real',
               value = '(ymc*cmath.sqrt(2))/vev',
               texname = '\\text{yc}')

ydo = Parameter(name = 'ydo',
                nature = 'internal',
                type = 'real',
                value = '(ymdo*cmath.sqrt(2))/vev',
                texname = '\\text{ydo}')

ye = Parameter(name = 'ye',
               nature = 'internal',
               type = 'real',
               value = '(yme*cmath.sqrt(2))/vev',
               texname = '\\text{ye}')

ym = Parameter(name = 'ym',
               nature = 'internal',
               type = 'real',
               value = '(ymm*cmath.sqrt(2))/vev',
               texname = '\\text{ym}')

ys = Parameter(name = 'ys',
               nature = 'internal',
               type = 'real',
               value = '(yms*cmath.sqrt(2))/vev',
               texname = '\\text{ys}')

yt = Parameter(name = 'yt',
               nature = 'internal',
               type = 'real',
               value = '(ymt*cmath.sqrt(2))/vev',
               texname = '\\text{yt}')

ytau = Parameter(name = 'ytau',
                 nature = 'internal',
                 type = 'real',
                 value = '(ymtau*cmath.sqrt(2))/vev',
                 texname = '\\text{ytau}')

yup = Parameter(name = 'yup',
                nature = 'internal',
                type = 'real',
                value = '(ymup*cmath.sqrt(2))/vev',
                texname = '\\text{yup}')

muH2 = Parameter(name = 'muH2',
                 nature = 'internal',
                 type = 'real',
                 value = '(lam1*vB**2)/2. + lamH*vev**2',
                 texname = '\\mu _H')

muS2 = Parameter(name = 'muS2',
                 nature = 'internal',
                 type = 'real',
                 value = 'lamS*vB**2 + (lam1*vev**2)/2.',
                 texname = '\\mu _S')

