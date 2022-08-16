import sys
import os
import ROOT as r
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

# Choose file to draw (no .root)
name = "Run262_1Jul22_Ba133_70Vto160V_FNAL316_Board1"

outdir = "./plots/{0}/waveforms/".format(name)
os.system("mkdir -p {0}".format(outdir))

f = r.TFile("../data/processed/{0}.root".format(name))
t = f.Get("Events")

times = np.zeros(1024, dtype=float)
voltages = np.zeros(1024, dtype=float)
evtHV = np.array([0], dtype=float)

### THESE NEED TO BE EDITED EACH TIME ###
# change to channel number you would like to draw
t.SetBranchAddress("times_CH1",times) 
t.SetBranchAddress("voltages_CH1",voltages)
t.SetBranchAddress("bias_voltage",evtHV)

# set channel number (for names of png)
chan = "CH1"
# set time window for calculating area
tstart = 50
tend   = 100
# set number of events you want to draw
N_PLOTS = 20
# choose bias of events that will be drawn
bias = 70
#########################################

plt.figure(1)



Nevt = t.GetEntries()
i=0
j=0
while j<N_PLOTS and i<Nevt:
    t.GetEntry(i)

    if evtHV[0] != bias:
        i+=1
        continue
    vs = -voltages
    if np.max(vs) < 15:
        i+=1
        continue
    istart = np.argmax(times>tstart+times[0])
    iend = np.argmax(times>tend+times[0])
    offset = np.mean(vs[10:istart * 3/4])
    noise = 0.5*(np.percentile(vs[:istart*3/4],95) - np.percentile(vs[:istart*3/4],5))
    

    imax = np.argmax(vs)
    # after peak
    vs_high = vs[imax:]
    # before peak
    vs_low = vs[:imax]
    rev_vs_low = vs_low[::-1]
    # manual off-set
    # where [axis][index]
    noise = 0.5*(np.percentile(vs[:100],95) - np.percentile(vs[:100],5))
    try:
        iend = np.where(vs_high < noise)[0][0] + imax
    except:
        iend = 1000
    try:
        istart = np.where(vs_low < noise)[0][-1]
    except:
        istart = 100
    istart = 100
    iend = 1000
    vMax = vs[imax]
    tMax = times[imax]
    offset = np.mean(vs[:int(istart*3/4)])
        #noise = 0.5*(np.percentile(vs[:int(istart*3/4)],
        #                                  95) - np.percentile(vs[:int(istart*3/4)], 5))


                    
    area = np.trapz(vs[istart:iend] - offset, times[istart:iend])
    #if area < 100:
    #    i+=1
    #    continue
    plt.clf()
    plt.plot(times,vs,'r')
    plt.grid()
    plt.xlabel("Time (ns)")
    plt.ylabel("Voltage (mV)")
    mint = np.amin(times)
    maxt = np.amax(times)
    plt.gca().set_xlim(mint-25, maxt+25)
    plt.gca().set_ylim(-10, 100)
    plt.plot([mint-25, maxt+25], [offset, offset], 'k-')
    plt.plot([mint-25, maxt+25], [offset+noise, offset+noise], 'k--')
    plt.plot([mint-25, maxt+25], [offset-noise, offset-noise], 'k--')
    plt.plot([times[istart],times[istart]], plt.gca().get_ylim(), 'k--')
    plt.plot([times[iend-1],times[iend-1]], plt.gca().get_ylim(), 'k--')
    plt.fill_between([mint-25, maxt+25], offset-noise, offset+noise, color='r', alpha=0.25)
    plt.text(0.60, 0.93, "Area = {0:.1f} mV$\cdot$nS".format(area), transform=plt.gca().transAxes)
    plt.text(0.60, 0.88, "Bias = -{0:.0f} V".format(evtHV[0]), transform=plt.gca().transAxes)
    #plt.text(0.60, 0.83, "Length = {0:.0f} ns".format(times[iend]-times[istart]), transform=plt.gca().transAxes)

    plt.savefig(outdir + chan + "_{0:.0f}V_rawevt{1:07d}_v2.png".format(evtHV[0],i))
    j+=1
    i+=1
