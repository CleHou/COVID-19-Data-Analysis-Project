#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 19:09:15 2020

@author: Clement
"""
import pandas
import numpy
import os
from tqdm import tqdm

import geoviews as gv
import geoviews.tile_sources as gvts
from geoviews import dim, opts
gv.extension('bokeh')
import holoviews as hv
import geopandas as gpd

def import_df_from_I ():
    partial_link = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_'
    df1 = pandas.read_csv(partial_link+ 'confirmed_global.csv')
    df2 = pandas.read_csv(partial_link+ 'deaths_global.csv')  
    df3 = pandas.read_csv(partial_link+ 'recovered_global.csv')
    to_replace = pandas.read_csv('https://github.com/CleHou/COVID-19-Data-Analysis-Project/raw/master/01-Graph/France_data.csv')
    
    Gposition = pandas.read_csv('https://github.com/CleHou/COVID-19-Data-Analysis-Project/raw/master/02-Maps/country.csv')
    
    Gpolygone = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    
    return [df1, df2, df3], to_replace, Gposition, Gpolygone

def creation_folder (paths):
    current = os.path.dirname(os.path.realpath(__file__))
    list_directory = [os.path.normcase(current + directory) for directory in paths]
    
    for directory in list_directory:
        if os.path.exists(directory) == False:
            print('Directory created')
            os.makedirs(directory)
    list_return = [current + x + '/' for x in paths]      
    return list_return

def save_df (list_df, to_replace, Gposition, Gpolygone):
    file_path = ['/3.0 - Data']
    file_path = creation_folder(file_path)
    
    df1, df2, df3 = list_df
    df1.to_csv(os.path.normcase(file_path [0] + 'confirmed.csv'), index=False)
    df2.to_csv(os.path.normcase(file_path [0] + 'death.csv'    ), index=False)
    df3.to_csv(os.path.normcase(file_path [0] + 'recovered.csv'), index=False)
    to_replace.to_csv(os.path.normcase(file_path [0] + 'Revised_France_Data.csv'), index=False, index_label="Date")
    Gposition.to_csv(os.path.normcase(file_path [0] + 'Gposition.csv'), index=False)
    Gpolygone.to_csv(os.path.normcase(file_path [0] + 'Gpolygone.csv'), index=False)
    
    return print('Saved')

def import_df_from_xlsx (current):
    file_path = [current+'/3.0 - Data/']
    
    df1 = pandas.read_csv(os.path.normcase(file_path [0] + 'confirmed.csv'))
    df2 = pandas.read_csv(os.path.normcase(file_path [0] + 'death.csv')  )
    df3 = pandas.read_csv(os.path.normcase(file_path [0] + 'recovered.csv'))
    to_replace = pandas.read_csv(os.path.normcase(file_path [0] + 'Revised_France_Data.csv'))
    Gposition = pandas.read_csv(os.path.normcase(file_path [0] + 'Gposition.csv'))
    Gpolygone = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    
    
    return [df1, df2, df3], to_replace, Gposition, Gpolygone

def clean_up (list_df):
    list_return = []
    for a_df in list_df:
        a_df = a_df.drop(['Lat', 'Long'], axis=1)
        a_df = a_df.groupby("Country/Region").sum()
        a_df.columns = pandas.to_datetime(a_df.columns)
        a_df.loc['World'] = a_df.sum()
        list_return.append(a_df)                               

    return list_return

def append_geography (list_df, Gposition, Gpolygone):
    list_return = []
    Gposition = Gposition.set_index('name')
    Gposition = Gposition[['latitude', 'longitude']]
    
    Gpolygone = Gpolygone.set_index('name')
    Gpolygone = Gpolygone.rename(index={'United States of America': 'US'})
    Gpolygone = Gpolygone[['geometry']]
    
    condition_print=True
    for a_df in list_df:
        a_df = pandas.concat([Gposition, a_df], axis=1)
        a_df = pandas.concat([Gpolygone, a_df], axis=1, join="inner")
        if condition_print: print("\nCountries with no data")
        
        for indexG in Gpolygone.index:
            if indexG not in (a_df.index):
                list_a = [Gpolygone.loc[indexG, 'geometry']]
                for k in range(len(a_df.columns)-1):
                    list_a.append(numpy.nan)
                                                     
                if condition_print: print(indexG)
                a_df.loc[indexG] = list_a
                
        condition_print=False
        
        list_return.append(a_df)                               
    
    return list_return
    
    

def ajusted_values(list_df, to_replace):
    to_replace = to_replace.set_index('Date')
    to_replace.loc[:,'Cases'] = pandas.to_numeric(to_replace.loc[:,'Cases'], downcast='float')
    to_replace.index = pandas.to_datetime(to_replace.index)
   
    for index in to_replace.index:
        list_df[0].loc['France', index] = to_replace.loc[index, 'Cases']

    return list_df

def smoothed_fun (df, nb_val=2): #Moving average smoothing on the 2 previous values
    list_date = list(df.columns)
    df_smoothed = df.iloc[:, :nb_val]
    
    for k in range(nb_val, len(list_date)):
        df_smoothed [list_date[k]] = 0
        for j in range(0, nb_val+1):
            df_smoothed [list_date[k]] += df[list_date[k-j]] / (nb_val+1)                            

    return df_smoothed

def smoothed_fun_2 (df, nb_val): #Moving average smoothing on the 2 previous values and 2 values after
    list_date = list(df.columns)
    df_smoothed = df.iloc[:, :nb_val]
    
    for k in range(nb_val, len(list_date)-nb_val):
        df_smoothed [list_date[k]] = 0

        for j in range(-nb_val, nb_val+1):
            df_smoothed [list_date[k]] += df[list_date[k-j]] /(2*nb_val+1)                  

    return df_smoothed
    

def fatality_rate (list_df):
    frate = list_df[1] / list_df[0]
  
    return frate

def growth_rate (df):
    list_date = list(df.columns)
    
    grate = df.iloc[:, :1]
    grate.loc[:,list_date[0]] = [0 for k in(range(df.shape[0]))]
    
    for k in range(len(list_date)-1):
        grate.loc[:,list_date[k+1]] = df.loc[:,list_date[k+1]] / df.loc[:,list_date[k]]
    
    grate = grate.replace([numpy.inf, -numpy.inf, numpy.NaN], 0)  
    
    for date in list_date:
        grate.loc[grate[date] >0 , date] = (grate.loc[grate[date] >0 , date]-1)*100
        grate.loc[grate[date] <0 , date] = -(grate.loc[grate[date] <0 , date]-1)*100
      
    return grate

def delta_df (df, parameter):
    list_date = list(df.columns)
    delta_df=df.iloc[:,:parameter]

    for k in range(len(list_date)-parameter):
        delta_df.loc[:, list_date[k+parameter]] = df.loc[:,list_date[k+parameter]] - df.loc[:,list_date[k+parameter-1]]
        
    return delta_df

def combine_delta (df, delta_df, delta2_df):
    combined_delta_df = delta_df.iloc[:,:2]
    
    date = list(delta_df.columns)[-1]
    delta_df[date]= delta_df[date].apply(numpy.floor)
    delta2_df[date]= delta2_df[date].apply(numpy.floor)

    combined_delta_df = pandas.concat([combined_delta_df, df.iloc[:, -1:]], axis=1)
    combined_delta_df = combined_delta_df.rename (columns={date:"Cas"})  
    
    combined_delta_df = pandas.concat([combined_delta_df, delta_df.iloc[:, -1:]], axis=1)
    combined_delta_df = combined_delta_df.rename (columns={date:"Delta cas"})                           
                                      
    combined_delta_df = pandas.concat([combined_delta_df, delta2_df.iloc[:, -1:]], axis=1)
    combined_delta_df = combined_delta_df.rename (columns={date:"Bilan"})
    

    return combined_delta_df

def df_Map1 (list_df):
    list_df = list_df[:2]
    list_col = list(list_df[0].columns)[3:]
    list_index = list(list_df[0].index)
    #list_index = ['France', 'US', 'Italy', 'Spain', 'Germany']

    new_df = pandas.DataFrame(columns = ['Country', 'Lat', 'Long', 'Date',
                                         'Cases', 'Death'])

    for a_country in tqdm(list_index, desc='Country loop', position=0):
        for a_date in list_col[:]:
            list_temp = [a_country, list_df[0].loc[a_country,'latitude'], list_df[0].loc[a_country, 'longitude']]
            list_temp.append(pandas.to_datetime(a_date))
            for df in list_df:
                list_temp.append(df.loc[a_country, a_date])
            new_df.loc[len(new_df)] = list_temp
       
    new_df.to_csv('DataMap.csv')
    
    new_df= new_df.dropna()
    print (new_df)
    return new_df

def Map1 (dfMap1):
    MapDataSet=gv.Dataset(dfMap1, kdims=['Country', 'Date'])

    MapCases = MapDataSet.to(gv.Points, ['Long', 'Lat'] ,['Country', 'Cases'], group='Number of cases')
    MapDeath = MapDataSet.to(gv.Points, ['Long', 'Lat'] ,['Country', 'Death'], group='Number of dead')
    
    MapCases = (gvts.CartoLight * MapCases).opts(
        opts.Points(width=1000, height=560, tools=['hover'], size=dim('Cases')*0.0001, xaxis=None, yaxis=None,
                    colorbar=True, toolbar='above', color='Cases', cmap='coolwarm'))
    
    MapDeath= (gvts.CartoLight * MapDeath).opts(
        opts.Points(width=1000, height=560, tools=['hover'], size=dim('Death')*0.001, xaxis=None, yaxis=None,
                    colorbar=True, toolbar='above', color='Death', cmap='coolwarm'))
    
    text = hv.Curve((0, 0)).opts(xaxis=None, yaxis=None) * hv.Text(0, 0, 'Source: John Hopkins University \nGraph: C.Houzard')
    
    MapOutput = (gv.Layout(MapCases + MapDeath + text)).cols(1)
    
    renderer = hv.renderer('bokeh')
    file_path = creation_folder (['/2.1 - Maps'])
    renderer.save(MapOutput, file_path[0] + 'MapCases-Death.html')

def df_Map2 (list_df):
    list_dfs = [[list_df[0], list_df[3], list_df[4]], 
                [list_df[1], list_df[5], list_df[6]]]
    list_return = []
    list_name = ['cases', 'death']
    for element, name in zip(list_dfs, list_name):
        combined_delta_df=element[0].loc[:,'geometry']
        date = list(element[0].columns)[-1]
        
        element[1][date]= element[1][date].apply(numpy.floor)
        element[2][date]= element[2][date].apply(numpy.floor)
    
        combined_delta_df = pandas.concat([combined_delta_df, element[0].iloc[:, -1:]], axis=1)
        combined_delta_df = combined_delta_df.rename (columns={date:f"Number {name}"})  
        
        combined_delta_df = pandas.concat([combined_delta_df, element[1].iloc[:, -1:]], axis=1)
        combined_delta_df = combined_delta_df.rename (columns={date:f"Delta {name}"})                           
                                          
        combined_delta_df = pandas.concat([combined_delta_df, element[2].iloc[:, -1:]], axis=1)
        combined_delta_df = combined_delta_df.rename (columns={date:f"Balance {name}"})
        
        #combined_delta_df[:,[f'Number {name}', f"Delta {name}", f"Delta {name}"]] = pandas.to_numeric( combined_delta_df[:,[f'Number {name}', f"Delta {name}", f"Delta {name}"]])
        
        list_return.append(combined_delta_df)
    return list_return

def Map2 (df_Map2_cases):
    print(df_Map2_cases)
    maxi = df_Map2_cases['Balance cases'].nlargest(2, keep='all')
    mini = df_Map2_cases['Balance cases'].nsmallest(2, keep='last')

    if max(mini[0]//mini[1], maxi[0]//maxi[1]) >=2:
        if -mini[1] > maxi[1]:
            val_lim = -1.1 * mini [1]
            print('mini ', val_lim)
        
        else:
            val_lim = 1.1 * maxi [1]
            print('maxi ', val_lim)
        
    DataSet = gv.Polygons(df_Map2_cases, vdims=[hv.Dimension('Balance cases', range=(-val_lim, +val_lim)), 'Delta cases', 'Number cases' ])
    FinalMap = DataSet.opts(width=1000, height=560, tools=['hover'], colorbar=True, cmap='coolwarm', 
                xaxis=None, yaxis=None, title='Evolution du nombre de cas')
    
    text = hv.Curve((0, 0)).opts(xaxis=None, yaxis=None) * hv.Text(0, 0, 'Source: John Hopkins University \nGraph: C.Houzard')

    MapOutput = (gv.Layout(FinalMap + text)).cols(1)

    renderer = gv.renderer('bokeh')
    file_path = creation_folder (['/2.1 - Maps'])
    renderer.save(MapOutput, file_path[0] + 'MapBalance.html')
    
#-- Creation DF --#
current = os.path.dirname(os.path.realpath(__file__))

#list_df, to_replace, Gpostion, Gpolygone = import_df_from_I()
list_df, to_replace, Gpostion, Gpolygone = import_df_from_xlsx(current)
save_df (list_df, to_replace, Gpostion, Gpolygone)

list_df= clean_up(list_df)
list_df = ajusted_values(list_df, to_replace) #list_df[0] to list_df[2]

delta_df11 = delta_df(list_df[0], 1)
delta_df11 = smoothed_fun (delta_df11, 2)
delta2_df11 = delta_df(delta_df11, 2)
list_df.extend([delta_df11, delta2_df11]) #list_df[3], list_df[4]

delta_df12 = delta_df(list_df[1], 1)
delta_df12 = smoothed_fun (delta_df12, 2)
delta2_df12 = delta_df(delta_df12, 2)
list_df.extend([delta_df12, delta2_df12]) #list_df[5], list_df[6]

frate = fatality_rate (list_df)
list_df.append(frate) #list_df[5]

grate = growth_rate (list_df[0])
grate2 = smoothed_fun (grate, 2)
list_df.append(grate2) #list_df[6]
list_df.append(grate)

list_df = append_geography(list_df, Gpostion, Gpolygone)

#-- Maps --#

dfMap1 = df_Map1 (list_df)
Map1(dfMap1)

df_Map2_cases, df_Map2_death = df_Map2 (list_df)
Map2 (df_Map2_cases)


