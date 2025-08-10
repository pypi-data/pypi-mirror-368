"""
Define some default axis labels

"""

def get_axis_labels():

    axisLabels = {}


    # VLQ stuff
    #axisLabels["xibpw"] = r"$\mathrm{BR}(B \rightarrow~tW)$"
    #axisLabels["xibph"] = r"$\mathrm{BR}(B \rightarrow~bH)$"
    axisLabels["xibpw"] = r"$\mathrm{BR}(Q \rightarrow~qW)$"
    axisLabels["xibph"] = r"$\mathrm{BR}(Q \rightarrow~qH)$"
    axisLabels["xibpz"] = r"$\mathrm{BR}(B \rightarrow~bZ)$"
    axisLabels["xitpw"] = r"$\mathrm{BR}(T \rightarrow~bW)$"
    axisLabels["xitph"] = r"$\mathrm{BR}(T \rightarrow~tH)$"
    axisLabels["xitpz"] = r"$\mathrm{BR}(T \rightarrow~tZ)$"
    axisLabels["kappa"] = r"$\kappa$"
    axisLabels["KT"]    = r"$\kappa$"
    axisLabels["mtp"]   = r"$M_{T^\prime}$ (GeV)"
    #axisLabels["mtp"]   = "$M_Q$ (GeV)"
    axisLabels["mbp"]   = r"$M_{B^\prime}$ (GeV)"
    axisLabels["mx"]    = r"$M_Q$ (GeV)"
    axisLabels["mb4"]   = r"$M_{B^\prime}$ (GeV)"


    # DM
    axisLabels["mXd"]  = r"$M_\mathrm{DM}$ (GeV)"
    axisLabels["mXm"]  = r"$M_\mathrm{DM}$ (GeV)"
    axisLabels["gVq"]  = r"$g_q$"
    axisLabels["gVl"]  = r"$g_l$"
    axisLabels["gVXd"] = r"$g_{DM}$"

    # IDM
    axisLabels["mmA0"]  = r"$M_\mathrm{A_0}$ (GeV)"
    axisLabels["mmH0"]  = r"$M_\mathrm{H_0}$ (GeV)"

    # Zprime
    axisLabels["mY1"] = r"$M_{Z^\prime}$ (GeV)"
    axisLabels["mzp"] = r"$M_{Z^\prime}$ (GeV)"

    # top colour
    axisLabels["mZp"]  = r"$M_{Z^\prime}$ (GeV)"
    axisLabels["cotH"] = r"$\cot\theta_\mathrm{H}$"
    axisLabels["GoM"]  = r"$\Gamma_{Z^\prime}/M_{Z^\prime}$"

    # B-L
    axisLabels["g1p"] = r"$g_1^{\prime}$"
    axisLabels["sa"]  = r"$\sin\alpha$"
    #axisLabels["mh2"] = r"$M_{h_2}$ (GeV)"

    # TFHM
    axisLabels["tsb"]    = r"$\theta_{sb}$"
    axisLabels["gzpmzp"] = r"$g_X \times \mathrm{TeV}/  M_{Z^\prime}$"

    # LQ
    axisLabels["mlq"] = r"$M_{LQ}$ (GeV)"

    # Heavy Neutrinos
    axisLabels["VeN1"] = r"$V_{e_\nu}$"
    axisLabels["MN1"]  = r"$M_{\nu_H}$ (GeV)"

    # 2HDM be careful, beta definitions may change between Ken Lane's and everyone else's conventions.
    axisLabels["mh3"]     = r"$M_A$ (GeV)"
    axisLabels["mh2"]     = r"$M_{H}$ (GeV)"
    axisLabels["mhc"]     = r"$M_{H^\pm}$ (GeV)"
    axisLabels["tanbeta"] = r"$\tan\beta$"
    axisLabels["sinbma"]  = r"$\sin(\beta-\alpha)$"
    axisLabels["cosbma"]  = r"$\cos(\beta-\alpha)$"
    # Kens Gildener-Weinberg thing
    #axisLabels["mh3"] = "$M_A = M_{H^\pm}$ (GeV)"

    axisLabels["mH02"] = r"$M_{H}$ (GeV)"

    # 2HDM+a
    axisLabels["mh4"]  = r"$M_a$ (GeV)"
    axisLabels["sinp"] = r"$\sin\theta$"

    # ALPS
    axisLabels["max"]   = r"$M_\mathrm{ALP}$ (GeV)"
    axisLabels["CaPhi"] = r"$c^\mathrm{eff}_t$"
    axisLabels["CGtil"] = r"$c^\mathrm{eff}_{agg}$"
    axisLabels["CG"] = r"$c^0_{\tilde{\mathrm{G}}}$"

    axisLabels["malp"] = r"$M_{ALP}$ (GeV)"
    axisLabels["caa"]  = r"$c_{\gamma\gamma}/\Lambda$ (TeV$^{-1}$)"
    axisLabels["cah"]  = r"$c_{ah}/\Lambda$ (TeV$^{-1}$)"
    axisLabels["gpl"]  = r"$c_{ee}/\Lambda$ (TeV$^{-1}$)"

    # general light scalar (mphi see below)
    axisLabels["fscale"] = r"$\Lambda$ (GeV)"

    # DE
    axisLabels["c1"]     = r"$C_1$"
    axisLabels["c2"]     = r"$C_2$"
    axisLabels["mphi"]   = r"$M_\phi$ (GeV)"
    axisLabels["mscale"] = r"$M_\mathrm{SCALE}$ (GeV)"

    # neutrino EFT
    axisLabels["mn1"]    = r"$m_N$ (GeV)"
    axisLabels["lambda"] = r"$\Lambda$ (GeV)"
    axisLabels["clnh"]   = r"$\alpha_{LNH}$"
    axisLabels["cnnh"]   = r"$\alpha_{NNH}$"
    axisLabels["cna"]    = r"$\alpha_{NA}$"

    # SUSY/SLHA
    axisLabels["1000022"] = r"$M(\tilde{\chi}_1^0)$ (GeV)"
    axisLabels["1000023"] = r"$M(\tilde{\chi}_2^0)$ (GeV)"
    axisLabels["1000024"] = r"$M(\tilde{\chi}_1^+)$ (GeV)"
    axisLabels["1000025"] = r"$M(\tilde{\chi}_3^0)$ (GeV)"
    axisLabels["1000035"] = r"$M(\tilde{\chi}_4^0)$ (GeV)"

    # Dark Mesons
    axisLabels["PionMass"]   = r"$m_{\pi_D}$ (GeV)"
    axisLabels["FermionEta"] = r"$\eta$"

    # type II seesaw
    axisLabels["mdpp"] = r"$M_{{\Delta}^{\pm\pm}}$~[GeV]"
    axisLabels["gap"]  = r"$\Delta_M=M_{\Delta^\pm}-M_{\Delta^{\pm\pm}}$~[GeV]"

    # SigmaSM (Higgs triplet)
    axisLabels["x0"] = r"$x_0$~[GeV]"
    axisLabels["m0"] = r"$M_H$~[GeV]"
    axisLabels["a2"] = r"$a_2$"
    axisLabels["b4"] = r"$b_4$"

    # LeptoBaryons
    axisLabels["gB"]   = r"$g_\mathrm{B}$"
    axisLabels["MCHI"] = r"$M_\chi$~[GeV]"
    axisLabels["MZB"]  = r"$M_{Z_\mathrm{B}}$~[GeV]"
    axisLabels["MHB"]  = r"$M_{h_\mathrm{B}}$~[GeV]"



    return axisLabels



    return axisLabels



