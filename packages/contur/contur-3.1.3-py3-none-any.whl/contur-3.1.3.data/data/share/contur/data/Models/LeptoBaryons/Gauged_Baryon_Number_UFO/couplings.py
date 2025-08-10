# This file was automatically created by FeynRules 2.3.49
# Mathematica version: 12.3.1 for Microsoft Windows (64-bit) (June 24, 2021)
# Date: Mon 16 Oct 2023 21:06:11


from object_library import all_couplings, Coupling

from function_library import complexconjugate, re, im, csc, sec, acsc, asec, cot



GC_1 = Coupling(name = 'GC_1',
                value = '(-3*complex(0,1))/2.',
                order = {'NP':1})

GC_2 = Coupling(name = 'GC_2',
                value = '-0.3333333333333333*(ee*complex(0,1))',
                order = {'QED':1})

GC_3 = Coupling(name = 'GC_3',
                value = '-0.5*(ee*complex(0,1))',
                order = {'QED':1})

GC_4 = Coupling(name = 'GC_4',
                value = '(2*ee*complex(0,1))/3.',
                order = {'QED':1})

GC_5 = Coupling(name = 'GC_5',
                value = '-(ee*complex(0,1))',
                order = {'QED':1})

GC_6 = Coupling(name = 'GC_6',
                value = 'ee*complex(0,1)',
                order = {'QED':1})

GC_7 = Coupling(name = 'GC_7',
                value = 'ee**2*complex(0,1)',
                order = {'QED':2})

GC_8 = Coupling(name = 'GC_8',
                value = '-G',
                order = {'QCD':1})

GC_9 = Coupling(name = 'GC_9',
                value = 'complex(0,1)*G',
                order = {'QCD':1})

GC_10 = Coupling(name = 'GC_10',
                 value = 'complex(0,1)*G**2',
                 order = {'QCD':2})

GC_11 = Coupling(name = 'GC_11',
                 value = '(complex(0,1)*gB)/3.',
                 order = {'NP':1})

GC_12 = Coupling(name = 'GC_12',
                 value = '(-3*complex(0,1)*gB)/2.',
                 order = {'NP':1})

GC_13 = Coupling(name = 'GC_13',
                 value = '(3*complex(0,1)*gB)/2.',
                 order = {'NP':1})

GC_14 = Coupling(name = 'GC_14',
                 value = '18*cth**2*complex(0,1)*gB**2',
                 order = {'NP':2})

GC_15 = Coupling(name = 'GC_15',
                 value = '-18*cth*complex(0,1)*gB**2*sth',
                 order = {'NP':2})

GC_16 = Coupling(name = 'GC_16',
                 value = '18*complex(0,1)*gB**2*sth**2',
                 order = {'NP':2})

GC_17 = Coupling(name = 'GC_17',
                 value = '-6*cth**3*complex(0,1)*lamH*sth + 3*cth**3*complex(0,1)*lamHB*sth + 6*cth*complex(0,1)*lamB*sth**3 - 3*cth*complex(0,1)*lamHB*sth**3',
                 order = {'QED':2})

GC_18 = Coupling(name = 'GC_18',
                 value = '6*cth**3*complex(0,1)*lamB*sth - 3*cth**3*complex(0,1)*lamHB*sth - 6*cth*complex(0,1)*lamH*sth**3 + 3*cth*complex(0,1)*lamHB*sth**3',
                 order = {'QED':2})

GC_19 = Coupling(name = 'GC_19',
                 value = '-6*cth**4*complex(0,1)*lamH - 6*cth**2*complex(0,1)*lamHB*sth**2 - 6*complex(0,1)*lamB*sth**4',
                 order = {'QED':2})

GC_20 = Coupling(name = 'GC_20',
                 value = '-6*cth**4*complex(0,1)*lamB - 6*cth**2*complex(0,1)*lamHB*sth**2 - 6*complex(0,1)*lamH*sth**4',
                 order = {'QED':2})

