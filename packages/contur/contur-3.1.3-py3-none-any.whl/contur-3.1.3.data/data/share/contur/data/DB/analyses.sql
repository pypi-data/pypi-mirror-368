PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;

-- Table for known/allowed beam configurations
-- Assumed to be colliding beams of effectively massless particles (so will need attention if we include fixed target)
-------------------------------------------------------------------------
CREATE TABLE beams (
    id      TEXT NOT NULL UNIQUE,
    collider TEXT NOT NULL,
    particle_a TEXT NOT NULL,
    particle_b TEXT NOT NULL,
    energy_a REAL NOT NULL,
    energy_b REAL NOT NULL,
    PRIMARY KEY(id)
);
INSERT INTO beams VALUES('7TeV','LHC','p+','p+',3500,3500);
INSERT INTO beams VALUES('8TeV','LHC','p+','p+',4000,4000);
INSERT INTO beams VALUES('13TeV','LHC','p+','p+',6500,6500);
-- INSERT INTO beams VALUES('em_27_p_920'); -- positron beam mode to be added for ZEUS analysis
-- INSERT INTO beams VALUES('ep_27_p_820');
-- LEP collider
-- INSERT INTO beams VALUES('em_ep_91_2','LEP','e+','e-',45.6,45.6);
-- INSERT INTO beams VALUES('pm_pp_1960'); -- Tevatron collider
INSERT INTO beams VALUES('2_76TeV','LHC','p+','p+',1380,1380); -- 2.76 TeV LHC running

-- Table for known/allowed experiments
-------------------------------------------------------------------------
CREATE TABLE experiments (
    id      TEXT NOT NULL UNIQUE,
    collider TEXT NOT NULL,
    PRIMARY KEY(id)
);
INSERT INTO experiments VALUES('CMS','LHC');
INSERT INTO experiments VALUES('ATLAS','LHC');
INSERT INTO experiments VALUES('LHCB','LHC');

