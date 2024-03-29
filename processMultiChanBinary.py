#! /usr/bin/env python

# take a binary file output from DRS scope
# create a ROOT file with time and voltage arrays
##
# note that time values are different for every event since
# DRS binning is uneven, and the trigger can occur in any bin

import os
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
from utils import *

def processMultiChanBinary(name, HV=[], currs=[], uts=[]):
    print("Processing " + name)
    indir = str(inpath)
    if not os.path.exists(outpath):
        os.makedirs(outpath)
    outdir = str(outpath)
        
    N_BINS = 1024  # number of timing bins per channel

    fin = indir+"/{0}.dat".format(name)
    fout = r.TFile(outdir+"/{0}.root".format(name), "RECREATE")
    ts1 = np.zeros(1024, dtype=float)
    vs1 = np.zeros(1024, dtype=float)
    area_CH1 = np.array([0], dtype=float)
    offset_CH1 = np.array([0], dtype=float)
    noise_CH1 = np.array([0], dtype=float)
    ts2 = np.zeros(1024, dtype=float)
    vs2 = np.zeros(1024, dtype=float)
    area_CH2 = np.array([0], dtype=float)
    offset_CH2 = np.array([0], dtype=float)
    noise_CH2 = np.array([0], dtype=float)
    ts3 = np.zeros(1024, dtype=float)
    vs3 = np.zeros(1024, dtype=float)
    area_CH3 = np.array([0], dtype=float)
    offset_CH3 = np.array([0], dtype=float)
    noise_CH3 = np.array([0], dtype=float)
    ts4 = np.zeros(1024, dtype=float)
    vs4 = np.zeros(1024, dtype=float)
    area_CH4 = np.array([0], dtype=float)
    offset_CH4 = np.array([0], dtype=float)
    noise_CH4 = np.array([0], dtype=float)
    trig_cell = np.array([0], dtype=int)
    evtHV = np.array([0], dtype=float)
    evtHV_adj = np.array([0], dtype=float)
    evtCurr = np.array([0], dtype=float)
    scan = np.array([0], dtype=int)

    vMax_CH1 = np.array([0], dtype=float)
    vMax_CH2 = np.array([0], dtype=float)
    vMax_CH3 = np.array([0], dtype=float)
    vMax_CH4 = np.array([0], dtype=float)

    tMax_CH1 = np.array([0], dtype=float)
    tMax_CH2 = np.array([0], dtype=float)
    tMax_CH3 = np.array([0], dtype=float)
    tMax_CH4 = np.array([0], dtype=float)

    vFix10_CH1 = np.array([0], dtype=float)
    vFix10_CH2 = np.array([0], dtype=float)
    vFix10_CH3 = np.array([0], dtype=float)
    vFix10_CH4 = np.array([0], dtype=float)
    vFix20_CH1 = np.array([0], dtype=float)
    vFix20_CH2 = np.array([0], dtype=float)
    vFix20_CH3 = np.array([0], dtype=float)
    vFix20_CH4 = np.array([0], dtype=float)
    vFix30_CH1 = np.array([0], dtype=float)
    vFix30_CH2 = np.array([0], dtype=float)
    vFix30_CH3 = np.array([0], dtype=float)
    vFix30_CH4 = np.array([0], dtype=float)

    pulseLength_CH1 = np.array([0], dtype=float)
    pulseLength_CH2 = np.array([0], dtype=float)
    pulseLength_CH3 = np.array([0], dtype=float)
    pulseLength_CH4 = np.array([0], dtype=float)

    riseTime_CH1 = np.array([0], dtype=float)
    riseTime_CH2 = np.array([0], dtype=float)
    riseTime_CH3 = np.array([0], dtype=float)
    riseTime_CH4 = np.array([0], dtype=float)

    slope_CH1 = np.array([0], dtype=float)
    slope_CH2 = np.array([0], dtype=float)
    slope_CH3 = np.array([0], dtype=float)
    slope_CH4 = np.array([0], dtype=float)

    t10_CH1 = np.array([0], dtype=float)
    t10_CH2 = np.array([0], dtype=float)
    t10_CH3 = np.array([0], dtype=float)
    t10_CH4 = np.array([0], dtype=float)

    t90_CH1 = np.array([0], dtype=float)
    t90_CH2 = np.array([0], dtype=float)
    t90_CH3 = np.array([0], dtype=float)
    t90_CH4 = np.array([0], dtype=float)

    v10_CH1 = np.array([0], dtype=float)
    v10_CH2 = np.array([0], dtype=float)
    v10_CH3 = np.array([0], dtype=float)
    v10_CH4 = np.array([0], dtype=float)

    v90_CH1 = np.array([0], dtype=float)
    v90_CH2 = np.array([0], dtype=float)
    v90_CH3 = np.array([0], dtype=float)
    v90_CH4 = np.array([0], dtype=float)

    t = r.TTree("Events", "Events")
    t1 = t.Branch("times_CH1", ts1, 'times[1024]/D')
    v1 = t.Branch("voltages_CH1", vs1, 'voltages[1024]/D')
    t2 = t.Branch("times_CH2", ts2, 'times[1024]/D')
    v2 = t.Branch("voltages_CH2", vs2, 'voltages[1024]/D')
    t3 = t.Branch("times_CH3", ts3, 'times[1024]/D')
    v3 = t.Branch("voltages_CH3", vs3, 'voltages[1024]/D')
    t4 = t.Branch("times_CH4", ts4, 'times[1024]/D')
    v4 = t.Branch("voltages_CH4", vs4, 'voltages[1024]/D')
    if len(HV) > 0 or len(uts) > 0:
        eHV = t.Branch("bias_voltage", evtHV, 'bias/D')
        eHV_adj = t.Branch("bias_voltage_adjusted", evtHV_adj, 'adjusted_bias/D')
        eCurr = t.Branch("bias_current", evtCurr, 'bias/D')
    b_scan = t.Branch("scan_number", scan, 'scan/I')

    b_area_CH1 = t.Branch("area_CH1", area_CH1, "area/D")
    b_offset_CH1 = t.Branch("offset_CH1", offset_CH1, "offset/D")
    b_noise_CH1 = t.Branch("noise_CH1", noise_CH1, "noise/D")
    b_area_CH2 = t.Branch("area_CH2", area_CH2, "area/D")
    b_offset_CH2 = t.Branch("offset_CH2", offset_CH2, "offset/D")
    b_noise_CH2 = t.Branch("noise_CH2", noise_CH2, "noise/D")
    b_area_CH3 = t.Branch("area_CH3", area_CH3, "area/D")
    b_offset_CH3 = t.Branch("offset_CH3", offset_CH3, "offset/D")
    b_noise_CH3 = t.Branch("noise_CH3", noise_CH3, "noise/D")
    b_area_CH4 = t.Branch("area_CH4", area_CH4, "area/D")
    b_offset_CH4 = t.Branch("offset_CH4", offset_CH4, "offset/D")
    b_noise_CH4 = t.Branch("noise_CH4", noise_CH4, "noise/D")
    b_tMax_CH1 = t.Branch("tMax_CH1", tMax_CH1, "dt/D")
    b_tMax_CH2 = t.Branch("tMax_CH2", tMax_CH2, "dt/D")
    b_tMax_CH3 = t.Branch("tMax_CH3", tMax_CH3, "dt/D")
    b_tMax_CH4 = t.Branch("tMax_CH4", tMax_CH4, "dt/D")
    b_vMax_CH1 = t.Branch("vMax_CH1", vMax_CH1, "dt/D")
    b_vMax_CH2 = t.Branch("vMax_CH2", vMax_CH2, "dt/D")
    b_vMax_CH3 = t.Branch("vMax_CH3", vMax_CH3, "dt/D")
    b_vMax_CH4 = t.Branch("vMax_CH4", vMax_CH4, "dt/D")
    b_vFix10_CH1 = t.Branch("vFix10_CH1", vFix10_CH1, "vFix10/D")
    b_vFix10_CH2 = t.Branch("vFix10_CH2", vFix10_CH2, "vFix10/D")
    b_vFix10_CH3 = t.Branch("vFix10_CH3", vFix10_CH3, "vFix10/D")
    b_vFix10_CH4 = t.Branch("vFix10_CH4", vFix10_CH4, "vFix10/D")
    b_vFix20_CH1 = t.Branch("vFix20_CH1", vFix20_CH1, "vFix20/D")
    b_vFix20_CH2 = t.Branch("vFix20_CH2", vFix20_CH2, "vFix20/D")
    b_vFix20_CH3 = t.Branch("vFix20_CH3", vFix20_CH3, "vFix20/D")
    b_vFix20_CH4 = t.Branch("vFix20_CH4", vFix20_CH4, "vFix20/D")
    b_vFix30_CH1 = t.Branch("vFix30_CH1", vFix30_CH1, "vFix30/D")
    b_vFix30_CH2 = t.Branch("vFix30_CH2", vFix30_CH2, "vFix30/D")
    b_vFix30_CH3 = t.Branch("vFix30_CH3", vFix30_CH3, "vFix30/D")
    b_vFix30_CH4 = t.Branch("vFix30_CH4", vFix30_CH4, "vFix30/D")

    b_pulseLength_CH1 = t.Branch("pulseLength_CH1", pulseLength_CH1, "pulseLength/D")
    b_pulseLength_CH2 = t.Branch("pulseLength_CH2", pulseLength_CH2, "pulseLength/D")
    b_pulseLength_CH3 = t.Branch("pulseLength_CH3", pulseLength_CH3, "pulseLength/D")
    b_pulseLength_CH4 = t.Branch("pulseLength_CH4", pulseLength_CH4, "pulseLength/D")
    
    b_riseTime_CH1 = t.Branch("riseTime_CH1", riseTime_CH1, "riseTime/D")
    b_riseTime_CH2 = t.Branch("riseTime_CH2", riseTime_CH2, "riseTime/D")
    b_riseTime_CH3 = t.Branch("riseTime_CH3", riseTime_CH3, "riseTime/D")
    b_riseTime_CH4 = t.Branch("riseTime_CH4", riseTime_CH4, "riseTime/D")

    b_slope_CH1 = t.Branch("slope_CH1", slope_CH1, "slope/D")
    b_slope_CH2 = t.Branch("slope_CH2", slope_CH2, "slope/D")
    b_slope_CH3 = t.Branch("slope_CH3", slope_CH3, "slope/D")
    b_slope_CH4 = t.Branch("slope_CH4", slope_CH4, "slope/D")
    
    b_t10_CH1 = t.Branch("t10_CH1", t10_CH1, "t10/D")
    b_t10_CH2 = t.Branch("t10_CH2", t10_CH2, "t10/D")
    b_t10_CH3 = t.Branch("t10_CH3", t10_CH3, "t10/D")
    b_t10_CH4 = t.Branch("t10_CH4", t10_CH4, "t10/D")
    
    b_t90_CH1 = t.Branch("t90_CH1", t90_CH1, "t90/D")
    b_t90_CH2 = t.Branch("t90_CH2", t90_CH2, "t90/D")
    b_t90_CH3 = t.Branch("t90_CH3", t90_CH3, "t90/D")
    b_t90_CH4 = t.Branch("t90_CH4", t90_CH4, "t90/D")
    
    b_v10_CH1 = t.Branch("v10_CH1", v10_CH1, "v10/D")
    b_v10_CH2 = t.Branch("v10_CH2", v10_CH2, "v10/D")
    b_v10_CH3 = t.Branch("v10_CH3", v10_CH3, "v10/D")
    b_v10_CH4 = t.Branch("v10_CH4", v10_CH4, "v10/D")
    
    b_v90_CH1 = t.Branch("v90_CH1", v90_CH1, "v90/D")
    b_v90_CH2 = t.Branch("v90_CH2", v90_CH2, "v90/D")
    b_v90_CH3 = t.Branch("v90_CH3", v90_CH3, "v90/D")
    b_v90_CH4 = t.Branch("v90_CH4", v90_CH4, "v90/D")
    
    fid = open(fin, 'rb')

    # make sure file header is correct
    fhdr = getStr(fid, 4)
    if fhdr != "DRS2":
        print("ERROR: unrecognized header "+fhdr)
        exit(1)

    # make sure timing header is correct
    thdr = getStr(fid, 4)
    if thdr != "TIME":
        print("ERROR: unrecognized time header "+thdr)
        exit(1)

    # get the boards in file
    n_boards = 0
    channels = []
    board_ids = []
    bin_widths = []
    while True:
        bhdr = getStr(fid, 2)
        if bhdr != "B#":
            fid.seek(-2, 1)
            break
        board_ids.append(getShort(fid))
        n_boards += 1
        bin_widths.append([])
        print("Found Board #"+str(board_ids[-1]))

        while True:
            chdr = getStr(fid, 3)
            if chdr != "C00":
                fid.seek(-3, 1)
                break
            cnum = int(getStr(fid, 1))
            print("Found channel #"+str(cnum))
            channels.append(cnum)
            bin_widths[n_boards-1].append(getFloat(fid, N_BINS))

        if len(bin_widths[n_boards-1]) == 0:
            print("ERROR: Board #{0} doesn't have any channels!".format(
                board_ids[-1]))

    if n_boards == 0:
        print("ERROR: didn't find any valid boards!")
        exit(1)

    if n_boards > 1:
        print(
            "ERROR: only support one board. Found {0} in file.".format(n_boards))
        exit(1)

    bin_widths = bin_widths[0]
    n_chan = len(bin_widths)
    rates = []

    epoch = dt.datetime.utcfromtimestamp(0)
    #-7 for March - November Daylight Savings Time, -8 otherwise for Standard Time
    #UTC_OFFSET = -8
    UTC_OFFSET = -7

    n_evt = 0
    bad_evt = 0
    lastHV = 0
    n_scan = 0
    scan_up = True
    start_row = 2
    while True:
        ehdr = getStr(fid, 4)
        if ehdr is None:
            break
        if ehdr != 'EHDR':
            raise Exception("Bad event header!")

        n_evt += 1
        # skip 2 digits for NO USE
        serial = getInt(fid)

        # print "  Serial #"+str(serial)
        # Following lines get event time convert to UNIX timestamp
        # Quick cheat to get from PST to UTC but doesn't account for daylight savings...
        date = getShort(fid, 7)
        date = dt.datetime(*date[:6], microsecond=1000*date[6])
        date = date - dt.timedelta(hours=UTC_OFFSET)
        timestamp = (date - epoch).total_seconds()
        # argmax(uts>timestamp) returns the index when
        # event time (timestamp) comes before a uts voltage change time
        # so the voltage of event corresponds to the previous argument
        # since it is the bin where timestamp occurred (> lower limit, < upper)
        if len(uts) > 0:
            nextChange = np.argmax(uts > timestamp)
            previous = nextChange-1
            gap = uts[nextChange] - uts[previous]
            lastHV = evtHV[0]
            evtHV[0] = HV[np.argmax(uts > timestamp)-1]
            evtHV_adj[0] = HV[np.argmax(uts > timestamp)-1] - 1.1e6*currs[np.argmax(uts > timestamp)-1]
            evtCurr[0] = currs[np.argmax(uts > timestamp)-1]
        
        if scan_up and evtHV[0] < lastHV:
            n_scan += 1
            scan_up = False
            scan[0] = n_scan
        elif (not scan_up) and evtHV[0] > lastHV:
            n_scan += 1
            scan_up = True
            scan[0] = n_scan
        else:
            scan[0] = n_scan

        if((n_evt-1) % 10000 == 0):
            print("Processing event "+str(n_evt-1))

        if n_evt == 1:
            t_start = date
        t_end = date
        # print "  Date: "+str(date)
        rangeCtr = getShort(fid)
        # print "  Range Center: "+str(rangeCtr)
        getStr(fid, 2)
        b_num = getShort(fid)
        getStr(fid, 2)
        trig_cell[0] = getShort(fid)
        # print "  Trigger Cell: "+str(trig_cell)


        goodFlag = True
        for ichn in range(n_chan):
            chdr = getStr(fid, 4)
            chdr = chdr
            if chdr != "C00"+str(channels[ichn]):
                print("ERROR: bad event data!")
                exit(1)

            # skipping digits again
            scaler = getInt(fid)
            voltages = np.array(getShort(fid, N_BINS))
            # if READ_CHN != channels[ichn]:
            #    continue
            # if (timestamp > (uts[nextChange] - 0.2*gap)):
            #     goodFlag = False
            #     continue
            voltages = voltages/65535. * 1000 - 500 + rangeCtr
            times = np.roll(np.array(bin_widths[ichn]), N_BINS-trig_cell[0])
            times = np.cumsum(times)
            times = np.append([0], times[:-1])
            rates.append((times[-1]-times[0])/(times.size-1))
            #try:
            area, offset, noise, tMax, vMax, vFix10, vFix20, vFix30, pulseLength, t10, t90, v10, v90, riseTime, slope = postprocess(voltages, times)