GC_21 = Coupling(name = 'GC_21',
                 value = '-(cth**4*complex(0,1)*lamHB) - 6*cth**2*complex(0,1)*lamB*sth**2 - 6*cth**2*complex(0,1)*lamH*sth**2 + 4*cth**2*complex(0,1)*lamHB*sth**2 - complex(0,1)*lamHB*sth**4',
                 order = {'QED':2})

GC_22 = Coupling(name = 'GC_22',
                 value = '-((ee**2*complex(0,1))/sw**2)',
                 order = {'QED':2})

GC_23 = Coupling(name = 'GC_23',
                 value = '(cth**2*ee**2*complex(0,1))/(2.*sw**2)',
                 order = {'QED':2})

GC_24 = Coupling(name = 'GC_24',
                 value = '(cw**2*ee**2*complex(0,1))/sw**2',
                 order = {'QED':2})

GC_25 = Coupling(name = 'GC_25',
                 value = '(cth*ee**2*complex(0,1)*sth)/(2.*sw**2)',
                 order = {'QED':2})

GC_26 = Coupling(name = 'GC_26',
                 value = '(ee**2*complex(0,1)*sth**2)/(2.*sw**2)',
                 order = {'QED':2})

GC_27 = Coupling(name = 'GC_27',
                 value = '(ee*complex(0,1))/(2.*sw)',
                 order = {'QED':1})

GC_28 = Coupling(name = 'GC_28',
                 value = '(ee*complex(0,1))/(sw*cmath.sqrt(2))',
                 order = {'QED':1})

GC_29 = Coupling(name = 'GC_29',
                 value = '(CKM1x1*ee*complex(0,1))/(sw*cmath.sqrt(2))',
                 order = {'QED':1})

GC_30 = Coupling(name = 'GC_30',
                 value = '(CKM1x2*ee*complex(0,1))/(sw*cmath.sqrt(2))',
                 order = {'QED':1})

GC_31 = Coupling(name = 'GC_31',
                 value = '(CKM1x3*ee*complex(0,1))/(sw*cmath.sqrt(2))',
                 order = {'QED':1})

GC_32 = Coupling(name = 'GC_32',
                 value = '(CKM2x1*ee*complex(0,1))/(sw*cmath.sqrt(2))',
                 order = {'QED':1})

GC_33 = Coupling(name = 'GC_33',
                 value = '(CKM2x2*ee*complex(0,1))/(sw*cmath.sqrt(2))',
                 order = {'QED':1})

GC_34 = Coupling(name = 'GC_34',
                 value = '(CKM2x3*ee*complex(0,1))/(sw*cmath.sqrt(2))',
                 order = {'QED':1})

GC_35 = Coupling(name = 'GC_35',
                 value = '(CKM3x1*ee*complex(0,1))/(sw*cmath.sqrt(2))',
                 order = {'QED':1})

GC_36 = Coupling(name = 'GC_36',
                 value = '(CKM3x2*ee*complex(0,1))/(sw*cmath.sqrt(2))',
                 order = {'QED':1})

GC_37 = Coupling(name = 'GC_37',
                 value = '(CKM3x3*ee*complex(0,1))/(sw*cmath.sqrt(2))',
                 order = {'QED':1})

GC_38 = Coupling(name = 'GC_38',
                 value = '-0.5*(cw*ee*complex(0,1))/sw',
                 order = {'QED':1})

GC_39 = Coupling(name = 'GC_39',
                 value = '(cw*ee*complex(0,1))/sw',
                 order = {'QED':1})

GC_40 = Coupling(name = 'GC_40',
                 value = '(-2*cw*ee**2*complex(0,1))/sw',
                 order = {'QED':2})

GC_41 = Coupling(name = 'GC_41',
                 value = '(ee*complex(0,1)*sw)/(3.*cw)',
                 order = {'QED':1})

GC_42 = Coupling(name = 'GC_42',
                 value = '(-2*ee*complex(0,1)*sw)/(3.*cw)',
                 order = {'QED':1})

