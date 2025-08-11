from flf_andychien009.fixedlengthfile import FixedLengthFile

import pandas as pd
import numpy as np

FS = "filespec.csv"
I = "sample.txt"
O = "sampleout.txt"

flf = FixedLengthFile(FS)

# Method 1: From Fixed Length File to
#    Python array, to Pandas Dataframe
data = []
for l in flf.getIterator(I):
    data.append(l)
df = pd.DataFrame(data, columns=flf.getHeader())
print(f"{df.head()}")

# Method 2: From Fixed Length File to
#    Pandas Dataframe
df1 = flf.getDataFrame(I)
print(f"{df1.head()}")

# Output Method 1: To CSV using Pandas Dataframe
df.to_csv("sample.csv", index=False)

# Output Method 2: Output Fixed Length File from
#    Pandas Dataframe
with open(O, 'w') as ofile:
    for i, r in df.iterrows():
        ofile.write(f"{flf.getFlfLine(r)}\n")
