#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
# PROGRAM: pha-prepare-glosat.py
#------------------------------------------------------------------------------
# Version 0.2
# 26 May, 2021
# Michael Taylor
# https://patternizer.github.io
# patternizer AT gmail DOT com
# michael DOT a DOT taylor AT uea DOT ac DOT uk
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
flag_stationlistmap = True

format_acorn = True

data_dir = 'DATA/'

#normals_file = data_dir + 'normals5.GloSAT.prelim03_FRYuse_ocPLAUS1_iqr3.600reg0.3_19411990_MIN15_OCany_19611990_MIN15_PERDEC00_NManySDreq.txt'
normals_file = data_dir + 'CRUTEM.5.0.1.0.normals5.txt'
anomaly_file = data_dir + 'df_anom.pkl'

#stations_file = data_dir + 'Iceland21.postmerge'
#stations_file = data_dir + 'Iceland21.postmerge'
#stations_file = data_dir + 'Iceland_all_rawlatest_270121.Tg'
#stations_file = data_dir + 'stat4.postqc.CRUTEM.5.0.1.0-202103.txt'
stations_file = data_dir + 'Australia_GHCNv4_adjusted.Tg'
#stations_file = data_dir + 'Australia_GHCNv4_unadjusted.Tg'

#------------------------------------------------------------------------------
# LOAD: station(s) monthly data (CRUTEM format)
#------------------------------------------------------------------------------
   
if format_acorn == True:

    #  309-183-1436  295 GEORGETOWN_POST_OFFI AUSTRALIA     18942007  99189400094275
    
    nheader = 0
    f = open(stations_file)
    lines = f.readlines()
    dates = []
    obs = []
    stationcodes = []
    stationlats = []
    stationlons = []
    stationelevations = []
    stationnames = []
    stationcountries = []
    for i in range(nheader,len(lines)):
        words = lines[i].split()    
        if len(words) == 6:
            geodata = words[0].split('-')
            stationcode = words[5]            
            stationlat = (float(geodata[1])/10) * -1.0
            stationlon = (float(geodata[2])/10) * 1.0
            stationelevation = int(words[1])
            stationname = words[2]
            stationcountry = words[3]
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
            stationcountries.append(stationcountry)
    f.close()    
    dates = np.array(dates)
    obs = np.array(obs)
    stationcodes = np.array(stationcodes)
    stationlats = np.array(stationlats)
    stationlons = np.array(stationlons)
    stationelevations = np.array(stationelevations)

else:
    
    nheader = 0
    f = open(stations_file)
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
df['stationlat'] = stationlats
df['stationlon'] = stationlons
df['stationelevation'] = stationelevations
df['stationname'] = stationnames
df['year'] = dates
for j in range(12):        
    df[df.columns[j+2]] = [ obs[i][j] for i in range(len(obs)) ]

# WRITE: station files in GHCNm-v3 format + stnlist

# NB: PHA requires station codes to be 11 characters in length - take first 6 and last 5 to reduce risk of duplicates

n = len(np.unique(stationcodes))
station_list = open('world1_stnlist.tavg', "w")
for i in range(n):
    da = df[df['stationcode']==np.unique(stationcodes)[i]]

    station_list.write('%s' % da['stationcode'].unique()[0][0:6] + da['stationcode'].unique()[0][-5:] + ' ')
#   station_list.write('%s' % 'PHA00' + da['stationcode'].unique()[0] + ' ')
    station_list.write('%s' % str(da['stationlat'].unique()[0]).rjust(5) + '     ')
    station_list.write('%s' % str(da['stationlon'].unique()[0]).rjust(5) + '    ')
    station_list.write('%s' % '+1 01' + ' ')
    station_list.write('%s' % str(da['stationelevation'].unique()[0]).rjust(4) + '    ')
    station_list.write('%s' % da['stationname'].unique()[0].ljust(35))    
    station_list.write('%s' % 'GloSAT')    
    station_list.write('\n')

    # Write station file out in GHCNm-v3 format

    filename = np.unique(stationcodes)[i][0:6] + np.unique(stationcodes)[i][-5:] + '.raw.tavg'
#   filename = 'PHA00' + np.unique(stationcodes)[i] + '.raw.tavg'
    station_file = open(filename, "w")
    for j in range(len(da)):
        station_file.write('%s' % da['stationcode'].unique()[0][0:6] + da['stationcode'].unique()[0][-5:] + ' ')
#       station_file.write('%s' % 'PHA00' + da['stationcode'].unique()[0] + ' ')
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

    n_pha = len(stationcodes_pha)
    x, y = np.meshgrid(stationlons_pha,stationlats_pha)    

    figstr = 'stationlistmap.png'
    titlestr = 'Stations processed by PHA v52i: n=' + str(n_pha)
            
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