GC_43 = Coupling(name = 'GC_43',
                 value = '(ee*complex(0,1)*sw)/cw',
                 order = {'QED':1})

GC_44 = Coupling(name = 'GC_44',
                 value = '-0.5*(cw*ee*complex(0,1))/sw - (ee*complex(0,1)*sw)/(6.*cw)',
                 order = {'QED':1})

GC_45 = Coupling(name = 'GC_45',
                 value = '(cw*ee*complex(0,1))/(2.*sw) - (ee*complex(0,1)*sw)/(6.*cw)',
                 order = {'QED':1})

GC_46 = Coupling(name = 'GC_46',
                 value = '-0.5*(cw*ee*complex(0,1))/sw - (ee*complex(0,1)*sw)/(2.*cw)',
                 order = {'QED':1})

GC_47 = Coupling(name = 'GC_47',
                 value = '(cw*ee*complex(0,1))/(2.*sw) - (ee*complex(0,1)*sw)/(2.*cw)',
                 order = {'QED':1})

GC_48 = Coupling(name = 'GC_48',
                 value = '-0.5*(cw*ee*complex(0,1))/sw + (ee*complex(0,1)*sw)/(2.*cw)',
                 order = {'QED':1})

GC_49 = Coupling(name = 'GC_49',
                 value = '(cw*ee*complex(0,1))/(2.*sw) + (ee*complex(0,1)*sw)/(2.*cw)',
                 order = {'QED':1})

GC_50 = Coupling(name = 'GC_50',
                 value = 'cth**2*ee**2*complex(0,1) + (cth**2*cw**2*ee**2*complex(0,1))/(2.*sw**2) + (cth**2*ee**2*complex(0,1)*sw**2)/(2.*cw**2)',
                 order = {'QED':2})

GC_51 = Coupling(name = 'GC_51',
                 value = 'cth*ee**2*complex(0,1)*sth + (cth*cw**2*ee**2*complex(0,1)*sth)/(2.*sw**2) + (cth*ee**2*complex(0,1)*sth*sw**2)/(2.*cw**2)',
                 order = {'QED':2})

GC_52 = Coupling(name = 'GC_52',
                 value = 'ee**2*complex(0,1)*sth**2 + (cw**2*ee**2*complex(0,1)*sth**2)/(2.*sw**2) + (ee**2*complex(0,1)*sth**2*sw**2)/(2.*cw**2)',
                 order = {'QED':2})

GC_53 = Coupling(name = 'GC_53',
                 value = '18*cth*complex(0,1)*gB**2*vB',
                 order = {'NP':1})

GC_54 = Coupling(name = 'GC_54',
                 value = '-18*complex(0,1)*gB**2*sth*vB',
                 order = {'NP':1})

GC_55 = Coupling(name = 'GC_55',
                 value = '-(cth**3*complex(0,1)*lamHB*vB) - 6*cth*complex(0,1)*lamB*sth**2*vB + 2*cth*complex(0,1)*lamHB*sth**2*vB',
                 order = {'NP':-1,'QED':2})

GC_56 = Coupling(name = 'GC_56',
                 value = '-6*cth**3*complex(0,1)*lamB*vB - 3*cth*complex(0,1)*lamHB*sth**2*vB',
                 order = {'NP':-1,'QED':2})

GC_57 = Coupling(name = 'GC_57',
                 value = '3*cth**2*complex(0,1)*lamHB*sth*vB + 6*complex(0,1)*lamB*sth**3*vB',
                 order = {'NP':-1,'QED':2})

GC_58 = Coupling(name = 'GC_58',
                 value = '6*cth**2*complex(0,1)*lamB*sth*vB - 2*cth**2*complex(0,1)*lamHB*sth*vB + complex(0,1)*lamHB*sth**3*vB',
                 order = {'NP':-1,'QED':2})

