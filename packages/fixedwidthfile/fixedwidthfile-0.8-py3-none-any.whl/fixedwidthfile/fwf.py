#!/usr/bin/python3

# Author: Hsiang-An Andy Chien
# Email: hsiangan.chien@utoronto.ca

# file specification file format
# column name,start,end
# the start and end number starts with 1

import csv
import sys

import pandas as pd
import numpy as np

import traceback

# character references used in parameters are 1 based

class FixedWidthFile:
    def __init__(self, fsfpath):
        self.flf = None
        self.fs = []
        self.header = []
        self.nextline = []
        self.specDict = {}
        
        with open(fsfpath,'r') as fsfhandle:
            csvr = csv.reader(fsfhandle)

            # skip first line because it is header
            next(csvr)

            for l in csvr:
                self.header.append(l[0])
                s = int(l[1])
                e = int(l[2])
                d = None if l[3].strip()=="" else int(l[3])
                if d is not None and d > e-s+1:
                    errtxt = f"""In specification file field '{l[0]}' conversion to deicmal 
    digit '{d}' requested is greater than the field length defined 
    'e:{e} - s:{s} + 1 = {e-s+1}'. Please review your field definition."""
                    raise Exception(errtxt)

                self.fs.append((s,e,d))
                self.specDict[l[0]] = [s,e,d]
        
        self.maxlen = max([v[1] for (k, v) in self.specDict.items()]) + 1

    def checkSpecCoverage(self):
        coverage = "0" * self.maxlen

        overlapped = False
        for k, v in self.specDict.items():
            repStr = getStrSliceOneBased(coverage, v[0], v[1])
            repStr = self.rollForwardCheckString(repStr)
            coverage = self.replaceAtLoc(coverage, v[0], v[1], repStr)

        issue = []
        for i, c in enumerate(coverage, 1):
            if c != '1':
                issue.append(i)
        
        if len(issue) > 0:
            errtxt = f"There maybe an issue with the coverage of the spec file,\n" + \
                  f"    please review the following position (position: {issue})\n" + \
                  f"    a full coverage should have each of the character position\n" + \
                  f"    referenced exactly onces (1) " + \
                  f"coverage: '{coverage}'"
            raise Exception(errtxt)

        return coverage

    def rollForwardCheckString(self, s):
        ret = s
        repArr = [['9','X'], ['8','9'], ['7','8'], ['6','7'], ['5','6'],
             ['4','5'], ['3','4'], ['2','3'], ['1','2'], ['0','1']]
        for i in repArr:
            ret = ret.replace(i[0], i[1])
        return ret

    def parseSingleLine(self, l):
        return parseLine(l, self.header, self.specDict)

    def getIterator(self, flfpath):
        return flfIterator(flfpath, self.header, self.specDict)

    def getHeader(self):
        return self.header

    def replaceAtLoc(self, l, s, e, rep):
        return replaceAtLoc(l, s, e, rep)

    def getFlfLine(self, data):
        if type(data) is dict:
            d = data
        elif type(data) is pd.Series:
            d = data.to_dict()
        else:
            errtxt = f"*** Cannot work with data type {type(data)} when composing\n    fixed length line, only pandas.Series or dict types are allowed."
            raise Exception(errtxt)

        ret = " " * self.maxlen

        for h in self.header:
            if h in data.keys():
                s = self.specDict[h][0]
                e = self.specDict[h][1]
                repStr = d[h]
                try:
                    ret = replaceAtLoc(ret, s, e, repStr)
                except Exception as e:
                    st = traceback.format_exc()
                    print(f"{e}\n{h}:{repStr}:{type(repStr)}\n{st}")
                    sys.exit(1)
        return ret

    def getDataFrame(self, I):
        data = []
        for l in self.getIterator(I):
            data.append(l)
        ret = pd.DataFrame(data, columns=self.getHeader())
        return ret


    def __repr__(self):
        return f"file: {self.flfpath}, spec: {self.specDict}"

def getStrSliceOneBased(s, start, end):
    if start == end:
        return s[start-1]
    elif len(s) < end:
        return s[start-1:].rstrip('\n')
    else:
        return s[start-1:end].strip('\n')

def replaceAtLoc(l, s, e, repStr):
    repedStr = getStrSliceOneBased(l, s, e)
    head = "" if s == 1 else getStrSliceOneBased(l, 1, s-1)
    tail = "" if e == len(l)-1 else l[e:len(l)]

    if len(repedStr) != len(repStr):
        errtxt = f"Cannot replace space and string of different length ({s}:{e})\n" + \
              f"    '{repedStr}'({len(repedStr)}) to '{repStr}'({len(repStr)})"
        raise Exception(errtxt)

    ret = head + repStr + tail
    return ret

def parseLine(l, header, fspecDict):
    ret = []
    for h in header:
        s = fspecDict[h][0]
        e = fspecDict[h][1]
        d = fspecDict[h][2]

        if s == e:
            ret.append(getStrSliceOneBased(l, s, e))
        else:
            i = getStrSliceOneBased(l, s, e)
            # test if any request to convert to float
            if d is None:
                ret.append(i)
            else:
                # need to convert value to number using decimal point
                # that is outlined in f[2]
                i_str = i[:len(i)-d]+"."+i[len(i)-d:] if d < e - s + 1 else "0." + i
                try:
                    i_float = float(i_str)
                except ValueError:
                    errtxt = f"On data file line:{self.lineno}. On field '{self.header[pos]}:{s}:{f[1]}' attempting to convert value '{i}' to numeric using the\n    supplied specification 'decimal:{f[2]}' which resulted in invalid output.\n    Program will continue with field populated as the original string of '{i}'\n"
                    print(errtxt)
                    i_str = i
                ret.append(i_str)
    return ret


class flfIterator():
    def __init__(self, flfpath, header, specDict):
        self.flfpath = flfpath
        self.header = header
        self.fspecDict = specDict
        self.flf = open(flfpath,'r')

    def __iter__(self):
        return self

    def __next__(self):
        l = self.flf.readline()

        if len(l) == 0:
            self.flf.close()
            raise StopIteration

        return parseLine(l, self.header, self.fspecDict)
