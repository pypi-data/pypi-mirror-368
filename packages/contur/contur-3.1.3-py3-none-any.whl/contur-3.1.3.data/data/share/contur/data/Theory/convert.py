

with open("ATLAS_2022_I2077575-Theory.yoda",'r') as fin:
   with open("ATLAS-xxx.yoda", 'w') as fout:
      for line in fin:
          if "y03" in line:
             fout.write(line.replace("REF", "THY"))
          else:
             fout.write(line)


