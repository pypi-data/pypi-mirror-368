import contur.data.static_db as cdb

"""
Defines the colour mapping to analysis pools.

"""

# a colour cycler for any unknown pools
from cycler import cycler
CONTURCOLORS = cycler(color=["black", "darkviolet", "darkcyan", "sienna", "firebrick", "navy"])

POOLCOLORS = {
    # ==================================
    "JETS": {
        "color" : "silver",
    },
    "TTHAD": {
        "color" : "saddlebrown",
    },
    "3L": {
        "color" : "crimson",
    },
    "4L": {
        "color" : "magenta",
    },
    "GAMMA": {
        "color" : "yellow",
    },
    "GAMMA_MET": {
        "color" : "goldenrod",
    },
    "LMET_GAMMA": {
        "color" : "gold",
    },
    "LL_GAMMA": {
        "color" : "darkgoldenrod",
    },
    "LLJET": {
        "color" : "orange",
    },
    "LMETJET": {
        "color" : "blue",
    },
    "LJET": {
        "color" : "darkorchid",
    },
    "METJET": {
        "color" : "green",
    },
    "L1L2MET": {
        "color" : "skyblue",
    },
    "L1L2METJET": {
        "color" : "turquoise",
    },
    "L1L2B": {
        "color" : "royalblue",
    },
    "LLMET": {
        "color" : "indigo",
    },
    "HMDY": {
        "color" : "salmon",
    },
    "LMDY": {
        "color" : "lime",
    },

    #        "color" : "hotpink",
    #        "color" : "dimgrey",
    #        "color" : "lightsalmon",
    #        "color" : "darksalmon",
    #        "color" : "powderblue",
    #        "color" : "deepskyblue",
    #        "color" : "steelblue",
    #        "color" : "darkgreen",
    #        "color" : "wheat",
    #        "color" : "seagreen",

    # ===============================================
    # other: used when there isn't room in the legend 
    # ===============================================
    "other": {
        "pools": ["other"],
        "color" : "whitesmoke",
    },
    "No data": {
        "pools": ["No data"],
        "color" : "black",
    },
}
    
# Create energy- and experiment-specific internal pool groupings for colour tinting
for poolGroupName, poolGroup in POOLCOLORS.items():
    if "pools" in poolGroup:
        continue

    pool_list = []
    for beam in cdb.get_beams():
        for expt in cdb.get_experiments(beam=beam):
            pool_name = "_".join([expt.id,beam.id[:-3],poolGroupName])
            if pool_name in cdb.get_pools():
                pool_list.append(pool_name)
            
    poolGroup["pools"] = pool_list

# generate a nice-looking, human-readable name for the pool from the poolid
def sanitise_poolName(poolid):
    split = poolid.split("_")

    finalState = " ".join([x for x in split[0:] if not x.isdigit()])

    known_finalStates = {
        "HMDY" : r"high-mass Drell-Yan $\ell\ell$",
        "L1L2B" : r"$e\mu+b$",
        "TTHAD" : r"hadronic $t\bar{t}$",
    }
    known_finalStates["HMDY EL"] = known_finalStates["HMDY"]
    known_finalStates["HMDY MU"] = known_finalStates["HMDY"]
    known_finalStates["LMDY"] = known_finalStates["HMDY"].replace("high", "low")

    if finalState in known_finalStates:
        finalState = known_finalStates[finalState]
    else:
        finalState = finalState.replace("JETS", "jets")
        finalState = finalState.replace("JET", "+jet")
        finalState = finalState.replace("MET", r"\met{}+")
        finalState = finalState.replace("GAMMA", r"$\gamma$+")
        finalState = finalState.replace("SSLL", r"$\ell^\pm\ell^\pm$+")
        finalState = finalState.replace("L1L2", r"$\ell_1\ell_2$+")
        finalState = finalState.replace("LL", r"$\ell^+\ell^-$+")
        finalState = finalState.replace("L", r"$\ell$+")
        finalState = finalState.replace("E", "$e$+")
        finalState = finalState.replace("M", r"$\mu$+")
        finalState = finalState.replace("W", "$W$+")
        finalState = finalState.replace(" ", "")
        finalState = finalState.replace("++", "+")
        finalState = finalState.replace("$+$", "")
        finalState = finalState.strip("+")

        finalState = finalState.replace("met", "MET") # do this now so there's no confusion with muons ("M")

    return finalState

# Create LaTeX pool names
for poolGroupName, poolGroup in POOLCOLORS.items():
    if "latexName" in poolGroup:
        continue
    poolGroup["latexName"] = sanitise_poolName(poolGroupName)
