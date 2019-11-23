import os
import sys
import struct
import csv
import glob
import argparse
import ROOT as r
import numpy as np

def parseIV(fname):
    HV = []
    currs = []
    with open(fname) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        reader = list(reader)
        # line 0 is just headers
        # line 1 has starting voltage
        for row in reader[1:]:
            # row[0] - first column - voltages
            # row[2] - third column - times
            HV.append(-1.0*float(row[0]))
            currs.append(float(row[1]))
    HV, currs = np.array(HV), np.array(currs)
    return HV, currs

def makeIV(csvpath):
    if not os.path.exists(outpath):
        os.makedirs(outpath)
    outdir = str(outpath)
    for fname in csvpath:
        print("CSV file: "+fname+" is being processed.")
        folder, name = fname.rsplit('/',1)
        name, ext = name.rsplit('.',1)
        if not (glob.glob(outdir+name+".root")):
            fout = r.TFile(outdir+"/{0}.root".format(name),"RECREATE")

            HV, currs = parseIV(fname)
            if(HV.size != currs.size):
                print("WARNING: I and V arrays different length!")
                nEntries = min(HV.size, currs.size)
            else:
                nEntries = HV.size
            
            Vbias = np.array([0], dtype=float)
            Ibias = np.array([0], dtype=float)
            scan  = np.array([0], dtype=int)

            t = r.TTree("Events","Events")
            b_Vbias = t.Branch("V_bias", Vbias, 'Vbias/D')
            b_Ibias = t.Branch("I_bias", Ibias, 'Ibias/D')
            b_scan  = t.Branch("scan",   scan,  'scan/I')

            scan[0] = 0
            scan_up = True
            for i in range(nEntries):
                if HV[i] < HV[i-1] and scan_up:
                    scan[0] += 1
                    scan_up = False
                elif HV[i] > HV[i-1] and not scan_up:
                    scan[0] += 1
                    scan_up = True
                Vbias[0] = HV[i]
                Ibias[0] = currs[i]
                t.Fill()
            
            t.Write()
            fout.Close()
            print("CSV file: "+fname+" is finished.")
        else:
            print("CSV file: "+fname+" is already processed.")
        print("")
            

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse Keithley .csv into root files")
    parser.add_argument('-c','--csvpath',help='Path to folder of CSV files',required=True,type=str)
    parser.add_argument('-o','--outputpath',help='Path to folder for output ROOT files',required=False,type=str)
    args = vars(parser.parse_args())

    csvpath = glob.glob(args['csvpath']+"/*.csv")
    outpath = args['outputpath']
    if outpath == None:
        outpath = "./IVcurves/"
    
    makeIV(csvpath)
