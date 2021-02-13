#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
# PROGRAM: pha-prepare.py
#------------------------------------------------------------------------------
# Version 0.1
# 12 February, 2021
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
# OS libraries:
import os
import os.path
from pathlib import Path
import sys
import subprocess
from subprocess import Popen
import time

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

#------------------------------------------------------------------------------
# LOAD: station(s) monthly data (CRUTEM format)
#------------------------------------------------------------------------------

filename = 'Iceland21.postmerge'

nheader = 0
f = open(filename)
lines = f.readlines()
dates = []
stationcodes = []
obs = []
for i in range(nheader,len(lines)):
    words = lines[i].split()    
    if len(words) == 9:
        stationcode = '0'+words[0][0:6]
    elif len(words) == 13:
        date = int(words[0])
        val = (len(words)-1)*[None]
        for j in range(len(val)):                
            try: val[j] = int(words[j+1])
            except:                    
                pass
        stationcodes.append(stationcode)
        dates.append(date)
        obs.append(val) 
f.close()    
dates = np.array(dates)
obs = np.array(obs)

# Convert data to GHCNm-v3 format

obs = obs *10
obs[obs==-9990] = -9999

# Create pandas dataframe

df = pd.DataFrame(columns=['stationcode','year','1','2','3','4','5','6','7','8','9','10','11','12'])
df['stationcode'] = stationcodes
df['year'] = dates
for j in range(12):        
    df[df.columns[j+2]] = [ obs[i][j] for i in range(len(obs)) ]

# Use CRUTEM archive to extract station metadata

dg = pd.read_pickle('df_anom.pkl', compression='bz2')

#Index(['year', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12',
#       'stationcode', 'stationlat', 'stationlon', 'stationelevation',
#       'stationname', 'stationcountry', 'stationfirstyear', 'stationlastyear',
#       'stationsource', 'stationfirstreliable'],

# Write station files in GHCNm-v3 format

station_list = open('world1_stnlist.tavg', "w")
for i in range(n):
    da = df[df['stationcode']==np.unique(stationcodes)[i]]
    db = dg[dg['stationcode']==np.unique(stationcodes)[i]]

    # Add file to station list if metadata exists

    if len(db)>0:
        station_list.write('%s' % db['stationcode'].unique()[0] + ' ')
        station_list.write('%s' % str(db['stationlat'].unique()[0]).rjust(5) + '     ')
        station_list.write('%s' % str(db['stationlon'].unique()[0]).rjust(5) + '    ')
        station_list.write('%s' % '+1 01' + ' ')
        station_list.write('%s' % str(db['stationelevation'].unique()[0]).rjust(4) + '    ')
        station_list.write('%s' % db['stationname'].unique()[0].ljust(35))    
        station_list.write('%s' % 'GloSAT')    
        station_list.write('\n')
    
        # Write station file out in GHCNm-v3 format

        filename = np.unique(stationcodes)[i] + '.raw.tavg'
        station_file = open(filename, "w")
        for j in range(len(da)):
            station_file.write('%s' % da['stationcode'].unique()[0] + ' ')
            station_file.write('%s' % str(da['year'].iloc[j]) + ' ')
            for k in range(1,13):
                val = str(da[str(k)].iloc[j]).rjust(5) + '    '
                station_file.write('%s' % val)
            station_file.write('\n')
        station_file.close()

station_list.close()

#------------------------------------------------------------------------------
print('** END')

