#!/usr/bin/env python3
import os,sys

os.makedirs("cards", exist_ok=True)

COMENERGY= sys.argv[1]

param_dict = {}
with open("width/width.dat") as f:
    for l in f.readlines():
        l = l.strip()
        param_dict[l.split(" ")[0]] = l.split(" ")[1]
        # param_dict[MASS] = WIDTH

for mass in param_dict:

    width = param_dict[mass]

    os.system("cp template/template.sh cards/mdpp-" + mass + "_template.sh")
    os.system("sed -i 's|__mdpp__|" + mass + "|g' cards/mdpp-" + mass + "_template.sh")
    os.system("sed -i 's|__wdpp__|" + width + "|g' cards/mdpp-" + mass + "_template.sh")

    os.system("cp param/param.dat cards/mdpp-" + mass + "_param.dat")
    os.system("sed -i 's|__mdpp__|" + mass + "|g' cards/mdpp-" + mass + "_param.dat")

    command = "contur-batch -m madgraph -p mdpp-" + mass + "_param.dat -t mdpp-" + mass + "_template.sh -n 80000 -b " + COMENERGY + " -Q medium -o mdpp-" + mass + "_" + COMENERGY + " -r RunInfo"
    print(command)
