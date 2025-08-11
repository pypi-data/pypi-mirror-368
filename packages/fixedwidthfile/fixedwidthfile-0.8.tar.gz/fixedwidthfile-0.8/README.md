# Overview
fixedwidthfile is a Python library that assists with the processing of fixed width file.

While CSV file format remain the popular non-proprietary data file format in the field of data analytics, much of the main frame input/output file remain to be fixed width file (see [appendix](#app-fll) to gain an understanding why). 

This library defines fixed width file as follows.
> Data with one continuous string having no delimiter for each of the record field. The deciphering of the data fields within the record can only be achieved by cross-referencing a file specification/definition that accompany the fixed width file in question.

For example the data file below
```
0123456789abcdefghijklmnopqrstuvwxyz0123456789abcdefghijklmnopqrstuvwxyz0123456789abcdefghijklmnopqrstuvwxyz
0123456789abcdefghijklmnopqrstuvwxyz0123456789abcdefghijklmnopqrstuvwxyz0123456789abcdefghijklmnopqrstuvwxyz
0123456789abcdefghijklmnopqrstuvwxyz0123456789abcdefghijklmnopqrstuvwxyz0123456789abcdefghijklmnopqrstuvwxyz
0123456789abcdefghijklmnopqrstuvwxyz0123456789abcdefghijklmnopqrstuvwxyz0123456789abcdefghijklmnopqrstuvwxyz
0123456789abcdefghijklmnopqrstuvwxyz0123456789abcdefghijklmnopqrstuvwxyz0123456789abcdefghijklmnopqrstuvwxyz
```

May have the following definition/specification file. It is important to notice this package uses 1-based positioning for the string start/end character. This design choice is explained in the [appendix](#app-1based)
```
fname,start,end,decimal
F1,1,10,
F2,17,22,
F3,34,34,
F4,35,40,
```

The two pieces of information above together can be used to produce a csv dataset that looks like the following when parsed out
```
F1,F2,F3,F4
0123456789,ghijkl,x,yz0123
0123456789,ghijkl,x,yz0123
0123456789,ghijkl,x,yz0123
0123456789,ghijkl,x,yz0123
0123456789,ghijkl,x,yz0123
```

# Prerequisite
This library does not have non Python core library (3.11) dependency. However, it is also dependent on the Pandas (https://pypi.org/project/pandas/) library for data processing methods using Pandas DataFrame.

Install pandas using
```
pip install pandas numpy
```

# Installation
This package is available from Pypi.org. Install it conveniently as follows
```
pip install fixedwithfile
```

# Basic Uses
Example uses can be found in the source folder [example/sample.py](example/sample.py)

Importing the library
```
from fwf import FixedWidthFile
```

Building the field specification file in csv
```
fname,start,end,decimal
```

The following table explains the field specification
| Field Name | Purpose |
| ---------- | ------- |
| fname      | The field name of the column extracted in the header |
| start      | The starting character count of the field (1-based) |
| end      | The ending character count of the field (1-based) |
| decimal      | Should the extracted field be a decimal figure, attempt to convert field to numerical value with the decimal point indicated in this field. For example extract with the field 12345 having the decimal 3 will produce 12.345 |

Back to Python, attaching the field specification to the fixedwidthfile definition
```
fwf = FixedWidthFile("field specification.csv")
```

At this point, you have several methods of using the field specification representation to access the file.

## Input Method 1: Fixed Width File to Python Arrays
Using input.txt as the fixed with file we are trying to load the following utilizes iterator feature by passing the file name "input.txt" to the fwf.getIterator() method. 

Each iterator returns the Python list representation of the data matching the order and position of the data header provided in the file specification.

The Python list then can be used to produce the Pandas DataFrame manually.
```
data = []
for l in fwf.getIterator("input.txt"):
    data.append(l)
df = pd.DataFrame(data, columns=fwf.getHeader())
print(f"{df.head()}")
```

## Input Method 2: Fixed Width File to Pandas DataFrame
Or... you can bypass all that and call the following convenient function and achieve the same thing in one statement.
```
df = fwf.getDataFrame("input.txt")
```

## Output Method 1: Pandas DataFrame to CSV or Excel
Output the data by leveraging Pandas DataFrame
```
df.to_csv("output.csv", index=False)
df.to_excel("output.xlsx", index=False)
```
## Output Method 2: Pandas DataFrame to Fixed With File
If you wish to output the data back to a fixed width file using the specification, you can use the following method call. Beware that you may encounter several errors with regarding field length and numeric to string conversions. It is not possible to proceed with the output until everything for every row is resolved.

Hopefully I have built in enough error messages to help guide you through the reconciliation.
```
with open(O, 'w') as ofile:
    for i, r in df.iterrows():
        ofile.write(f"{fwf.getFlfLine(r)}\n")
```
# About Me
My name is Hsiang-An (Andy) Chien. Currently, full-time data scientist slash ETL engineer (the title changes so fast these days), part-time general computing and gaming enthuiast.

Would love to see my work being used in more ways than one to tackle common challenges others may have encountered along their way. Share this library with others who may need it.

If you have success story to tell, it would make my day! Message me at andy_chien (at) hotmail.com.

# Dedication
I dedicate this work and hopefully a piece of me to the world for my loving family: Jina Chiang, Julia, and Alison Chien. I hope that a piece of me will be around and kicking on the interweb watching over you through time.

# Appendix
## Why is fixed width file sill favoured by mainframe?
<a name="app-fll"/>
Other than working with legacy content, it did not occur to me that the fixed width file retain its usefulness in today's climate because of big data.

From the days of the old, fixed width file was favoured by the mainframe due to it's simplistic nature free from any proprietary file format. It does not take specialized library or package to produce and parse basic string from the mainframe.

Today, the fixed width file continue to serve such functionality through its predictability over big data function. For example, it is possible to build an index by passing though the entire data set once (incurring O(n) time where n is the number of records). Then comes retrieval, the memory offset to the specific row (facilitated by the index produced earlier) and even the column (down to the specific byte) to retrieve using the index can be calculated using a constant time (a meagre cost of O(1)); circumventing the costly loop through a massive dataset.

Source: https://stackoverflow.com/questions/7666780/why-are-fixed-width-file-formats-still-in-use

## Why does your library use 1-based positioning instead of 0 based?
<a name="app-1based"/>
The goal of this library
