#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
# PROGRAM: rate-of-station-loss.py
#------------------------------------------------------------------------------
# Version 0.1
# 16 February, 2021
# Michael Taylor
# https://patternizer.github.io
# patternizer AT gmail DOT com
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# IMPORT PYTHON LIBRARIES
#------------------------------------------------------------------------------
# Dataframe libraries:
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Silence library version notifications
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# SETTINGS: 
#------------------------------------------------------------------------------

fontsize = 20
max_years = 100
flag_normals = False

#------------------------------------------------------------------------------
# LOAD: station(s) monthly data (CRUTEM format)
#------------------------------------------------------------------------------

#filename = 'Iceland21.postmerge'
filename = 'Iceland_all_rawlatest_270121.Tg'

# 40300 641  219   52 REYKJAVIK            ICELAND       17792020  951779       1

nheader = 0
f = open(filename)
lines = f.readlines()
dates = []
obs = []
stationcodes = []
stationlats = []
stationlons = []
stationelevations = []
stationnames = []
for i in range(nheader,len(lines)):
    words = lines[i].split()    
    if len(words) == 9:
        stationcode = '0'+words[0][0:6]
        stationlat = float(words[1])/10
        stationlon = -float(words[2])/10
        stationelevation = int(words[3])
        stationname = words[4]
    elif len(words) == 13:
        date = int(words[0])
        val = (len(words)-1)*[None]
        for j in range(len(val)):                
            try: val[j] = int(words[j+1])
            except:                    
                pass
        dates.append(date)
        obs.append(val) 
        stationcodes.append(stationcode)
        stationlats.append(stationlat)
        stationlons.append(stationlon)
        stationelevations.append(stationelevation)
        stationnames.append(stationname)
f.close()    
dates = np.array(dates)
obs = np.array(obs)
stationcodes = np.array(stationcodes)
stationlats = np.array(stationlats)
stationlons = np.array(stationlons)
stationelevations = np.array(stationelevations)

# Convert data to GHCNm-v3 format

obs = obs *10
obs[obs==-9990] = -9999

# Create pandas dataframe for station data

df = pd.DataFrame(columns=['stationcode','year','1','2','3','4','5','6','7','8','9','10','11','12'])
df['stationcode'] = stationcodes
df['year'] = dates
for j in range(12):        
    df[df.columns[j+2]] = [ obs[i][j] for i in range(len(obs)) ]

# Create pandas dataframe for station list

dg = pd.DataFrame(columns=['stationcode','stationlat','stationlon','stationelevation','stationname'])
dg['stationcode'] = stationcodes
dg['stationlat'] = stationlats
dg['stationlon'] = stationlons
dg['stationelevation'] = stationelevations
dg['stationname'] = stationnames

if flag_normals == True:

    # LOAD: CRUTEM archive --> for station metadata (lat, lon, elevation)
    # LOAD: CRUTEM normals --> to filter out stations without normals

    dg = pd.read_pickle('df_anom.pkl', compression='bz2')
    nheader = 0
    f = open('normals5.GloSAT.prelim03_FRYuse_ocPLAUS1_iqr3.600reg0.3_19411990_MIN15_OCany_19611990_MIN15_PERDEC00_NManySDreq.txt')
    lines = f.readlines()
    normals_stationcodes = []
    normals_sourcecodes = []
    for i in range(nheader,len(lines)):
        words = lines[i].split()    
        normals_stationcode = words[0][0:6]
        normals_sourcecode = int(words[17])
        normals_stationcodes.append(normals_stationcode)
        normals_sourcecodes.append(normals_sourcecode)
    f.close()    
    dn = pd.DataFrame({'stationcode':normals_stationcodes,'sourcecode':normals_sourcecodes})
    dg_normals = dg[dg['stationcode'].isin(dn[dn['sourcecode']>1]['stationcode'])].reset_index()
    dg = dg_normals.copy()

# CALCULATE: number of filtered stations as a function of min years

filtered = []
for min_years in range(max_years+1):

    n = len(np.unique(stationcodes))
    nstations = 0
    for i in range(n):
        da = df[df['stationcode']==np.unique(stationcodes)[i]]
        db = dg[dg['stationcode']==np.unique(stationcodes)[i]]
        condition = (len(da)>min_years) # > minimum number of years of data
        if condition:
            nstations += 1
    filtered.append(nstations)

# PLOT: rate of loss of stations with required length in years

figstr = 'rate-of-station-loss.png'
titlestr = 'Rate of loss of stations with required min length in years'
                 
fig, ax = plt.subplots(figsize=(15,10))     
plt.plot(filtered, color='grey', lw=3)
ax1 = plt.gca()
ax2 = ax.twinx()
ax2.plot(np.array(filtered)/n*100.0, color='red', lw=3)
ax1.set_xlabel(r'Min length in years', fontsize=fontsize)
ax1.set_ylabel('Number of stations', fontsize=fontsize)
ax1.xaxis.grid(True, which='major')      
ax1.tick_params(labelsize=16)    
ax2.set_ylabel('Percentage of stations', fontsize=fontsize, color='red')
ax2.tick_params(labelsize=16, colors='red')    
ax2.spines['right'].set_color('red')
plt.title(titlestr, fontsize=fontsize)
plt.savefig(figstr)
plt.close(fig)

#------------------------------------------------------------------------------
print('** END')

