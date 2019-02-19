import sys
import os
import ROOT as r
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

# Choose file to draw (no .root)
name = "13022019_KUBoard_BothChan_200V_4V_LED_1000evts"

outdir = "/homes/sheplock/Timing/drs_scope/plots/{0}/waveforms/".format(name)
os.system("mkdir -p {0}".format(outdir))

f = r.TFile("/homes/sheplock/Timing/drs_scope/data/processed/{0}.root".format(name))
t = f.Get("Events")

times = np.zeros(1024, dtype=float)
voltages = np.zeros(1024, dtype=float)

### THESE NEED TO BE EDITED EACH TIME ###
# change to channel number you would like to draw
t.SetBranchAddress("times_CH1",times) 
t.SetBranchAddress("voltages_CH1",voltages)
# set channel number (for names of png)
chan = "CH1"
# set time window for calculating area
tstart = 560
tend   = 640
# set number of events you want to draw
N_PLOTS = 20
#########################################

plt.figure(1)



Nevt = t.GetEntries()
for i in range(N_PLOTS):
    t.GetEntry(i)

    vs = -voltages

    istart = np.argmax(times>tstart+times[0])
    iend = np.argmax(times>tend+times[0])

    offset = np.mean(vs[10:istart * 3/4])
    noise = 0.5*(np.percentile(vs[:istart*3/4],95) - np.percentile(vs[:istart*3/4],5))
    
    area = np.trapz(vs[istart:iend] - offset, times[istart:iend])

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

    plt.savefig(outdir + chan + "rawevt{0:06d}.png".format(i))
