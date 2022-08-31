
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import os

cwd = os.getcwd()
files = []
files_split = []

for file in os.listdir(str(cwd)):
    if "GTEX" in file and file.endswith(".csv"):
        files.append(os.path.join(str(cwd), file))
for file in files:
        print(file)
        if "GTEX" in file:
                files_split.append(file.split("/")[8][:-4]) #grab only the sample name

print(files_split)
df_files = pd.DataFrame(files, columns = ['URL'])
df_files['Name'] = files_split
df_files.to_csv("pathwayToNodes.csv", sep=',', index = False, header = True)
