#! /usr/bin/env/python

# take output root file from processBinary.py and
# add higher level information like pulse time, area, etc

import sys
import ROOT as r
import numpy as np
import matplotlib.pyplot as plt
# import cPickle as pickle


def postprocessMultiChan(name, chn1, chn2, chn3, chn4):
    print("doing post-processing: {0}".format(name))

    f = r.TFile("./processed/{0}.root".format(name), "UPDATE")
    t = f.Get("Events")

    times_CH1 = np.zeros(1024, dtype=float)
    voltages_CH1 = np.zeros(1024, dtype=float)
    area_CH1 = np.array([0], dtype=float)
    offset_CH1 = np.array([0], dtype=float)
    noise_CH1 = np.array([0], dtype=float)
    times_CH2 = np.zeros(1024, dtype=float)
    voltages_CH2 = np.zeros(1024, dtype=float)
    area_CH2 = np.array([0], dtype=float)
    offset_CH2 = np.array([0], dtype=float)
    noise_CH2 = np.array([0], dtype=float)
    times_CH3 = np.zeros(1024, dtype=float)
    voltages_CH3 = np.zeros(1024, dtype=float)
    area_CH3 = np.array([0], dtype=float)
    offset_CH3 = np.array([0], dtype=float)
    noise_CH3 = np.array([0], dtype=float)
    times_CH4 = np.zeros(1024, dtype=float)
    voltages_CH4 = np.zeros(1024, dtype=float)
    area_CH4 = np.array([0], dtype=float)
    offset_CH4 = np.array([0], dtype=float)
    noise_CH4 = np.array([0], dtype=float)

    evtHV = np.array([0], dtype=float)

    max_CH1 = np.array([0], dtype=float)
    max_CH2 = np.array([0], dtype=float)
    max_CH3 = np.array([0], dtype=float)
    max_CH4 = np.array([0], dtype=float)

    tMax_CH1 = np.array([0], dtype=float)
    tMax_CH2 = np.array([0], dtype=float)
    tMax_CH3 = np.array([0], dtype=float)
    tMax_CH4 = np.array([0], dtype=float)

    t.SetBranchStatus("*", 0)
    t.SetBranchStatus("times_CH1", 1)
    t.SetBranchStatus("voltages_CH1", 1)
    t.SetBranchStatus("times_CH2", 1)
    t.SetBranchStatus("voltages_CH2", 1)
    t.SetBranchStatus("times_CH3", 1)
    t.SetBranchStatus("voltages_CH3", 1)
    t.SetBranchStatus("times_CH4", 1)
    t.SetBranchStatus("voltages_CH4", 1)
    t.SetBranchStatus("bias_voltage", 1)
    nt = t.CloneTree()

    nt.SetBranchAddress("times_CH1", times_CH1)
    nt.SetBranchAddress("voltages_CH1", voltages_CH1)
    nt.SetBranchAddress("times_CH2", times_CH2)
    nt.SetBranchAddress("voltages_CH2", voltages_CH2)
    nt.SetBranchAddress("times_CH3", times_CH3)
    nt.SetBranchAddress("voltages_CH3", voltages_CH3)
    nt.SetBranchAddress("times_CH4", times_CH4)
    nt.SetBranchAddress("voltages_CH4", voltages_CH4)
    nt.SetBranchAddress("bias_voltage", evtHV)
    b_area_CH1 = nt.Branch("area_CH1", area_CH1, "area/D")
    b_offset_CH1 = nt.Branch("offset_CH1", offset_CH1, "offset/D")
    b_noise_CH1 = nt.Branch("noise_CH1", noise_CH1, "noise/D")
    b_area_CH2 = nt.Branch("area_CH2", area_CH2, "area/D")
    b_offset_CH2 = nt.Branch("offset_CH2", offset_CH2, "offset/D")
    b_noise_CH2 = nt.Branch("noise_CH2", noise_CH2, "noise/D")
    b_area_CH3 = nt.Branch("area_CH3", area_CH3, "area/D")
    b_offset_CH3 = nt.Branch("offset_CH3", offset_CH3, "offset/D")
    b_noise_CH3 = nt.Branch("noise_CH3", noise_CH3, "noise/D")
    b_area_CH4 = nt.Branch("area_CH4", area_CH4, "area/D")
    b_offset_CH4 = nt.Branch("offset_CH4", offset_CH4, "offset/D")
    b_noise_CH4 = nt.Branch("noise_CH4", noise_CH4, "noise/D")

    b_tMax_CH1 = nt.Branch("tMax_CH1", tMax_CH1, "dt/D")
    b_tMax_CH2 = nt.Branch("tMax_CH2", tMax_CH2, "dt/D")
    b_tMax_CH3 = nt.Branch("tMax_CH3", tMax_CH3, "dt/D")
    b_tMax_CH4 = nt.Branch("tMax_CH4", tMax_CH4, "dt/D")

    b_max_CH1 = nt.Branch("max_CH1", max_CH1, "dt/D")
    b_max_CH2 = nt.Branch("max_CH2", max_CH2, "dt/D")
    b_max_CH3 = nt.Branch("max_CH3", max_CH3, "dt/D")
    b_max_CH4 = nt.Branch("max_CH4", max_CH4, "dt/D")

    Nevt = nt.GetEntries()

    for ievt in range(Nevt):
        nt.GetEntry(ievt)

        if ievt % 10000 == 0:
            print("iEvt:", ievt)
            # added
            #print("Time elapsed (since loop start): {} seconds".format(time.time()-tLoopStart))

        max1 = False
        max2 = False
        max3 = False
        max4 = False

        # Chunk of code repeated for each channel
        # Calculates offset, noise, area and fills branches
        if(chn1):
            vs = -voltages_CH1
            max_vs = max(vs)
            # max is just the highet point
            imax = np.argmax(vs)
            #istart = np.argmax(times_CH1>tstart_1+times_CH1[0])
            #iend = np.argmax(times_CH1>tend_1+times_CH1[0])
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
                max_CH1[0] = max_vs
                tMax_CH1[0] = times_CH1[imax]
                offset_CH1[0] = np.mean(vs[30:int(istart*3/4)])
                noise_CH1[0] = 0.5*(np.percentile(vs[:int(istart*3/4)],
                                                  95) - np.percentile(vs[:int(istart*3/4)], 5))
                vs -= offset_CH1[0]
                area_CH1[0] = np.trapz(vs[istart:iend], times_CH1[istart:iend])
                b_area_CH1.Fill()
                b_offset_CH1.Fill()
                b_noise_CH1.Fill()
                b_tMax_CH1.Fill()
                b_max_CH1.Fill()

        if(chn2):
            vs = -voltages_CH2
            max_vs = max(vs)
            imax = np.argmax(vs)
            if(imax > 0 and imax < 1024):
                vs_high = vs[imax:]
                vs_low = vs[:imax]
                rev_vs_low = vs_low[::-1]
                iend = np.argmax(vs_high < 5.0) + imax
                istart = len(rev_vs_low) - np.argmax(rev_vs_low < 5.0) - 1
                max_CH2[0] = max_vs
                tMax_CH2[0] = times_CH1[imax]
                offset_CH2[0] = np.mean(vs[30:istart*3/4])
                noise_CH2[0] = 0.5*(np.percentile(vs[:istart*3/4],
                                                  95) - np.percentile(vs[:istart*3/4], 5))
                vs -= offset_CH2[0]
                area_CH2[0] = np.trapz(vs[istart:iend], times_CH2[istart:iend])
                b_area_CH2.Fill()
                b_offset_CH2.Fill()
                b_noise_CH2.Fill()
                b_tMax_CH2.Fill()
                b_max_CH2.Fill()

        if(chn3):
            vs = -voltages_CH3
            max_vs = max(vs)
            imax = np.argmax(vs)
            if(imax > 0 and imax < 1024):
                vs_high = vs[imax:]
                vs_low = vs[:imax]
                rev_vs_low = vs_low[::-1]
                iend = np.argmax(vs_high < 5.0) + imax
                istart = len(rev_vs_low) - np.argmax(rev_vs_low < 5.0) - 1
                max_CH3[0] = max_vs
                tMax_CH3[0] = times_CH1[imax]
                offset_CH3[0] = np.mean(vs[30:istart*3/4])
                noise_CH3[0] = 0.5*(np.percentile(vs[:istart*3/4],
                                                  95) - np.percentile(vs[:istart*3/4], 5))
                vs -= offset_CH3[0]
                area_CH3[0] = np.trapz(vs[istart:iend], times_CH3[istart:iend])
                b_area_CH3.Fill()
                b_offset_CH3.Fill()
                b_noise_CH3.Fill()
                b_tMax_CH3.Fill()
                b_max_CH3.Fill()

        if(chn4):
            vs = -voltages_CH4
            max_vs = max(vs)
            imax = np.argmax(vs)
            if(imax > 0 and imax < 1024):
                vs_high = vs[imax:]
                vs_low = vs[:imax]
                rev_vs_low = vs_low[::-1]
                iend = np.argmax(vs_high < 5.0) + imax
                istart = len(rev_vs_low) - np.argmax(rev_vs_low < 5.0) - 1
                max_CH4[0] = max_vs
                tMax_CH4[0] = times_CH1[imax]
                offset_CH4[0] = np.mean(vs[30:istart*3/4])
                offset_CH4[0] = np.mean(vs[30:istart*3/4])
                noise_CH4[0] = 0.5*(np.percentile(vs[:istart*3/4],
                                                  95) - np.percentile(vs[:istart*3/4], 5))
                vs -= offset_CH4[0]
                area_CH4[0] = np.trapz(vs[istart:iend], times_CH4[istart:iend])
                b_area_CH4.Fill()
                b_offset_CH4.Fill()
                b_noise_CH4.Fill()
                b_tMax_CH4.Fill()
                b_max_CH4.Fill()

    nt.Write("Events", r.TObject.kWriteDelete)
    f.Close()


if __name__ == "__main__":

    # Set which channels have data
    chn1 = True
    chn2 = False
    chn3 = False
    chn4 = False

    args = sys.argv[1:]
    for filename in args:
        folder, name = filename.rsplit('/', 1)
        name, ext = name.rsplit('.', 1)
        postprocessMultiChan(name, chn1, chn2, chn3, chn4)
