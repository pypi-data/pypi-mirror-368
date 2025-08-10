def PertUni(paramDict):
    """ return 1 if  excluded, 0 otherwise """

    import numpy as np

    mY1=float(paramDict["Y1"])
    gYXm=float(paramDict["gYXm"])
    mXm=float(paramDict["Xm"])
    gYq=float(paramDict["gYq"])

    return (mXm-mY1)/1000.0