-- Analysis pools (independent beam/experiment/final state configurations
-------------------------------------------------------------------------
CREATE TABLE analysis_pool (
    pool    TEXT NOT NULL UNIQUE,
    beam    TEXT,
    description TEXT,
    PRIMARY KEY(pool),
    FOREIGN KEY(beam) REFERENCES beams(id)
);

INSERT INTO analysis_pool VALUES('ATLAS_13_TAU','13TeV','tau measurements');

-- same sign leptons + missing energy
INSERT INTO analysis_pool VALUES('ATLAS_13_SSLLMET','13TeV','two same-sign leptons (e/mu) plus missing transverse momentum and jets');

-- all-hadronic inclusive measurements
INSERT INTO analysis_pool VALUES('CMS_2_76_DJET','2_76TeV','inclusive and Mueller Navelet dijet final states');
INSERT INTO analysis_pool VALUES('ATLAS_7_JETS','7TeV','inclusive hadronic final states');
INSERT INTO analysis_pool VALUES('CMS_7_JETS','7TeV','inclusive hadronic final states');
INSERT INTO analysis_pool VALUES('ATLAS_8_JETS','8TeV','inclusive hadronic final states');
INSERT INTO analysis_pool VALUES('CMS_8_JETS','8TeV','inclusive hadronic final states');
INSERT INTO analysis_pool VALUES('ATLAS_13_JETS','13TeV','inclusive hadronic final states');
INSERT INTO analysis_pool VALUES('CMS_13_JETS','13TeV','inclusive hadronic final states');

-- ALICE_2012_I944757 (charm production) good cross section but can't really use without
-- the theory prediction, since the theory uncertainties are vastly bigger than expt.

-- all-hadronic on top pole
INSERT INTO analysis_pool VALUES('ATLAS_13_TTHAD','13TeV','fully hadronic top events');
INSERT INTO analysis_pool VALUES('CMS_13_TTHAD','13TeV','fully hadronic top events');
 
-- inclusive isolated photons
INSERT INTO analysis_pool VALUES('ATLAS_7_GAMMA','7TeV','inclusive (multi)photons');
INSERT INTO analysis_pool VALUES('CMS_7_GAMMA','7TeV','inclusive (multi)photons');
INSERT INTO analysis_pool VALUES('ATLAS_8_GAMMA','8TeV','inclusive (multi)photons');
-- INSERT INTO analysis_pool VALUES('CMS_8_GAMMA','8TeV','inclusive (multi)photons');
INSERT INTO analysis_pool VALUES('ATLAS_13_GAMMA','13TeV','inclusive (multi)photons');

-- dileptons below Z pole
INSERT INTO analysis_pool VALUES('ATLAS_7_LMDY','7TeV','dileptons below the Z pole');

-- dileptons (+jets) on Z pole
INSERT INTO analysis_pool VALUES('ATLAS_7_LLJET','7TeV','dielectrons at the Z pole, plus optional jets');
INSERT INTO analysis_pool VALUES('CMS_7_LLJET','7TeV','dileptons at the Z pole, plus optional jets');
INSERT INTO analysis_pool VALUES('LHCB_7_LLJET','7TeV','dimuons at the Z pole, plus optional jets');

INSERT INTO analysis_pool VALUES('ATLAS_8_LLJET','8TeV','dileptons at the Z pole, plus optional jets'); 
INSERT INTO analysis_pool VALUES('CMS_8_LLJET','8TeV','dileptons at the Z pole, plus optional jets');
INSERT INTO analysis_pool VALUES('LHCB_8_LLJET','8TeV','dimuons at the Z pole, plus optional jets');

INSERT INTO analysis_pool VALUES('ATLAS_13_LLJET','13TeV','dileptons at the Z pole, plus optional jets');
INSERT INTO analysis_pool VALUES('CMS_13_LLJET','13TeV','dileptons at the Z pole, plus optional jets');

-- dileptons (+optional jets) above Z pole
INSERT INTO analysis_pool VALUES('ATLAS_7_HMDY','7TeV','dileptons above the Z pole');
INSERT INTO analysis_pool VALUES('ATLAS_8_HMDY','8TeV','dileptons above the Z pole');
INSERT INTO analysis_pool VALUES('ATLAS_13_HMDY','13TeV','dileptons above the Z pole');
INSERT INTO analysis_pool VALUES('CMS_13_HMDY','13TeV','dileptons above the Z pole');

-- three leptons
INSERT INTO analysis_pool VALUES('ATLAS_8_3L','8TeV','trileptons');
INSERT INTO analysis_pool VALUES('CMS_8_3L','8TeV','trileptons');
INSERT INTO analysis_pool VALUES('ATLAS_13_3L','13TeV','trileptons');

-- four leptons
INSERT INTO analysis_pool VALUES('ATLAS_7_4L','7TeV','four leptons');
INSERT INTO analysis_pool VALUES('ATLAS_8_4L','8TeV','four leptons');
INSERT INTO analysis_pool VALUES('ATLAS_13_4L','13TeV','four leptons');

INSERT INTO analysis_pool VALUES('ATLAS_7_LLMET','7TeV','dileptons plus missing transverse momentum');
INSERT INTO analysis_pool VALUES('ATLAS_8_LLMET','8TeV','dileptons plus missing transverse momentum');

-- three leptons(WZ) + MET  and two leptons with two JETs (WW)

INSERT INTO analysis_pool VALUES('CMS_13_3LJET','13TeV','dileptons or trileptons + MET');

-- two leptons plus gamma
INSERT INTO analysis_pool VALUES('ATLAS_7_LL_GAMMA','7TeV','dileptons plus photon(s)');
INSERT INTO analysis_pool VALUES('ATLAS_8_LL_GAMMA','8TeV','dileptons plus photon(s)');
INSERT INTO analysis_pool VALUES('ATLAS_13_LL_GAMMA','13TeV','dileptons plus photon');
INSERT INTO analysis_pool VALUES('CMS_7_LL_GAMMA','7TeV','dimuons plus photon(s)');

-- two leptons + gamma + associated jets (not needed since the measurements includethe 0 jet and more cases)
-- INSERT INTO analysis_pool VALUES('ATLAS_13_LL_GAMMA_JET','13TeV','dileptons + photon + jets');

-- lepton, MET (+optional jets)
INSERT INTO analysis_pool VALUES('ATLAS_7_LMETJET','7TeV','lepton, missing transverse momentum, plus optional jets (typically W, semi-leptonic ttbar analyses)');
INSERT INTO analysis_pool VALUES('CMS_7_LMETJET','7TeV','electron, missing transverse momentum, plus optional jets (typically W, semi-leptonic ttbar analyses)');
INSERT INTO analysis_pool VALUES('ATLAS_8_LMETJET','8TeV','lepton, missing transverse momentum, plus optional jets (typically W, semi-leptonic ttbar analyses)');
INSERT INTO analysis_pool VALUES('CMS_8_LMETJET','8TeV','lepton, missing transverse momentum, plus optional jets (typically W, semi-leptonic ttbar analyses)');
INSERT INTO analysis_pool VALUES('ATLAS_13_LMETJET','13TeV','lepton, missing transverse momentum, plus optional jets (typically W, semi-leptonic ttbar analyses)');
INSERT INTO analysis_pool VALUES('CMS_13_LMETJET','13TeV','lepton, missing transverse momentum, plus optional jets (typically W, semi-leptonic ttbar analyses)');

INSERT INTO analysis_pool VALUES('LHCB_8_LJET','8TeV','muons (aimed at W)');


-- lepton, met, gamma
INSERT INTO analysis_pool VALUES('ATLAS_7_LMET_GAMMA','7TeV','lepton, missing transverse momentum, plus photon');
INSERT INTO analysis_pool VALUES('ATLAS_13_LMET_GAMMA','13TeV','semileptonic ttbar plus photon');
--INSERT INTO analysis_pool VALUES('ATLAS_13_L1L2_JETS', '13TeV', 'e plus mu plus b-jets');

INSERT INTO analysis_pool VALUES('ATLAS_13_L1L2MET_GAMMA','13TeV','fully leptonic ttbar plus photon');

-- dileptons (non-resonant), met
INSERT INTO analysis_pool VALUES('ATLAS_7_L1L2MET','7TeV','WW analyses in dileptons plus missing transverse momentum channel');
INSERT INTO analysis_pool VALUES('ATLAS_8_L1L2MET','8TeV','WW analyses in dileptons plus missing transverse momentum channel');
INSERT INTO analysis_pool VALUES('CMS_8_L1L2MET','8TeV','WW analyses in dileptons plus missing transverse momentum channel');
INSERT INTO analysis_pool VALUES('ATLAS_13_L1L2MET','13TeV','unlike dileptons plus missing transverse momentum channel, with jet veto');
INSERT INTO analysis_pool VALUES('ATLAS_13_L1L2METJET','13TeV','unlike dileptons plus missing transverse momentum and jets');

-- dileptons, jet
INSERT INTO analysis_pool VALUES('CMS_13_L1L2MET','13TeV','WW analyses in dileptons plus optional jets');
--INSERT INTO analysis_pool VALUES('CMS_13_LLJET','13TeV','Z/gamma->ll analyses');


-- dileptons+b
INSERT INTO analysis_pool VALUES('LHCB_13_L1L2B','13TeV','top pairs via e mu plus b');

-- gamma plus MET
INSERT INTO analysis_pool VALUES('ATLAS_8_GAMMA_MET','8TeV','photon plus missing transverse momentum');
INSERT INTO analysis_pool VALUES('ATLAS_13_GAMMA_MET','13TeV','photon plus missing transverse momentum');

-- hadrons plus MET
INSERT INTO analysis_pool VALUES('ATLAS_13_METJET','13TeV','missing transverse momentum plus jets');

-- unlike dileptons, MET, photon (WWgamma)
INSERT INTO analysis_pool VALUES('CMS_13_L1L2MET_GAMMA','13TeV','unlike dileptons, MET, photons');
-- INSERT INTO analysis_pool VALUES('CMS_13_METJET','13TeV','missing transverse momentum plus jets');

-- track based minimum biased
-- INSERT INTO analysis_pool VALUES('ATLAS_13_TRA','13TeV','track based events');


-- OTHER BEAMS

-- HERA
-- NC DIS inclusive dijets
-- INSERT INTO analysis_pool VALUES('ZEUS_em_27_5_p_920_DJETS', 'em_27_5_p_920','single and double differential inclusive dijet cross sections in NC DIS of em_p beam');
-- INSERT INTO analysis_pool VALUES('ZEUS_ep_27.5_p_920_DJETS', 'ep_27.5_p_920','single and double differential inclusive dijet cross sections in NC DIS of ep_p beam');

-- NC DIS transverse energy flow 
-- INSERT INTO analysis_pool VALUES('H1_ep_27_5_p_820_TE', 'ep_27_5_p_820', 'transverse energy');

-- LEP
-- Hadronic Z decay in EE collisions
-- INSERT INTO analysis_pool VALUES('DELPHI_em_ep_91_2_LLJET', 'em_ep_91_2', 'hadronic z decay to two leptons');
-- INSERT INTO analysis_pool VALUES('OPAL_912_JETS', 'em_ep_91_2', 'z decay to multiple hadronic final states');
-- INSERT INTO analysis_pool VALUES('OPAL_912_JETS_GAMMA', 'em_ep_91_2', 'z decay to hadronic and photon final states');
-- INSERT INTO analysis_pool VALUES('ALEPH_em_ep_91_2_JETS', 'em_ep_91_2', 'z decay to multiple hadronic final states');
-- INSERT INTO analysis_pool VALUES('L3_em_ep_91_2_JETS', 'em_ep_91_2', 'z decay to multiple hadronic final states');

-- TEVATRON
-- dileptons
-- INSERT INTO analysis_pool VALUES('D0_pm_pp_1960_L1L2', 'pm_pp_1960', 'z_star and gamma to dileptons production');

--ttbar + bjets -> L1L2
--INSERT INTO analysis_pool VALUES('ATLAS_13_L1L2METJET','13TeV','ttbar to jets and e mu pair');  --DB



-- Now the actual analyses, assigning them to pools
-------------------------------------------------------------------------
-- id: is the uninque identifier of the analysis, including any options strings.
-- plots, or be 1 for event count plots.
-- pool: the analysis pool this is assigned to.

CREATE TABLE analysis (
    id      TEXT NOT NULL UNIQUE,
    pool    TEXT,
    PRIMARY KEY(id),
    FOREIGN KEY(pool) REFERENCES analysis_pool(pool)
);


----------------------------------

-- Superseded/deprecated analyses
-- INSERT INTO analysis VALUES('ATLAS_2012_I1083318',NULL);
-- INSERT INTO analysis VALUES('ATLAS_2011_I945498',NULL);
-- INSERT INTO analysis VALUES('ATLAS_2011_I921594',NULL);
-- INSERT INTO analysis VALUES('ATLAS_2011_S9128077',NULL);

--2.76 TeV hadronic
INSERT INTO analysis VALUES('CMS_2021_I1963239','CMS_2_76_DJET');

-- 7 TeV fully hadronic
INSERT INTO analysis VALUES('ATLAS_2016_I1478355','ATLAS_7_JETS');
INSERT INTO analysis VALUES('ATLAS_2014_I1325553','ATLAS_7_JETS');
INSERT INTO analysis VALUES('ATLAS_2014_I1268975','ATLAS_7_JETS');
INSERT INTO analysis VALUES('ATLAS_2014_I1326641','ATLAS_7_JETS');
INSERT INTO analysis VALUES('ATLAS_2014_I1307243','ATLAS_7_JETS');
INSERT INTO analysis VALUES('CMS_2014_I1298810','CMS_7_JETS');
INSERT INTO analysis VALUES('CMS_2013_I1273574','CMS_7_JETS');
INSERT INTO analysis VALUES('CMS_2013_I1208923','CMS_7_JETS');
INSERT INTO analysis VALUES('CMS_2012_I1089835','CMS_7_JETS');

-- 7 TeV photons
INSERT INTO analysis VALUES('ATLAS_2012_I1093738','ATLAS_7_GAMMA');
INSERT INTO analysis VALUES('ATLAS_2013_I1244522','ATLAS_7_GAMMA');
INSERT INTO analysis VALUES('ATLAS_2013_I1263495','ATLAS_7_GAMMA');
INSERT INTO analysis VALUES('ATLAS_2012_I1199269','ATLAS_7_GAMMA');
INSERT INTO analysis VALUES('CMS_2014_I1266056','CMS_7_GAMMA');

-- 7 TeV high mass Drell Yan
INSERT INTO analysis VALUES('ATLAS_2013_I1234228','ATLAS_7_HMDY');


-- 7 TeV Z+jets
INSERT INTO analysis VALUES('ATLAS_2013_I1230812','ATLAS_7_LLJET');
INSERT INTO analysis VALUES('ATLAS_2014_I1306294:LMODE=EL','ATLAS_7_LLJET'); -- this really needs a "both" mode.
INSERT INTO analysis VALUES('CMS_2015_I1310737','CMS_7_LLJET');
INSERT INTO analysis VALUES('LHCB_2014_I1262703','LHCB_7_LLJET');

-- 7 TeV inclusive Z
INSERT INTO analysis VALUES('ATLAS_2016_I1502620:LMODE=Z','ATLAS_7_LLJET');
INSERT INTO analysis VALUES('LHCB_2012_I1208102','LHCB_7_LLJET');

-- 7 TeV ttbar --- TODO this can be split into E and MU channels
INSERT INTO analysis VALUES('ATLAS_2015_I1345452','ATLAS_7_LMETJET');

-- 7 TeV Low mass DY
INSERT INTO analysis VALUES('ATLAS_2014_I1288706','ATLAS_7_LMDY');

-- 7 TeV single jet masses: The rivet routines actually use only electrons, even though
-- the measurement used muons too. Not very confident about the normalisation.
INSERT INTO analysis VALUES('CMS_2013_I1224539:JMODE=W','CMS_7_LMETJET');
INSERT INTO analysis VALUES('CMS_2013_I1224539:JMODE=Z','CMS_7_LLJET');

-- 7 TeV W+jets.
INSERT INTO analysis VALUES('ATLAS_2016_I1502620:LMODE=W','ATLAS_7_LMETJET');
INSERT INTO analysis VALUES('ATLAS_2014_I1319490','ATLAS_7_LMETJET');
INSERT INTO analysis VALUES('CMS_2014_I1303894','CMS_7_LMETJET');

-- 7 TeV W+charm
INSERT INTO analysis VALUES('ATLAS_2014_I1282447','ATLAS_7_LMETJET');

-- 7 TeV W+b
INSERT INTO analysis VALUES('ATLAS_2013_I1219109','ATLAS_7_LMETJET'); --W plus b jets

-- 7 TeV Z+bb
INSERT INTO analysis VALUES('CMS_2013_I1256943','CMS_7_LLJET');

-- 7 TeV WW. Plots in fb.
INSERT INTO analysis VALUES('ATLAS_2013_I1190187','ATLAS_7_L1L2MET'); -- jet veto is correctly applied in fiducial cuts.

-- 7 TeV dibosons, plots in fb
INSERT INTO analysis VALUES('ATLAS_2013_I1217863:LMODE=ZEL','ATLAS_7_LL_GAMMA');
INSERT INTO analysis VALUES('ATLAS_2013_I1217863:LMODE=ZMU','ATLAS_7_LL_GAMMA');
INSERT INTO analysis VALUES('CMS_2015_I1346843','CMS_7_LL_GAMMA');

INSERT INTO analysis VALUES('ATLAS_2013_I1217863:LMODE=WEL','ATLAS_7_LMET_GAMMA');
INSERT INTO analysis VALUES('ATLAS_2013_I1217863:LMODE=WMU','ATLAS_7_LMET_GAMMA');
INSERT INTO analysis VALUES('ATLAS_2012_I1203852:LMODE=LL','ATLAS_7_4L');
INSERT INTO analysis VALUES('ATLAS_2012_I1203852:LMODE=LNU','ATLAS_7_LLMET');

-- 8 TeV fully hadronic
-- plots in fb
INSERT INTO analysis VALUES('ATLAS_2015_I1394679','ATLAS_8_JETS');
INSERT INTO analysis VALUES('ATLAS_2017_I1598613:BMODE=3MU','ATLAS_8_JETS');
-- for the b hadron mode
-- plots in pb
INSERT INTO analysis VALUES('ATLAS_2017_I1604271','ATLAS_8_JETS');
INSERT INTO analysis VALUES('CMS_2016_I1487277','CMS_8_JETS');
INSERT INTO analysis VALUES('CMS_2017_I1598460','CMS_8_JETS'); -- triple differential dijets

-- normalised, no total xsec yet INSERT INTO analysis VALUES('CMS_2016_I1421646',19700,'CMS_8_JETS');

-- 8 TeV photons
-- in pb
INSERT INTO analysis VALUES('ATLAS_2016_I1457605','ATLAS_8_GAMMA');
INSERT INTO analysis VALUES('ATLAS_2017_I1632756','ATLAS_8_GAMMA'); -- +hf
-- in fb
INSERT INTO analysis VALUES('ATLAS_2017_I1591327','ATLAS_8_GAMMA');
INSERT INTO analysis VALUES('ATLAS_2014_I1306615','ATLAS_8_GAMMA'); -- higgs to photons
INSERT INTO analysis VALUES('ATLAS_2017_I1644367','ATLAS_8_GAMMA'); -- 3gamma (fb)


-- 8 TeV High mass DY
-- in pb
INSERT INTO analysis VALUES('ATLAS_2016_I1467454:LMODE=EL','ATLAS_8_HMDY');
INSERT INTO analysis VALUES('ATLAS_2016_I1467454:LMODE=MU','ATLAS_8_HMDY');

-- 8 TeV leptons+MET, dileptons

-- normalised
INSERT INTO analysis VALUES('ATLAS_2014_I1279489','ATLAS_8_LLJET'); -- electroweak Z+jets

INSERT INTO analysis VALUES('ATLAS_2015_I1408516:LMODE=EL','ATLAS_8_LLJET'); -- Z production -- lose some sensitivity by combining these two.
INSERT INTO analysis VALUES('ATLAS_2015_I1408516:LMODE=MU','ATLAS_8_LLJET'); -- Z production

INSERT INTO analysis VALUES('ATLAS_2019_I1744201','ATLAS_8_LLJET'); -- Z+jets
INSERT INTO analysis VALUES('CMS_2016_I1471281:VMODE=Z','CMS_8_LLJET'); -- Z pT
INSERT INTO analysis VALUES('CMS_2016_I1471281:VMODE=W','CMS_8_LMETJET'); -- W pT

-- plots in pb
INSERT INTO analysis VALUES('ATLAS_2017_I1589844','ATLAS_8_LLJET');
INSERT INTO analysis VALUES('CMS_2017_I1499471','CMS_8_LLJET');
INSERT INTO analysis VALUES('CMS_2016_I1491953','CMS_8_LMETJET');
INSERT INTO analysis VALUES('ATLAS_2015_I1404878','ATLAS_8_LMETJET');


INSERT INTO analysis VALUES('LHCB_2016_I1454404:MODE=WJET','LHCB_8_LJET');
INSERT INTO analysis VALUES('LHCB_2016_I1454404:MODE=ZJET','LHCB_8_LLJET');

-- ATLAS_2016_I1487726: collinear Wj at 8 TeV Cross sections, but the theory uncertainty is too large
-- to use it without the having the theory prediction

-- plots in fb
INSERT INTO analysis VALUES('CMS_2016_I1454211','CMS_8_LMETJET'); -- NB partonic phase space?
INSERT INTO analysis VALUES('ATLAS_2015_I1397637','ATLAS_8_LMETJET'); -- ttbar
INSERT INTO analysis VALUES('ATLAS_2017_I1517194','ATLAS_8_LMETJET'); -- electroweak W+jets
INSERT INTO analysis VALUES('ATLAS_2018_I1635273:LMODE=EL','ATLAS_8_LMETJET'); -- W+jets. NB some plots in pb -- this really needs a "both" mode.
INSERT INTO analysis VALUES('ATLAS_2018_I1635273:LMODE=MU','ATLAS_8_LMETJET'); -- W+jets. NB some plots in pb -- this really needs a "both" mode.

-- plots in fb
INSERT INTO analysis VALUES('CMS_2017_I1518399','CMS_8_LMETJET');  -- TTBAR
INSERT INTO analysis VALUES('ATLAS_2016_I1426515','ATLAS_8_L1L2MET'); -- nb jet veto is implemented in fiducial cuts.
INSERT INTO analysis VALUES('CMS_2017_I1467451','CMS_8_L1L2MET'); -- nb b-jet veto is NOT implemented in fiducial cuts; and large data driven bg subtraction.

-- fb
INSERT INTO analysis VALUES('ATLAS_2015_I1394865','ATLAS_8_4L');
INSERT INTO analysis VALUES('ATLAS_2014_I1310835','ATLAS_8_4L');
INSERT INTO analysis VALUES('ATLAS_2016_I1494075:LMODE=4L','ATLAS_8_4L');
INSERT INTO analysis VALUES('ATLAS_2016_I1494075:LMODE=2L2NU','ATLAS_8_LLMET');

INSERT INTO analysis VALUES('ATLAS_2016_I1448301:LMODE=LL','ATLAS_8_LL_GAMMA');
INSERT INTO analysis VALUES('ATLAS_2016_I1448301:LMODE=NU','ATLAS_8_GAMMA_MET');
INSERT INTO analysis VALUES('ATLAS_2016_I1492320:LMODE=3L','ATLAS_8_3L');
INSERT INTO analysis VALUES('ATLAS_2016_I1492320:LMODE=2L2J','ATLAS_8_L1L2MET'); -- nb b-jet veto IS implemented in fiducial cuts
INSERT INTO analysis VALUES('ATLAS_2016_I1444991','ATLAS_8_L1L2MET'); -- nb jet veto IS implemented in fiducial cuts; but large data-driven top subtraction

INSERT INTO analysis VALUES('CMS_2016_I1487288','CMS_8_3L');

-- 13 TeV fully hadronic
INSERT INTO analysis VALUES('ATLAS_2018_I1634970','ATLAS_13_JETS');
INSERT INTO analysis VALUES('ATLAS_2019_I1724098','ATLAS_13_JETS'); -- jet substructure.
INSERT INTO analysis VALUES('ATLAS_2017_I1637587','ATLAS_13_JETS'); -- soft drop jet mass
INSERT INTO analysis VALUES('ATLAS_2020_I1808726','ATLAS_13_JETS');  -- multijet event shapes
INSERT INTO analysis VALUES('CMS_2019_I1753720','CMS_13_TTHAD'); -- all-jet top events with b-jets.
INSERT INTO analysis VALUES('CMS_2021_I1932460','CMS_13_JETS');
INSERT INTO analysis VALUES('CMS_2021_I1847230:MODE=QCD13TeV','CMS_13_JETS'); -- 13TeV mode three jets
INSERT INTO analysis VALUES('CMS_2021_I1847230:MODE=QCD8TeV','CMS_8_JETS'); -- 8TeV mode three jets

-- INSERT INTO analysis VALUES('ATLAS_2019_I1772062','ATLAS_13_JETS'); -- soft drop variables
-- (not really suitable, at least without more work. normalisation not provided, and theory uncertainties large)

INSERT INTO analysis VALUES('CMS_2016_I1459051','CMS_13_JETS');
INSERT INTO analysis VALUES('CMS_2018_I1682495','CMS_13_JETS'); -- jet mass

-- 13 TeV DY. 
INSERT INTO analysis VALUES('ATLAS_2019_I1725190','ATLAS_13_HMDY'); -- lumi is set in routine, to give event counts
INSERT INTO analysis VALUES('CMS_2018_I1711625','CMS_13_HMDY');    -- plots in pb

-- 13 TeV dileptons+jets
-- plots in pb
INSERT INTO analysis VALUES('ATLAS_2017_I1627873','ATLAS_13_LLJET');
INSERT INTO analysis VALUES('ATLAS_2022_I2077570','ATLAS_13_LLJET'); -- Z+jets
INSERT INTO analysis VALUES('ATLAS_2017_I1514251:LMODE=EMU','ATLAS_13_LLJET'); -- Z+jets (we potentially lose some sensitivity here in some cases by only looking at the combined ones).
INSERT INTO analysis VALUES('ATLAS_2020_I1788444','ATLAS_13_LLJET'); -- Z+bb
INSERT INTO analysis VALUES('ATLAS_2020_I1803608','ATLAS_13_LLJET'); -- Electroweak Z+jets
INSERT INTO analysis VALUES('ATLAS_2019_I1768911','ATLAS_13_LLJET'); -- plots in pb
INSERT INTO analysis VALUES('CMS_2022_I2079374','CMS_13_LLJET'); -- CMS inclusive dilepton (Z pole and above, so kept in LL rather than HMDY
INSERT INTO analysis VALUES('CMS_2018_I1667854:LMODE=EMU','CMS_13_LLJET'); -- Z+jets
INSERT INTO analysis VALUES('CMS_2019_I1753680:LMODE=EMU','CMS_13_LLJET'); -- Z production
INSERT INTO analysis VALUES('CMS_2020_I1814328','CMS_13_L1L2MET'); -- WW -> 2l with one or zero jet. Includes SF leptons but excludes the Z pole.
INSERT INTO analysis VALUES('CMS_2021_I1866118','CMS_13_LLJET'); -- DY Z production -> mm 

INSERT INTO analysis VALUES('CMS_2021_I1847230:MODE=ZJet','CMS_8_LLJET');-- Z (dimuons) + jets in ZJet mode need to be careful when using these histos! Normalisation factors are uncertain. 

INSERT INTO analysis VALUES('ATLAS_2024_I2809112','ATLAS_13_L1L2METJET'); --DB Test


-- plot in fb
INSERT INTO analysis VALUES('ATLAS_2019_I1738841','ATLAS_13_SSLLMET'); -- Electroweak same sign WW -> 2l at least 2 jets

-- 13 TeV leptons+MET
INSERT INTO analysis VALUES('CMS_2017_I1610623','CMS_13_LMETJET'); -- W+jets
INSERT INTO analysis VALUES('CMS_2016_I1491950','CMS_13_LMETJET'); --ttbar
INSERT INTO analysis VALUES('CMS_2018_I1662081','CMS_13_LMETJET'); --ttbar
INSERT INTO analysis VALUES('CMS_2018_I1663958','CMS_13_LMETJET'); -- ttbar+jets (pb)
INSERT INTO analysis VALUES('CMS_2019_I1705068','CMS_13_LMETJET'); -- W+charm
INSERT INTO analysis VALUES('CMS_2019_I1744604','CMS_13_LMETJET'); -- single top
INSERT INTO analysis VALUES ('CMS_2021_I1901295','CMS_13_LMETJET'); -- semileptonic ttbar (pb)

INSERT INTO analysis VALUES('ATLAS_2017_I1614149','ATLAS_13_LMETJET'); --ttbar
INSERT INTO analysis VALUES('ATLAS_2019_I1750330:TYPE=BOTH','ATLAS_13_LMETJET'); --ttbar
INSERT INTO analysis VALUES('ATLAS_2023_I2628732','ATLAS_13_LMETJET'); --W+D
INSERT INTO analysis VALUES('ATLAS_2022_I2037744','ATLAS_13_LMETJET'); --semileptonic ttbar

-- 13 TeV photon + MET
INSERT INTO analysis VALUES('ATLAS_2018_I1698006:LVETO=ON','ATLAS_13_GAMMA_MET');


INSERT INTO analysis VALUES('LHCB_2018_I1662483','LHCB_13_L1L2B'); --ttbar

-- 13 TeV 4 leptons
INSERT INTO analysis VALUES('ATLAS_2017_I1625109','ATLAS_13_4L');  -- ZZ
INSERT INTO analysis VALUES('ATLAS_2019_I1720442','ATLAS_13_4L');  -- inclusive
INSERT INTO analysis VALUES('ATLAS_2021_I1849535','ATLAS_13_4L');  -- inclusive
INSERT INTO analysis VALUES('ATLAS_2023_I2690799','ATLAS_13_4L');  -- 4L + 2 jets

-- Various BG regions from LQ search. plots in pb
INSERT INTO analysis VALUES('ATLAS_2019_I1718132:LMODE=ELMU','ATLAS_13_L1L2METJET');

-- SUSY insprired WW
INSERT INTO analysis VALUES('ATLAS_2022_I2103950','ATLAS_13_L1L2MET');

-- lost some potential sensitivity by combining these two.
INSERT INTO analysis VALUES('ATLAS_2019_I1718132:LMODE=ELEL','ATLAS_13_LLJET');
INSERT INTO analysis VALUES('ATLAS_2019_I1718132:LMODE=MUMU','ATLAS_13_LLJET');

-- b and c + Z
INSERT INTO analysis VALUES('ATLAS_2024_I2771257','ATLAS_13_LLJET');

INSERT INTO analysis VALUES('ATLAS_2018_I1656578','ATLAS_13_LMETJET'); --Top + jets
INSERT INTO analysis VALUES('ATLAS_2018_I1705857','ATLAS_13_LMETJET'); --Top + b jets (normalised)

-- 13 TeV MET+JET
INSERT INTO analysis VALUES('ATLAS_2017_I1609448','ATLAS_13_METJET'); -- HAVE THEORY
INSERT INTO analysis VALUES('ATLAS_2024_I2765017:TYPE=BSM','ATLAS_13_METJET');  -- HAVE THEORY. Full Run-2 measurement.
INSERT INTO analysis VALUES('ATLAS_2016_I1458270','ATLAS_13_METJET'); -- HAVE THEORY. 0l+MET+nJets search. Lumi is set to 3.2 in the routine

-- ditau
INSERT INTO analysis VALUES('ATLAS_2025_I2905252','ATLAS_13_TAU');  -- full run 2

-- INSERT INTO analysis VALUES('CMS_2020_I1837084','CMS_13_METJET'); -- CMS z->vv; however, rivet runs only on muons

-- hadronic top
INSERT INTO analysis VALUES('ATLAS_2018_I1646686','ATLAS_13_TTHAD'); -- Hadronic top pairs (pb)
INSERT INTO analysis VALUES('ATLAS_2020_I1801434','ATLAS_13_TTHAD'); -- Hadronic top pairs (pb)
INSERT INTO analysis VALUES('CMS_2019_I1764472','CMS_13_TTHAD'); -- Hadronic top pairs (fb)
INSERT INTO analysis VALUES('ATLAS_2022_I2077575','ATLAS_13_TTHAD'); -- Hadronic top pairs (fb) boosted

-- 13 TeV ttbar + gamma
INSERT INTO analysis VALUES('ATLAS_2018_I1707015:LMODE=SINGLE','ATLAS_13_LMET_GAMMA'); -- semileptonic
INSERT INTO analysis VALUES('ATLAS_2018_I1707015:LMODE=DILEPTON','ATLAS_13_L1L2MET_GAMMA'); -- leptonic
INSERT INTO analysis VALUES('ATLAS_2024_I2768921:LMODE=SINGLE','ATLAS_13_LMET_GAMMA'); -- semileptonic
INSERT INTO analysis VALUES('ATLAS_2024_I2768921:LMODE=DILEPTON','ATLAS_13_L1L2MET_GAMMA'); -- leptonic


-- 13 TeV ttbar + jets
INSERT InTO analysis VALUES('ATLAS_2023_I2648096', 'ATLAS_13_L1L2METJET'); -- dileptonic ttbar + jets (fb)

-- 13 TeV photons
INSERT INTO analysis VALUES('ATLAS_2021_I1887997','ATLAS_13_GAMMA');
INSERT INTO analysis VALUES('ATLAS_2017_I1645627','ATLAS_13_GAMMA');
INSERT INTO analysis VALUES('ATLAS_2019_I1772071','ATLAS_13_GAMMA');
INSERT INTO analysis VALUES('ATLAS_2022_I2023464','ATLAS_13_GAMMA');
INSERT INTO analysis VALUES('ATLAS_2024_I2765017:MODE=EXTRAPOLATED:TYPE=BSM','ATLAS_13_GAMMA');  -- the photon xsec from this paper


-- 13 TeV photons+ll
INSERT INTO analysis VALUES('ATLAS_2019_I1764342','ATLAS_13_LL_GAMMA'); -- Z+gamma
INSERT INTO analysis VALUES('ATLAS_2022_I2593322','ATLAS_13_LL_GAMMA'); -- Z+diphoton
INSERT INTO analysis VALUES('ATLAS_2022_I2614196','ATLAS_13_LL_GAMMA'); -- Z+gamma (sometimes in association with jets) 

-- 13 TeV WW production cross-section
INSERT INTO analysis VALUES('ATLAS_2019_I1734263','ATLAS_13_L1L2MET'); -- no jets
INSERT INTO analysis VALUES('ATLAS_2021_I1852328','ATLAS_13_L1L2METJET'); -- inclusive of possible jets

-- 13 TeV WWgamma
INSERT INTO analysis VALUES('CMS_2023_I2709669','CMS_13_L1L2MET_GAMMA');

-- 13 TeV leptonic ttbar
INSERT INTO analysis VALUES('ATLAS_2019_I1759875','ATLAS_13_L1L2METJET');

-- 13 TeV

-- dodgy ATLAS 13TeV 3L
INSERT INTO analysis VALUES('ATLAS_2016_I1469071','ATLAS_13_3L');

-- 13 TeV track based minimum biased events, in pb^{-1}
INSERT INTO analysis VALUES('ATLAS_2016_I1419652','ATLAS_13_JETS'); -- 
INSERT INTO analysis VALUES('ATLAS_2016_I1467230','ATLAS_13_JETS'); --  with low pT tracks
INSERT INTO analysis VALUES('ATLAS_2019_I1740909','ATLAS_13_JETS'); --  jet fragmentation using charged particles
INSERT INTO analysis VALUES('ATLAS_2020_I1790256','ATLAS_13_JETS'); --  Lund jet plane with charged particles

--13 TeV WW or WZ production cross-section with three or two leptons
INSERT INTO analysis VALUES('CMS_2020_I1794169','CMS_13_3LJET'); 

INSERT INTO analysis VALUES('CMS_2022_I2080534','CMS_13_L1L2MET');

-- OTHER BEAMS ANALYSES

-- HERA
-- INSERT INTO analysis VALUES('ZEUS_2010_I875006', 203.0, 'ZEUS_em275_920_DJETS'); -- inclusive diject cross sections (highest Q2 dataset of ep and em data used) 
-- INSERT INTO analysis VALUES('H1_2000_S4129130', 8.2, 'H1_ep27_820_TE'); -- transverse energy flow (using highest Q2 luminosity)

-- LEP Z decays
-- INSERT INTO analysis VALUES('DELPHI_1994_I375963', 0.0405, 'DELPHI_em_ep_91_2_LLJET'); -- dimuons
-- INSERT INTO analysis VALUES('OPAL_1992_I321190', 'pb', 'OPAL_912_JETS'); -- Charged Particle Multiplicities of hadronic final states (normalised but we don't have the value. can't use.)
-- INSERT INTO analysis VALUES('ALEPH_2001_I555653', 160, 'ALEPH_em_ep_91_2'); -- tau polarization (lots of different decay modes?)
-- INSERT INTO analysis VALUES('ALEPH_1996_I421984', 132, 'ALEPH_em_ep_91_2_JETS'); -- tau decays with eta and omega mesons
-- INSERT INTO analysis VALUES('L3_1994_I374698', 35, 'L3_em_ep_91_2_JETS'); -- particle identification and multiple decay modes?
-- INSERT INTO analysis VALUES('L3_1997_I427107', 112, 'L3_em_ep_91_2_JETS'); -- eta' and omega meson production rates
-- INSERT INTO analysis VALUES('L3_1998_I467929', 149, 'l3_em_ep_91_2_JETS'); -- multiple different final states?
-- INSERT INTO analysis VALUES('OPAL_1993_S2692198', 'pb', 'OPAL_912_JETS_GAMMA'); -- photon production from quarks (normalised to hadronic Z. Can't use unless we get the SM prediction.)
-- INSERT INTO analysis VALUES('OPAL_1994_S2927284', 'pb', 'OPAL_912_JETS'); -- meson and hadron production rates (don't have the normalisation)
-- INSERT INTO analysis VALUES('OPAL_1995_I393503', 45.9, 'OPAL_em_ep_91_2_JETS'); -- K0 particle identification?
-- INSERT INTO analysis VALUES('OPAL_1998_S3780481', 177, 'OPAL_em_ep_91_2_JETS'); -- qqbar fragmentation functions
-- INSERT INTO analysis VALUES('OPAL_2001_I554583', 151, 'OPAL_em_ep_91_2_JETS'); -- tau polarization (lots of decay modes?)

-- TEVATRON
-- INSERT INTO analysis VALUES('D0_2015_I1324946', 10.4, 'D0_pm_pp_1960_L1L2'); -- Zstarandphoton production to two muons, fb-1

-- VARIOUS ANALYSIS WHICH HAVE BEEN CONSIDERED BUT NOT CURRENTLY USED
-- See also the gitlab "new data" tickets.
-- https://gitlab.com/hepcedar/contur/-/issues?scope=all&state=all&label_name[]=New%20data
-- Note that the ones where we don't have normalisation could be used if we had SM theory.
--
-- -------------------------------------------------------------------------------------------------------------------
-- TODO: Why aren't we using these? 
-- -------------------------------------------------------------------------------------------------------------------
-- ATLAS_2017_I1626105  Dileptonic ttbar at 8 TeV
-- ATLAS_2017_I1604029 – ttbar + gamma at 8 TeV

-- -------------------------------------------------------------------------------------------------------------------
-- These ones we can use if we get SM predictions
-- -------------------------------------------------------------------------------------------------------------------
-- INSERT INTO analysis VALUES('CMS_2015_I1370682',  Top quark. Particle-level, but don't have normalisation. Can use if we get SM theory predictions (Maybe from MA?)
-- INSERT INTO analysis VALUES('CMS_2017_I1519995',2600,'CMS_13_JETS'); --  search, with unfolded data. don't have normalisation
-- INSERT INTO analysis VALUES('CMS_2013_I1224539_DIJET',5000.0,'CMS_7_JETS'); 
-- ATLAS_2017_I1495243',3.2,'ATLAS_13_LMETJET'); --Top + jets, but all area normalised sadly, without providing the xsec.
-- CMS_2018_I1690148 jet substr in top ALL NORMALISED, DONT USE
-- CMS_2016_I1421646 – Dijet azimuthal decorrelations in $pp$ collisions at $\sqrt{s} = 8$ TeV (normalised)
-- g->bb ATLAS_2018_I1711114  Would be nice but need normalisation
-- Dileptonic emu tt early cross-section measurement at 13 TeV
-- off-resonance.  ATLAS_2018_I1677498 Would be nice but need normalisation
-- ATLAS_2021_I1913061 b frag  (normalised) https://gitlab.com/hepcedar/contur/-/issues/218

-- -------------------------------------------------------------------------------------------------------------------
-- These are probably not useful here 
-- -------------------------------------------------------------------------------------------------------------------
-- INSERT INTO analysis VALUES('ATLAS_2017_I1598613:BMODE=BB',11.4,'ATLAS_8_JETS'); cant use two modes in same pool. also, we don't have normalisation for this one.
-- INSERT INTO analysis VALUES('CMS_2018_I1686000',1960.0,'CMS_8_3L'); -- huge bg subtraction, BDTs etc.
-- LHCB_2018_I1665223 -- inelastic pp total cross section not really relevant here.
-- CMS_2018_I1708620 -- soft QCD/energy density
-- ALICE_2012_I944757 -- charm in central rapidity region
-- INSERT INTO analysis VALUES('ATLAS_2016_I1468168' inclusive/extrapolated only. do not use.
-- CMS_2020_I1837084 z->vv and ll. Both measured separately, however, only the muon version is in rivet. There are
--                                 also multiple vetos in the analysis which are not in the fiducial phase space,
--                                 so applicability is limited.
-- ATLAS_2021_I1941095 ttbar asymmetry see https://gitlab.com/hepcedar/contur/-/issues/204

-- lumi: gives the intergrated luminosity units which the rivet plots are normalised to. Note that if the value given here is
-- parseable as a number, it will override the lumi in the rivet info file. If so, it should always match the units of the cross section
CREATE TABLE lumi_unit (
    id      TEXT NOT NULL,
    lumi    TEXT,
    pattern TEXT,
    intLumi REAL,
    UNIQUE(id,lumi),
    FOREIGN KEY(id) REFERENCES analysis(id)
);


----------------------------------

-- Superseded/deprecated analyses
-- INSERT INTO analysis VALUES('ATLAS_2012_I1083318','pb',NULL);
-- INSERT INTO analysis VALUES('ATLAS_2011_I945498','pb',NULL);
-- INSERT INTO analysis VALUES('ATLAS_2011_I921594','pb',NULL);
-- INSERT INTO analysis VALUES('ATLAS_2011_S9128077','pb',NULL);

-- Z+ b,c
INSERT INTO lumi_unit VALUES('ATLAS_2024_I2771257','pb','',NULL);

--SUSY WW
INSERT INTO lumi_unit VALUES('ATLAS_2022_I2103950','fb','',NULL);

--2.76 TeV hadronic
INSERT INTO lumi_unit VALUES('CMS_2021_I1963239','pb','',NULL);

-- 7 TeV fully hadronic
INSERT INTO lumi_unit VALUES('ATLAS_2016_I1478355','pb','',NULL);
INSERT INTO lumi_unit VALUES('ATLAS_2014_I1325553','pb','',NULL);
INSERT INTO lumi_unit VALUES('ATLAS_2014_I1268975','pb','',NULL);
INSERT INTO lumi_unit VALUES('ATLAS_2014_I1326641','pb','',NULL);
INSERT INTO lumi_unit VALUES('ATLAS_2014_I1307243','pb','',NULL);
INSERT INTO lumi_unit VALUES('CMS_2014_I1298810','pb','',NULL);
INSERT INTO lumi_unit VALUES('CMS_2013_I1273574','pb','',NULL);
INSERT INTO lumi_unit VALUES('CMS_2013_I1208923','pb','',NULL);
INSERT INTO lumi_unit VALUES('CMS_2012_I1089835','pb','',NULL);

-- 7 TeV photons
INSERT INTO lumi_unit VALUES('ATLAS_2012_I1093738','pb','',NULL);
INSERT INTO lumi_unit VALUES('ATLAS_2013_I1244522','pb','',NULL);
INSERT INTO lumi_unit VALUES('ATLAS_2013_I1263495','pb','',NULL);
INSERT INTO lumi_unit VALUES('ATLAS_2012_I1199269','pb','',NULL);
INSERT INTO lumi_unit VALUES('CMS_2014_I1266056','pb','',NULL);

-- 7 TeV high mass Drell Yan
INSERT INTO lumi_unit VALUES('ATLAS_2013_I1234228','pb','',NULL);


-- 7 TeV Z+jets
INSERT INTO lumi_unit VALUES('ATLAS_2013_I1230812','pb','',NULL);
INSERT INTO lumi_unit VALUES('ATLAS_2014_I1306294:LMODE=EL','pb','',NULL);
INSERT INTO lumi_unit VALUES('CMS_2015_I1310737','pb','',NULL);
INSERT INTO lumi_unit VALUES('LHCB_2014_I1262703','pb','',NULL);
-- 7 TeV inclusive Z
INSERT INTO lumi_unit VALUES('ATLAS_2016_I1502620:LMODE=Z','pb','',NULL);
INSERT INTO lumi_unit VALUES('LHCB_2012_I1208102','pb','',NULL);

-- 7 TeV ttbar --- TODO this can be split into E and MU channels
INSERT INTO lumi_unit VALUES('ATLAS_2015_I1345452','pb','',NULL);

-- 7 TeV Low mass DY
INSERT INTO lumi_unit VALUES('ATLAS_2014_I1288706','pb','',NULL);

-- 7 TeV single jet masses: The rivet routines actually use only electrons, even though
-- the measurement used muons too. Not very confident about the normalisation.
INSERT INTO lumi_unit VALUES('CMS_2013_I1224539:JMODE=W','fb','',NULL);
INSERT INTO lumi_unit VALUES('CMS_2013_I1224539:JMODE=Z','fb','',NULL);

-- 7 TeV W+jets.
INSERT INTO lumi_unit VALUES('ATLAS_2016_I1502620:LMODE=W','pb','',NULL);
INSERT INTO lumi_unit VALUES('ATLAS_2014_I1319490','pb','',NULL);
INSERT INTO lumi_unit VALUES('CMS_2014_I1303894','pb','',NULL);

-- 7 TeV W+charm
INSERT INTO lumi_unit VALUES('ATLAS_2014_I1282447','pb','',NULL);

-- 7 TeV W+b
INSERT INTO lumi_unit VALUES('ATLAS_2013_I1219109','fb','',NULL); --W plus b jets

-- 7 TeV Z+bb
INSERT INTO lumi_unit VALUES('CMS_2013_I1256943','pb','',NULL);

-- 7 TeV WW. Plots in fb.
INSERT INTO lumi_unit VALUES('ATLAS_2013_I1190187','fb','',NULL); -- jet veto is correctly applied in fiducial cuts.

-- 7 TeV dibosons, plots in fb
INSERT INTO lumi_unit VALUES('ATLAS_2013_I1217863:LMODE=ZEL','fb','',NULL);
INSERT INTO lumi_unit VALUES('ATLAS_2013_I1217863:LMODE=ZMU','fb','',NULL);
INSERT INTO lumi_unit VALUES('CMS_2015_I1346843','fb','',NULL);

INSERT INTO lumi_unit VALUES('ATLAS_2013_I1217863:LMODE=WEL','fb','',NULL);
INSERT INTO lumi_unit VALUES('ATLAS_2013_I1217863:LMODE=WMU','fb','',NULL);
INSERT INTO lumi_unit VALUES('ATLAS_2012_I1203852:LMODE=LL','fb','',NULL);
INSERT INTO lumi_unit VALUES('ATLAS_2012_I1203852:LMODE=LNU','fb','',NULL);

-- 8 TeV fully hadronic
-- plots in fb
INSERT INTO lumi_unit VALUES('ATLAS_2015_I1394679','fb','',NULL);
INSERT INTO lumi_unit VALUES('ATLAS_2017_I1598613:BMODE=3MU','fb','',NULL);
-- for the b hadron mode
-- plots in pb
INSERT INTO lumi_unit VALUES('ATLAS_2017_I1604271','pb','',NULL);
INSERT INTO lumi_unit VALUES('CMS_2016_I1487277','pb','',NULL);
INSERT INTO lumi_unit VALUES('CMS_2017_I1598460','pb','',NULL); -- triple differential dijets

-- normalised, no total xsec yet INSERT INTO analysis VALUES('CMS_2016_I1421646',19700,'CMS_8_JETS');

-- 8 TeV photons
-- in pb
INSERT INTO lumi_unit VALUES('ATLAS_2016_I1457605','pb','',NULL);
INSERT INTO lumi_unit VALUES('ATLAS_2017_I1632756','pb','',NULL); -- +hf
-- in fb
INSERT INTO lumi_unit VALUES('ATLAS_2017_I1591327','fb','',NULL);
INSERT INTO lumi_unit VALUES('ATLAS_2014_I1306615','fb','',NULL); -- higgs to photons
INSERT INTO lumi_unit VALUES('ATLAS_2017_I1644367','fb','',NULL); -- 3gamma (fb)


-- 8 TeV High mass DY
-- in pb
INSERT INTO lumi_unit VALUES('ATLAS_2016_I1467454:LMODE=EL','pb','',NULL);
INSERT INTO lumi_unit VALUES('ATLAS_2016_I1467454:LMODE=MU','pb','',NULL);

-- 8 TeV leptons+MET, dileptons

-- normalised
INSERT INTO lumi_unit VALUES('ATLAS_2014_I1279489','pb','',NULL); -- electroweak Z+jets
INSERT INTO lumi_unit VALUES('ATLAS_2015_I1408516:LMODE=EL','pb','',NULL); -- Z production
INSERT INTO lumi_unit VALUES('ATLAS_2015_I1408516:LMODE=MU','pb','',NULL); -- Z production
INSERT INTO lumi_unit VALUES('ATLAS_2019_I1744201','fb','',NULL); -- Z+jets
INSERT INTO lumi_unit VALUES('CMS_2016_I1471281:VMODE=Z','fb','',NULL); -- Z pT
INSERT INTO lumi_unit VALUES('CMS_2016_I1471281:VMODE=W','fb','',NULL); -- W pT

-- plots in pb
INSERT INTO lumi_unit VALUES('ATLAS_2017_I1589844','pb','',NULL);
INSERT INTO lumi_unit VALUES('CMS_2017_I1499471','pb','',NULL);
INSERT INTO lumi_unit VALUES('CMS_2016_I1491953','pb','',NULL);
INSERT INTO lumi_unit VALUES('ATLAS_2015_I1404878','pb','',NULL);


INSERT INTO lumi_unit VALUES('LHCB_2016_I1454404:MODE=WJET','fb','',NULL);
INSERT INTO lumi_unit VALUES('LHCB_2016_I1454404:MODE=ZJET','fb','',NULL);

-- ATLAS_2016_I1487726: collinear Wj at 8 TeV Cross sections, but the theory uncertainty is too large
-- to use it without the having the theory prediction

-- plots in fb
INSERT INTO lumi_unit VALUES('CMS_2016_I1454211','fb','',NULL); -- NB partonic phase space?
INSERT INTO lumi_unit VALUES('ATLAS_2015_I1397637','fb','',NULL); -- ttbar
INSERT INTO lumi_unit VALUES('ATLAS_2017_I1517194','fb','',NULL); -- electroweak W+jets
INSERT INTO lumi_unit VALUES('ATLAS_2018_I1635273:LMODE=EL','fb','',NULL); -- W+jets. NB some plots in pb
INSERT INTO lumi_unit VALUES('ATLAS_2018_I1635273:LMODE=MU','fb','',NULL); -- W+jets. NB some plots in pb


-- plots in fb
INSERT INTO lumi_unit VALUES('CMS_2017_I1518399','fb','',NULL);  -- TTBAR
INSERT INTO lumi_unit VALUES('ATLAS_2016_I1426515','fb','',NULL); -- nb jet veto is implemented in fiducial cuts.
INSERT INTO lumi_unit VALUES('CMS_2017_I1467451','fb','',NULL); -- nb b-jet veto is NOT implemented in fiducial cuts; and large data driven bg subtraction.

-- fb
INSERT INTO lumi_unit VALUES('ATLAS_2015_I1394865','fb','',NULL);
INSERT INTO lumi_unit VALUES('ATLAS_2014_I1310835','fb','',NULL);
INSERT INTO lumi_unit VALUES('ATLAS_2016_I1494075:LMODE=4L','fb','d0[2-3]',NULL);
INSERT INTO lumi_unit VALUES('ATLAS_2016_I1494075:LMODE=4L','pb','d0[4-5]',NULL);
INSERT INTO lumi_unit VALUES('ATLAS_2016_I1494075:LMODE=2L2NU','fb','',NULL);

INSERT INTO lumi_unit VALUES('ATLAS_2016_I1448301:LMODE=LL','fb','',NULL);
INSERT INTO lumi_unit VALUES('ATLAS_2016_I1448301:LMODE=NU','fb','',NULL);
INSERT INTO lumi_unit VALUES('ATLAS_2016_I1492320:LMODE=3L','fb','',NULL);
INSERT INTO lumi_unit VALUES('ATLAS_2016_I1492320:LMODE=2L2J','fb','',NULL); -- nb b-jet veto IS implemented in fiducial cuts
INSERT INTO lumi_unit VALUES('ATLAS_2016_I1444991','fb','',NULL); -- nb jet veto IS implemented in fiducial cuts; but large data-driven top subtraction

INSERT INTO lumi_unit VALUES('CMS_2016_I1487288','fb','',NULL);

-- 13 TeV fully hadronic
INSERT INTO lumi_unit VALUES('ATLAS_2018_I1634970','pb','',NULL);
INSERT INTO lumi_unit VALUES('ATLAS_2019_I1724098','pb','',NULL); -- jet substructure.
INSERT INTO lumi_unit VALUES('ATLAS_2017_I1637587','pb','',NULL); -- soft drop jet mass
INSERT INTO lumi_unit VALUES('ATLAS_2020_I1808726','fb','',NULL);  -- multijet event shapes
INSERT INTO lumi_unit VALUES('CMS_2019_I1753720','pb','',NULL); -- all-jet top events with b-jets.
INSERT INTO lumi_unit VALUES('CMS_2021_I1932460','pb','',NULL);
INSERT INTO lumi_unit VALUES('CMS_2021_I1847230:MODE=QCD13TeV','fb','',2.3); -- 13TeV mode three jets
INSERT INTO lumi_unit VALUES('CMS_2021_I1847230:MODE=QCD8TeV','fb','',19.8); -- 8TeV mode three jets

-- INSERT INTO lumi_unit VALUES('ATLAS_2019_I1772062',32900.0,'ATLAS_13_JETS'); -- soft drop variables
-- (not really suitable, at least without more work. normalisation not provided, and theory uncertainties large)

INSERT INTO lumi_unit VALUES('CMS_2016_I1459051','pb','',NULL);
INSERT INTO lumi_unit VALUES('CMS_2018_I1682495','pb','',NULL); -- jet mass

-- 13 TeV DY. 
INSERT INTO lumi_unit VALUES('ATLAS_2019_I1725190','eventcount','',NULL); -- lumi is set in routine, to give event counts
INSERT INTO lumi_unit VALUES('CMS_2018_I1711625','pb','',NULL);    -- plots in pb

-- 13 TeV dileptons+jets
-- plots in pb
INSERT INTO lumi_unit VALUES('ATLAS_2017_I1627873','pb','',NULL);
INSERT INTO lumi_unit VALUES('ATLAS_2022_I2077570','pb','',NULL); -- Z+jets
INSERT INTO lumi_unit VALUES('ATLAS_2017_I1514251:LMODE=EMU','pb','',NULL); -- Z+jets
INSERT INTO lumi_unit VALUES('ATLAS_2020_I1788444','pb','',NULL); -- Z+bb
INSERT INTO lumi_unit VALUES('ATLAS_2020_I1803608','fb','',NULL); -- Electroweak Z+jets
INSERT INTO lumi_unit VALUES('ATLAS_2019_I1768911','pb','',NULL); -- plots in pb
INSERT INTO lumi_unit VALUES('CMS_2022_I2079374','pb','',NULL); -- CMS inclusive dilepton (Z pole and above)
INSERT INTO lumi_unit VALUES('CMS_2018_I1667854:LMODE=EMU','pb','',NULL); -- Z+jets
INSERT INTO lumi_unit VALUES('CMS_2019_I1753680:LMODE=EMU','pb','',NULL); -- Z production
INSERT INTO lumi_unit VALUES('CMS_2020_I1814328','pb','',NULL); -- WW -> 2l with one or zero jet. Includes SF leptons but excludes the Z pole.
INSERT INTO lumi_unit VALUES('CMS_2021_I1866118','fb','',NULL); -- DY Z production -> mm 

INSERT INTO lumi_unit VALUES('CMS_2021_I1847230:MODE=ZJet','fb','',19.8);-- Z (dimuons) + jets in ZJet mode need to be careful when using these histos! Normalisation factors are uncertain. 



-- plot in fb
INSERT INTO lumi_unit VALUES('ATLAS_2019_I1738841','fb','',NULL); -- Electroweak same sign WW -> 2l at least 2 jets


-- 13 TeV leptons+MET
INSERT INTO lumi_unit VALUES('CMS_2017_I1610623','pb','',NULL); -- W+jets
INSERT INTO lumi_unit VALUES('CMS_2016_I1491950','pb','',NULL); --ttbar
INSERT INTO lumi_unit VALUES('CMS_2018_I1662081','pb','',NULL); --ttbar
INSERT INTO lumi_unit VALUES('CMS_2018_I1663958','pb','',NULL); -- ttbar+jets (pb)
INSERT INTO lumi_unit VALUES('CMS_2019_I1705068','pb','',NULL); -- W+charm
INSERT INTO lumi_unit VALUES('CMS_2019_I1744604','pb','',NULL); -- single top
INSERT INTO lumi_unit VALUES('CMS_2021_I1901295','pb','',NULL); -- ttbar

INSERT INTO lumi_unit VALUES('ATLAS_2017_I1614149','pb','',NULL); --ttbar
INSERT INTO lumi_unit VALUES('ATLAS_2019_I1750330:TYPE=BOTH','pb','',NULL); --ttbar
INSERT INTO lumi_unit VALUES('ATLAS_2023_I2628732','pb','',NULL); --W+D

-- 13 TeV photon + MET
INSERT INTO lumi_unit VALUES('ATLAS_2018_I1698006:LVETO=ON','fb','',NULL);


INSERT INTO lumi_unit VALUES('LHCB_2018_I1662483','fb','',NULL); --ttbar

-- 13 TeV 4 leptons
INSERT INTO lumi_unit VALUES('ATLAS_2017_I1625109','fb','',NULL);  -- ZZ
INSERT INTO lumi_unit VALUES('ATLAS_2019_I1720442','fb','',NULL);  -- inclusive
INSERT INTO lumi_unit VALUES('ATLAS_2021_I1849535','fb','',NULL);  -- inclusive
INSERT INTO lumi_unit VALUES('ATLAS_2023_I2690799','fb','',NULL);  -- 4L + 2 jets


-- Various BG regions from LQ search. plots in pb
INSERT INTO lumi_unit VALUES('ATLAS_2019_I1718132:LMODE=ELMU','pb','',NULL);
INSERT INTO lumi_unit VALUES('ATLAS_2019_I1718132:LMODE=ELEL','pb','',NULL);
INSERT INTO lumi_unit VALUES('ATLAS_2019_I1718132:LMODE=MUMU','pb','',NULL);
INSERT INTO lumi_unit VALUES('ATLAS_2018_I1656578','fb','',NULL); --Top + jets
INSERT INTO lumi_unit VALUES('ATLAS_2018_I1705857','fb','',NULL); --Top + b jets (normalised)

-- 13 TeV MET+JET
INSERT INTO lumi_unit VALUES('ATLAS_2017_I1609448','pb','',NULL); -- HAVE THEORY
INSERT INTO lumi_unit VALUES('ATLAS_2016_I1458270','eventcount','',NULL); -- HAVE THEORY. 0l+MET+nJets search. Lumi is set to 3.2 in the routine
INSERT INTO lumi_unit VALUES('ATLAS_2024_I2765017:TYPE=BSM','fb','',NULL);  -- Full Run-2 measurement with theory predictions
INSERT INTO lumi_unit VALUES('ATLAS_2024_I2765017:MODE=EXTRAPOLATED:TYPE=BSM','fb','',NULL);  -- Full Run-2 measurement with theory predictions
INSERT INTO lumi_unit VALUES('ATLAS_2025_I2905252','fb','',NULL);  -- full run 2
-- INSERT INTO lumi_unit VALUES('CMS_2020_I1837084','pb','CMS_13_METJET'); -- CMS z->vv; however, rivet runs only on muons

-- hadronic top
INSERT INTO lumi_unit VALUES('ATLAS_2018_I1646686','pb','',NULL); -- Hadronic top pairs (pb)
INSERT INTO lumi_unit VALUES('ATLAS_2020_I1801434','pb','',NULL); -- Hadronic top pairs (pb)
INSERT INTO lumi_unit VALUES('CMS_2019_I1764472','fb','',NULL); -- Hadronic top pairs (fb)
INSERT INTO lumi_unit VALUES('ATLAS_2022_I2077575', 'fb','',NULL); -- Hadronic top pairs (fb) boosted

-- 13 TeV ttbar + gamma
INSERT INTO lumi_unit VALUES('ATLAS_2018_I1707015:LMODE=SINGLE','fb','',NULL); -- semileptonic
INSERT INTO lumi_unit VALUES('ATLAS_2018_I1707015:LMODE=DILEPTON','fb','',NULL); -- leptonic
INSERT INTO lumi_unit VALUES('ATLAS_2024_I2768921:LMODE=SINGLE','fb','',NULL); 
INSERT INTO lumi_unit VALUES('ATLAS_2024_I2768921:LMODE=DILEPTON','fb','',NULL);

-- 13 TeV ttbar + jets
INSERT INTO lumi_unit VALUES('ATLAS_2023_I2648096', 'fb', '', NULL); -- dileptonic
INSERT INTO lumi_unit VALUES('ATLAS_2024_I2809112','pb','',NULL); --DB Test


-- 13 TeV photons
INSERT INTO lumi_unit VALUES('ATLAS_2021_I1887997','pb','',NULL);
INSERT INTO lumi_unit VALUES('ATLAS_2017_I1645627','pb','',NULL);
INSERT INTO lumi_unit VALUES('ATLAS_2019_I1772071','pb','',NULL);
INSERT INTO lumi_unit VALUES('ATLAS_2022_I2023464','fb','',NULL);

-- 13 TeV photons+ll
INSERT INTO lumi_unit VALUES('ATLAS_2019_I1764342','fb','',NULL); -- Z+gamma
INSERT INTO lumi_unit VALUES('ATLAS_2022_I2593322','fb','',NULL); -- Z+diphoton

-- 13 TeV ll+photon+jet
INSERT INTO lumi_unit VALUES('ATLAS_2022_I2614196','fb','',NULL); -- Z+gamma in association with jets

-- 13 TeV WW production cross-section
INSERT INTO lumi_unit VALUES('ATLAS_2019_I1734263','fb','',NULL); -- no jets
INSERT INTO lumi_unit VALUES('ATLAS_2021_I1852328','fb','',NULL); -- with jets

-- 13 TeV Semileptonic ttbar
INSERT INTO lumi_unit VALUES('ATLAS_2022_I2037744','pb','',NULL);
-- 13 TeV leptonic ttbar
INSERT INTO lumi_unit VALUES('ATLAS_2019_I1759875','fb','',NULL);

-- dodgy ATLAS 13TeV 3L
INSERT INTO lumi_unit VALUES('ATLAS_2016_I1469071','fb','',NULL);

-- 13 TeV track based minimum biased events, in pb^{-1}
INSERT INTO lumi_unit VALUES('ATLAS_2016_I1419652','ub','',NULL); -- 
INSERT INTO lumi_unit VALUES('ATLAS_2016_I1467230','ub','',NULL); --  with low pT tracks
INSERT INTO lumi_unit VALUES('ATLAS_2019_I1740909','pb','',NULL); --  jet fragmentation using charged particles
INSERT INTO lumi_unit VALUES('ATLAS_2020_I1790256','pb','',NULL); --  Lund jet plane with charged particles

--13 TeV WW or WZ production cross-section with three or two leptons
INSERT INTO lumi_unit VALUES('CMS_2020_I1794169','fb','',NULL); 

INSERT INTO lumi_unit VALUES('CMS_2023_I2709669','fb','',NULL);

-- 13 TeV WWjets
INSERT INTO lumi_unit VALUES('CMS_2022_I2080534','fb','',NULL);

-- Table to store the mapping of a histogram to its covariance or correlation matrix
-- id is the measurement, cov is the relevant matrix, and corr = 0 means its a covariance matrix, corr = 1 means it a correlation matrix
CREATE TABLE covariances (
    id      TEXT NOT NULL UNIQUE,
    cov     TEXT,
    corr    INTEGER,
    PRIMARY KEY(id)
);
-- ATLAS ditau
INSERT INTO covariances VALUES('/REF/ATLAS_2025_I2905252/mll','/REF/ATLAS_2025_I2905252/d03-x01-y01',0);

-- 13TeV SUSY inspired WW
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2103950/d07-x01-y01','/REF/ATLAS_2022_I2103950/d20-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2103950/d09-x01-y01','/REF/ATLAS_2022_I2103950/d22-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2103950/d11-x01-y01','/REF/ATLAS_2022_I2103950/d24-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2103950/d13-x01-y01','/REF/ATLAS_2022_I2103950/d26-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2103950/d15-x01-y01','/REF/ATLAS_2022_I2103950/d28-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2103950/d17-x01-y01','/REF/ATLAS_2022_I2103950/d30-x01-y01',1);

-- 13TeV semileptonic ttbar
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2037744/d03-x01-y01','/REF/ATLAS_2022_I2037744/d04-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2037744/d06-x01-y01','/REF/ATLAS_2022_I2037744/d07-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2037744/d09-x01-y01','/REF/ATLAS_2022_I2037744/d10-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2037744/d12-x01-y01','/REF/ATLAS_2022_I2037744/d13-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2037744/d15-x01-y01','/REF/ATLAS_2022_I2037744/d16-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2037744/d18-x01-y01','/REF/ATLAS_2022_I2037744/d19-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2037744/d21-x01-y01','/REF/ATLAS_2022_I2037744/d22-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2037744/d24-x01-y01','/REF/ATLAS_2022_I2037744/d25-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2037744/d27-x01-y01','/REF/ATLAS_2022_I2037744/d28-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2037744/d30-x01-y01','/REF/ATLAS_2022_I2037744/d31-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2037744/d33-x01-y01','/REF/ATLAS_2022_I2037744/d34-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2037744/d36-x01-y01','/REF/ATLAS_2022_I2037744/d37-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2037744/d39-x01-y01','/REF/ATLAS_2022_I2037744/d40-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2037744/d42-x01-y01','/REF/ATLAS_2022_I2037744/d43-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2037744/d45-x01-y01','/REF/ATLAS_2022_I2037744/d46-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2037744/d48-x01-y01','/REF/ATLAS_2022_I2037744/d49-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2037744/d51-x01-y01','/REF/ATLAS_2022_I2037744/d52-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2037744/d54-x01-y01','/REF/ATLAS_2022_I2037744/d55-x01-y01',0);
-- INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2037744/d60-x01-y01','/REF/ATLAS_2022_I2037744/d63-x01-y01',0);
-- INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2037744/d61-x01-y01','/REF/ATLAS_2022_I2037744/d65-x01-y01',0);
-- INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2037744/d62-x01-y01','/REF/ATLAS_2022_I2037744/d68-x01-y01',0);
-- INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2037744/d72-x01-y01','/REF/ATLAS_2022_I2037744/d75-x01-y01',0);
-- INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2037744/d73-x01-y01','/REF/ATLAS_2022_I2037744/d77-x01-y01',0);
-- INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2037744/d74-x01-y01','/REF/ATLAS_2022_I2037744/d80-x01-y01',0);
-- INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2037744/d84-x01-y01','/REF/ATLAS_2022_I2037744/d87-x01-y01',0);
-- INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2037744/d85-x01-y01','/REF/ATLAS_2022_I2037744/d89-x01-y01',0);
-- INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2037744/d86-x01-y01','/REF/ATLAS_2022_I2037744/d92-x01-y01',0);
-- INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2037744/d96-x01-y01','/REF/ATLAS_2022_I2037744/d99-x01-y01',0);
-- INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2037744/d97-x01-y01','/REF/ATLAS_2022_I2037744/d101-x01-y01',0);
-- INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2037744/d98-x01-y01','/REF/ATLAS_2022_I2037744/d104-x01-y01',0);


-- 13TeV W+jets These are onlystat correlations.
--INSERT INTO covariances VALUES('/REF/ATLAS_2018_I1635273:LMODE=EL/d01-x01-y01','/REF/ATLAS_2018_I1635273:LMODE=EL/d02-x01-y01',1);
--INSERT INTO covariances VALUES('/REF/ATLAS_2018_I1635273:LMODE=MU/d01-x01-y01','/REF/ATLAS_2018_I1635273:LMODE=EL/d02-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2018_I1635273/d30-x01-y01','/REF/ATLAS_2018_I1635273/d31-x01-y01',1);
-- statistical correlations could in principle be added for other graphs as well, but it's not clear that's better
-- if they don't cover the systematics. We use this one because if we build the total
-- covariance from the error breakdown, we get unfeasibly low p value.

-- 13 TeV H->yy
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2023464/d02-x01-y01','/REF/ATLAS_2022_I2023464/d12-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2023464/d03-x01-y01','/REF/ATLAS_2022_I2023464/d13-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2023464/d04-x01-y01','/REF/ATLAS_2022_I2023464/d14-x01-y01',1);
-- INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2023464/d05-x01-y01','/REF/ATLAS_2022_I2023464/d15-x01-y01',0); Matrix has fewer entries than xsec
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2023464/d06-x01-y01','/REF/ATLAS_2022_I2023464/d16-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2023464/d07-x01-y01','/REF/ATLAS_2022_I2023464/d17-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2023464/d08-x01-y01','/REF/ATLAS_2022_I2023464/d18-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2023464/d09-x01-y01','/REF/ATLAS_2022_I2023464/d20-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2023464/d10-x01-y01','/REF/ATLAS_2022_I2023464/d19-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2023464/d21-x01-y01','/REF/ATLAS_2022_I2023464/d22-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2023464/d23-x01-y01','/REF/ATLAS_2022_I2023464/d24-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2023464/d25-x01-y01','/REF/ATLAS_2022_I2023464/d26-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2023464/d27-x01-y01','/REF/ATLAS_2022_I2023464/d28-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2023464/d29-x01-y01','/REF/ATLAS_2022_I2023464/d30-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2023464/d31-x01-y01','/REF/ATLAS_2022_I2023464/d32-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2023464/d33-x01-y01','/REF/ATLAS_2022_I2023464/d34-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2023464/d35-x01-y01','/REF/ATLAS_2022_I2023464/d36-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2023464/d37-x01-y01','/REF/ATLAS_2022_I2023464/d38-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2023464/d39-x01-y01','/REF/ATLAS_2022_I2023464/d40-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2023464/d41-x01-y01','/REF/ATLAS_2022_I2023464/d42-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2023464/d43-x01-y01','/REF/ATLAS_2022_I2023464/d44-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2023464/d45-x01-y01','/REF/ATLAS_2022_I2023464/d46-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2023464/d47-x01-y01','/REF/ATLAS_2022_I2023464/d48-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2023464/d49-x01-y01','/REF/ATLAS_2022_I2023464/d50-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2023464/d51-x01-y01','/REF/ATLAS_2022_I2023464/d52-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2023464/d53-x01-y01','/REF/ATLAS_2022_I2023464/d54-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2023464/d55-x01-y01','/REF/ATLAS_2022_I2023464/d56-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2023464/d57-x01-y01','/REF/ATLAS_2022_I2023464/d58-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2022_I2023464/d59-x01-y01','/REF/ATLAS_2022_I2023464/d60-x01-y01',1);

-- Note: for ATLAS_2023_I2628732 the covariances spread over the W+ and W- histgrams so the current machinery can't handle them.
-- Could be addressed in future.
INSERT INTO covariances VALUES('/REF/CMS_2021_I1866118/d01-x01-y01','/REF/CMS_2021_I1866118/d16-x01-y01',0);
INSERT INTO covariances VALUES('/REF/CMS_2021_I1866118/d02-x01-y01','/REF/CMS_2021_I1866118/d17-x01-y01',0);
INSERT INTO covariances VALUES('/REF/CMS_2021_I1866118/d03-x01-y01','/REF/CMS_2021_I1866118/d18-x01-y01',0);
INSERT INTO covariances VALUES('/REF/CMS_2021_I1866118/d04-x01-y01','/REF/CMS_2021_I1866118/d19-x01-y01',0);
INSERT INTO covariances VALUES('/REF/CMS_2021_I1866118/d05-x01-y01','/REF/CMS_2021_I1866118/d20-x01-y01',0);

INSERT INTO covariances VALUES('/REF/CMS_2022_I2079374/d01-x01-y01','/REF/CMS_2022_I2079374/d02-x01-y01',0);
INSERT INTO covariances VALUES('/REF/CMS_2022_I2079374/d03-x01-y01','/REF/CMS_2022_I2079374/d04-x01-y01',0);
INSERT INTO covariances VALUES('/REF/CMS_2022_I2079374/d05-x01-y01','/REF/CMS_2022_I2079374/d06-x01-y01',0);
INSERT INTO covariances VALUES('/REF/CMS_2022_I2079374/d07-x01-y01','/REF/CMS_2022_I2079374/d08-x01-y01',0);
INSERT INTO covariances VALUES('/REF/CMS_2022_I2079374/d09-x01-y01','/REF/CMS_2022_I2079374/d10-x01-y01',0);
INSERT INTO covariances VALUES('/REF/CMS_2022_I2079374/d11-x01-y01','/REF/CMS_2022_I2079374/d12-x01-y01',0);
INSERT INTO covariances VALUES('/REF/CMS_2022_I2079374/d13-x01-y01','/REF/CMS_2022_I2079374/d14-x01-y01',0);
INSERT INTO covariances VALUES('/REF/CMS_2022_I2079374/d15-x01-y01','/REF/CMS_2022_I2079374/d16-x01-y01',0);
INSERT INTO covariances VALUES('/REF/CMS_2022_I2079374/d17-x01-y01','/REF/CMS_2022_I2079374/d18-x01-y01',0);
INSERT INTO covariances VALUES('/REF/CMS_2022_I2079374/d19-x01-y01','/REF/CMS_2022_I2079374/d20-x01-y01',0);
INSERT INTO covariances VALUES('/REF/CMS_2022_I2079374/d21-x01-y01','/REF/CMS_2022_I2079374/d22-x01-y01',0);
INSERT INTO covariances VALUES('/REF/CMS_2022_I2079374/d23-x01-y01','/REF/CMS_2022_I2079374/d24-x01-y01',0);
INSERT INTO covariances VALUES('/REF/CMS_2022_I2079374/d25-x01-y01','/REF/CMS_2022_I2079374/d26-x01-y01',0);
INSERT INTO covariances VALUES('/REF/CMS_2022_I2079374/d27-x01-y01','/REF/CMS_2022_I2079374/d28-x01-y01',0);


INSERT INTO covariances VALUES('/REF/ATLAS_2017_I1637587/d01-x01-y01','/REF/ATLAS_2017_I1637587/d10-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2017_I1637587/d02-x01-y01','/REF/ATLAS_2017_I1637587/d11-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2017_I1637587/d03-x01-y01','/REF/ATLAS_2017_I1637587/d12-x01-y01',0);

INSERT INTO covariances VALUES('/REF/ATLAS_2019_I1734263/d01-x01-y01','/REF/ATLAS_2019_I1734263/d03-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2019_I1734263/d04-x01-y01','/REF/ATLAS_2019_I1734263/d06-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2019_I1734263/d07-x01-y01','/REF/ATLAS_2019_I1734263/d09-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2019_I1734263/d10-x01-y01','/REF/ATLAS_2019_I1734263/d12-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2019_I1734263/d13-x01-y01','/REF/ATLAS_2019_I1734263/d15-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2019_I1734263/d16-x01-y01','/REF/ATLAS_2019_I1734263/d18-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2019_I1734263/d19-x01-y01','/REF/ATLAS_2019_I1734263/d21-x01-y01',1);

INSERT INTO covariances VALUES('/REF/ATLAS_2017_I1625109/d02-x01-y01','/REF/ATLAS_2017_I1625109/d07-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2017_I1625109/d08-x01-y01','/REF/ATLAS_2017_I1625109/d13-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2017_I1625109/d14-x01-y01','/REF/ATLAS_2017_I1625109/d19-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2017_I1625109/d20-x01-y01','/REF/ATLAS_2017_I1625109/d25-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2017_I1625109/d26-x01-y01','/REF/ATLAS_2017_I1625109/d31-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2017_I1625109/d32-x01-y01','/REF/ATLAS_2017_I1625109/d37-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2017_I1625109/d38-x01-y01','/REF/ATLAS_2017_I1625109/d43-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2017_I1625109/d44-x01-y01','/REF/ATLAS_2017_I1625109/d49-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2017_I1625109/d50-x01-y01','/REF/ATLAS_2017_I1625109/d55-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2017_I1625109/d56-x01-y01','/REF/ATLAS_2017_I1625109/d61-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2017_I1625109/d62-x01-y01','/REF/ATLAS_2017_I1625109/d67-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2017_I1625109/d68-x01-y01','/REF/ATLAS_2017_I1625109/d73-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2017_I1625109/d74-x01-y01','/REF/ATLAS_2017_I1625109/d79-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2017_I1625109/d80-x01-y01','/REF/ATLAS_2017_I1625109/d85-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2017_I1625109/d86-x01-y01','/REF/ATLAS_2017_I1625109/d91-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2017_I1625109/d92-x01-y01','/REF/ATLAS_2017_I1625109/d97-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2017_I1625109/d98-x01-y01','/REF/ATLAS_2017_I1625109/d103-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2017_I1625109/d104-x01-y01','/REF/ATLAS_2017_I1625109/d109-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2017_I1625109/d110-x01-y01','/REF/ATLAS_2017_I1625109/d115-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2017_I1625109/d116-x01-y01','/REF/ATLAS_2017_I1625109/d121-x01-y01',1);

INSERT INTO covariances VALUES('/REF/ATLAS_2021_I1852328/d02-x01-y01','/REF/ATLAS_2021_I1852328/d04-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2021_I1852328/d05-x01-y01','/REF/ATLAS_2021_I1852328/d07-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2021_I1852328/d08-x01-y01','/REF/ATLAS_2021_I1852328/d10-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2021_I1852328/d11-x01-y01','/REF/ATLAS_2021_I1852328/d13-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2021_I1852328/d14-x01-y01','/REF/ATLAS_2021_I1852328/d16-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2021_I1852328/d17-x01-y01','/REF/ATLAS_2021_I1852328/d19-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2021_I1852328/d20-x01-y01','/REF/ATLAS_2021_I1852328/d22-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2021_I1852328/d23-x01-y01','/REF/ATLAS_2021_I1852328/d25-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2021_I1852328/d26-x01-y01','/REF/ATLAS_2021_I1852328/d28-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2021_I1852328/d29-x01-y01','/REF/ATLAS_2021_I1852328/d31-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2021_I1852328/d32-x01-y01','/REF/ATLAS_2021_I1852328/d34-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2021_I1852328/d35-x01-y01','/REF/ATLAS_2021_I1852328/d37-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2021_I1852328/d38-x01-y01','/REF/ATLAS_2021_I1852328/d40-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2021_I1852328/d41-x01-y01','/REF/ATLAS_2021_I1852328/d43-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2021_I1852328/d44-x01-y01','/REF/ATLAS_2021_I1852328/d46-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2021_I1852328/d47-x01-y01','/REF/ATLAS_2021_I1852328/d49-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2021_I1852328/d50-x01-y01','/REF/ATLAS_2021_I1852328/d52-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2021_I1852328/d53-x01-y01','/REF/ATLAS_2021_I1852328/d55-x01-y01',1);

INSERT INTO covariances VALUES('/REF/ATLAS_2019_I1759875/d01-x01-y01','/REF/ATLAS_2019_I1759875/d23-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2019_I1759875/d03-x01-y01','/REF/ATLAS_2019_I1759875/d27-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2019_I1759875/d05-x01-y01','/REF/ATLAS_2019_I1759875/d31-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2019_I1759875/d07-x01-y01','/REF/ATLAS_2019_I1759875/d35-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2019_I1759875/d09-x01-y01','/REF/ATLAS_2019_I1759875/d39-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2019_I1759875/d11-x01-y01','/REF/ATLAS_2019_I1759875/d43-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2019_I1759875/d13-x01-y01','/REF/ATLAS_2019_I1759875/d47-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2019_I1759875/d15-x01-y01','/REF/ATLAS_2019_I1759875/d51-x01-y01',1);

-- note these a listed as statistical correlations. we scale them by the whole uncertainty,
-- and this gives very simialr results to taking the covariance from the error breakdown
INSERT INTO covariances VALUES('/REF/ATLAS_2018_I1707015/d03-x01-y01','/REF/ATLAS_2018_I1707015/d11-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2018_I1707015/d04-x01-y01','/REF/ATLAS_2018_I1707015/d12-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2018_I1707015/d05-x01-y01','/REF/ATLAS_2018_I1707015/d13-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2018_I1707015/d06-x01-y01','/REF/ATLAS_2018_I1707015/d14-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2018_I1707015/d07-x01-y01','/REF/ATLAS_2018_I1707015/d15-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2018_I1707015/d08-x01-y01','/REF/ATLAS_2018_I1707015/d16-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2018_I1707015/d09-x01-y01','/REF/ATLAS_2018_I1707015/d17-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2018_I1707015/d10-x01-y01','/REF/ATLAS_2018_I1707015/d18-x01-y01',1);

INSERT INTO covariances VALUES('/REF/ATLAS_2019_I1750330/d04-x01-y01','/REF/ATLAS_2019_I1750330/d05-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2019_I1750330/d08-x01-y01','/REF/ATLAS_2019_I1750330/d09-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2019_I1750330/d12-x01-y01','/REF/ATLAS_2019_I1750330/d13-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2019_I1750330/d16-x01-y01','/REF/ATLAS_2019_I1750330/d17-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2019_I1750330/d20-x01-y01','/REF/ATLAS_2019_I1750330/d21-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2019_I1750330/d24-x01-y01','/REF/ATLAS_2019_I1750330/d25-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2019_I1750330/d28-x01-y01','/REF/ATLAS_2019_I1750330/d29-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2019_I1750330/d32-x01-y01','/REF/ATLAS_2019_I1750330/d33-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2019_I1750330/d36-x01-y01','/REF/ATLAS_2019_I1750330/d37-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2019_I1750330/d40-x01-y01','/REF/ATLAS_2019_I1750330/d41-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2019_I1750330/d44-x01-y01','/REF/ATLAS_2019_I1750330/d45-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2019_I1750330/d48-x01-y01','/REF/ATLAS_2019_I1750330/d49-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2019_I1750330/d52-x01-y01','/REF/ATLAS_2019_I1750330/d53-x01-y01',0);

INSERT INTO covariances VALUES('/REF/ATLAS_2019_I1750330/d843-x01-y01','/REF/ATLAS_2019_I1750330/d844-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2019_I1750330/d847-x01-y01','/REF/ATLAS_2019_I1750330/d848-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2019_I1750330/d851-x01-y01','/REF/ATLAS_2019_I1750330/d852-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2019_I1750330/d855-x01-y01','/REF/ATLAS_2019_I1750330/d856-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2019_I1750330/d859-x01-y01','/REF/ATLAS_2019_I1750330/d860-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2019_I1750330/d863-x01-y01','/REF/ATLAS_2019_I1750330/d864-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2019_I1750330/d867-x01-y01','/REF/ATLAS_2019_I1750330/d868-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2019_I1750330/d871-x01-y01','/REF/ATLAS_2019_I1750330/d872-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2019_I1750330/d875-x01-y01','/REF/ATLAS_2019_I1750330/d876-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2019_I1750330/d879-x01-y01','/REF/ATLAS_2019_I1750330/d880-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2019_I1750330/d883-x01-y01','/REF/ATLAS_2019_I1750330/d884-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2019_I1750330/d887-x01-y01','/REF/ATLAS_2019_I1750330/d888-x01-y01',0);

INSERT INTO covariances VALUES('/REF/ATLAS_2017_I1614149/d15-x01-y01','/REF/ATLAS_2017_I1614149/d01-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2017_I1614149/d17-x01-y01','/REF/ATLAS_2017_I1614149/d05-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2017_I1614149/d19-x01-y01','/REF/ATLAS_2017_I1614149/d11-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2017_I1614149/d21-x01-y01','/REF/ATLAS_2017_I1614149/d13-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2017_I1614149/d23-x01-y01','/REF/ATLAS_2017_I1614149/d09-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2017_I1614149/d25-x01-y01','/REF/ATLAS_2017_I1614149/d03-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2017_I1614149/d27-x01-y01','/REF/ATLAS_2017_I1614149/d07-x01-y01',0);

INSERT INTO covariances VALUES('/REF/ATLAS_2018_I1656578/d96-x01-y01','/REF/ATLAS_2018_I1656578/d56-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2018_I1656578/d98-x01-y01','/REF/ATLAS_2018_I1656578/d58-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2018_I1656578/d100-x01-y01','/REF/ATLAS_2018_I1656578/d60-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2018_I1656578/d102-x01-y01','/REF/ATLAS_2018_I1656578/d62-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2018_I1656578/d104-x01-y01','/REF/ATLAS_2018_I1656578/d64-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2018_I1656578/d106-x01-y01','/REF/ATLAS_2018_I1656578/d66-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2018_I1656578/d108-x01-y01','/REF/ATLAS_2018_I1656578/d68-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2018_I1656578/d110-x01-y01','/REF/ATLAS_2018_I1656578/d70-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2018_I1656578/d112-x01-y01','/REF/ATLAS_2018_I1656578/d72-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2018_I1656578/d114-x01-y01','/REF/ATLAS_2018_I1656578/d74-x01-y01',0);

INSERT INTO covariances VALUES('/REF/ATLAS_2018_I1646686/d02-x01-y01','/REF/ATLAS_2018_I1646686/d28-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2018_I1646686/d03-x01-y01','/REF/ATLAS_2018_I1646686/d32-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2018_I1646686/d04-x01-y01','/REF/ATLAS_2018_I1646686/d36-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2018_I1646686/d05-x01-y01','/REF/ATLAS_2018_I1646686/d40-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2018_I1646686/d06-x01-y01','/REF/ATLAS_2018_I1646686/d44-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2018_I1646686/d07-x01-y01','/REF/ATLAS_2018_I1646686/d48-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2018_I1646686/d08-x01-y01','/REF/ATLAS_2018_I1646686/d52-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2018_I1646686/d09-x01-y01','/REF/ATLAS_2018_I1646686/d56-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2018_I1646686/d10-x01-y01','/REF/ATLAS_2018_I1646686/d60-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2018_I1646686/d11-x01-y01','/REF/ATLAS_2018_I1646686/d64-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2018_I1646686/d12-x01-y01','/REF/ATLAS_2018_I1646686/d68-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2018_I1646686/d13-x01-y01','/REF/ATLAS_2018_I1646686/d72-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2018_I1646686/d14-x01-y01','/REF/ATLAS_2018_I1646686/d76-x01-y01',0);

INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d04-x01-y01','/REF/ATLAS_2020_I1801434/d05-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d08-x01-y01','/REF/ATLAS_2020_I1801434/d09-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d12-x01-y01','/REF/ATLAS_2020_I1801434/d13-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d16-x01-y01','/REF/ATLAS_2020_I1801434/d17-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d20-x01-y01','/REF/ATLAS_2020_I1801434/d21-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d24-x01-y01','/REF/ATLAS_2020_I1801434/d25-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d28-x01-y01','/REF/ATLAS_2020_I1801434/d29-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d32-x01-y01','/REF/ATLAS_2020_I1801434/d33-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d36-x01-y01','/REF/ATLAS_2020_I1801434/d37-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d40-x01-y01','/REF/ATLAS_2020_I1801434/d41-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d44-x01-y01','/REF/ATLAS_2020_I1801434/d45-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d48-x01-y01','/REF/ATLAS_2020_I1801434/d49-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d52-x01-y01','/REF/ATLAS_2020_I1801434/d53-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d56-x01-y01','/REF/ATLAS_2020_I1801434/d57-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d60-x01-y01','/REF/ATLAS_2020_I1801434/d61-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d64-x01-y01','/REF/ATLAS_2020_I1801434/d65-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d68-x01-y01','/REF/ATLAS_2020_I1801434/d69-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d72-x01-y01','/REF/ATLAS_2020_I1801434/d73-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d76-x01-y01','/REF/ATLAS_2020_I1801434/d77-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d80-x01-y01','/REF/ATLAS_2020_I1801434/d81-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d84-x01-y01','/REF/ATLAS_2020_I1801434/d85-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d88-x01-y01','/REF/ATLAS_2020_I1801434/d89-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d92-x01-y01','/REF/ATLAS_2020_I1801434/d93-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d96-x01-y01','/REF/ATLAS_2020_I1801434/d97-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d100-x01-y01','/REF/ATLAS_2020_I1801434/d101-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d104-x01-y01','/REF/ATLAS_2020_I1801434/d105-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d108-x01-y01','/REF/ATLAS_2020_I1801434/d109-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d112 x01-y01','/REF/ATLAS_2020_I1801434/d113-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d116-x01-y01','/REF/ATLAS_2020_I1801434/d117-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d120-x01-y01','/REF/ATLAS_2020_I1801434/d121-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d124-x01-y01','/REF/ATLAS_2020_I1801434/d125-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d128-x01-y01','/REF/ATLAS_2020_I1801434/d129-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d132-x01-y01','/REF/ATLAS_2020_I1801434/d133-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d136-x01-y01','/REF/ATLAS_2020_I1801434/d137-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d153-x01-y01','/REF/ATLAS_2020_I1801434/d157-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d154-x01-y01','/REF/ATLAS_2020_I1801434/d159-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d155-x01-y01','/REF/ATLAS_2020_I1801434/d162-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d156-x01-y01','/REF/ATLAS_2020_I1801434/d166-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d181-x01-y01','/REF/ATLAS_2020_I1801434/d185-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d182-x01-y01','/REF/ATLAS_2020_I1801434/d187-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d183-x01-y01','/REF/ATLAS_2020_I1801434/d190-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d184-x01-y01','/REF/ATLAS_2020_I1801434/d194-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d209-x01-y01','/REF/ATLAS_2020_I1801434/d213-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d210-x01-y01','/REF/ATLAS_2020_I1801434/d215-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d211-x01-y01','/REF/ATLAS_2020_I1801434/d218-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d212-x01-y01','/REF/ATLAS_2020_I1801434/d222-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d237-x01-y01','/REF/ATLAS_2020_I1801434/d241-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d238-x01-y01','/REF/ATLAS_2020_I1801434/d243-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d239-x01-y01','/REF/ATLAS_2020_I1801434/d246-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d240-x01-y01','/REF/ATLAS_2020_I1801434/d250-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d265-x01-y01','/REF/ATLAS_2020_I1801434/d269-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d266-x01-y01','/REF/ATLAS_2020_I1801434/d271-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d267-x01-y01','/REF/ATLAS_2020_I1801434/d274-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d268-x01-y01','/REF/ATLAS_2020_I1801434/d278-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d293-x01-y01','/REF/ATLAS_2020_I1801434/d297-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d294-x01-y01','/REF/ATLAS_2020_I1801434/d299-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d295-x01-y01','/REF/ATLAS_2020_I1801434/d302-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d296-x01-y01','/REF/ATLAS_2020_I1801434/d306-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d321-x01-y01','/REF/ATLAS_2020_I1801434/d325-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d322-x01-y01','/REF/ATLAS_2020_I1801434/d327-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d323-x01-y01','/REF/ATLAS_2020_I1801434/d330-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d324-x01-y01','/REF/ATLAS_2020_I1801434/d334-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d349-x01-y01','/REF/ATLAS_2020_I1801434/d353-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d350-x01-y01','/REF/ATLAS_2020_I1801434/d355-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d351-x01-y01','/REF/ATLAS_2020_I1801434/d358-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d352-x01-y01','/REF/ATLAS_2020_I1801434/d362-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d377-x01-y01','/REF/ATLAS_2020_I1801434/d381-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d378-x01-y01','/REF/ATLAS_2020_I1801434/d383-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d379-x01-y01','/REF/ATLAS_2020_I1801434/d386-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d380-x01-y01','/REF/ATLAS_2020_I1801434/d390-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d433-x01-y01','/REF/ATLAS_2020_I1801434/d437-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d434-x01-y01','/REF/ATLAS_2020_I1801434/d439-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d435-x01-y01','/REF/ATLAS_2020_I1801434/d442-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2020_I1801434/d436-x01-y01','/REF/ATLAS_2020_I1801434/d446-x01-y01',0);

-- these mapping should be correct but there is a problem with the HEPData record in that the xsec histograms
-- are exported as scatter3D (they have an additional bin number column) and rivet uses a different yoda file
-- with the xsec names -x02- and the correlation matrices borked.
--INSERT INTO covariances VALUES('/REF/CMS_2016_I1491950/d01-x01-y01','/REF/CMS_2016_I1491950/d02-x01-y01',0);
--INSERT INTO covariances VALUES('/REF/CMS_2016_I1491950/d03-x01-y01','/REF/CMS_2016_I1491950/d04-x01-y01',0);
--INSERT INTO covariances VALUES('/REF/CMS_2016_I1491950/d05-x01-y01','/REF/CMS_2016_I1491950/d06-x01-y01',0);
--INSERT INTO covariances VALUES('/REF/CMS_2016_I1491950/d07-x01-y01','/REF/CMS_2016_I1491950/d08-x01-y01',0);
--INSERT INTO covariances VALUES('/REF/CMS_2016_I1491950/d09-x01-y01','/REF/CMS_2016_I1491950/d10-x01-y01',0);
--INSERT INTO covariances VALUES('/REF/CMS_2016_I1491950/d11-x01-y01','/REF/CMS_2016_I1491950/d12-x01-y01',0);
--INSERT INTO covariances VALUES('/REF/CMS_2016_I1491950/d13-x01-y01','/REF/CMS_2016_I1491950/d14-x01-y01',0);
--INSERT INTO covariances VALUES('/REF/CMS_2016_I1491950/d15-x01-y01','/REF/CMS_2016_I1491950/d16-x01-y01',0);

INSERT INTO covariances VALUES('/REF/CMS_2018_I1663958/d01-x01-y01','/REF/CMS_2018_I1663958/d02-x01-y01',0);
INSERT INTO covariances VALUES('/REF/CMS_2018_I1663958/d03-x01-y01','/REF/CMS_2018_I1663958/d04-x01-y01',0);
INSERT INTO covariances VALUES('/REF/CMS_2018_I1663958/d05-x01-y01','/REF/CMS_2018_I1663958/d06-x01-y01',0);
INSERT INTO covariances VALUES('/REF/CMS_2018_I1663958/d07-x01-y01','/REF/CMS_2018_I1663958/d08-x01-y01',0);
INSERT INTO covariances VALUES('/REF/CMS_2018_I1663958/d09-x01-y01','/REF/CMS_2018_I1663958/d10-x01-y01',0);
INSERT INTO covariances VALUES('/REF/CMS_2018_I1663958/d11-x01-y01','/REF/CMS_2018_I1663958/d12-x01-y01',0);
INSERT INTO covariances VALUES('/REF/CMS_2018_I1663958/d13-x01-y01','/REF/CMS_2018_I1663958/d14-x01-y01',0);
INSERT INTO covariances VALUES('/REF/CMS_2018_I1663958/d15-x01-y01','/REF/CMS_2018_I1663958/d16-x01-y01',0);

INSERT INTO covariances VALUES('/REF/CMS_2019_I1744604/d13-x01-y01','/REF/CMS_2019_I1744604/d14-x01-y01',0);
INSERT INTO covariances VALUES('/REF/CMS_2019_I1744604/d15-x01-y01','/REF/CMS_2019_I1744604/d16-x01-y01',0);
INSERT INTO covariances VALUES('/REF/CMS_2019_I1744604/d17-x01-y01','/REF/CMS_2019_I1744604/d18-x01-y01',0);
INSERT INTO covariances VALUES('/REF/CMS_2019_I1744604/d19-x01-y01','/REF/CMS_2019_I1744604/d20-x01-y01',0);
INSERT INTO covariances VALUES('/REF/CMS_2019_I1744604/d21-x01-y01','/REF/CMS_2019_I1744604/d22-x01-y01',0);
INSERT INTO covariances VALUES('/REF/CMS_2019_I1744604/d23-x01-y01','/REF/CMS_2019_I1744604/d24-x01-y01',0);

INSERT INTO covariances VALUES('/REF/ATLAS_2015_I1394865/d01-x01-y01','/REF/ATLAS_2015_I1394865/d04-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2015_I1394865/d02-x01-y01','/REF/ATLAS_2015_I1394865/d05-x01-y01',0);

INSERT INTO covariances VALUES('/REF/CMS_2019_I753680/d26-x01-y02','/REF/CMS_2019_I1753680/d43-x01-y01',0);
INSERT INTO covariances VALUES('/REF/CMS_2019_I753680/d27-x01-y02','/REF/CMS_2019_I1753680/d42-x01-y01',0);
INSERT INTO covariances VALUES('/REF/CMS_2019_I753680/d28-x01-y02','/REF/CMS_2019_I1753680/d44-x01-y01',0);

INSERT INTO covariances VALUES('/REF/CMS_2019_I753680/d26-x01-y01','/REF/CMS_2019_I1753680/d35-x01-y01',0);
INSERT INTO covariances VALUES('/REF/CMS_2019_I753680/d27-x01-y01','/REF/CMS_2019_I1753680/d34-x01-y01',0);
INSERT INTO covariances VALUES('/REF/CMS_2019_I753680/d28-x01-y01','/REF/CMS_2019_I1753680/d36-x01-y01',0);

INSERT INTO covariances VALUES('/REF/ATLAS_2013_I1190187/d04-x01-y01','/REF/ATLAS_2013_I1190187/d05-x01-y01',1);

INSERT INTO covariances VALUES('/REF/LHCB_2016_I1454404/d04-x01-y01','/REF/LHCB_2016_I1454404/d11-x01-y01',1);
INSERT INTO covariances VALUES('/REF/LHCB_2016_I1454404/d04-x01-y02','/REF/LHCB_2016_I1454404/d12-x01-y01',1);
INSERT INTO covariances VALUES('/REF/LHCB_2016_I1454404/d05-x01-y01','/REF/LHCB_2016_I1454404/d13-x01-y01',1);
INSERT INTO covariances VALUES('/REF/LHCB_2016_I1454404/d05-x01-y02','/REF/LHCB_2016_I1454404/d14-x01-y01',1);
INSERT INTO covariances VALUES('/REF/LHCB_2016_I1454404/d06-x01-y01','/REF/LHCB_2016_I1454404/d15-x01-y01',1);
INSERT INTO covariances VALUES('/REF/LHCB_2016_I1454404/d06-x01-y02','/REF/LHCB_2016_I1454404/d16-x01-y01',1);

INSERT INTO covariances VALUES('/REF/LHCB_2016_I1454404/d07-x01-y01','/REF/LHCB_2016_I1454404/d17-x01-y01',1);
INSERT INTO covariances VALUES('/REF/LHCB_2016_I1454404/d08-x01-y01','/REF/LHCB_2016_I1454404/d18-x01-y01',1);
INSERT INTO covariances VALUES('/REF/LHCB_2016_I1454404/d09-x01-y01','/REF/LHCB_2016_I1454404/d19-x01-y01',1);
INSERT INTO covariances VALUES('/REF/LHCB_2016_I1454404/d10-x01-y01','/REF/LHCB_2016_I1454404/d20-x01-y01',1);
INSERT INTO covariances VALUES('/REF/ATLAS_2023_I2648096/d06-x01-y02','/REF/ATLAS_2023_I2648096/d07-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2023_I2648096/d09-x01-y02','/REF/ATLAS_2023_I2648096/d10-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2023_I2648096/d12-x01-y02','/REF/ATLAS_2023_I2648096/d13-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2023_I2648096/d15-x01-y02','/REF/ATLAS_2023_I2648096/d16-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2023_I2648096/d18-x01-y02','/REF/ATLAS_2023_I2648096/d19-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2023_I2648096/d21-x01-y02','/REF/ATLAS_2023_I2648096/d22-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2023_I2648096/d24-x01-y02','/REF/ATLAS_2023_I2648096/d25-x01-y01',0);
INSERT INTO covariances VALUES('/REF/ATLAS_2023_I2648096/d27-x01-y02','/REF/ATLAS_2023_I2648096/d28-x01-y01',0);

INSERT INTO covariances VALUES("/REF/CMS_2021_I1901295/d159-x01-y01","/REF/CMS_2021_I1901295/d160-x01-y01",0);
INSERT INTO covariances VALUES("/REF/CMS_2021_I1901295/d163-x01-y01","/REF/CMS_2021_I1901295/d164-x01-y01",0);
INSERT INTO covariances VALUES("/REF/CMS_2021_I1901295/d167-x01-y01","/REF/CMS_2021_I1901295/d168-x01-y01",0);
INSERT INTO covariances VALUES("/REF/CMS_2021_I1901295/d171-x01-y01","/REF/CMS_2021_I1901295/d172-x01-y01",0);
INSERT INTO covariances VALUES("/REF/CMS_2021_I1901295/d175-x01-y01","/REF/CMS_2021_I1901295/d176-x01-y01",0);
INSERT INTO covariances VALUES("/REF/CMS_2021_I1901295/d179-x01-y01","/REF/CMS_2021_I1901295/d180-x01-y01",0);
INSERT INTO covariances VALUES("/REF/CMS_2021_I1901295/d183-x01-y01","/REF/CMS_2021_I1901295/d184-x01-y01",0);
INSERT INTO covariances VALUES("/REF/CMS_2021_I1901295/d187-x01-y01","/REF/CMS_2021_I1901295/d188-x01-y01",0);
INSERT INTO covariances VALUES("/REF/CMS_2021_I1901295/d191-x01-y01","/REF/CMS_2021_I1901295/d192-x01-y01",0);
INSERT INTO covariances VALUES("/REF/CMS_2021_I1901295/d195-x01-y01","/REF/CMS_2021_I1901295/d196-x01-y01",0);
INSERT INTO covariances VALUES("/REF/CMS_2021_I1901295/d199-x01-y01","/REF/CMS_2021_I1901295/d200-x01-y01",0);
INSERT INTO covariances VALUES("/REF/CMS_2021_I1901295/d203-x01-y01","/REF/CMS_2021_I1901295/d204-x01-y01",0);
INSERT INTO covariances VALUES("/REF/CMS_2021_I1901295/d207-x01-y01","/REF/CMS_2021_I1901295/d208-x01-y01",0);
INSERT INTO covariances VALUES("/REF/CMS_2021_I1901295/d211-x01-y01","/REF/CMS_2021_I1901295/d212-x01-y01",0);
INSERT INTO covariances VALUES("/REF/CMS_2021_I1901295/d317-x01-y01","/REF/CMS_2021_I1901295/d318-x01-y01",0);
-- INSERT INTO covariances VALUES("/REF/CMS_2021_I1901295/d321-x01-y01","/REF/CMS_2021_I1901295/d322-x01-y01",0);
INSERT INTO covariances VALUES("/REF/CMS_2021_I1901295/d325-x01-y01","/REF/CMS_2021_I1901295/d326-x01-y01",0);
INSERT INTO covariances VALUES("/REF/CMS_2021_I1901295/d329-x01-y01","/REF/CMS_2021_I1901295/d330-x01-y01",0);

-- TODO: ATLAS_2023_I2690799 has bin to bin correlations for all observables, need a way to use this in contur

-- Histograms where overflow and/ or underflow bin should be used.
CREATE TABLE overflows (
    id      TEXT NOT NULL,
    overflow INT,
    underflow INT,
    UNIQUE(id)
);
INSERT INTO overflows VALUES('/ATLAS_2025_I2905252/mll',1,0);
INSERT INTO overflows VALUES('/ATLAS_2025_I2905252/d03-x01-y01',1,0);
INSERT INTO overflows VALUES('/ATLAS_2025_I2905252/mll_nlops',1,0);
INSERT INTO overflows VALUES('/ATLAS_2025_I2905252/mll_meps',1,0);


-- Histograms in a given analysis which should be ignored.
CREATE TABLE blacklist (
    id      TEXT NOT NULL,
    pattern TEXT NOT NULL,
    UNIQUE(id,pattern),
    FOREIGN KEY(id) REFERENCES analysis(id)
);
INSERT INTO blacklist VALUES('ATLAS_2025_I2905252','d02,d04,d05');
-- remove the correlations
INSERT INTO blacklist VALUES('ATLAS_2019_I1720442','d1[5-9],d2[0-9]');
-- remove the theory predictions
INSERT INTO blacklist VALUES('ATLAS_2019_I1720442','y0[2-4]');

-- N-jets differential measurement with poor theory modelling
INSERT INTO blacklist VALUES('CMS_2021_I1901295','d321');

-- remove the 3D correlations
INSERT INTO blacklist VALUES('ATLAS_2017_I1609448','d0[5-7]');
-- remove theory predictions
INSERT INTO blacklist VALUES('ATLAS_2017_I1609448','y0[2-4]');

-- don't use the normalised plots
INSERT INTO blacklist VALUES('CMS_2013_I1273574','d1[0-2]');

INSERT INTO blacklist VALUES('CMS_2014_I1298810','d1[3-8]');

INSERT INTO blacklist VALUES('ATLAS_2016_I1426515','d1[0-5]-x01-y02,d11-x01-y02');

INSERT INTO blacklist VALUES('ATLAS_2014_I1306615','d29,d30');

-- ATLAS Z+jets ratios
INSERT INTO blacklist VALUES('ATLAS_2017_I1514251:LMODE=EMU','d0[7-9]');

INSERT INTO blacklist VALUES('CMS_2017_I1518399','d02');

INSERT INTO blacklist VALUES('CMS_2016_I1491953','d3[6-9]');

-- have to veto all these at the moment because contur doesn't know
-- how to handle weighted differential xsecs presented as a 2D scatter.
INSERT INTO blacklist VALUES('ATLAS_2017_I1598613:BMODE=3MU','d01');

-- remove the normalised versions of the plots from CMS top.
INSERT INTO blacklist VALUES('CMS_2016_I1491950','d42,d44,d46,d48,d50,d52,d54,d56,d58,d59,d6[0-9],d7[0-9],d8[0-1]');

-- remove the normalised and 2d histograms
INSERT INTO blacklist VALUES('ATLAS_2023_I2648096', 'd30,d33,d36,d39,d42,d45,d48,d51,d54,d57,d60,d63,d78,d79,d80,d81,d82,d83,d84,d85');

-- CMS Z+b ratios
INSERT INTO blacklist VALUES('CMS_2017_I1499471','d02,d04,d06,d08,d10,Z_pt,Dphi_Zj,first_jet,HT');

-- ATLAS inclusive W/Z ratios
INSERT INTO blacklist VALUES('ATLAS_2016_I1502620:LMODE=W','d35-x01-y0[1-2]');

INSERT INTO blacklist VALUES('CMS_2018_I1662081','d0[1-7]');

-- CMS jet mass normalised plots.
INSERT INTO blacklist VALUES('CMS_2018_I1682495','d2[5-9],d3[0-9],d4[0-9]');

INSERT INTO blacklist VALUES('CMS_2018_I1711625','d03'); -- DY extrapolated

-- ATLAS WZ "total cross section"
INSERT INTO blacklist VALUES('ATLAS_2016_I1469071','d06');

-- W+/- ratios
INSERT INTO blacklist VALUES('ATLAS_2018_I1635273:LMODE=EL','y03');
INSERT INTO blacklist VALUES('ATLAS_2018_I1635273:LMODE=MU','y03');

-- pt mass ratio
INSERT INTO blacklist VALUES('ATLAS_2020_I1788444','d15');

-- both actual and normalised are produced in the rivet analysis CMS_2021_I1932460, hence blocked normalised plots
INSERT INTO blacklist VALUES('CMS_2021_I1932460','d09-x01-y01,d1[0-4]-x01-y01'); 

-- If an analysis has entries here, only the histograms mathcing the enetries will
-- be used, the rest will be ignored.
CREATE TABLE whitelist (
    id      TEXT NOT NULL,
    pattern TEXT NOT NULL,
    UNIQUE(id,pattern),
    FOREIGN KEY(id) REFERENCES analysis(id)
);

-- Z+b,c
INSERT INTO whitelist VALUES('ATLAS_2024_I2771257','d0[1-9],d10,d11');

-- SUSY inspired WW
INSERT INTO whitelist VALUES('ATLAS_2022_I2103950','d07,d09,d11,d13,d15,d17');

-- BG subtracted tt bb
INSERT INTO whitelist VALUES('ATLAS_2018_I1705857','d02,d04,d06,d08,d10,d12,d14,d16,d18,d20,d22,d24,d26,d28,d30,d32,d34,d36,d38,d40,d42,d44,d46,d48,d50,d52');

-- 7 TeV W & Z gamma
INSERT INTO whitelist VALUES('ATLAS_2013_I1217863:LMODE=ZEL','d11-x01-y01,d12-x01-y01');
INSERT INTO whitelist VALUES('ATLAS_2013_I1217863:LMODE=ZMU','d11-x01-y02,d12-x01-y02');
INSERT INTO whitelist VALUES('ATLAS_2013_I1217863:LMODE=WEL','d07-x01-y01,d08-x01-y01');
INSERT INTO whitelist VALUES('ATLAS_2013_I1217863:LMODE=WMU','d07-x01-y02,d08-x01-y02');

-- 7 TeV Z+jet -- e and mu
INSERT INTO whitelist VALUES('ATLAS_2013_I1230812','d01-x01-y02,d03-x01-y02,d05-x01-y02,d07-x01-y02,d09-x01-y02,d1[0-9]-x01-y02,d2[0-8]-x01-y02');
INSERT INTO whitelist VALUES('ATLAS_2013_I1230812','d01-x01-y03,d03-x01-y03,d05-x01-y03,d07-x01-y03,d09-x01-y03,d1[0-9]-x01-y03,d2[0-8]-x01-y03');

-- ttbar
INSERT INTO whitelist VALUES('ATLAS_2017_I1614149','d15,d17,d19,d21,d23,d25,d27');

-- WW
INSERT INTO whitelist VALUES('ATLAS_2019_I1734263','d01,d04,d07,d10,d13,d16,d19');  

-- hadronic top
INSERT INTO whitelist VALUES('ATLAS_2020_I1801434','d04-x01-y01,d08-x01-y01,d12-x01-y01,d16-x01-y01,d20-x01-y01,d24-x01-y01,d28-x01-y01');
INSERT INTO whitelist VALUES('ATLAS_2020_I1801434','d32-x01-y01,d36-x01-y01,d40-x01-y01,d44-x01-y01,d48-x01-y01,d52-x01-y01,d56-x01-y01');
INSERT INTO whitelist VALUES('ATLAS_2020_I1801434','d60-x01-y01,d64-x01-y01,d68-x01-y01,d72-x01-y01,d76-x01-y01,d80-x01-y01,d84-x01-y01');
INSERT INTO whitelist VALUES('ATLAS_2020_I1801434','d88-x01-y01,d92-x01-y01,d96-x01-y01,d100-x01-y01,d104-x01-y01,d108-x01-y01,d112-x01-y01');
INSERT INTO whitelist VALUES('ATLAS_2020_I1801434','d116-x01-y01,d120-x01-y01,d124-x01-y01,d128-x01-y01,d132-x01-y01,d136-x01-y01');

-- Z->mumu + jets
INSERT INTO whitelist VALUES('CMS_2021_I1866118','d0[1-5]');

-- LLMET
INSERT INTO whitelist VALUES('ATLAS_2016_I1494075:LMODE=2L2NU','d0[6-8]-x01-y01');
-- 4L (currently cant use 4 and 5 cos they are in pb)
INSERT INTO whitelist VALUES('ATLAS_2016_I1494075:LMODE=4L','d0[2-5]-x01-y01');

-- W+D
INSERT INTO whitelist VALUES('ATLAS_2023_I2628732','d0[3-9]-x01-y01,d10-x01-y01');

-- Z->vv
-- INSERT INTO whitelist VALUES('CMS_2020_I1837084','d04-x01-y04');

-- Z+jets
INSERT INTO whitelist VALUES('CMS_2022_I2079374','d01,d03,d05,d07,d09,d11,d13,15,17,19,21,23,25,27');

-- ttbar whitelist only the particle-level normalised plots (these appear directly in the paper)
INSERT INTO whitelist VALUES('ATLAS_2022_I2077575','d(02|7[5-9]|[89][0-9]|1[0-3][0-9]|14[0-6])');

-- LLgamma
INSERT INTO whitelist VALUES('ATLAS_2019_I1764342','y01');
INSERT INTO whitelist VALUES('ATLAS_2022_I2593322','d0[2-7]');
-- 4L
INSERT INTO whitelist VALUES('ATLAS_2021_I1849535','y01');
INSERT INTO whitelist VALUES('ATLAS_2023_I2690799','(d0[7-9]|d1[0-9]|d2[0-6])-x01-y01');

-- W charm
INSERT INTO whitelist VALUES('ATLAS_2014_I1282447','d03-x01-y01,d04-x01-y03');

-- EW Z+jets
INSERT INTO whitelist VALUES('ATLAS_2014_I1279489','d0[1-7]-x01-y01,d1[4-7]-x01-y01');
--
INSERT INTO whitelist VALUES('ATLAS_2014_I1307243','d1[3-9],d2[0-8]');

--
INSERT INTO whitelist VALUES('CMS_2016_I1454211','d02,d04,d06,d08');
--
INSERT INTO whitelist VALUES('ATLAS_2018_I1646686','d0[1-9]-x01-y01,d1[0-4]-x01-y01');
--
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d01-,d03-,d05-,d07-,d09-,d11-,d13-,d15-,d17-,d17[0-2]-,d1[8-9]-,d20-,d2[2-5]-');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d2[7-9]-,d30-,d3[2-5]-,d3[7-9],d40,d4[2-5],d4[7-9],d5[0-4],d5[6-9],d6[0-3]');
INSERT INTO whitelist VALUES('CMS_2018_I1663958','d6[5-9],d7[0-2],d7[4-9],d8[0-1]');

-- ttbar+jets
INSERT INTO whitelist VALUES('ATLAS_2018_I1656578','d96,d98,d100,d102,d104,d106,d108,d110,d112,d114');

-- EW W+jet
INSERT INTO whitelist VALUES('ATLAS_2017_I1517194','d10,d6[4-7],d69,d7[0-9],d8[0-3],d8[5-9],d9[0-8],d11[0-5],d13[5-9],d14[0-9]');

-- H to WW
INSERT INTO whitelist VALUES('ATLAS_2016_I1444991','d0[2-5]-x01-y01');

-- ttbar
INSERT INTO whitelist VALUES('ATLAS_2015_I1404878','d01,d03,d05,d07,d09,d11,d13,d15,d17,d19,d21');

-- [d159 to d211], [d317 to d329]: absolute, single differential dist'ns
INSERT INTO whitelist VALUES('CMS_2021_I1901295','d159,d163,d167,d171,d175,d179,d183,d187,d191,d195,d199,d203,d207,d211,d317,d325,d329');
-- [d220 to d307]: absolute, double differential dist'ns, removed for now d21[5-9],d220,d229,d23[0-4],d24[3-8],d25[7-9],d26[0-2],d27[1-6],d28[5-8],d29[5-7],d30[3-7]'); 

-- atlas z+jets
INSERT INTO whitelist VALUES('ATLAS_2017_I1627873','d02');
-- cms z+jets
INSERT INTO whitelist VALUES('CMS_2014_I1303894','d');

-- cms z+b
INSERT INTO whitelist VALUES('CMS_2013_I1256943','d');

-- ATLAS 0-lepton search
INSERT INTO whitelist VALUES('ATLAS_2016_I1458270','d0[4-9]-x01-y01,d10-x01-y01');

-- ttbar leptonic
INSERT INTO whitelist VALUES('ATLAS_2019_I1759875','d01,d03,d05,d07,d09,d11,d13,d15,d17,d19,d21');
INSERT INTO whitelist VALUES('ATLAS_2022_I2037744','d03,d06,d09,d12,d15,d18,d21,24,d27,d30,d33,d36,d39,d42,d45,d48,d51,d54'); --,d6[0-2],d7[2-4],d8[4-6],d9[6-8]'); no theory uncertainties available for d60 onwards
-- softdrop mass
INSERT INTO whitelist VALUES('ATLAS_2017_I1637587','d0[1-3]');

-- single top
INSERT INTO whitelist VALUES('CMS_2019_I1744604','d13,d15,d17,d19,d21,d23');

-- top pairs (resolved)
INSERT INTO whitelist VALUES('ATLAS_2019_I1750330:TYPE=BOTH','d04-,d08-,d12-,d16-,d20-,d24-,d28-,d32-,d36-,d40-,d44-,d48-,d52-');
-- boosted
INSERT INTO whitelist VALUES('ATLAS_2019_I1750330:TYPE=BOTH','d843-,d847-,d851-,d855-,d859-,d863-,d867-,d871-,d875-,d879-,d883-,d887-');

-- ttgamma
INSERT INTO whitelist VALUES('ATLAS_2018_I1707015:LMODE=SINGLE','d0[3-5]');
INSERT INTO whitelist VALUES('ATLAS_2018_I1707015:LMODE=DILEPTON','d0[6-9],d10');
INSERT INTO whitelist VALUES('ATLAS_2024_I2768921:LMODE=SINGLE','d06,d08,d10,d44,d46,d48');
INSERT INTO whitelist VALUES('ATLAS_2024_I2768921:LMODE=DILEPTON','d12,d14,d16,d50,d52,d54');

-- W and Z
INSERT INTO whitelist VALUES('LHCB_2016_I1454404:MODE=WJET','d0[4-9]');
INSERT INTO whitelist VALUES('LHCB_2016_I1454404:MODE=ZJET','d10');

-- Z
--INSERT INTO whitelist VALUES('ATLAS_2015_I1408516:LMODE=EL','y01');
--INSERT INTO whitelist VALUES('ATLAS_2015_I1408516:LMODE=MU','y04');


INSERT INTO whitelist VALUES('ATLAS_2015_I1408516:LMODE=EL','d0[2-9]-x01-y01');
INSERT INTO whitelist VALUES('ATLAS_2015_I1408516:LMODE=EL','d1[0-3]-x01-y01');
INSERT INTO whitelist VALUES('ATLAS_2015_I1408516:LMODE=EL','d1[7-9]-x01-y01');
INSERT INTO whitelist VALUES('ATLAS_2015_I1408516:LMODE=EL','d2[0-2]-x01-y01');

INSERT INTO whitelist VALUES('ATLAS_2015_I1408516:LMODE=MU','d0[2-9]-x01-y04');
INSERT INTO whitelist VALUES('ATLAS_2015_I1408516:LMODE=MU','d1[0-3]-x01-y04');
INSERT INTO whitelist VALUES('ATLAS_2015_I1408516:LMODE=MU','d1[7-9]-x01-y04');
INSERT INTO whitelist VALUES('ATLAS_2015_I1408516:LMODE=MU','d2[0-2]-x01-y04');


-- gamma met
INSERT INTO whitelist VALUES('ATLAS_2016_I1448301:LMODE=NU','d02-x01-y01,d04-x01-y01,d07-x01-y01,d08-x01-y01');
-- gamma ee
INSERT INTO whitelist VALUES('ATLAS_2016_I1448301:LMODE=LL','d01-x01-y01,d03-x01-y01');
-- gamma mumu
INSERT INTO whitelist VALUES('ATLAS_2016_I1448301:LMODE=LL','d01-x01-y02,d03-x01-y02');
-- gamma ll
INSERT INTO whitelist VALUES('ATLAS_2016_I1448301:LMODE=LL','d0[5-6]-x01-y01,d09-x01-y01,d1[0-1]-x01-y01');
-- gamma ll jet
INSERT INTO whitelist VALUES('ATLAS_2022_I2614196','d0[1-5],d0[6-9],d1[0-4],d1[7-9],d2[0-5]');
-- HMDY ee
INSERT INTO whitelist VALUES('ATLAS_2016_I1467454:LMODE=EL','d1[8-9],d2[0-8]');
-- HMDY mumu
INSERT INTO whitelist VALUES('ATLAS_2016_I1467454:LMODE=MU','d29,d3[0-9]');

-- Hadronic top mass
INSERT INTO whitelist VALUES('CMS_2019_I1764472','d01');

-- plots with b-jet veto applied.
INSERT INTO whitelist VALUES('ATLAS_2021_I1852328','y02');

-- pick out the plots we want
INSERT INTO whitelist VALUES('CMS_2019_I1753680:LMODE=EMU','d2[6-8]-x01-y02');  -- need to sort out the theory
INSERT INTO whitelist VALUES('CMS_2019_I1753680:LMODE=EMU','d29-x01-y02'); -- these are LL
INSERT INTO whitelist VALUES('CMS_2019_I1753680:LMODE=EMU','d2[6-8]-x01-y01');
INSERT INTO whitelist VALUES('CMS_2019_I1753680:LMODE=EMU','d29-x01-y01'); -- these are LL

-- 13TeV H->yy
INSERT INTO whitelist VALUES('ATLAS_2022_I2023464','d0[2-9],d10,d21,d23,d25,d27,d29,d31,d33,d35,d37,d39,d41,d43,d45,d47,d49,d51,d53,d55,d57,d59');

-- WWgamma fiducial cross section
INSERT INTO whitelist VALUES('CMS_2023_I2709669','d01-x01-y01');

-- 13TeV WW+jets
INSERT INTO whitelist VALUES('CMS_2022_I2080534','d01-x01-y01');

-- Measurements in a subpool will be treated as uncorrelated, so will be combined to give
-- a single likelihood, as though they were a single measurement
CREATE TABLE subpool (
    id      TEXT NOT NULL,
    pattern TEXT NOT NULL,
    subid   TEXT NOT NULL,
    UNIQUE(id,pattern),
    FOREIGN KEY(id) REFERENCES analysis(id)
);
-- 7 TeV
--INSERT INTO subpool VALUES('ATLAS_2012_I1203852','(d01-x01-y01|d01-x01-y03)',0); -- inc 4l vs 2l + met
--INSERT INTO subpool VALUES('ATLAS_2012_I1203852','(d03|d04)',1); -- pt 4l vs 2l + met
--INSERT INTO subpool VALUES('ATLAS_2012_I1203852','(d05|d06)',2); -- dphi 4l vs 2l + met
--INSERT INTO subpool VALUES('ATLAS_2012_I1203852','(d07|d08)',3); -- mT 4l vs 2l + met

-- eand mu of each measurement are a subpool
INSERT INTO subpool VALUES('ATLAS_2017_I1589844','d01-x01-y01,d01-x01-y02',0);
INSERT INTO subpool VALUES('ATLAS_2017_I1589844','d01-x01-y03,d01-x01-y04',1);
INSERT INTO subpool VALUES('ATLAS_2017_I1589844','d01-x01-y05,d01-x01-y06',2);
INSERT INTO subpool VALUES('ATLAS_2017_I1589844','d01-x01-y07,d01-x01-y08',3);
INSERT INTO subpool VALUES('ATLAS_2017_I1589844','d02-x01-y01,d02-x01-y02',0);
INSERT INTO subpool VALUES('ATLAS_2017_I1589844','d02-x01-y03,d02-x01-y04',1);
INSERT INTO subpool VALUES('ATLAS_2017_I1589844','d02-x01-y05,d02-x01-y06',2);
INSERT INTO subpool VALUES('ATLAS_2017_I1589844','d02-x01-y07,d02-x01-y08',3);
INSERT INTO subpool VALUES('ATLAS_2017_I1589844','d03-x01-y01,d03-x01-y02',0);
INSERT INTO subpool VALUES('ATLAS_2017_I1589844','d03-x01-y03,d03-x01-y04',1);
INSERT INTO subpool VALUES('ATLAS_2017_I1589844','d03-x01-y05,d03-x01-y06',2);
INSERT INTO subpool VALUES('ATLAS_2017_I1589844','d03-x01-y07,d03-x01-y08',3);
INSERT INTO subpool VALUES('ATLAS_2017_I1589844','d04-x01-y01,d04-x01-y02',0);
INSERT INTO subpool VALUES('ATLAS_2017_I1589844','d04-x01-y03,d04-x01-y04',1);
INSERT INTO subpool VALUES('ATLAS_2017_I1589844','d04-x01-y05,d04-x01-y06',2);
INSERT INTO subpool VALUES('ATLAS_2017_I1589844','d04-x01-y07,d04-x01-y08',3);
INSERT INTO subpool VALUES('ATLAS_2017_I1589844','d05-x01-y01,d05-x01-y02',0);
INSERT INTO subpool VALUES('ATLAS_2017_I1589844','d05-x01-y03,d05-x01-y04',1);
INSERT INTO subpool VALUES('ATLAS_2017_I1589844','d05-x01-y05,d05-x01-y06',2);
INSERT INTO subpool VALUES('ATLAS_2017_I1589844','d05-x01-y07,d05-x01-y08',3);
INSERT INTO subpool VALUES('ATLAS_2017_I1589844','d06-x01-y01,d06-x01-y02',0);
INSERT INTO subpool VALUES('ATLAS_2017_I1589844','d06-x01-y03,d06-x01-y04',1);
INSERT INTO subpool VALUES('ATLAS_2017_I1589844','d06-x01-y05,d06-x01-y06',2);
INSERT INTO subpool VALUES('ATLAS_2017_I1589844','d06-x01-y07,d06-x01-y08',3);
INSERT INTO subpool VALUES('ATLAS_2017_I1589844','d07-x01-y01,d07-x01-y02',0);
INSERT INTO subpool VALUES('ATLAS_2017_I1589844','d07-x01-y03,d07-x01-y04',1);
INSERT INTO subpool VALUES('ATLAS_2017_I1589844','d07-x01-y05,d07-x01-y06',2);
INSERT INTO subpool VALUES('ATLAS_2017_I1589844','d07-x01-y07,d07-x01-y08',3);
INSERT INTO subpool VALUES('ATLAS_2017_I1589844','d08-x01-y01,d08-x01-y02',0);
INSERT INTO subpool VALUES('ATLAS_2017_I1589844','d08-x01-y03,d08-x01-y04',1);
INSERT INTO subpool VALUES('ATLAS_2017_I1589844','d08-x01-y05,d08-x01-y06',2);
INSERT INTO subpool VALUES('ATLAS_2017_I1589844','d08-x01-y07,d08-x01-y08',3);


-- eand mu of each measurement are a subpool
INSERT INTO subpool VALUES('ATLAS_2013_I1230812','d01-x01-y02,d01-x01-y03',0);
INSERT INTO subpool VALUES('ATLAS_2013_I1230812','d03-x01-y02,d01-x01-y03',1);
INSERT INTO subpool VALUES('ATLAS_2013_I1230812','d05-x01-y02,d01-x01-y03',2);
INSERT INTO subpool VALUES('ATLAS_2013_I1230812','d07-x01-y02,d01-x01-y03',3);
INSERT INTO subpool VALUES('ATLAS_2013_I1230812','d09-x01-y02,d01-x01-y03',4);
INSERT INTO subpool VALUES('ATLAS_2013_I1230812','d10-x01-y02,d01-x01-y03',5);
INSERT INTO subpool VALUES('ATLAS_2013_I1230812','d11-x01-y02,d01-x01-y03',6);
INSERT INTO subpool VALUES('ATLAS_2013_I1230812','d12-x01-y02,d01-x01-y03',7);
INSERT INTO subpool VALUES('ATLAS_2013_I1230812','d13-x01-y02,d01-x01-y03',8);
INSERT INTO subpool VALUES('ATLAS_2013_I1230812','d14-x01-y02,d01-x01-y03',9);
INSERT INTO subpool VALUES('ATLAS_2013_I1230812','d15-x01-y02,d01-x01-y03',10);
INSERT INTO subpool VALUES('ATLAS_2013_I1230812','d16-x01-y02,d01-x01-y03',11);
INSERT INTO subpool VALUES('ATLAS_2013_I1230812','d17-x01-y02,d01-x01-y03',12);
INSERT INTO subpool VALUES('ATLAS_2013_I1230812','d18-x01-y02,d01-x01-y03',13);
INSERT INTO subpool VALUES('ATLAS_2013_I1230812','d19-x01-y02,d01-x01-y03',14);
INSERT INTO subpool VALUES('ATLAS_2013_I1230812','d20-x01-y02,d01-x01-y03',15);
INSERT INTO subpool VALUES('ATLAS_2013_I1230812','d21-x01-y02,d01-x01-y03',16);
INSERT INTO subpool VALUES('ATLAS_2013_I1230812','d22-x01-y02,d01-x01-y03',17);
INSERT INTO subpool VALUES('ATLAS_2013_I1230812','d23-x01-y02,d01-x01-y03',18);
INSERT INTO subpool VALUES('ATLAS_2013_I1230812','d24-x01-y02,d01-x01-y03',19);
INSERT INTO subpool VALUES('ATLAS_2013_I1230812','d25-x01-y02,d01-x01-y03',20);
INSERT INTO subpool VALUES('ATLAS_2013_I1230812','d26-x01-y02,d01-x01-y03',21);
INSERT INTO subpool VALUES('ATLAS_2013_I1230812','d27-x01-y02,d01-x01-y03',22);
INSERT INTO subpool VALUES('ATLAS_2013_I1230812','d28-x01-y02,d01-x01-y03',23);

INSERT INTO subpool VALUES('ATLAS_2014_I1325553','d01-x01-y0[1-6]',0); -- r=0.4 inclusive jet y bins
INSERT INTO subpool VALUES('ATLAS_2014_I1325553','d02-x01-y0[1-6]',1); -- r=0.6 inclusive jet y bins
INSERT INTO subpool VALUES('ATLAS_2014_I1268975','d01-x01-y0[1-6]',0); -- r=0.4 dijet y* bins
INSERT INTO subpool VALUES('ATLAS_2014_I1268975','d02-x01-y0[1-6]',1); -- r=0.6 dijet y* bins
INSERT INTO subpool VALUES('ATLAS_2014_I1326641','d0[1-5]-x01-y01',0);       -- r=0.4 3 jet y* bins
INSERT INTO subpool VALUES('ATLAS_2014_I1326641','(d10|d0[6-9])-x01-y01',1); -- r=0.6 3 jet y* bins
INSERT INTO subpool VALUES('CMS_2014_I1298810','d0[1-6]-x01-y01',0);           -- r=0.5 y bins
INSERT INTO subpool VALUES('CMS_2014_I1298810','(d1[0-2]|d0[7-9])-x01-y01',1); -- r=0.7 y bins
INSERT INTO subpool VALUES('ATLAS_2014_I1307243','(d20|d1[3-9])-x01-y01',0);   -- deta jets Dy bins, inclusive
INSERT INTO subpool VALUES('ATLAS_2014_I1307243','d2[1-8]-x01-y01',1);         -- deta jets Dy bins, gap events
INSERT INTO subpool VALUES('ATLAS_2013_I1263495','d0[1-2]-x01-y01',0);         -- isolated photon eta bins
-- 8 TeV
INSERT INTO subpool VALUES('ATLAS_2016_I1457605','.',0); -- inclusive photon eta-gamma bins
INSERT INTO subpool VALUES('ATLAS_2017_I1604271','d0[1-6]-x01-y01',0);   -- inclusive jet pt, y bins, r=0.6
INSERT INTO subpool VALUES('ATLAS_2017_I1604271','(d1[0-2]|d0[7-9])',1); -- inclusive jet pt, y bins, r=0.4

INSERT INTO subpool VALUES('ATLAS_2015_I1408516:LMODE=EL','d0[2-4]-x01-y01',0); -- low mass phi* distributions in eta bins
INSERT INTO subpool VALUES('ATLAS_2015_I1408516:LMODE=EL','(d0[5-9]-x01-y01|d10-x01-y01)',1); -- medium mass phi* distributions in eta bins
INSERT INTO subpool VALUES('ATLAS_2015_I1408516:LMODE=EL','d1[1-3]-x01-y01',2); -- medium mass phi* distributions in eta bins
INSERT INTO subpool VALUES('ATLAS_2015_I1408516:LMODE=MU','d0[2-4]-x01-y04',3); -- low mass phi* distributions in eta bins
INSERT INTO subpool VALUES('ATLAS_2015_I1408516:LMODE=MU','(d0[5-9]-x01-y04|d10-x01-y04)',4); -- low mass phi* distributions in eta bins
INSERT INTO subpool VALUES('ATLAS_2015_I1408516:LMODE=MU','d1[1-3]-x01-y04',5); -- low mass phi* distributions in eta bins

INSERT INTO subpool VALUES('CMS_2016_I1454211','d02|d06',0); -- top pt (el and mu)
INSERT INTO subpool VALUES('CMS_2016_I1454211','d04|d08',0); -- top y (el and mu)


-- 13 TeV
INSERT INTO subpool VALUES('ATLAS_2018_I1634970','d0[1-6]-x01-y01',0);   -- inclusive jet pt, y bins
INSERT INTO subpool VALUES('ATLAS_2018_I1634970','(d1[0-2]|d0[7-9])',1); -- dijet mass, y* bins

INSERT INTO subpool VALUES('CMS_2016_I1459051','d0[1-7]-x01-y01','07pTvy');   -- inclusive jet pt, y bins R=0.7
INSERT INTO subpool VALUES('CMS_2016_I1459051','(d1[0-4]|d0[8-9])','04pTvy'); -- inclusive jet pt, y bins R=0.4

INSERT INTO subpool VALUES('ATLAS_2019_I1725190','d0[1-2]-x01-y01','FlavourSplit'); -- HMDY e and mu distributions

INSERT INTO subpool VALUES('CMS_2018_I1711625','d0[5-6]-x01-y01','FlavourSplit'); -- HMDY e and mu distributions

INSERT INTO subpool VALUES('ATLAS_2019_I1720442','d01-x01-y01','M4Linclusive'); -- M4L inclusive
INSERT INTO subpool VALUES('ATLAS_2019_I1720442','d0[2-5]-x01-y01','M4LvpT'); -- M4L vs pT
INSERT INTO subpool VALUES('ATLAS_2019_I1720442','d0[6-9]-x01-y01','M4Lvy'); -- M4L vs y
INSERT INTO subpool VALUES('ATLAS_2019_I1720442','d1[2-4]-x01-y01','M4LvFlavour'); -- M4L vs flavour

INSERT INTO subpool VALUES('ATLAS_2021_I1849535','d0[2-4]-x01-y01','M4LvFlavour'); -- M4L vs flavour

INSERT INTO subpool VALUES('ATLAS_2021_I1849535','d0[5-8]','MZ1'); -- MZ1 in different 4L regions
INSERT INTO subpool VALUES('ATLAS_2021_I1849535','(d09|d1[0-2])','MZ2'); -- MZ1 in different 4L regions
INSERT INTO subpool VALUES('ATLAS_2021_I1849535','d1[3-6]','pTZ1'); -- pT(Z1) in different 4L mass regions
INSERT INTO subpool VALUES('ATLAS_2021_I1849535','(d1[7-9]|d20)','pTZ2'); -- pT(Z2) in different 4L mass regions
INSERT INTO subpool VALUES('ATLAS_2021_I1849535','d2[1-4]','costsZ1'); -- cost(theta*) Z1 in different 4L mass regions
INSERT INTO subpool VALUES('ATLAS_2021_I1849535','d2[5-8]','costsZ2'); -- cost(theta*) Z2 in different 4L mass regions
INSERT INTO subpool VALUES('ATLAS_2021_I1849535','(d29|d3[0-2])','Dy'); -- delta y between pairs in different 4L mass regions
INSERT INTO subpool VALUES('ATLAS_2021_I1849535','d3[3-6]','Dphipairs'); -- delta phi between pairs in different 4L mass regions
INSERT INTO subpool VALUES('ATLAS_2021_I1849535','(d3[7-9]|d40)','Dphileptons'); -- delta phi between leading leptons in different 4L mass regions
INSERT INTO subpool VALUES('ATLAS_2021_I1849535','d4[1-5]-x01-y01','ptslices'); -- ptslices
INSERT INTO subpool VALUES('ATLAS_2021_I1849535','(d4[6-9]|d50)-x01-y01','yslices'); -- yslices

-- 13 TeV multijet event shapes
INSERT INTO subpool VALUES('ATLAS_2020_I1808726','(d0[1-9]|d1[1-2])','TThrustMaj'); -- transverse thrust major in non-overlapping regions.
INSERT INTO subpool VALUES('ATLAS_2020_I1808726','(d1[3-9]|d2[0-4])','ThrustMin'); -- thrust minor in non-overlapping regions.
INSERT INTO subpool VALUES('ATLAS_2020_I1808726','(d2[5-9]|d3[0-6])','TSphericity'); --  transverse sphericity in non-overlapping regions.
INSERT INTO subpool VALUES('ATLAS_2020_I1808726','(d3[7-9]|d4[0-8])','Aplanarity'); --  aplanarity in non-overlapping regions.
INSERT INTO subpool VALUES('ATLAS_2020_I1808726','(d49|d5[0-9])|d60','C'); --  C in non-overlapping regions.
INSERT INTO subpool VALUES('ATLAS_2020_I1808726','(d6[1-9]|d7[1-2])','D'); --  D in non-overlapping regions.
INSERT INTO subpool VALUES('ATLAS_2020_I1808726','d7[3-5]','Multiplicity'); --  jet multiplicity in non-overlapping regions.

-- 13TeV HMDY search
INSERT INTO subpool VALUES('ATLAS_2019_I1725190','d0[1-2]','Mass'); --  electrons and muons

-- 13TeV ttbar boosted
INSERT INTO subpool VALUES('ATLAS_2022_I2077575','(d9[4-7])','y_2');
INSERT INTO subpool VALUES('ATLAS_2022_I2077575','(d9[8-9]|d10[0-1])','Pt_1');
INSERT INTO subpool VALUES('ATLAS_2022_I2077575','(d10[2-5])','Pt_2');
INSERT INTO subpool VALUES('ATLAS_2022_I2077575','(d10[6-9])','P_tt');
INSERT INTO subpool VALUES('ATLAS_2022_I2077575','(d11[0-3])','Pt_1');
INSERT INTO subpool VALUES('ATLAS_2022_I2077575','(d11[4-7])','y_tt/Pt_1');
INSERT INTO subpool VALUES('ATLAS_2022_I2077575','(d11[8-9]|d12[0-1])','y_tt/y_1');
INSERT INTO subpool VALUES('ATLAS_2022_I2077575','(d12[2-5])','y_t1/m_tt');
INSERT INTO subpool VALUES('ATLAS_2022_I2077575','(d12[6-9])','y_tt/Pt_1');
INSERT INTO subpool VALUES('ATLAS_2022_I2077575','(d13[0-3])','P_tt/m_tt');
INSERT INTO subpool VALUES('ATLAS_2022_I2077575','(d13[4-7])','y_tt/P_tt');

-- VBS enhanced and VBS suppressed regions
INSERT INTO subpool VALUES('ATLAS_2023_I2690799','d07,d08','mjj');
INSERT INTO subpool VALUES('ATLAS_2023_I2690799','d09,d10','m4l');
INSERT INTO subpool VALUES('ATLAS_2023_I2690799','d11,d12','pT4l');
INSERT INTO subpool VALUES('ATLAS_2023_I2690799','d13,d14','dphijj');
INSERT INTO subpool VALUES('ATLAS_2023_I2690799','d15,d16','dyjj');
INSERT INTO subpool VALUES('ATLAS_2023_I2690799','d17,d18','costhetastar12');
INSERT INTO subpool VALUES('ATLAS_2023_I2690799','d19,d20','costhetastar34');
INSERT INTO subpool VALUES('ATLAS_2023_I2690799','d21,d22','pTjj');
INSERT INTO subpool VALUES('ATLAS_2023_I2690799','d23,d24','pT4ljj');
INSERT INTO subpool VALUES('ATLAS_2023_I2690799','d25,d26','ST4ljj');



CREATE TABLE normalization (
--  analysis id, plot pattern, norm factor for ref data, number of x units an n_event distribution is differential in (nx; 0 if not applicable).
--
--  The normalisation is applied on the assumption the Rivet plots have been area-normalised to one, i.e. are
--  presented as 1/sigma(fid) * dsigma(fid)/dX where X is some kinematic variable.
--
--  Therefore the norm factor number needs to be the integrated cross section for the fiducial region considered,
--  and should be in pb since that is what Rivet reports.
--
--  The nx applies for n_event distributions in searches which typically have no uncertainty in y. If the plot
--  is in e.g. n_events/10 GeV, to get the number of events, we multiply by the bin width and divide by nx; from this
--  the Poisson (~ root(n)) uncertainty can be calculated. nx < 0 means the bin width is constant and the plot is just differential in that. (nx = 0 means this is already a differential cross section with uncertinties.)
    id      TEXT NOT NULL,
    pattern TEXT NOT NULL,
    norm    REAL NOT NULL,
    nxdiff INT NOT NULL,
    UNIQUE(id,pattern),
    FOREIGN KEY(id) REFERENCES analysis(id)
);
-- CMS 3L is normalised in the Rivet routine to 24.09 pb which is allegedly the WZ cross-section
-- in the region.
-- Note that way the signal is dealt within Contur means this is turned into a cross-section
-- normalisation just as though the scaling were to unity; the 24.09 makes rather than 1.0 makes
-- no difference. However, the data are presented as WZ cross sections, that is is (a) they are
-- not nu lll cross sections but (b) and they not area normalised. What this means is we have to
-- turn them into nu lll cross sections to compare to the MC. This means multiplying by the
-- BR WZ --> lll nu where lll are electrons or muons.
-- This is still a fudge, since we don't know the correction for the fiducial cuts, but that
-- should at least lead to an underestimate of any sensitivity.

--
INSERT INTO normalization VALUES('CMS_2016_I1487288','d',0.0363*2.0*0.1080*2.0,0); -- 3l

-- ATLAS 13TeV ttbar -> bjets
INSERT INTO normalization VALUES('ATLAS_2024_I2809112', '(d95|d72|d74|d76|d78|d77|d79|d80|d81|d88|d89|d90|d91|d97|d99)', 0.143, 0); -- 3 b jets
INSERT INTO normalization VALUES('ATLAS_2024_I2809112', '(d98|d101)', 0.087, 0); -- 3 b jets + 1 light jet
INSERT INTO normalization VALUES('ATLAS_2024_I2809112', '(d128|d129|d130|d131)', 0.022, 0); -- 4 b jets
 

-- 7 TeV 4L (cross section and BF to leptons)
INSERT INTO normalization VALUES('ATLAS_2012_I1203852:LMODE=LL','(d03|d05|d07)',0.0254,0); -- 4l
INSERT INTO normalization VALUES('ATLAS_2012_I1203852:LMODE=LNU','(d04|d06|d08)',0.0127,0); -- 2l met

-- Normalisation from ATLAS aux material
INSERT INTO normalization VALUES('ATLAS_2019_I1724098','(d0[1-6]|d2[3-8])' ,48200000.0/33000.0,0); -- dijet selection
INSERT INTO normalization VALUES('ATLAS_2019_I1724098','(d0[7-9]|d1[0-4]|d29|d3[0-6])',14400.0/33000.0,0); -- top
INSERT INTO normalization VALUES('ATLAS_2019_I1724098','(d1[5-9]|d2[0-2]|d3[7-9]|d4[0-4])',13900.0/33000.0,0); -- W selection

-- normalisation for 8TeV 3Jet mode using sum of eventcount
INSERT INTO normalization VALUES('CMS_2021_I1847230:MODE=QCD8TeV','d01-x01-y01',7.8344933,0);
INSERT INTO normalization VALUES('CMS_2021_I1847230:MODE=QCD8TeV','d02-x01-y01',7.7247165,0);
INSERT INTO normalization VALUES('CMS_2021_I1847230:MODE=QCD8TeV','d03-x01-y01',10.0000004,0);
INSERT INTO normalization VALUES('CMS_2021_I1847230:MODE=QCD8TeV','d04-x01-y01',10.0000007,0);

--normalisation for 13TeV 3Jet mode using sum of eventcount
INSERT INTO normalization VALUES('CMS_2021_I1847230:MODE=QCD13TeV','d05-x01-y01',7.6331767,0);
INSERT INTO normalization VALUES('CMS_2021_I1847230:MODE=QCD13TeV','d06-x01-y01',7.5335873,0);
INSERT INTO normalization VALUES('CMS_2021_I1847230:MODE=QCD13TeV','d07-x01-y01',10.0000004,0);
INSERT INTO normalization VALUES('CMS_2021_I1847230:MODE=QCD13TeV','d08-x01-y01',10.0000005,0);
-- more attention needed if using the ZJet mode results other than these two modes.
-- normalisation factor with integrated cross section in pb for CMS_2020_I1814328
INSERT INTO normalization VALUES('CMS_2020_I1814328','(d02|d04|d05|d06|d07)',122.0,0);


-- normalisation factor with integrated cross section in pb for ATLAS_2019_I1768911 
INSERT INTO normalization VALUES('ATLAS_2019_I1768911','d27-x01-y01,d28-x01-y01',736.2,0); -- NB these are approx (LO born) but ok

-- this is BR to a single charged lepton, needed when the xsec is report as a W
-- and the generator reports the final state.
-- INSERT INTO normalization VALUES('ATLAS_2014_I1319490_MU','d',0.108059,0);
-- INSERT INTO normalization VALUES('ATLAS_2014_I1319490_EL','d',0.108059,0);
-- INSERT INTO normalization VALUES('CMS_2014_I1303894','d',0.108059,0);

-- these are the integrated cross section of the plot, in pb
-- EW Z+jets
INSERT INTO normalization VALUES('ATLAS_2014_I1279489','d01-x01-y01,d03-x01-y01',5.88,0); -- baseline region
INSERT INTO normalization VALUES('ATLAS_2014_I1279489','d14-x01-y01,d16-x01-y01',1.82,0); -- high pT region
INSERT INTO normalization VALUES('ATLAS_2014_I1279489','d05-x01-y01,d06-x01-y01,d07-x01-y01',0.066,0); -- high mass region
INSERT INTO normalization VALUES('ATLAS_2014_I1279489','d02-x01-y01,d04-x01-y01',1.1,0); -- search region
INSERT INTO normalization VALUES('ATLAS_2014_I1279489','d15-x01-y01,d17-x01-y01',0.447,0); -- control region

-- these are the integrated cross section of the plot, in pb
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=EL','d23',1.45,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=EL','d24',1.03,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=EL','d25',0.97,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=EL','(d0[2-4]|d14|d26)',14.96,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=EL','(d0[5-9]|d10|d15|d1[7-9]|d2[0-2]|d27)',537.10,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=EL','(d1[1-3]|d16|d28)',5.59,0);

-- these are the integrated cross section of the plot, in pb
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=MU','d23',1.45,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=MU','d24',1.03,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=MU','d25',0.97,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=MU','(d0[2-4]|d14|d26)',14.96,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=MU','(d0[5-9]|d10|d15|d1[7-9]|d2[0-2]|d27)',537.10,0);
INSERT INTO normalization VALUES('ATLAS_2015_I1408516:LMODE=MU','(d1[1-3]|d16|d28)',5.59,0);

-- CMS single jet mass stuff here
-- WJETS. Cross section in pb
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=W','(d52|d56|d60|d64|d68)',1.06,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=W','(d53|d57|d61|d65|d69|d72)',2.3,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=W','(d54|d58|d62|d66|d70|d73)',0.962,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=W','(d55|d59|d63|d67|d71|d74)',0.43,0);

-- ZJETS. Cross section in pb
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=Z','(d29|d33|d37|d41|d45)',0.852,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=Z','(d30|d34|d38|d42|d46|d49)',1.22,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=Z','(d31|d35|d39|d43|d47|d50)',0.377,0);
INSERT INTO normalization VALUES('CMS_2013_I1224539:JMODE=Z','(d32|d36|d40|d44|d48|d51)',0.141,0);

-- 7 TeV WW cross section in fb
INSERT INTO normalization VALUES('ATLAS_2013_I1190187','d04-x01-y01',392.6,0);
-- 8 TeV b hadron cross section in fb
INSERT INTO normalization VALUES('ATLAS_2017_I1598613:BMODE=3MU','d',17700000,0);
-- 7 TeV LHCb stuff
INSERT INTO normalization VALUES('LHCB_2012_I1208102','d',76,0);
-- 20 GeV threshold
INSERT INTO normalization VALUES('LHCB_2014_I1262703','d0[4-8]-x01-y01',6.3,0);
-- 10 GeV threshold
INSERT INTO normalization VALUES('LHCB_2014_I1262703','d03|d0[4-8]-x01-y02',16.0,0);

-- ttbb in fb
INSERT INTO normalization VALUES('ATLAS_2018_I1705857','(d04|d06|d12|d14|d16|d26|d28|d30|d38|d40|d42)',181,0);
INSERT INTO normalization VALUES('ATLAS_2018_I1705857','(d08|d10)',2450,0);
INSERT INTO normalization VALUES('ATLAS_2018_I1705857','(d18|d20|d22|d24|d32|d34|d36|d44|d46|d48|d50)',359,0);

-- HMDY 13 TeV search
INSERT INTO normalization VALUES('ATLAS_2019_I1725190','(d01-x01-y01|d02-x01-y01)',0,10);

-- 13TeV SUSY MET 0-lepton search
INSERT INTO normalization VALUES('ATLAS_2016_I1458270','(d0[4-9]-x01-y01|d10-x01-y01)',0,-1);

-- ATLAS softdrop mass
INSERT INTO normalization VALUES('ATLAS_2017_I1637587','d01-x01-y01',140,0);
INSERT INTO normalization VALUES('ATLAS_2017_I1637587','d02-x01-y01',190,0);
INSERT INTO normalization VALUES('ATLAS_2017_I1637587','d03-x01-y01',210,0);
-- ttbar gamma
INSERT INTO normalization VALUES('ATLAS_2018_I1707015:LMODE=SINGLE','d0[3-5]',521,0);
INSERT INTO normalization VALUES('ATLAS_2018_I1707015:LMODE=DILEPTON','(d0[6-9]|d10)',69,0);

-- 13 TeV multijet event shapes. cross sections in pb
INSERT INTO normalization VALUES('ATLAS_2020_I1808726','(d01|d13|d25|d37|d49|d61)',371.7,0);  -- 3jets, low HT
INSERT INTO normalization VALUES('ATLAS_2020_I1808726','(d02|d14|d26|d38|d50|d62)',371.7,0);  -- 4jets, low HT
INSERT INTO normalization VALUES('ATLAS_2020_I1808726','(d03|d15|d27|d39|d51|d63)',371.7,0);  -- 5jets, low HT
INSERT INTO normalization VALUES('ATLAS_2020_I1808726','(d04|d16|d28|d40|d52|d64)',371.7,0);  -- 6jets, low HT

INSERT INTO normalization VALUES('ATLAS_2020_I1808726','(d05|d17|d29|d41|d53|d65)',35.5,0);  -- 3jets, mid HT
INSERT INTO normalization VALUES('ATLAS_2020_I1808726','(d06|d18|d30|d42|d54|d66)',35.5,0);  -- 4jets, mid HT
INSERT INTO normalization VALUES('ATLAS_2020_I1808726','(d07|d19|d31|d43|d55|d67)',35.5,0); -- 5jets, mid HT
INSERT INTO normalization VALUES('ATLAS_2020_I1808726','(d08|d20|d32|d44|d56|d68)',35.5,0); -- 6jets, mid HT

INSERT INTO normalization VALUES('ATLAS_2020_I1808726','(d09|d21|d33|d45|d57|d69)',7.09,0);   -- 3jets, high HT
INSERT INTO normalization VALUES('ATLAS_2020_I1808726','(d10|d22|d34|d46|d58|d70)',7.09,0); -- 4jets, high HT
INSERT INTO normalization VALUES('ATLAS_2020_I1808726','(d11|d23|d35|d47|d59|d71)',7.09,0); -- 5jets, high HT
INSERT INTO normalization VALUES('ATLAS_2020_I1808726','(d12|d24|d36|d48|d60|d72)',7.09,0); -- 6jets, high HT

-- 8 TeV W, Z pT
INSERT INTO normalization VALUES('CMS_2016_I1471281:VMODE=Z','d09',440,0);
INSERT INTO normalization VALUES('CMS_2016_I1471281:VMODE=W','d08',6290,0);

--Track-based 13 TeV in ATLAS - pb
INSERT INTO normalization VALUES('ATLAS_2016_I1467230','d',61589403974,0);
INSERT INTO normalization VALUES('ATLAS_2016_I1419652','d',52176470588,0);
INSERT INTO normalization VALUES('ATLAS_2020_I1790256','d',14750000/139000,0); 

-- 13 TeV ttbar to hadrons
-- the fiducial xs d02 is not normalised, d75 to d146 are
INSERT INTO normalization VALUES('ATLAS_2022_I2077575','d(7[5-9]|[89][0-9]|1[0-3][0-9]|14[0-6])',331,0);

-- This is a table to store any histograms which can only be used
-- if running in SM theory mode
CREATE TABLE metratio (
    id      TEXT NOT NULL,
    pattern TEXT NOT NULL,
    UNIQUE(id,pattern),
    FOREIGN KEY(id) REFERENCES analysis(id)
);
INSERT INTO metratio VALUES('ATLAS_2017_I1609448','d');
INSERT INTO metratio VALUES('ATLAS_2024_I2765017:TYPE=BSM','rmiss');


-- This is a table to store histograms which use tracks only
-- (Useful for e.g. Dark Shower models where we may not trust calorimeter jet calibration
CREATE TABLE tracksonly (
    id      TEXT NOT NULL,
    pattern TEXT NOT NULL,
    UNIQUE(id,pattern),
    FOREIGN KEY(id) REFERENCES analysis(id)
);
INSERT INTO tracksonly VALUES('ATLAS_2016_I1419652','d');
INSERT INTO tracksonly VALUES('ATLAS_2016_I1467230','d');
INSERT INTO tracksonly VALUES('ATLAS_2019_I1740909','d');
INSERT INTO tracksonly VALUES('ATLAS_2020_I1790256','d');

-- This is a table to store histograms which are very sensitive to soft physics
-- and so should not be used by default
CREATE TABLE softphysics (
    id      TEXT NOT NULL,
    pattern TEXT NOT NULL,
    UNIQUE(id,pattern),
    FOREIGN KEY(id) REFERENCES analysis(id)
);
INSERT INTO softphysics VALUES('ATLAS_2016_I1419652','d');
INSERT INTO softphysics VALUES('ATLAS_2016_I1467230','d');
INSERT INTO softphysics VALUES('ATLAS_2019_I1740909','d');
INSERT INTO softphysics VALUES('ATLAS_2020_I1790256','d');
INSERT INTO softphysics VALUES('CMS_2021_I1932460','d');


-- This is a table to store any histograms which require and use SM theory whatever run mode is used.
-- This includes searches, which require a background model, ratios to SM, and single-point histograms
CREATE TABLE needtheory (
    id      TEXT NOT NULL,
    pattern TEXT NOT NULL,
    UNIQUE(id,pattern),
    FOREIGN KEY(id) REFERENCES analysis(id)
);
INSERT INTO needtheory VALUES('ATLAS_2017_I1609448','d');
INSERT INTO needtheory VALUES('ATLAS_2016_I1458270','d');
INSERT INTO needtheory VALUES('ATLAS_2019_I1725190','d');
INSERT INTO needtheory VALUES('ATLAS_2021_I1887997','yy_xs');
INSERT INTO needtheory VALUES('ATLAS_2021_I1852328','d01-x01-y02');
INSERT INTO needtheory VALUES('ATLAS_2019_I1738841','d');
INSERT INTO needtheory VALUES('ATLAS_2012_I1203852:LMODE=LL','d');
INSERT INTO needtheory VALUES('ATLAS_2012_I1203852:LMODE=LNU','d');
INSERT INTO needtheory VALUES('ATLAS_2016_I1492320:LMODE=3L','d');
INSERT INTO needtheory VALUES('ATLAS_2016_I1492320:LMODE=2L2J','d');
INSERT INTO needtheory VALUES('ATLAS_2016_I1448301:LMODE=LL','d');
INSERT INTO needtheory VALUES('ATLAS_2016_I1448301:LMODE=NU','d02');
INSERT INTO needtheory VALUES('ATLAS_2016_I1448301:LMODE=NU','d04');
INSERT INTO needtheory VALUES('CMS_2019_I1753720','d');
INSERT INTO needtheory VALUES('LHCB_2018_I1662483','d');
INSERT INTO needtheory VALUES('ATLAS_2024_I2765017:TYPE=BSM','rmiss');


-- This is a table to store any histograms which are made using
-- background-subtracted Higgs gamma-gamma signal and which
-- should therefore not be used to exclude continuum diphotons
CREATE TABLE higgsgg (
    id      TEXT NOT NULL,
    pattern TEXT NOT NULL,
    UNIQUE(id,pattern),
    FOREIGN KEY(id) REFERENCES analysis(id)
);
INSERT INTO higgsgg VALUES('ATLAS_2014_I1306615','d');
INSERT INTO higgsgg VALUES('ATLAS_2022_I2023464','d');

-- This is a table to flag search distributions (ie event count histograms which are not unfolded)
CREATE TABLE searches (
    id      TEXT NOT NULL,
    pattern TEXT NOT NULL,
    UNIQUE(id,pattern),
    FOREIGN KEY(id) REFERENCES analysis(id)
);
INSERT INTO searches VALUES('ATLAS_2016_I1458270','d');
INSERT INTO searches VALUES('ATLAS_2019_I1725190','d');

-- This is a table to store any histograms which are made using
-- background-subtracted Higgs ww signal and which
-- should therefore not be used to exclude bsm top/w production
CREATE TABLE higgsww (
    id      TEXT NOT NULL,
    pattern TEXT NOT NULL,
    UNIQUE(id,pattern),
    FOREIGN KEY(id) REFERENCES analysis(id)
);
INSERT INTO higgsww VALUES('CMS_2017_I1467451','d');
INSERT INTO higgsww VALUES('ATLAS_2016_I1444991','d');

-- This is a table to store ATLAS WZ measurements which assume the SM in their neutrino flavour assignment.
CREATE TABLE atlaswz (
    id      TEXT NOT NULL,
    pattern TEXT NOT NULL,
    UNIQUE(id,pattern),
    FOREIGN KEY(id) REFERENCES analysis(id)
);
INSERT INTO atlaswz VALUES('ATLAS_2016_I1469071','d');

-- This is a table to store measurements which have a secret b-jet veto
CREATE TABLE bveto (
    id      TEXT NOT NULL,
    pattern TEXT NOT NULL,
    UNIQUE(id,pattern),
    FOREIGN KEY(id) REFERENCES analysis(id)
);
INSERT INTO bveto VALUES('CMS_2014_I1303894','d');
INSERT INTO bveto VALUES('CMS_2016_I1491953','d');
INSERT INTO bveto VALUES('CMS_2017_I1610623','d');
INSERT INTO bveto VALUES('CMS_2017_I1467451','d');
INSERT INTO bveto VALUES('CMS_2020_I1794169','d');
-- INSERT INTO bveto VALUES('CMS_2020_I1837084','d');

--

-- Index the theory predictions that Contur knows about.
--------------------------------------------------------
-- id: an identifier for this prediction unique to this analysis. This should be a short string which
--     will also be used to select the prediction at run time, and will be appended to the dat and graphics files.
--     if ID is "A", this is the default prediction
-- analysis: the full analysis name, including any options
-- inspids: inspire IDs of theory references
-- origin: where the data comes from. See contur/run/run_mkthy.py for meaning 
-- pattern: histogram patterns these predictions are for. (ONLY USED WHEN MAKING THE FILES IN /Theory)
-- axis: for HEPData record, the name of the axis to take the theory from. The record used will the one where the end
--       of the HEPData path matches this (ONLY USED WHEN MAKING THE FILES IN /Theory)
-- file_name: the name of the file the prediction is stored in, in /Theory. 
-- short_description: for plot legends 
-- long_description: for web pages, does not need to repeat the short description
CREATE TABLE theory_predictions (
    id         TEXT NOT NULL,
    ananame    TEXT NOT NULL,
    inspids    TEXT,
    origin     TEXT,
    pattern    TEXT,
    axis       TEXT,
    file_name TEXT,
    short_description TEXT,
    long_description TEXT,
    FOREIGN KEY(ananame) REFERENCES analysis(ID)
--    UNIQUE(file_name, pattern, id)
);

-- ttbb
INSERT INTO theory_predictions VALUES('A','ATLAS_2024_I2809112', '2809112,1736301', 'SPECIAL', 'd01','y01',
       'ATLAS_2024_I2809112-Theory_Sherpa.yoda',
       'Sherpa',
       'Sherpa SM prediction from measurement paper'); 
INSERT INTO theory_predictions VALUES('B','ATLAS_2024_I2809112', '2809112,845712,1321709,1600591', 'SPECIAL', 'd01','y01',
       'ATLAS_2024_I2809112-Theory_Powheg.yoda',
       'Powheg',
       'Powheg + Herwig/Pythia SM prediction from measurement paper'); 

-- ditau
INSERT INTO theory_predictions VALUES('A','ATLAS_2025_I2905252','2905252,1736301','REF','mll$','_meps',
       'ATLAS_2025_I2905252-Theory_MEPS.yoda',
       'SM (MEPS@NLO,Sherpa,Powheg+Pythia)',
       'Internally produced');
INSERT INTO theory_predictions VALUES('B','ATLAS_2025_I2905252','2905252,659055,760769,845712,764903','REF','mll$','_nlops',
       'ATLAS_2025_I2905252-Theory_NLOPS.yoda',
       'SM (NLOPS,Powheg+Pythia)',
       'Internally produced');

-- Z+b,c
INSERT INTO theory_predictions VALUES('B','ATLAS_2024_I2771257','2771257',
        'REF','y01','y02',
        'ATLAS_2024_I2771257-Theory_MGFxFx.yoda',
        'MGaMC+Py8 FxFx 5FS (NLO)',
        'From measurement paper, arXiv:2403.15093 [hep-ex]');

-- Z+b,c
INSERT INTO theory_predictions VALUES('A','ATLAS_2024_I2771257','2771257',
        'REF','y01','y03',
        'ATLAS_2024_I2771257-Theory_Sherpa.yoda',
        'Sherpa 5FS (NLO)',
        'From measurement paper, arXiv:2403.15093 [hep-ex]');
	
-- (SUSY WW)
INSERT INTO theory_predictions VALUES('A','ATLAS_2022_I2103950','2103950',
        'REF','y01','y02',
        'ATLAS_2022_I2103950-Theory_POWHEG.yoda',
        'POWHEG (stat only)',
        'From measurement paper, arXiv:2206.15231 [hep-ex]');
-- (SUSY WW)
INSERT INTO theory_predictions VALUES('B','ATLAS_2022_I2103950','2103950',
        'REF','y01','y03',
        'ATLAS_2022_I2103950-Theory_Sherpa.yoda',
        'Sherpa (stat only)',
        'From measurement paper, arXiv:2206.15231 [hep-ex]');

-- the NLO  (HEJ also available but prelim)

INSERT INTO theory_predictions VALUES('A','CMS_2018_I1711625','1711625','SPECIAL',
	NULL, NULL, 
	'CMS_2018_I1711625-Theory_A.yoda',
	'aMC@NLO',
	'figure 5 on paper');

INSERT INTO theory_predictions VALUES('A','ATLAS_2024_I2765017:MODE=EXTRAPOLATED:TYPE=BSM','2765017','REF',
        'sr0l_cr1ig_0v_mjj_vbf_dbp$','_nlo',
        'ATLAS_2024_I2765017:MODE=EXTRAPOLATED:TYPE=BSM-Theory_A.yoda',
        'MEPS@NLO',
        'From paper');
INSERT INTO theory_predictions VALUES('B','ATLAS_2024_I2765017:MODE=EXTRAPOLATED:TYPE=BSM','2765017','SPECIAL',
        'sr0l_cr1ig_0v_mjj_vbf_dbp$','_dbp',
        'ATLAS_2024_I2765017:MODE=EXTRAPOLATED:TYPE=BSM-Theory_B.yoda',
        'HEJ',
        'From Jeppe, prelim');
INSERT INTO theory_predictions VALUES('C','ATLAS_2024_I2765017:MODE=EXTRAPOLATED:TYPE=BSM','2765017','SPECIAL',
        'sr0l_cr1ig_0v_mjj_vbf_dbp$','_dbp',
        'ATLAS_2024_I2765017:MODE=EXTRAPOLATED:TYPE=BSM-Theory_C.yoda',
        'HEJ (scaled)',
        'From Jeppe, prelim (scaled version)');


-- the NNLO and HEJ where available, NLO otherwise (first in list for given ID takes precendence...)
INSERT INTO theory_predictions VALUES('A','ATLAS_2024_I2765017:TYPE=BSM','2765017',
        'REF','^(?!.*rmiss)^(?!.*thy)^(?!.*dbp)^(?!.*vbf).*(sr0l).*$','_thy_nnlo',
        'ATLAS_2024_I2765017:TYPE=BSM-Theory.yoda',
        'NNLO QCD $\times$ nNLO EW',
        'From measurement paper arXiv: 2403.02793 [hep-ex]');
INSERT INTO theory_predictions VALUES('A','ATLAS_2024_I2765017:TYPE=BSM','2765017','REF',
        '^(?!.*rmiss)^(?!.*thy)^(?!.*dbp).*(sr0l).*$','_thy_hej',
        'ATLAS_2024_I2765017:TYPE=BSM-Theory.yoda',
        'HEJ',
        'From measurement paper arXiv: 2403.02793 [hep-ex]');
INSERT INTO theory_predictions VALUES('A','ATLAS_2024_I2765017:TYPE=BSM','2765017','REF',
        '^(?!.*rmiss)^(?!.*thy)^(?!.*dbp).*(sr0l).*$','_thy_nlo',
        'ATLAS_2024_I2765017:TYPE=BSM-Theory.yoda',
        'MEPS@NLO $\times$ nNLO EW',
        'From measurement paper arXiv: 2403.02793 [hep-ex]');
INSERT INTO theory_predictions VALUES('A','ATLAS_2024_I2765017:TYPE=BSM','2765017','SPECIAL',
        '^(?!.*thy)^(?!.*dbp).*(rmiss).*$','_thy_nlo',
        'ATLAS_2024_I2765017:TYPE=BSM-Theory.yoda',
        'MEPS@NLO $\times$ nNLO EW',
        'From measurement paper arXiv: 2403.02793 [hep-ex]');

-- the NLO everywhere
INSERT INTO theory_predictions VALUES('B','ATLAS_2024_I2765017:TYPE=BSM','2765017',
        'REF','^(?!.*thy)^(?!.*dbp).*(sr0l|rmiss).*$','_thy_nlo',
        'ATLAS_2024_I2765017:TYPE=BSM-Theory_MEPSNLO.yoda',
        'MEPS@NLO $\times$ nNLO EW',
        'From paper measurement arXiv: 2403.02793 [hep-ex]');

INSERT INTO theory_predictions VALUES('D','ATLAS_2022_I2614196','2614196','REF','y01','y06',
        'ATLAS_2022_I2614196-Theory.yoda',
        'MATRIX NNLO',
        'Taken from HEPData record https://www.hepdata.net/record/ins2614196');
INSERT INTO theory_predictions VALUES('B','ATLAS_2022_I2614196','2614196','REF','y01','y05',
        'ATLAS_2022_I2614196-Theory_B.yoda',
        'MiNNLO_PS',
        'Taken from HEPData record https://www.hepdata.net/record/ins2614196');
INSERT INTO theory_predictions VALUES('C','ATLAS_2022_I2614196','2614196','REF','y01','y04',
        'ATLAS_2022_I2614196-Theory_C.yoda',
        'MadGraph5_aMC@NLO',
        'Taken from HEPData record https://www.hepdata.net/record/ins2614196');
INSERT INTO theory_predictions VALUES('A','ATLAS_2022_I2614196','2614196','REF','y01','y03',
        'ATLAS_2022_I2614196-Theory_D.yoda',
        'Sherpa 2.2.11',
        'Taken from HEPData record https://www.hepdata.net/record/ins2614196');
INSERT INTO theory_predictions VALUES('E','ATLAS_2022_I2614196','2614196','REF','y01','y02',
        'ATLAS_2022_I2614196-Theory_E.yoda',
        'Sherpa 2.2.4',
        'Taken from HEPData record https://www.hepdata.net/record/ins2614196');
INSERT INTO theory_predictions VALUES('A','ATLAS_2022_I2037744','2037744','SPECIAL',NULL,NULL,
        'ATLAS_2022_I2037744-Theory.yoda',
        'Powheg + Pythia 8',
        'Central values taken from HEPData record https://www.hepdata.net/record/134011?version=2, uncertainties generated from paper');
-- INSERT INTO theory_predictions VALUES('A','CMS_2021_I1866118','1866118','HEPDATA','d01-x01','y01',
--       'CMS_2021_I1866118-Theory.yoda',
--       'Sherpa NLO + LO'
--       'Taken from paper results');   not being able to use atm due to rivet routine not supporting
INSERT INTO theory_predictions VALUES('A','CMS_2022_I2080534','2080534','REF','y01','y02',
        'CMS_2022_I2080534-Theory.yoda',
        'MG5_aMC+Pythia8',
        'See measurement paper for details, Hepdata record: https://doi.org/10.17182/hepdata.127763');
INSERT INTO theory_predictions VALUES('A','CMS_2018_I1667854:LMODE=EMU','1667854','SPECIAL',NULL,NULL,
       'CMS_2018_I1667854:LMODE=EMU-Theory.yoda',
       'MADGRAPH5_aMC+Pythia8',
       'Generated from the mean of data taken from the paper');
INSERT INTO theory_predictions VALUES('B','CMS_2018_I1667854:LMODE=EMU','1667854','SPECIAL','d03,d04,d05,d07,d08,d10,d11,d13,d14,d16,d17,d18','y01',
       'CMS_2018_I1667854:LMODE=EMU-Theory_B.yoda',
       'GE+PY8',
       'Generated from the mean of data taken from the paper');
INSERT INTO theory_predictions VALUES('A','ATLAS_2019_I1718132:LMODE=ELMU','1718132','SPECIAL',NULL,NULL,
       'ATLAS_2019_I1718132:LMODE=ELMU-Theory.yoda',
       'MADGRAPH5_aMC+Pythia and Powheg',
       'Generated from the mean of data taken from the paper');
INSERT INTO theory_predictions VALUES('A','ATLAS_2019_I1718132:LMODE=MUMU','1718132','SPECIAL',NULL,NULL,
       'ATLAS_2019_I1718132:LMODE=MUMU-Theory.yoda',
       'MADGRAPH5_aMC+Pythia and Sherpa2.1.1',
       'Generated from the mean of data taken from the paper');
INSERT INTO theory_predictions VALUES('A','ATLAS_2019_I1718132:LMODE=ELEL','1718132','SPECIAL',NULL,NULL,
       'ATLAS_2019_I1718132:LMODE=ELEL-Theory.yoda',
       'MADGRAPH5_aMC+Pythia and Sherpa2.1.1',
       'Generated from the mean of data taken from the paper');

INSERT INTO theory_predictions VALUES('A','CMS_2016_I1471281:VMODE=W','1471281','SPECIAL',NULL,NULL,
       'CMS_2016_I1471281:VMODE=W-Theory.yoda',
       'ResBos',
       'Generated from data taken from the paper');
INSERT INTO theory_predictions VALUES('B','CMS_2016_I1471281:VMODE=W','1471281','SPECIAL',NULL,NULL,
       'CMS_2016_I1471281:VMODE=W-Theory_B.yoda',
       'POWHEG',
       'Generated from data taken from the paper');
INSERT INTO theory_predictions VALUES('C','CMS_2016_I1471281:VMODE=W','1471281','SPECIAL',NULL,NULL,
       'CMS_2016_I1471281:VMODE=W-Theory_C.yoda',
       'FEWZ',
       'Generated from data taken from the paper');
INSERT INTO theory_predictions VALUES('A','CMS_2016_I1471281:VMODE=Z','1471281','SPECIAL',NULL,NULL,
       'CMS_2016_I1471281:VMODE=Z-Theory.yoda',
       'ResBos',
       'Generated from data taken from the paper');
INSERT INTO theory_predictions VALUES('B','CMS_2016_I1471281:VMODE=Z','1471281','SPECIAL',NULL,NULL,
       'CMS_2016_I1471281:VMODE=Z-Theory_B.yoda',
       'POWHEG',
       'Generated from data taken from the paper');
INSERT INTO theory_predictions VALUES('C','CMS_2016_I1471281:VMODE=Z','1471281','SPECIAL',NULL,NULL,
       'CMS_2016_I1471281:VMODE=Z-Theory_C.yoda',
       'FEWZ',
       'Generated from data taken from the paper');
INSERT INTO theory_predictions VALUES('A','ATLAS_2022_I2023464','2023464','SPECIAL',NULL,NULL,
       'ATLAS_2022_I2023464-Theory.yoda',
       'gg $\rightarrow H$ default MC + XH',
       'Generated from data taken from the paper');
INSERT INTO theory_predictions VALUES('A','ATLAS_2018_I1707015:LMODE=SINGLE','1707015','SPECIAL',NULL,NULL,
       'ATLAS_2018_I1707015:LMODE=SINGLE-Theory.yoda',
       'MG5_aMC + Pythia8',
       'Generated from data taken from the paper');
INSERT INTO theory_predictions VALUES('A','ATLAS_2018_I1707015:LMODE=DILEPTON','1707015','SPECIAL',NULL,NULL,
       'ATLAS_2018_I1707015:LMODE=DILEPTON-Theory.yoda',
       'MG5_aMC + Pythia8',
       'Generated from data taken from the paper');
INSERT INTO theory_predictions VALUES('A','CMS_2020_I1814328','1814328','SPECIAL',NULL,NULL,
       'CMS_2020_I1814328-Theory.yoda',
       'POWHEG+PYTHIA',
       'Generated from data taken from the paper');

-- EW W+jet 8 TeV
-- Triphoton 8 TeV
INSERT INTO theory_predictions VALUES('A','ATLAS_2017_I1644367','1644367','SPECIAL',NULL,NULL,
       'ATLAS_2017_I1644367-Theory.yoda',
       'MG5_aMC+Py8',
       'Generated from data taken from the paper');
INSERT INTO theory_predictions VALUES('B','ATLAS_2017_I1644367','1644367','SPECIAL',NULL,NULL,
       'ATLAS_2017_I1644367-Theory_B.yoda',
       'MCFM',
       'Generated from data taken from the paper');
INSERT INTO theory_predictions VALUES('A','ATLAS_2019_I1734263','1734263,1636973,946998,1353132,1459055,1457600','SPECIAL',NULL,NULL,
       'ATLAS_2019_I1734263-Theory.yoda',
       'NNLO(qq)+NLO(gg)xNLO(EW)',
       'Generated from data taken from the paper');
INSERT INTO theory_predictions VALUES('A','ATLAS_2019_I1744201','1744201','SPECIAL',NULL,NULL,
       'ATLAS_2019_I1744201-Theory.yoda',
       'NNLOJet',
       'Generated from data taken from the paper');
INSERT INTO theory_predictions VALUES('B','ATLAS_2019_I1744201','1744201','SPECIAL',NULL,NULL,
       'ATLAS_2019_I1744201-Theory_B.yoda',
       'MCFM 6.8',
       'Generated from data taken from the paper');
INSERT INTO theory_predictions VALUES('A','ATLAS_2016_I1448301:LMODE=LL','1448301','SPECIAL',NULL,NULL,
       'ATLAS_2016_I1448301:LMODE=LL-Theory.yoda',
       'NNLO (MMHT2014)',
       'Generated from data taken from the paper');
INSERT INTO theory_predictions VALUES('A','ATLAS_2016_I1448301:LMODE=NU','897881','RAW','d02-x01-y01|d04-x01-y01',NULL,
       'ATLAS_2016_I1448301:LMODE=NU-Theory.yoda',
       'MCFM',
       'MCFM NLO calculations, from measurement paper');       
INSERT INTO theory_predictions VALUES('A','ATLAS_2016_I1448301:LMODE=LL','1357993,897881','RAW','d01-x01-y01|d03-x01-y01',NULL,
       'ATLAS_2016_I1448301:LMODE=LL-Theory.yoda',
       'GKR and MCFM',
       'MCFM NLO and (for Z-gamma only) Grazzini, Kalleit, Rathlev NNLO Calculations, from measurement paper'); -- TODO check this works
INSERT INTO theory_predictions VALUES('A','ATLAS_2016_I1448301:LMODE=LL','1357993,897881','RAW','d01-x01-y02|d03-x01-y02',NULL,
       'ATLAS_2016_I1448301:LMODE=LL-Theory.yoda',
       'GKR and MCFM',
       'MCFM NLO and (for Z-gamma only) Grazzini, Kalleit, Rathlev NNLO Calculations, from measurement paper');       
INSERT INTO theory_predictions VALUES('A','ATLAS_2018_I1635273:LMODE=EL','1635273','SPECIAL',NULL,NULL,
       'ATLAS_2018_I1635273:LMODE=EL-Theory.yoda',
       'SHERPA 2.2.1 NLO',
       'Generated from data taken from the paper');
INSERT INTO theory_predictions VALUES('A','ATLAS_2018_I1698006:LVETO=ON','1698006','SPECIAL',NULL,NULL,
       'ATLAS_2018_I1698006:LVETO=ON-Theory.yoda',
       'NNLO MCFM',
       'Generated from data taken from the paper');
INSERT INTO theory_predictions VALUES('A','ATLAS_2015_I1394679','1394679','SPECIAL',NULL,NULL,
       'ATLAS_2015_I1394679-Theory.yoda',
       'NJet/Sherpa (x 1.0)',
       'Generated from data taken from the paper');
INSERT INTO theory_predictions VALUES('A','CMS_2020_I1794169','1794169','SPECIAL',NULL,NULL,
       'CMS_2020_I1794169-Theory.yoda',
       'MADGRAPH5_aMC@NLO+Pythia8 with NLO corr',
       'Generated from data taken from the paper');
INSERT INTO theory_predictions VALUES('A','CMS_2019_I1753680:LMODE=EMU','1753680','SPECIAL',NULL,NULL,
       'CMS_2019_I1753680:LMODE=EMU-Theory.yoda',
       'aMC@NLO',
       'Generated from data taken from the paper');
INSERT INTO theory_predictions VALUES('A','ATLAS_2017_I1517194','1225115,1218997,659055,760769','REF','y01','y02',
        'ATLAS_2017_I1517194-Theory.yoda',
        'POWHEG+Pythia8',
        'Taken from HEPData record https://doi.org/10.17182/hepdata.76505');
INSERT INTO theory_predictions VALUES('B','ATLAS_2017_I1517194','1120302','REF','y01','y03',
        'ATLAS_2017_I1517194-Theory_HEJ.yoda',
        'HEJ(QCD)+POW+PY(EW)',
        'Taken from HEPData record https://doi.org/10.17182/hepdata.76505');
INSERT INTO theory_predictions VALUES('C','ATLAS_2017_I1517194','803708','REF','y01','y04',
        'ATLAS_2017_I1517194-Theory_Sherpa.yoda',
        'SHERPA',
        'Taken from HEPData record https://doi.org/10.17182/hepdata.76505');

-- Top-quark pair single- and double-differential cross-sections in the all-hadronic channel 36/fb
INSERT INTO theory_predictions VALUES('A','ATLAS_2020_I1801434','760769,845712','SPECIAL',NULL,NULL,
        'ATLAS_2020_I1801434-Theory.yoda',
        'POWHEG+Pythia8',
        'Taken from the envelope of predictions from POWHEG+Pythia8.');
INSERT INTO theory_predictions VALUES('B','ATLAS_2020_I1801434','760769,845712','REF','y01','y02',
        'ATLAS_2020_I1801434-Theory_B.yoda',
        'POWHEG+Pythia8',
        'Taken from HEPData record https://doi.org/10.17182/hepdata.103063. No uncertainties.');

-- ATLAS Run 2 Z+b jets
INSERT INTO theory_predictions VALUES('A','ATLAS_2020_I1788444','1788444','REF','y01','y02',
        'ATLAS_2020_I1788444-Theory.yoda',
        'Sherpa 5FNS (NLO)',
        'Taken from HEPData record https://doi.org/10.17182/hepdata.94219');
-- ATLAS Run 2 Z+b jets
INSERT INTO theory_predictions VALUES('B','ATLAS_2020_I1788444','1788444','REF','y01','y04',
        'ATLAS_2020_I1788444-Theory_B.yoda',
        'MGaMC+Py8 Zbb 4FNS (NLO)',
        'Taken from HEPData record https://doi.org/10.17182/hepdata.94219');
-- ATLAS Run 2 Z+b jets
INSERT INTO theory_predictions VALUES('C','ATLAS_2020_I1788444','1788444','REF','y01','y05',
        'ATLAS_2020_I1788444-Theory_C.yoda',
        'MGaMC+Py8 5FNS (NLO)',
        'Taken from HEPData record https://doi.org/10.17182/hepdata.94219');
-- ATLAS Run 2 Z+b jets
INSERT INTO theory_predictions VALUES('D','ATLAS_2020_I1788444','1788444','REF','y01','y06',
        'ATLAS_2020_I1788444-Theory_D.yoda',
        'Sherpa Zbb 4FNS (NLO)',
        'Taken from HEPData record https://doi.org/10.17182/hepdata.94219');
-- ATLAS Run 2 Z+b jets
INSERT INTO theory_predictions VALUES('E','ATLAS_2020_I1788444','1788444','REF','y01','y07',
        'ATLAS_2020_I1788444-Theory_E.yoda',
        'Sherpa Fusing 4FNS+5FNS (NLO)',
        'Taken from HEPData record https://doi.org/10.17182/hepdata.94219');


-- ATLAS high Z+jets 139/fb
INSERT INTO theory_predictions VALUES('A','ATLAS_2022_I2077570','2077570','SPECIAL',NULL,NULL,
       'ATLAS_2022_I2077570-Theory.yoda',
       'Sherpa 2.2.11',
       'Generated by ATLAS, see paper for full list of references.');
-- ATLAS Early Run 2 Z+jets
INSERT INTO theory_predictions VALUES('A','ATLAS_2022_I2593322','2593322','REF','y01','y02',
        'ATLAS_2022_I2593322-Theory.yoda',
        'SHERPA 2.2.10',
        'Taken from the HEPData');
INSERT INTO theory_predictions VALUES('B','ATLAS_2022_I2593322','2593322','REF','y01','y03',
        'ATLAS_2022_I2593322-Theory_B.yoda',
        'MadGraph5_aMC@NLO 2.7.3 ',
        'Taken from the HEPData');
INSERT INTO theory_predictions VALUES('A','ATLAS_2016_I1494075:LMODE=4L','1494075','SPECIAL',NULL,NULL,
       'ATLAS_2016_I1494075:LMODE=4L-Theory.yoda',
       'POWHEG + Pythia',
       'Generated from ATLAS setup, with scale and stat uncertainties');
INSERT INTO theory_predictions VALUES('A','ATLAS_2016_I1494075:LMODE=2L2NU','1494075','SPECIAL',NULL,NULL,
       'ATLAS_2016_I1494075:LMODE=2L2NU-Theory.yoda',
       'POWHEG + Pythia',
       'Generated from ATLAS setup, with scale and stat uncertainties');
INSERT INTO theory_predictions VALUES('A','ATLAS_2017_I1627873','1627873','REF','y01','y02',
        'ATLAS_2017_I1627873-Theory.yoda',
        'SHERPA(QCD+Zjj)+POWHEG(EW-Zjj)',
        'Taken from the HEPData record of the experimental paper');
INSERT INTO theory_predictions VALUES('B','ATLAS_2017_I1627873','1627873','REF','y01','y03',
        'ATLAS_2017_I1627873-Theory_B.yoda',
        'MG5_aMC(QCD+Zjj)+POWHEG(EW-Zjj)',
        'Taken from the HEPData record of the experimental paper'); 
INSERT INTO theory_predictions VALUES('C','ATLAS_2017_I1627873','1627873','REF','y01','y04',
        'ATLAS_2017_I1627873-Theory_C.yoda',
        'ALPGEN(QCD+Zjj)+POWHEG(EW-Zjj)',
        'Taken from the HEPData record of the experimental paper');
-- CMS 2.76 TeV Dijet ()
INSERT INTO theory_predictions VALUES('A','CMS_2021_I1963239','1963239','REF','y01','y02',
        'CMS_2021_I1963239-Theory.yoda',
        'Pythia8 4C',
        'Taken from the HEPData record of the experimental paper');
INSERT INTO theory_predictions VALUES('B','CMS_2021_I1963239','1963239','REF','y01','y03',
        'CMS_2021_I1963239-Theory_B.yoda',
        'HERWIG++ EE3C',
        'Taken from the HEPData record of the experimental paper');
INSERT INTO theory_predictions VALUES('C','CMS_2021_I1963239','1963239','REF','y01','y04',
        'CMS_2021_I1963239-Theory_C.yoda',
        'HEJ+ARIADNE',
        'Taken from the HEPData record of the experimental paper');    
INSERT INTO theory_predictions VALUES('D','CMS_2021_I1963239','1963239','REF','y01','y05',
        'CMS_2021_I1963239-Theory_D.yoda',
        'POWHEG+PYTHIA8',
        'Taken from the HEPData record of the experimental paper');  
INSERT INTO theory_predictions VALUES('E','CMS_2021_I1963239','1963239','REF','y01','y06',
        'CMS_2021_I1963239-Theory_E.yoda',
        'POWHEG+HERWIG++',
        'Taken from the HEPData record of the experimental paper');  
INSERT INTO theory_predictions VALUES('F','CMS_2021_I1963239','1963239','REF','y01','y07',
        'CMS_2021_I1963239-Theory_F.yoda',
        'POWHEG+HERWIG7',
        'Taken from the HEPData record of the experimental paper');
INSERT INTO theory_predictions VALUES('A', 'ATLAS_2022_I2077575','2077575','SPECIAL',NULL,NULL,
       'ATLAS_2022_I2077575-Theory.yoda',
       'POWHEG+Pythia8',
       'Plots digitised from experimental paper. Uncertainties taken as the envelope of theory predictions.');
-- replaced below by values digitised from paper (with uncertainty estimates)
INSERT INTO theory_predictions VALUES('B', 'ATLAS_2022_I2077575','2077575','REF','y01','y03',
       'ATLAS_2022_I2077575-Theory_nounc.yoda',
       'POWHEG+Pythia8',
       'Taken from the HEPData record of the experimental paper. No uncertainties.');
INSERT INTO theory_predictions VALUES('A','ATLAS_2019_I1764342','1736301','SPECIAL',NULL,NULL,
       'ATLAS_2019_I1764342-Theory.yoda',
       'Sherpa NLO (2)',
       'Generated from ATLAS setup, with scale and stat uncertainties');
INSERT INTO theory_predictions VALUES('B','ATLAS_2019_I1764342','1764342,1736301','REF','y01','y04',
       'ATLAS_2019_I1764342-Theory_orig.yoda',
       'Sherpa NLO',
       'Taken from the HEPData record of the experimental paper. No uncertainties.');
INSERT INTO theory_predictions VALUES('A','ATLAS_2019_I1772071','1736301,562391,946998,760143','REF','y01','y02',
       'ATLAS_2019_I1772071-Theory.yoda',
       'Sherpa NLO',
       'Taken from the HEPData record of the experimental paper');
INSERT INTO theory_predictions VALUES('A','CMS_2021_I1932460','1932460','HEPDATA','d50-x01-y01','y03',
       'CMS_2021_I1932460-Theory.yoda',
       'Powheg NLO 2to2 + Double-parton scattering',
       'Taken from the HEPData record of the experimental paper (Table 44)');
INSERT INTO theory_predictions VALUES('A','CMS_2019_I1753720','1753720','HEPDATA','d01-x01','y01',
       'CMS_2019_I1753720-Theory.yoda',
       'MADGRAPH5 aMC@NLO (5FS tt+jets, FxFx)',
       'From measurement paper, Figure 3');
INSERT INTO theory_predictions VALUES('A','ATLAS_2019_I1738841','1738841','HEPDATA','d01-x01-y01','y01',
       'ATLAS_2019_I1738841-Theory.yoda',
       'Powheg+Pythia8',
       'From measurement paper in page 8 above the diagram.');
       
-- Note, there are two with same prediction ID because different subsets of the histograms use different SM implementations.
INSERT INTO theory_predictions VALUES('A','ATLAS_2021_I1887997','1887997','HEPDATA_APPEND','ph1|ph2|yy_cosTS|yy_m|yy_xs','_NNLO',
       'ATLAS_2021_I1887997-Theory.yoda',
       'NNLOJet',
       'Taken from the HEPData record of the experimental paper doi.org/10.17182/hepdata.104925');
INSERT INTO theory_predictions VALUES('A','ATLAS_2021_I1887997','1887997','HEPDATA_APPEND','yy_pT|yy_phiStar|yy_piMDphi','_SHERPA',
       'ATLAS_2021_I1887997-Theory.yoda',
       'Sherpa',
       'Taken from the HEPData record of the experimental paper');
-- Another good prediction (diphoton mass) here: https://inspirehep.net/literature/2072920 which looks like it might
-- describe that better
       
INSERT INTO theory_predictions VALUES('A','ATLAS_2012_I1199269','1653472','SPECIAL','',NULL,
       'ATLAS_2012_I1199269-Theory.yoda',
       'Catani et al',
       'NNLO QCD, read from figures in paper.');
INSERT INTO theory_predictions VALUES('A','ATLAS_2012_I1203852:LMODE=LL','845712,920312,789541','RAW','d01-x01-y01|d01-x01-y02',NULL,
       'ATLAS_2012_I1203852:LMODE=LL-Theory.yoda',
       'PowhegBox+gg2zz',
       'From measurement paper. See additional references therein.');
INSERT INTO theory_predictions VALUES('A','ATLAS_2012_I1203852:LMODE=LNU','845712,920312,789541','RAW','d01-x01-y03',NULL,
       'ATLAS_2012_I1203852:LMODE=LNU-Theory.yoda',
       'PowhegBox+gg2zz',
       'From measurement paper. See additional references therein.');
-- INSERT INTO theory_predictions VALUES('A','ATLAS_2013_I1230812:LMODE=EL','NK','RAW','d',NULL,
--       'ATLAS_2013_I1230812-Theory.yoda',
--      'Not known',
--      'Think this came from Herwig/Matchbox, needs to be checked/replaced.');
-- INSERT INTO theory_predictions VALUES('A','ATLAS_2013_I1230812:LMODE=MU','NK','RAW','d',NULL,
--      'ATLAS_2013_I1230812-Theory.yoda',
--      'Not known',
--      'Think this came from Herwig/Matchbox, needs to be checked/replaced.');
INSERT INTO theory_predictions VALUES('A','ATLAS_2014_I1306615','1095242,1239172','RAW','d',NULL,
       'ATLAS_2014_I1306615-Theory.yoda',
       'HRES 2.2',
       'Read from plot(s) in the measurement paper, since only the non-gg theory is provided in HEPData. \n See measurement paper for more details of the calculation.');
INSERT INTO theory_predictions VALUES('A','ATLAS_2014_I1310835','1118569,1310835','REF','y01','y02',
       'ATLAS_2014_I1310835-Theory.yoda',
       'Powheg Minlo HJ + non-ggF',
       'See paper for more details. HEPData record at https://doi.org/10.17182/hepdata.78567.v1  ');
INSERT INTO theory_predictions VALUES('B','ATLAS_2014_I1310835','1095242,1239172,1310835','REF','y01','y03',
       'ATLAS_2014_I1310835-Theory_HRES.yoda',
       'HRES + non-ggF',
       'See paper for more details. HEPData record at https://doi.org/10.17182/hepdata.78567.v1  ');
INSERT INTO theory_predictions VALUES('A','ATLAS_2015_I1397637','1838799,1838807,1980698','RAW','d',NULL,
       'ATLAS_2015_I1397637-Theory.yoda',
       'PowhegBoxZpWp',
       'As used in Altakach et all arXiv:2111.15406');
INSERT INTO theory_predictions VALUES('A','ATLAS_2015_I1404878','1838799,1838807','RAW','d',NULL,
       'ATLAS_2015_I1404878-Theory.yoda',
       'PowhegBoxZpWp',
       'As used in Altakach et all arXiv:2111.15406');
INSERT INTO theory_predictions VALUES('A','ATLAS_2015_I1408516:LMODE=MU','1673183','SPECIAL','d',NULL,
       'ATLAS_2015_I1408516:LMODE=MU-Theory.yoda',
       'Bizon et al',
       'Digitised files from author. NNLO + N3LL: NNLOJET + RADISH.');
INSERT INTO theory_predictions VALUES('A','ATLAS_2015_I1408516:LMODE=EL','1673183','SPECIAL','d',NULL,
       'ATLAS_2015_I1408516:LMODE=EL-Theory.yoda',
       'Bizon et al',
       'Digitised files from author. NNLO + N3LL: NNLOJET + RADISH.');
INSERT INTO theory_predictions VALUES('A','ATLAS_2016_I1457605','1727794','SPECIAL','d',NULL,
       'ATLAS_2016_I1457605-Theory.yoda',
       'NNLO QCD Chen et al',
       'NLO QCD, Xuan Chen, Thomas Gehrmann, Nigel Glover, Marius Hoefer, Alexander Huss');
INSERT INTO theory_predictions VALUES('A','ATLAS_2016_I1458270','1458270','REF','d','y02',
       'ATLAS_2016_I1458270-Theory.yoda',
       'Expected SM events',
       'Background expectation from search paper.');
INSERT INTO theory_predictions VALUES('A','ATLAS_2016_I1467454:LMODE=MU','1182519,725573,877524','SPECIAL','d',NULL,
       'ATLAS_2016_I1467454:LMODE=MU-Theory.yoda',
       'FEWZ',
       'Predictions from the paper, taken from the ll ratio plot (Born) but applied to the dressed level ee & mm data as mult. factors.');
INSERT INTO theory_predictions VALUES('A','ATLAS_2016_I1467454:LMODE=EL','1182519,725573,877524','SPECIAL','d',NULL,
       'ATLAS_2016_I1467454:LMODE=EL-Theory.yoda',
       'FEWZ',
       'Predictions from the paper, taken from the ll ratio plot (Born) but applied to the dressed level ee & mm data as mult. factors.');
INSERT INTO theory_predictions VALUES('A','ATLAS_2016_I1492320:LMODE=3L','1293923','RAW','d01-x01-y01',NULL,
       'ATLAS_2016_I1492320:LMODE=3L-Theory.yoda',
       'MadGraph',
       'Taken from measurement paper');
INSERT INTO theory_predictions VALUES('A','ATLAS_2016_I1492320:LMODE=2L2J','1293923','RAW','d01-x01-y02',NULL,
       'ATLAS_2016_I1492320:LMODE=2L2J-Theory.yoda',
       'MadGraph',
       'Taken from measurement paper');
INSERT INTO theory_predictions VALUES('A','ATLAS_2017_I1591327','1664354,1893572','SPECIAL','d',NULL,
       'ATLAS_2017_I1591327-Theory.yoda',
       'N$^3$LL$^\prime$ + NNLO',
       'Neumann; Boussaha, Iddir, Semlala.');
INSERT INTO theory_predictions VALUES('B','ATLAS_2017_I1591327','1664354,939520','SPECIAL','d',NULL,
       'ATLAS_2017_I1591327-Theory_B.yoda',
       'NNLO QCD',
       'Boussaha, Iddir, Semlala; 2gamma from Catani, Cieri, de Florian, Ferrera and Grazzini, Diphoton production at hadron colliders: a fully-differential QCD calculation at NNLO.');
-- Note the ptGG is very poorly described, but better here, for example: https://inspirehep.net/literature/1893572

INSERT INTO theory_predictions VALUES('A','ATLAS_2017_I1609448','1736301,1609448','REF','d','y02',
       'ATLAS_2017_I1609448-Theory.yoda',
       'SM (Sherpa $\times$ NNLO)',
       'From Measurement paper.');
INSERT INTO theory_predictions VALUES('A','ATLAS_2017_I1614149','1838799,1980698','RAW','d',NULL,
       'ATLAS_2017_I1614149-Theory.yoda',
       'PowhegBoxZpWp',
       'As used in Altakach et all arXiv:2111.15406');
INSERT INTO theory_predictions VALUES('A','ATLAS_2017_I1645627','1727794','SPECIAL','d',NULL,
       'ATLAS_2017_I1645627-Theory.yoda',
       'NNLO QCD arXiv:1904.01044',
       'Isolated photon and photon+jet production at NNLO QCD accuracy, from Chen et al');
INSERT INTO theory_predictions VALUES('A','ATLAS_2018_I1646686','1838799,1838807,1980698','RAW','d',NULL,
       'ATLAS_2018_I1646686-Theory.yoda',
       'PowhegBoxZpWp',
       'As used in Altakach et all arXiv:2111.15406');
INSERT INTO theory_predictions VALUES('A','ATLAS_2018_I1656578','1838799,1838807','RAW','d',NULL,
       'ATLAS_2018_I1656578-Theory.yoda',
       'PowhegBoxZpWp',
       'As used in Altakach et all arXiv:2111.15406');
INSERT INTO theory_predictions VALUES('A','ATLAS_2019_I1720442','1736301,1720442','REF','d','y02',
       'ATLAS_2019_I1720442-Theory.yoda',
       'Sherpa+NLO EW',
       'See measurement paper for full details. HEPData record at https://doi.org/10.17182/hepdata.84818');
INSERT INTO theory_predictions VALUES('A','ATLAS_2019_I1725190','1725190','SPECIAL','d',NULL,
       'ATLAS_2019_I1725190-Theory.yoda',
       'Background fit',
       'The \"Theory prediction\" is the background fit to data from the measurement paper.');
INSERT INTO theory_predictions VALUES('A','ATLAS_2019_I1750330:TYPE=BOTH','1838799,1838807,1980698','RAW','d',NULL,
       'ATLAS_2019_I1750330:TYPE=BOTH-Theory.yoda',
       'PowhegBoxZpWp',
       'As used in Altakach et all arXiv:2111.15406');
INSERT INTO theory_predictions VALUES('A','ATLAS_2019_I1759875','1838799,1838807,1980698','RAW','d',NULL,
       'ATLAS_2019_I1759875-Theory.yoda',
       'PowhegBoxZpWp',
       'As used in Altakach et all arXiv:2111.15406');
INSERT INTO theory_predictions VALUES('A','ATLAS_2021_I1849535','1736301,1849535','REF','y01','y02',
       'ATLAS_2021_I1849535-Theory.yoda',
       'Sherpa+NLO EW',
       'See measurement paper for full details. HEPData record at https://doi.org/10.17182/hepdata.94413.v1');
INSERT INTO theory_predictions VALUES('A','ATLAS_2023_I2690799','2690799','REF','y01','y02',
        'ATLAS_2023_I2690799-Theory.yoda',
        'Strong 4ljj (SHERPA) + EW 4ljj (MG+PY8)',
        'See measurement paper for full details. Hepdata record at https://doi.org/10.17182/hepdata.144086.v1');
INSERT INTO theory_predictions VALUES('B','ATLAS_2023_I2690799','2690799','REF','y01','y03',
        'ATLAS_2023_I2690799-Theory_B.yoda',
        'Strong 4ljj (MADGRAPH) + EW 4ljj (MG5+PY8)',
        'See measurement paper for full details. Hepdata record at https://doi.org/10.17182/hepdata.144086.v1');
INSERT INTO theory_predictions VALUES('A','ATLAS_2021_I1852328','1852328,1636973,946998,1311991,1456822,1736301,1334525','SPECIAL','d',NULL,
       'ATLAS_2021_I1852328-Theory.yoda',
       'MATRIX nNNLO x NLO EW',
       'Rescaled to b-veto measurement using data. See measurement paper for full details of calculation. HEPData record at https://doi.org/10.17182/hepdata.100511.v1');

INSERT INTO theory_predictions VALUES('A','CMS_2016_I1491950','1838799,1980698','RAW','d',NULL,
       'CMS_2016_I1491950-Theory.yoda',
       'PowhegBoxZpWp',
       'As used in Altakach et all arXiv:2111.15406');
INSERT INTO theory_predictions VALUES('A','CMS_2017_I1467451','1095242,1239172','SPECIAL','d',NULL,
       'CMS_2017_I1467451-Theory.yoda',
       'HRes 2.2',
       'Calculation from measurement paper. See that paper for more details.');
INSERT INTO theory_predictions VALUES('A','CMS_2017_I1518399','1838799,1838807,1980698','RAW','d',NULL,
       'CMS_2017_I1518399-Theory.yoda',
       'PowhegBoxZpWp',
       'As used in Altakach et all arXiv:2111.15406');
INSERT INTO theory_predictions VALUES('A','CMS_2018_I1662081','1838799,1838807,1980698','RAW','d',NULL,
       'CMS_2018_I1662081-Theory.yoda',
       'PowhegBoxZpWp',
       'As used in Altakach et all arXiv:2111.15406');
INSERT INTO theory_predictions VALUES('A','CMS_2018_I1663958','1838799,1838807,1980698','RAW','d',NULL,
       'CMS_2018_I1663958-Theory.yoda',
       'PowhegBoxZpWp',
       'As used in Altakach et all arXiv:2111.15406');
INSERT INTO theory_predictions VALUES('A','CMS_2019_I1764472','1838799,1838807,1980698','RAW','d',NULL,
       'CMS_2019_I1764472-Theory.yoda',
       'PowhegBoxZpWp',
       'As used in Altakach et all arXiv:2111.15406');
INSERT INTO theory_predictions VALUES('A','CMS_2021_I1866118','1866118','SPECIAL',NULL,NULL,
       'CMS_2021_I1866118-Theory.yoda',
       'MG5_aMC (NLO) PYTHIA8, CP5 tune',
       'Generated by CMS, see paper for full list of references.');
INSERT INTO theory_predictions VALUES('A','LHCB_2018_I1662483','1838799,1838807,1980698','RAW','d',NULL,
       'LHCB_2018_I1662483-Theory.yoda',
       'PowhegBoxZpWp',
       'As used in Altakach et all arXiv:2111.15406');
INSERT INTO theory_predictions VALUES('A','ATLAS_2018_I1634970','1838799','RAW','d',NULL,
       'ATLAS_2018_I1634970-Theory.yoda',
       'Powheg',
       'As used in Altakach et all arXiv:2111.15406');

INSERT INTO theory_predictions VALUES('A','ATLAS_2018_I1705857','1705857','SPECIAL',NULL,NULL,
       'ATLAS_2018_I1705857-Theory.yoda',
       'POWHEG+PYTHIA8',
       'Generated from data taken from paper, used Sherpa 2.2 ttbb (4FS) for d02-x01-y01');

INSERT INTO theory_predictions VALUES('A','CMS_2022_I2079374','2079374,1750311,1799842','SPECIAL',NULL,NULL,
       'CMS_2022_I2079374-Theory.yoda',
       'MiNNLO_PS',
       'Generated from data taken from paper.'); 

INSERT INTO theory_predictions VALUES('B','CMS_2022_I2079374','2079374','SPECIAL',NULL,NULL,
       'CMS_2022_I2079374-Theory_B.yoda',
       'MG5_aMC(0,1,2j)+PY8',
       'Generated from data taken from paper.'); 

INSERT INTO theory_predictions VALUES('A','ATLAS_2023_I2648096','2648096,1407976,845712','SPECIAL',NULL,NULL,
       'ATLAS_2023_I2648096-Theory.yoda',
       'Powheg+Herwig7.0.4',
       'Generated from data taken from paper. Uncertainties from envelope of predictions.'); 

INSERT INTO theory_predictions VALUES('A','CMS_2023_I2709669','2709669','REF','d01','y02',
       'CMS_2023_I2709669-Theory.yoda',
       'MG5_aMC (NLO) + Py8',
       'See measurement paper for details, hepdata at https://doi.org/10.17182/hepdata.144361.v2');

INSERT INTO theory_predictions VALUES('A','ATLAS_2024_I2768921:LMODE=SINGLE','2768921','SPECIAL','d06,d08,d10,d44,d46,d48','y03',
       'ATLAS_2024_I2768921:LMODE=SINGLE-Theory_A.yoda',
       'MG5_aMC+H7',
       'Central value from Hepdata (https://doi.org/10.17182/hepdata.146899.v1) Uncertainties from difference to prediction B');

INSERT INTO theory_predictions VALUES('B','ATLAS_2024_I2768921:LMODE=SINGLE','2768921','SPECIAL','d06,d08,d10,d44,d46,d48','y02',
       'ATLAS_2024_I2768921:LMODE=SINGLE-Theory_B.yoda',
       'MG5_aMC+P8',
       'Central value from Hepdata (https://doi.org/10.17182/hepdata.146899.v1) Uncertainties from difference to prediction A');
INSERT INTO theory_predictions VALUES('A','ATLAS_2024_I2768921:LMODE=DILEPTON','2768921','SPECIAL','d12,d14,d16,d50,d52,d54','y03',
       'ATLAS_2024_I2768921:LMODE=DILEPTON-Theory_A.yoda',
       'MG5_aMC+H7',
       'Central value from Hepdata (https://doi.org/10.17182/hepdata.146899.v1) Uncertainties from difference to prediction B');

INSERT INTO theory_predictions VALUES('B','ATLAS_2024_I2768921:LMODE=DILEPTON','2768921','SPECIAL','d12,d14,d16,d50,d52,d54','y02',
       'ATLAS_2024_I2768921:LMODE=DILEPTON-Theory_B.yoda',
       'MG5_aMC+P8',
       'Central value from Hepdata (https://doi.org/10.17182/hepdata.146899.v1) Uncertainties from difference to prediction A');

INSERT INTO theory_predictions VALUES('A','CMS_2021_I1901295','1901295,1293923,1321709','SPECIAL',
                                      'd159,d163,d167,d171,d175,d179,d183,d187,d191,d195,d199,d203,d207,d211,d317,d321,d325,d329',
                                      'y01','CMS_2021_I1901295-Theory.yoda','MG5_aMC + Pythia8',
                                      'Generated from data in paper available at: https://doi.org/10.1103/PhysRevD.104.092013');


COMMIT;
