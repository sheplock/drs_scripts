import sys
import struct
import datetime as dt
import json
import csv
import glob
import argparse
import numpy as np
import ROOT as r
import time
from multiprocessing import Pool
def getStr(fid, length):
    data = fid.read(length)
    if len(data) == 0:
        return None
    res = struct.unpack("c"*length, data)
    res = b"".join(res).decode("utf-8")
    return res


def getShort(fid, num=1):
    data = fid.read(2*num)
    if len(data) == 0:
        return None
    res = struct.unpack("H"*num, data)
    return res[0] if num == 1 else res


def getFloat(fid, num=1):
    data = fid.read(4*num)
    if len(data) == 0:
        return None
    res = struct.unpack("f"*num, data)
    return res[0] if num == 1 else res


def getInt(fid, num=1):
    data = fid.read(4*num)
    if len(data) == 0:
        return None
    res = struct.unpack("I"*num, data)
    return res[0] if num == 1 else res


def parseCSV(csvpaths):
    # numpy append may cuase issue, convert at the end
    HV = []
    currs = []
    uts = []
    for fname in csvpaths:
        print("CSV file: "+fname+" is processed.")
        with open(fname) as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            reader = list(reader)
            # line 0 is just headers
            # line 1 has starting voltage
            HV.append(-1.0*float(reader[1][0]))
            currs.append(float(reader[1][1]))
            uts.append(float(reader[1][2]))
            for row in reader[2:]:
                # row[0] - first column - voltages
                # row[2] - third column - times
                # when next row has different voltage from
                # previous row, save new voltage to HV
                # and time of voltage change to uts
                if float(row[0]) != -1.0*HV[-1]:
                    HV.append(-1.0*float(row[0]))
                    currs.append(float(row[1]))
                    uts.append(float(row[2]))
    HV, currs, uts = np.array(HV), np.array(currs), np.array(uts)
    return HV, currs, uts
def postprocess(voltages, times):
    vs = -voltages
    max_vs = max(vs)
    # max is just the highet point
    imax = np.argmax(vs)
    # istart = np.argmax(times_CH1>tstart_1+times_CH1[0])
    # iend = np.argmax(times_CH1>tend_1+times_CH1[0])
    if(imax > 24 and imax < 1000):
        # after peak
        vs_high = vs[imax:]
        # before peak
        vs_low = vs[:imax]
        rev_vs_low = vs_low[::-1]
        # manual off-set
        # where [axis][index]
        iend = np.where(vs_high < 5.0)[0][0] + imax
        istart = np.where(vs_low < 5.0)[0][-1]
        vMax = max_vs
        tMax = times[imax]
        offset = np.mean(vs[30:int(istart*3/4)])
        noise = 0.5*(np.percentile(vs[:int(istart*3/4)],
                                          95) - np.percentile(vs[:int(istart*3/4)], 5))
        vs -= offset
        area = np.trapz(vs[istart:iend], times[istart:iend])
        return area, offset, noise, tMax, vMax