GC_59 = Coupling(name = 'GC_59',
                 value = '(cth*ee**2*complex(0,1)*vev)/(2.*sw**2)',
                 order = {'QED':1})

GC_60 = Coupling(name = 'GC_60',
                 value = '(ee**2*complex(0,1)*sth*vev)/(2.*sw**2)',
                 order = {'QED':1})

GC_61 = Coupling(name = 'GC_61',
                 value = '-(cth**3*complex(0,1)*lamHB*vev) - 6*cth*complex(0,1)*lamH*sth**2*vev + 2*cth*complex(0,1)*lamHB*sth**2*vev',
                 order = {'QED':1})

GC_62 = Coupling(name = 'GC_62',
                 value = '-6*cth**3*complex(0,1)*lamH*vev - 3*cth*complex(0,1)*lamHB*sth**2*vev',
                 order = {'QED':1})

GC_63 = Coupling(name = 'GC_63',
                 value = '-3*cth**2*complex(0,1)*lamHB*sth*vev - 6*complex(0,1)*lamH*sth**3*vev',
                 order = {'QED':1})

GC_64 = Coupling(name = 'GC_64',
                 value = '-6*cth**2*complex(0,1)*lamH*sth*vev + 2*cth**2*complex(0,1)*lamHB*sth*vev - complex(0,1)*lamHB*sth**3*vev',
                 order = {'QED':1})

GC_65 = Coupling(name = 'GC_65',
                 value = 'cth*ee**2*complex(0,1)*vev + (cth*cw**2*ee**2*complex(0,1)*vev)/(2.*sw**2) + (cth*ee**2*complex(0,1)*sw**2*vev)/(2.*cw**2)',
                 order = {'QED':1})

GC_66 = Coupling(name = 'GC_66',
                 value = 'ee**2*complex(0,1)*sth*vev + (cw**2*ee**2*complex(0,1)*sth*vev)/(2.*sw**2) + (ee**2*complex(0,1)*sth*sw**2*vev)/(2.*cw**2)',
                 order = {'QED':1})

GC_67 = Coupling(name = 'GC_67',
                 value = '-((cth*complex(0,1)*yb)/cmath.sqrt(2))',
                 order = {'QED':1})

GC_68 = Coupling(name = 'GC_68',
                 value = '-((complex(0,1)*sth*yb)/cmath.sqrt(2))',
                 order = {'QED':1})

GC_69 = Coupling(name = 'GC_69',
                 value = '-((cth*complex(0,1)*yc)/cmath.sqrt(2))',
                 order = {'QED':1})

GC_70 = Coupling(name = 'GC_70',
                 value = '-((complex(0,1)*sth*yc)/cmath.sqrt(2))',
                 order = {'QED':1})

GC_71 = Coupling(name = 'GC_71',
                 value = '-(cth*complex(0,1)*ychi)',
                 order = {'NP':1})

GC_72 = Coupling(name = 'GC_72',
                 value = 'complex(0,1)*sth*ychi',
                 order = {'NP':1})

GC_73 = Coupling(name = 'GC_73',
                 value = '-((cth*complex(0,1)*ydo)/cmath.sqrt(2))',
                 order = {'QED':1})

GC_74 = Coupling(name = 'GC_74',
                 value = '-((complex(0,1)*sth*ydo)/cmath.sqrt(2))',
                 order = {'QED':1})

GC_75 = Coupling(name = 'GC_75',
                 value = '-((cth*complex(0,1)*ye)/cmath.sqrt(2))',
                 order = {'QED':1})

GC_76 = Coupling(name = 'GC_76',
                 value = '-((complex(0,1)*sth*ye)/cmath.sqrt(2))',
                 order = {'QED':1})

GC_77 = Coupling(name = 'GC_77',
                 value = '-((cth*complex(0,1)*ym)/cmath.sqrt(2))',
                 order = {'QED':1})

GC_78 = Coupling(name = 'GC_78',
                 value = '-((complex(0,1)*sth*ym)/cmath.sqrt(2))',
                 order = {'QED':1})

