from fixedwidthfile.fwf import FixedWidthFile

import pandas as pd
import numpy as np

FS = "fieldspec.csv"
I = "sample.txt"
O = "sampleout.txt"

fwf = FixedWidthFile(FS)

# Input Method 1: From Fixed Length File to
#    Python array, to Pandas Dataframe
data = []
for l in fwf.getIterator(I):
    data.append(l)
df = pd.DataFrame(data, columns=fwf.getHeader())
print(f"{df.head()}")

# Input Method 2: From Fixed Length File to
#    Pandas Dataframe
df1 = fwf.getDataFrame(I)
print(f"{df1.head()}")

# Output Method 1: To CSV using Pandas Dataframe
df.to_csv("sample.csv", index=False)

# Output Method 2: Output Fixed Length File from
#    Pandas Dataframe
with open(O, 'w') as ofile:
    for i, r in df.iterrows():
        ofile.write(f"{fwf.getFlfLine(r)}\n")
