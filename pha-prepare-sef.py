#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
# PROGRAM: pha-prepare-sef.py
#------------------------------------------------------------------------------
# Version 0.1
# 19 May, 2022
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

# OS libraries:
import os, glob

# Plotting libraries:
import matplotlib
import matplotlib.pyplot as plt
#import seaborn as sns; sns.set()
import cartopy
import cartopy.crs as ccrs
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# SETTINGS: 
#------------------------------------------------------------------------------

fontsize = 20
flag_stationlistmap = True

filepath = 'DATA/Norway/*.tsv'
filenames = sorted(glob.glob( filepath ))

#------------------------------------------------------------------------------
# LOAD: station SEF files into Pandas and write station files and station list for PHAv52i
#------------------------------------------------------------------------------
# NB: missing values are -9999 and are 4-digit scaled integers i.e. AA.A --> AAA0

# INITIALISE: empty pandas dataframe for storing archive station dataframes

ds = []

# INITIALISE: arrays for storing archive station variables

dates = []
obs = []
stationcodes = []
stationnames = []
stationlats = []
stationlons = []
stationelevations = []

# LOOP: over archive and append station dataframe

for s in range(len(filenames)):
        
    f = open(filenames[s])

    years = []
    months = []
    values = []

    lines = f.readlines()
    for i in range(len(lines)):

        words = lines[i].split()    
        if i == 1:
            if len(str(words[1])) == 5:			
                stationcode = '0'+str(words[1])
            elif len(str(words[1]))==6:			
                stationcode = str(words[1])
        if i == 2: stationname = words[1]
        if i == 3: stationlat = float(words[1])
        if i == 4: stationlon = float(words[1])
        if i == 5: stationelevation = int(words[1])
        if (i==0) | ((i>5) & (i<13)): continue 
        if i >= 13: # start of observations
            if (words[0]=='NA') | (words[1]=='NA'):
                continue
            else: 
                year = int(words[0])
                month = int(words[1])
                value = words[-1]
                if value == 'NA':
                    value = -9999
                else:
                    value = int(float(value)*100)
                years.append(year)
                months.append(month)
                values.append(value)        
    f.close()    
        
    # PAD: time vector to cater for skipped months
    
    datetimes_filled = pd.date_range( start=str(np.min(years)), end=str(np.max(years)+1), freq='MS')[0:-1]
    datetimes_data = [ pd.to_datetime( str(years[i])+'-'+str(months[i])+'-01', format='%Y-%m-%d' ) for i in range(len(years)) ]
    df_filled = pd.DataFrame( {'datetime':datetimes_filled} )
    df_data = pd.DataFrame( {'datetime':datetimes_data, 'values':values} )
    df = df_filled.merge(df_data, how='left', on='datetime')

    years = np.unique( df.datetime.dt.year.values )
    obs = np.array( df['values'].values ).reshape(len(years),12)       
    codes = list( [stationcode]*len(years) ) 
    names = list( [stationname]*len(years) ) 
    lats = list( [stationlat]*len(years) ) 
    lons = list( [stationlon]*len(years) ) 
    elevations = list( [stationelevation]*len(years) )
    

    # FILL VALUE: -9999 for GHCNm-v3 format

    obs[ ~np.isfinite(obs) ] = -9999.0
    obs = obs.astype(int)    
    
    # DATAFRAME: for station data
    
    da = pd.DataFrame(columns=['stationcode','year','1','2','3','4','5','6','7','8','9','10','11','12','stationlat','stationlon','stationelevation','stationname' ])
    da['stationcode'] = codes
    da['year'] = years
    for j in range(12):        
        da[da.columns[j+2]] = [ obs[i][j] for i in range(len(obs)) ]
    da['stationlat'] = lats
    da['stationlon'] = lons
    da['stationelevation'] = elevations
    da['stationname'] = names

    # APPEND: dataframe to mothership

    ds.append(da)
    
# CONCATENATE
    
ds = pd.concat(ds, axis=0)

# WRITE: station files in GHCNm-v3 format + stnlist

n = len(np.unique(ds['stationcode']))
station_list = open('world1_stnlist.tavg', "w")

for i in range(n):

    da = ds[ds['stationcode']==np.unique(ds['stationcode'])[i]]

    # Add file to station list

    station_list.write('%s' % 'PHA00' + da['stationcode'].unique()[0] + ' ')
    station_list.write('%s' % str(da['stationlat'].unique()[0]).rjust(5) + '     ')
    station_list.write('%s' % str(da['stationlon'].unique()[0]).rjust(5) + '    ')
    station_list.write('%s' % '+1 01' + ' ')
    station_list.write('%s' % str(da['stationelevation'].unique()[0]).rjust(4) + '    ')
    station_list.write('%s' % da['stationname'].unique()[0].ljust(35))    
    station_list.write('%s' % 'Norway')    
    station_list.write('\n')

    # Write station file out in GHCNm-v3 format

    filename = 'PHA00' + np.unique(ds['stationcode'])[i] + '.raw.tavg'
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
# PLOT: stationlist map
#------------------------------------------------------------------------------

if flag_stationlistmap == True:

    n = len(np.unique(ds.stationcode))
    x = ds.groupby('stationcode')['stationlon'].mean()
    y = ds.groupby('stationcode')['stationlat'].mean()
    c = np.ones(n)    

    figstr = 'stationlistmap.png'
    titlestr = 'Stations: n=' + str(n)            

    fig  = plt.figure(figsize=(15,10))
    p = ccrs.PlateCarree(central_longitude=0)
    ax = plt.axes(projection=p)
    extent = [x.min(),x.max(),y.min(),y.max()]
    ax.set_extent(extent)
    plt.scatter( x=x, y=y, c=c, marker='o', s=10, alpha=0.5, transform=ccrs.PlateCarree())  
    ax.stock_img()
    plt.tick_params(labelsize=fontsize)        
    ax.set_xticks(ax.get_xticks()[abs(ax.get_xticks())<=180])
    ax.set_yticks(ax.get_yticks()[abs(ax.get_yticks())<=90])
    ax.tick_params(labelsize=16)    
    plt.xlim(x.min(),x.max())
    plt.ylim(y.min(),y.max())
    plt.xlabel(r'Longitude, $^{\circ}E$', fontsize=fontsize)
    plt.ylabel(r'Latitude, $^{\circ}N$', fontsize=fontsize)
    plt.title( titlestr, fontsize=fontsize )
    plt.savefig( figstr, dpi=300)
    plt.close('all')

#------------------------------------------------------------------------------
print('** END')

