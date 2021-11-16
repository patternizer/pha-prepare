#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
# PROGRAM: pha-prepare.py
#------------------------------------------------------------------------------
# Version 0.3
# 17 February, 2021
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
import matplotlib as mpl
#matplotlib.use('agg')
import matplotlib.pyplot as plt
import cmocean

# Mapping libraries:
import cartopy
import cartopy.crs as ccrs
from cartopy.io import shapereader
import cartopy.feature as cf

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
min_years = 10
flag_normals = True
flag_stationfiles = True
flag_stationlistmap = True

#filename = 'DATA/Iceland21.postmerge'
filename = 'DATA/Iceland_all_rawlatest_270121.Tg'
normals_file = 'DATA/normals5.GloSAT.prelim03_FRYuse_ocPLAUS1_iqr3.600reg0.3_19411990_MIN15_OCany_19611990_MIN15_PERDEC00_NManySDreq.txt'
anomaly_file = 'DATA/df_anom.pkl'

#------------------------------------------------------------------------------
# LOAD: station(s) monthly data (CRUTEM format)
#------------------------------------------------------------------------------

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
#dg.drop_duplicates().sort_values(by='stationcode').reset_index(drop=True)

if flag_normals == True:

    # LOAD: CRUTEM archive --> for station metadata (lat, lon, elevation)
    # LOAD: CRUTEM normals --> to filter out stations without normals

    dg = pd.read_pickle(anomaly_file, compression='bz2')
    nheader = 0
    f = open(normals_file)
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

    if flag_normals == True:
        condition = (len(db)>0)  # normals existant 
    else:
        condition = (len(da)>min_years) # > minimum number of years of data

    if condition:
        station_list.write('%s' % 'PHA00' + db['stationcode'].unique()[0] + ' ')
        station_list.write('%s' % str(db['stationlat'].unique()[0]).rjust(5) + '     ')
        station_list.write('%s' % str(db['stationlon'].unique()[0]).rjust(5) + '    ')
        station_list.write('%s' % '+1 01' + ' ')
        station_list.write('%s' % str(db['stationelevation'].unique()[0]).rjust(4) + '    ')
        station_list.write('%s' % db['stationname'].unique()[0].ljust(35))    
        station_list.write('%s' % 'GloSAT')    
        station_list.write('\n')

        if flag_stationfiles == True:    

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

# PLOT: stationlist map

if flag_stationlistmap == True:

    nheader = 0
    f = open('world1_stnlist.tavg')
    lines = f.readlines()
    stationcodes_pha = []
    stationlats_pha = []
    stationlons_pha = []
    for i in range(nheader,len(lines)):
        words = lines[i].split()    
        stationcode = words[0]
        stationlat = float(words[1])
        stationlon = float(words[2])
        stationcodes_pha.append(stationcode)
        stationlats_pha.append(stationlat)
        stationlons_pha.append(stationlon)
    f.close()   
    stationcodes_pha = np.array(stationcodes_pha)
    stationlats_pha = np.array(stationlats_pha)
    stationlons_pha = np.array(stationlons_pha)

    n = len(np.unique(stationcodes))
    n_pha = len(stationcodes_pha)
    x, y = np.meshgrid(stationlons,stationlats)    

    figstr = 'stationlistmap.png'
    titlestr = 'Stations processed by PHA v52i: n=' + str(n_pha) + '/' + str(n)
            
    fig  = plt.figure(figsize=(15,10))
    p = ccrs.PlateCarree(central_longitude=0); threshold = 0
    ax = plt.axes(projection=p)
    g = ccrs.Geodetic()
    trans = ax.projection.transform_points(g, x, y)
    x0 = trans[:,:,0]
    x1 = trans[:,:,1]
    extent = [x0.min(),x0.max(),x1.min(),x1.max()]
    ax.set_extent(extent)
    ax.add_feature(cf.BORDERS, edgecolor="green")
    ax.add_feature(cf.COASTLINE, edgecolor="grey")
#   ax.coastlines()
    ax.gridlines()  
    for i in range(len(stationcodes)):
        if i == 0:
            ax.scatter(x=stationlons[i], y=stationlats[i], marker='s', facecolor='lightgrey', edgecolor='black', transform=ccrs.PlateCarree(), label='PHA: not processed')
        else:
            ax.scatter(x=stationlons[i], y=stationlats[i], marker='s', facecolor='lightgrey', edgecolor='black', transform=ccrs.PlateCarree())
    for i in range(len(stationcodes_pha)):
        if i == 0:
            ax.scatter(x=stationlons_pha[i], y=stationlats_pha[i], marker='s', facecolor='red', edgecolor='darkred', transform=ccrs.PlateCarree(), label='PHA: processed')
        else:
            ax.scatter(x=stationlons_pha[i], y=stationlats_pha[i], marker='s', facecolor='red', edgecolor='darkred', transform=ccrs.PlateCarree())
    plt.tick_params(labelsize=fontsize)        
    ax.set_xticks(ax.get_xticks()[abs(ax.get_xticks())<=180])
    ax.set_yticks(ax.get_yticks()[abs(ax.get_yticks())<=90])
    ax.tick_params(labelsize=16)    
    plt.legend(loc='lower left', bbox_to_anchor=(0, -0.8), ncol=1, facecolor='lightgrey', framealpha=1, fontsize=fontsize)    
    fig.subplots_adjust(left=None, bottom=0.4, right=None, top=None, wspace=None, hspace=None)             
    plt.title(titlestr, fontsize=fontsize, pad=20)
    plt.savefig(figstr)
    plt.close('all')

#------------------------------------------------------------------------------
print('** END')

