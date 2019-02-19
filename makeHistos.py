import sys
import ROOT as r
import numpy as np
import matplotlib.pyplot as plt
import cPickle as pickle
import os
from array import array

def makeHistos(name,x,y1,yerr1,y2,yerr2):

    print "making histograms: {0}".format(name)

    volt = name.split('_')[3]
    volt = volt[:-1]
    volt = float(volt)
        
    filename = r.TFile("/homes/sheplock/Timing/drs_scope/data/processed/{0}.root".format(name))
    tree = filename.Get("Events")

    outdir = "/homes/sheplock/Timing/drs_scope/plots/{0}/histograms/".format(name)
    os.system("mkdir -p {0}".format(outdir))
    outfile = r.TFile("/homes/sheplock/Timing/drs_scope/plots/{0}/histograms/histos.root".format(name),"RECREATE")

    tree.Draw("area_CH1>>h1","","goff")
    h1 = r.gDirectory.Get("h1")
    mean1 = h1.GetMean()
    rms1 = h1.GetRMS()

    tree.Draw("max_CH1>>h2","","goff")
    h2 = r.gDirectory.Get("h2")
    mean2 = h2.GetMean()
    rms2 = h2.GetRMS()

    x = np.append(x,volt)
    y1 = np.append(y1,mean1)
    yerr1 = np.append(yerr1,rms1)
    y2 = np.append(y2,mean2)
    yerr2 = np.append(yerr2,rms2)

    filename.Close()
    outfile.Close()

    return x,y1,yerr1,y2,yerr2

if __name__ == "__main__":

    areas = np.array([],dtype=float)
    a_err = np.array([],dtype=float)
    height = np.array([], dtype=float)
    h_err = np.array([], dtype=float)
    vs = np.array([],dtype=float)
    
    args = sys.argv[1:]
    for filename in args:
        folder, name = filename.rsplit('/',1)
        name, ext = name.rsplit('.',1)
        vs,areas,a_err,height,h_err = makeHistos(name,vs,areas,a_err,height,h_err)

    v_err = np.zeros_like(vs)

    c = r.TCanvas()
    gr1 = r.TGraphErrors(vs.size,array('d',vs),array('d',areas),array('d',v_err),array('d',a_err))
    gr1.SetMarkerStyle(20)
    gr1.SetMarkerColor(4)
    gr1.GetXaxis().SetTitle('Bias voltage [-V]')
    gr1.GetYaxis().SetTitle('Pulse area [mV.ns]')
    gr1.SetTitle('Pulse area vs bias voltage for LED test')
    gr1.Draw('ap')
    c.Update()
    c.SaveAs('plot_area_13Feb2019_v2.png')
    c.WaitPrimitive()

    gr2 = r.TGraphErrors(vs.size,array('d',vs),array('d',height),array('d',v_err),array('d',h_err))
    gr2.SetMarkerStyle(20)
    gr2.SetMarkerColor(2)
    gr2.GetXaxis().SetTitle('Bias voltage [-V]')
    gr2.GetYaxis().SetTitle('Pulse height [mV]')
    gr2.SetTitle('Pulse height vs bias voltage for LED test')
    gr2
    gr2.Draw('ap')
    c.Update()
    c.SaveAs('plot_height_13Feb2019_v2.png')
    c.WaitPrimitive()
    
