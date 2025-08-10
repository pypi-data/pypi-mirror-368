#custom function to load a datagrid, any file reading format will do, here we use pandas to directly read a csv contraint file
import pandas as pd
import numpy as np

scan = "LFscan1"

# Unitarity bound
def Unitarity(paramDict):
    """ return 1 if excluded by Borexino neutrino-electron scattering cross section, 0 otherwise """
    import numpy as np

    if scan == "LFscan1":
        gYXm = 1.0
    else:
        return None, None

    pts=[]
    vals=[]

    lmY1 = np.linspace(10,3610.,500)
    lmXm = np.linspace(10,1610.,500)

    for mY1 in lmY1:
        for mXm in lmXm:
            temp=dict.fromkeys(paramDict)
            temp["Y1"]=mY1
            temp["Xm"]=mXm
            pts.append(temp)     
            vals.append(mY1/mXm-0.5)
    return pts, vals


