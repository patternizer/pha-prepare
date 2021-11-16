#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#------------------------------------------------------------------------------
# PROGRAM: convert-sef-2-ghcn.py
#------------------------------------------------------------------------------
# Version 0.1
# 15 November, 2021
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

#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# SETTINGS: 
#------------------------------------------------------------------------------

filename = 'DATA/MetNo_18700_Oslo_1816_2020_ta_monthly.tsv'

#------------------------------------------------------------------------------
# LOAD: station metadata and values (SEF format)
#------------------------------------------------------------------------------
# NB: missing values are -9999 and are 4-digit scaled integers i.e. AA.A --> AAA0

nheader = 0
f = open(filename)
lines = f.readlines()
years = []
values = []
for i in range(nheader,len(lines)):
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
    if i >= 13:
        year = int(words[0])
        value = words[-1]
        if value == 'NA':
            value = -9999
        else:
            value = int(float(value)*100)
        years.append(year)
        values.append(value)        
f.close()    
years = np.unique(years)
values = np.array(values).reshape((len(years), 12))
 
#------------------------------------------------------------------------------
# CREATE: pandas dataframe for station data
#------------------------------------------------------------------------------

df = pd.DataFrame(columns=['stationcode','year','1','2','3','4','5','6','7','8','9','10','11','12'])
df['year'] = years
df['stationcode'] = stationcode
df.iloc[:,2:14] = values

#------------------------------------------------------------------------------
# WRITE: dataframe to CSV in GHCNm-v3 format ( required by PHAv52i )
#------------------------------------------------------------------------------

filename = 'PHA00' + stationcode + '.raw.tavg'
station_file = open(filename, "w")
for j in range(len(df)):
    station_file.write('%s' % 'PHA00' + df['stationcode'].unique()[0] + ' ')
    station_file.write('%s' % str(df['year'].iloc[j]) + ' ')
    for k in range(1,13):
        val = str(df[str(k)].iloc[j]).rjust(5) + '    '
        station_file.write('%s' % val)
    station_file.write('\n')
station_file.close()
            
#------------------------------------------------------------------------------
# WRITE: station metadata as line entry in station list file ( required by PHAv52i )
#------------------------------------------------------------------------------

#99184109646 -42.9     147.5    +1 01   54    HOBARTTASMANWAS_9497               GloSAT

station_list = open('world1_stnlist.tavg', "w")
station_list.write('%s' % 'PHA00' + stationcode + ' ')
station_list.write('%s' % str(stationlat).rjust(5) + '     ')
station_list.write('%s' % str(stationlon).rjust(5) + '    ')
station_list.write('%s' % '+1 01' + ' ')
station_list.write('%s' % str(stationelevation).rjust(4) + '    ')
station_list.write('%s' % stationname.ljust(35))    
station_list.write('%s' % 'GloSAT')    
station_list.write('\n')
station_list.close()

#------------------------------------------------------------------------------
print('** END')

