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
    avgCurr = 0.0
    evts = 0
    for fname in csvpaths:
        print("CSV file: "+fname+" is processed.")
        with open(fname) as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            reader = list(reader)
            # line 0 is just headers
            # line 1 has starting voltage
            HV.append(-1.0*float(reader[1][0]))
            #currs.append(float(reader[1][1]))
            uts.append(float(reader[1][2]))
            avgCurr += float(reader[1][1])
            evts += 1
            for row in reader[2:]:
                # row[0] - first column - voltages
                # row[2] - third column - times
                # when next row has different voltage from
                # previous row, save new voltage to HV
                # and time of voltage change to uts
                if float(row[0]) != -1.0*HV[-1]:
                    HV.append(-1.0*float(row[0]))
                    uts.append(float(row[2]))
                    #print(row[0],row[2],evts)
                    currs.append(-1.0*float(avgCurr)/float(evts))
                    avgCurr = 0.0
                    evts = 1
                else:
                    avgCurr += float(row[1])
                    evts += 1
            currs.append(-1.0*float(avgCurr)/float(evts))
    HV, currs, uts = np.array(HV), np.array(currs), np.array(uts)
    return HV, currs, uts


def getIV(csvpaths, time, start_row):
    for fname in csvpaths:
        with open(fname) as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            reader = list(reader)
            for row in range(start_row,len(reader)):
                if time < float(reader[row][2]) and time > float(reader[row-1][2]):
                    return float(reader[row-1][1]), float(reader[row-1][0]), row
    print("ERROR: No I-V for event! t = ",time)


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
        try:
            iend = np.where(vs_high < 5.0)[0][0] + imax
        except:
            iend = 1000
        try:
            istart = np.where(vs_low < 5.0)[0][-1]
        except:
            istart = 24
        vMax = max_vs
        tMax = times[imax]
        offset = np.mean(vs[:int(istart*3/4)])
        noise = 0.5*(np.percentile(vs[:int(istart*3/4)],
                                          95) - np.percentile(vs[:int(istart*3/4)], 5))
        vs -= offset
        area = np.trapz(vs[istart:iend], times[istart:iend])

        try:
            vFix10 = vs[istart+20]
        except:
            vFix10 = -999
        try:
            vFix20 = vs[istart+40]
        except:
            vFix20 = -999
        try:
            vFix30 = vs[istart+60]
        except:
            vFix30 = -999
        
        return area, offset, noise, tMax, vMax, vFix10, vFix20, vFix30