#except:
                #if ichn == 0:
                #    print("ERROR: bad event "+str(n_evt-1))
                #    bad_evt += 1
                #continue
                # area, offset, noise, tMax, vMax = 0,0,0,0,0
            if ichn == 0:
                np.copyto(ts1, times)
                np.copyto(vs1, voltages)
                np.copyto(area_CH1, area)
                np.copyto(offset_CH1, offset)
                np.copyto(noise_CH1, noise)
                np.copyto(tMax_CH1, tMax)
                np.copyto(vMax_CH1, vMax)
                np.copyto(vFix10_CH1, vFix10)
                np.copyto(vFix20_CH1, vFix20)
                np.copyto(vFix30_CH1, vFix30)
                np.copyto(pulseLength_CH1, pulseLength)
                np.copyto(riseTime_CH1, riseTime)
                np.copyto(slope_CH1, slope)
                np.copyto(t10_CH1, t10)
                np.copyto(t90_CH1, t90)
                np.copyto(v10_CH1, v10)
                np.copyto(v90_CH1, v90)
            elif ichn == 1:
                np.copyto(ts2, times)
                np.copyto(vs2, voltages)
                np.copyto(area_CH2, area)
                np.copyto(offset_CH2, offset)
                np.copyto(noise_CH2, noise)
                np.copyto(tMax_CH2, tMax)
                np.copyto(vMax_CH2, vMax)
                np.copyto(vFix10_CH2, vFix10)
                np.copyto(vFix20_CH2, vFix20)
                np.copyto(vFix30_CH2, vFix30)
                np.copyto(pulseLength_CH2, pulseLength)
                np.copyto(riseTime_CH2, riseTime)
                np.copyto(slope_CH2, slope)
                np.copyto(t10_CH2, t10)
                np.copyto(t90_CH2, t90)
                np.copyto(v10_CH2, v10)
                np.copyto(v90_CH2, v90)
            elif ichn == 2:
                np.copyto(ts3, times)
                np.copyto(vs3, voltages)
                np.copyto(area_CH3, area)
                np.copyto(offset_CH3, offset)
                np.copyto(noise_CH3, noise)
                np.copyto(tMax_CH3, tMax)
                np.copyto(vMax_CH3, vMax)
                np.copyto(vFix10_CH3, vFix10)
                np.copyto(vFix20_CH3, vFix20)
                np.copyto(vFix30_CH3, vFix30)
                np.copyto(pulseLength_CH3, pulseLength)
                np.copyto(riseTime_CH3, riseTime)
                np.copyto(slope_CH3, slope)
                np.copyto(t10_CH3, t10)
                np.copyto(t90_CH3, t90)
                np.copyto(v10_CH3, v10)
                np.copyto(v90_CH3, v90)
            elif ichn == 3:
                np.copyto(ts4, times)
                np.copyto(vs4, voltages)
                np.copyto(area_CH4, area)
                np.copyto(offset_CH4, offset)
                np.copyto(noise_CH4, noise)
                np.copyto(tMax_CH4, tMax)
                np.copyto(vMax_CH4, vMax)
                np.copyto(vFix10_CH4, vFix10)
                np.copyto(vFix20_CH4, vFix20)
                np.copyto(vFix30_CH4, vFix30)
                np.copyto(pulseLength_CH4, pulseLength)
                np.copyto(riseTime_CH4, riseTime)
                np.copyto(slope_CH4, slope)
                np.copyto(t10_CH4, t10)
                np.copyto(t90_CH4, t90)
                np.copyto(v10_CH4, v10)
                np.copyto(v90_CH4, v90)
            else:
                print("ERROR: Channel out of range! "+str(ichn))
                exit(1)

        if goodFlag:
            t.Fill()

    t_tot = t_end - t_start
    t_sec = t_tot.total_seconds()

    print("Measured sampling rate: {0:.2f} GHz".format(1.0/np.mean(rates)))
    print("Total time of run = " + str(t_tot) +
          " = " + str(t_sec) + " seconds.")
    print("Event rate = " + str(n_evt/t_sec) + " Hz")
    t.Write()
    fout.Close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Parse DRS .dat file and .csv into .root files")
    parser.add_argument('-b', '--binaryfile',
                        help='Path to binary files', required=True, type=str)
    parser.add_argument('-o', '--outputpath',
                        help='Path for output ROOT file', required=False, type=str)
    parser.add_argument('-c', '--csvpath', 
                        help='Path to folder of CSV file', required=False, type=str)
    args = vars(parser.parse_args())

    datfiles = glob.glob(args["binaryfile"]+"/*.dat")
    try:
        csvpath = glob.glob(args['csvpath']+"/*.csv")
    except TypeError:
        csvpath = []
    outpath = args['outputpath']
    if outpath == None:
        outpath = "./processed/"

    HV, currs, uts = parseCSV(csvpath)
    poolargs = []
    for each in datfiles:
        folder, name = each.rsplit('/', 1)
        name, ext = name.rsplit('.', 1)
        # avoid overwrite
        if not (glob.glob(outpath+name+".root")):
            #poolargs.append((name, HV, currs, uts))
            inpath = folder
            processMultiChanBinary(name, HV, currs, uts)
            
    #pool = Pool(processes=5)
    #pool.starmap(processMultiChanBinary, poolargs)
