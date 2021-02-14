#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
# PROGRAM: pha-prepare.py
#------------------------------------------------------------------------------
# Version 0.2
# 13 February, 2021
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

# LOAD: CRUTEM archive --> for station metadata (lat, lon, elevation)

dg = pd.read_pickle('df_anom.pkl', compression='bz2')

# LOAD: CRUTEM normals --> to filter out stations without normals

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

# WRITE: station files in GHCNm-v3 format + stnlist

n = len(np.unique(stationcodes))
station_list = open('world1_stnlist.tavg', "w")
for i in range(n):
    da = df[df['stationcode']==np.unique(stationcodes)[i]]
    db = dg[dg['stationcode']==np.unique(stationcodes)[i]]

    # Add file to station list if metadata exists --> station is in CRUTEM archive (with normals)

    if len(db)>0:
        station_list.write('%s' % 'PHA00' + db['stationcode'].unique()[0] + ' ')
        station_list.write('%s' % str(db['stationlat'].unique()[0]).rjust(5) + '     ')
        station_list.write('%s' % str(db['stationlon'].unique()[0]).rjust(5) + '    ')
        station_list.write('%s' % '+1 01' + ' ')
        station_list.write('%s' % str(db['stationelevation'].unique()[0]).rjust(4) + '    ')
        station_list.write('%s' % db['stationname'].unique()[0].ljust(35))    
        station_list.write('%s' % 'GloSAT')    
        station_list.write('\n')
    
        # Write station file out in GHCNm-v3 format

        filename = 'PHA00' + np.unique(stationcodes)[i] + '.raw.tavg'
        station_file = open(filename, "w")
        for j in range(len(da)):
            station_file.write('%s' % 'PHA00' + da['stationcode'].unique()[0] + ' ')
            station_file.write('%s' % str(da['year'].iloc[j]) + ' ')
            for k in range(1,13):
                val = str(da[str(k)].iloc[j]).rjust(5) + '    '
                station_file.write('%s' % val)
            station_file.write('\n')
        station_file.close()

station_list.close()

#------------------------------------------------------------------------------
print('** END')