GC_79 = Coupling(name = 'GC_79',
                 value = '-((cth*complex(0,1)*ypsi)/cmath.sqrt(2))',
                 order = {'NP':1})

GC_80 = Coupling(name = 'GC_80',
                 value = '(complex(0,1)*sth*ypsi)/cmath.sqrt(2)',
                 order = {'NP':1})

GC_81 = Coupling(name = 'GC_81',
                 value = '-((cth*complex(0,1)*ys)/cmath.sqrt(2))',
                 order = {'QED':1})

GC_82 = Coupling(name = 'GC_82',
                 value = '-((complex(0,1)*sth*ys)/cmath.sqrt(2))',
                 order = {'QED':1})

GC_83 = Coupling(name = 'GC_83',
                 value = '-(cth*complex(0,1)*ysig*cmath.sqrt(2))',
                 order = {'NP':1})

GC_84 = Coupling(name = 'GC_84',
                 value = 'complex(0,1)*sth*ysig*cmath.sqrt(2)',
                 order = {'NP':1})

GC_85 = Coupling(name = 'GC_85',
                 value = '-((cth*complex(0,1)*yt)/cmath.sqrt(2))',
                 order = {'QED':1})

GC_86 = Coupling(name = 'GC_86',
                 value = '-((complex(0,1)*sth*yt)/cmath.sqrt(2))',
                 order = {'QED':1})

GC_87 = Coupling(name = 'GC_87',
                 value = '-((cth*complex(0,1)*ytau)/cmath.sqrt(2))',
                 order = {'QED':1})

GC_88 = Coupling(name = 'GC_88',
                 value = '-((complex(0,1)*sth*ytau)/cmath.sqrt(2))',
                 order = {'QED':1})

GC_89 = Coupling(name = 'GC_89',
                 value = '-((cth*complex(0,1)*yup)/cmath.sqrt(2))',
                 order = {'QED':1})

GC_90 = Coupling(name = 'GC_90',
                 value = '-((complex(0,1)*sth*yup)/cmath.sqrt(2))',
                 order = {'QED':1})

GC_91 = Coupling(name = 'GC_91',
                 value = '(ee*complex(0,1)*complexconjugate(CKM1x1))/(sw*cmath.sqrt(2))',
                 order = {'QED':1})

GC_92 = Coupling(name = 'GC_92',
                 value = '(ee*complex(0,1)*complexconjugate(CKM1x2))/(sw*cmath.sqrt(2))',
                 order = {'QED':1})

GC_93 = Coupling(name = 'GC_93',
                 value = '(ee*complex(0,1)*complexconjugate(CKM1x3))/(sw*cmath.sqrt(2))',
                 order = {'QED':1})

GC_94 = Coupling(name = 'GC_94',
                 value = '(ee*complex(0,1)*complexconjugate(CKM2x1))/(sw*cmath.sqrt(2))',
                 order = {'QED':1})

GC_95 = Coupling(name = 'GC_95',
                 value = '(ee*complex(0,1)*complexconjugate(CKM2x2))/(sw*cmath.sqrt(2))',
                 order = {'QED':1})

GC_96 = Coupling(name = 'GC_96',
                 value = '(ee*complex(0,1)*complexconjugate(CKM2x3))/(sw*cmath.sqrt(2))',
                 order = {'QED':1})

GC_97 = Coupling(name = 'GC_97',
                 value = '(ee*complex(0,1)*complexconjugate(CKM3x1))/(sw*cmath.sqrt(2))',
                 order = {'QED':1})

GC_98 = Coupling(name = 'GC_98',
                 value = '(ee*complex(0,1)*complexconjugate(CKM3x2))/(sw*cmath.sqrt(2))',
                 order = {'QED':1})

GC_99 = Coupling(name = 'GC_99',
                 value = '(ee*complex(0,1)*complexconjugate(CKM3x3))/(sw*cmath.sqrt(2))',
                 order = {'QED':1})

