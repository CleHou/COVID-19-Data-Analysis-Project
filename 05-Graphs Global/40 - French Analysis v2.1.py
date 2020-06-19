#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  4 21:51:51 2020

@author: Clement
"""
import pandas
import os
import matplotlib.pyplot as plt
import matplotlib.image as image
#import matplotlib.ticker as ticker
from matplotlib import dates
import numpy
import datetime
import geopandas
import geoviews
import geoviews.tile_sources as gvts
#from geoviews import dim, opts
import holoviews as hv
import tqdm

def import_df_from_I ():
    df_main = pandas.read_csv('https://raw.githubusercontent.com/opencovid19-fr/data/master/dist/chiffres-cles.csv')
    #data_map = pandas.read_csv('https://github.com/etalab/covid19-dashboard/raw/master/data/donnees_carte_synthese_tricolore.csv')
    data_map=df_main
    france_shapefile = geopandas.read_file('https://www.data.gouv.fr/fr/datasets/r/eb36371a-761d-44a8-93ec-3d728bec17ce')
    
    return df_main, data_map, france_shapefile

def creation_folder (paths):
    current = os.path.dirname(os.path.realpath(__file__))
    list_directory = [os.path.normcase(current + directory) for directory in paths]
    
    for directory in list_directory:
        if os.path.exists(directory) == False:
            print('Directory created')
            os.makedirs(directory)
    list_return = [current + x + '/' for x in paths]      
    return list_return

def save_df (df_main, data_map, france_shapefile):
    file_path = ['/4.0 - Data']
    file_path = creation_folder(file_path)
    
    df_main.to_csv(os.path.normcase(file_path [0] + 'data_main.csv'), index=False)
    data_map.to_csv(os.path.normcase(file_path [0] + 'data_map.csv'), index=False)
    france_shapefile.to_file(os.path.normcase(file_path [0] + 'france_shapefile.geojson'), driver='GeoJSON')
    
    return print('Saved')

def import_df_from_xlsx (current):
    file_path = [current+'/4.0 - Data/']
    
    df_main = pandas.read_csv(os.path.normcase(file_path [0] + 'data_main.csv'))
    data_map = pandas.read_csv(os.path.normcase(file_path [0] + 'data_map.csv'))
    france_shapefile = geopandas.read_file(os.path.normcase(file_path [0] + 'france_shapefile.geojson'))
    
    return df_main, data_map, france_shapefile

def clean_up (df_main):
    df_sorted1 = df_main[(df_main.loc[:,'granularite']=='pays') & (df_main.loc[:,'source_type']=='ministere-sante')]
    df_sorted1 = df_sorted1.set_index('date')
    df_sorted1.loc['2020-04-28', 'cas_confirmes'] = 128390
    df_sorted1.index = pandas.to_datetime(df_sorted1.index, format='%Y-%m-%d')
    df_sorted1['deces_ehpad'] = df_sorted1['deces_ehpad'].fillna(method='ffill')
    df_sorted1['deces_ehpad'] = df_sorted1['deces_ehpad'].fillna(0)
    
    df_main, data_map, france_shapefile = import_df_from_xlsx(current)
    df_sorted2 = df_main[(df_main.loc[:,'granularite']=='departement') & (df_main.loc[:,'source_type']=='sante-publique-france-data')]
    df_sorted2.loc[:,'date'] = pandas.to_datetime(df_sorted2.loc[:,'date'], format='%Y-%m-%d')
    df_sorted2.loc[:,'maille_code'] = df_sorted2.loc[:,'maille_code'].apply(lambda dpt: dpt[4:])
    df_sorted2.set_index(['date', 'maille_code'], inplace=True)

    df_global = pandas.DataFrame(index=df_sorted1.index, columns=['Cases', 'Death', 'ICU', 'Hospitals'])
    df_global.loc[:,'Cases'] = df_sorted1.loc[:,'cas_confirmes']
    df_global.loc[:,'Death'] = df_sorted1.loc[:,'deces'] + df_sorted1.loc[:,'deces_ehpad']
    df_global.loc[:,'ICU']=df_sorted1.loc[:,'reanimation']
    df_global.loc[:,'Hospitals']=df_sorted1.loc[:,'hospitalises']
    print(df_global.iloc[-8:])
    
    df_local = pandas.DataFrame(index=df_sorted2.index, columns=['Death', 'ICU', 'Hospitalized'])
    df_local.loc[:,'Death']=df_sorted2.loc[:,'deces']
    df_local.loc[:,'ICU']=df_sorted2.loc[:,'reanimation']
    df_local.loc[:,'Hospitalized']=df_sorted2.loc[:,'hospitalises']
    df_local.loc[:,'Département']=df_sorted2.loc[:,'maille_nom']
    
    return df_global, df_local

def smoothed_fun_2 (df, nb_val): #Moving average smoothing on the 2 previous values and 2 values after
    list_date = list(df.columns)
    df_smoothed = df.iloc[:, :nb_val]
    
    for k in range(nb_val, len(list_date)-nb_val):
        df_smoothed [list_date[k]] = 0

        for j in range(-nb_val, nb_val+1):
            df_smoothed [list_date[k]] += df[list_date[k-j]] /(2*nb_val+1)                  

    return df_smoothed


def delta_df (df_global):
    delta_df=pandas.DataFrame(index = df_global.index, columns=['dC/dt', 'dD/dt'])
    
    delta_df.loc[:]=df_global.loc[:, ['Cases', 'Death']].diff()
    delta_df=delta_df.rolling(3).mean()
    df_global = pandas.concat([df_global, delta_df], axis=1)
        
    return df_global

def plot (df_instant, date_ini):
    long_date = df_instant.index[-1].strftime("%d %B, %Y")
    month = df_instant.index[-1].strftime("%m - %B")
    short_date = df_instant.index[-1].strftime("%d-%m-%Y")
    
    new_df = df_instant.loc[date_ini:]
    
    df_tile = pandas.DataFrame(index=['ICU', 'Hospitals', 'dC/dt', 'dD/dt'],
                                 data=[['Nombre de personnes en réanimation'], ['Nombres de personnes hopitalisées'],['Nombre de cas journaliers'],['Nombre de morts journaliers']],
                                 columns=['title'])
    
    para_to_plot = ['ICU', 'Hospitals', 'dC/dt', 'dD/dt']
    fig, axs = plt.subplots(2,2, figsize=(15,15), num=f'Evolution of prediction on {short_date}')                             
    
    for axes, para in zip(numpy.ravel(axs), para_to_plot):
        axes.plot(new_df.index, new_df.loc[:,para], label=df_tile.loc[para, 'title'], linewidth=0.75, marker='2')
        axes.set_title(df_tile.loc[para, 'title'])
        axes.set_ylabel(para)
        axes.set_xlabel('Date')
        axes.grid()
        axes.xaxis.set_major_formatter(dates.DateFormatter('%d/%m/%Y'))
        axes.xaxis.set_major_locator(dates.DayLocator(interval=5))
        
    fig.autofmt_xdate()
    handles, labels = axs[0][0].get_legend_handles_labels()
    #fig.legend(handles, labels, loc="center right", borderaxespad=0)
    #plt.subplots_adjust(right=0.90)
    fig.suptitle(f"French data on\n{long_date}", size=16)
    fig.autofmt_xdate()
    
    logo = image.imread('https://raw.githubusercontent.com/CleHou/COVID-19-Data-Analysis-Project/master/99-Other/99.1-Logo/Logo2_200px.png')
    fig.figimage(logo, 30, 20, zorder=3)
    
    fig.text(0.83, 0.05, 'Data source: Santé Publique France \nAnalysis: C.Houzard', fontsize=8)
    
    file_path = creation_folder ([f'/4.1 - Graph/{month}', f'/4.3 - Preview/{month}'])
    fig.savefig(file_path[0] + f'French_Data_{short_date}.pdf', dpi=200)
    fig.savefig(file_path[1] + f'Preview_French_Data_{short_date}.png', format='png', dpi=300)

def to_print (df_cumulated, df_instant):
    df_print = pandas.concat([df_cumulated, df_instant], axis=1)
    print(df_print.iloc[-5:])
    
def creation_df_map (data_map, france_shapefile, df_local):
    data_map.loc[:,'extract_date'] = pandas.to_datetime(data_map.loc[:,'extract_date'], format='%Y-%m-%d')
    data_map = data_map.set_index(['extract_date', 'departement'])
    
    missing_index = df_local.loc[data_map.index[-1][0]:].index
    last_date = data_map.index[-1][0]
    for index in missing_index:
        data_map.loc[index,:] = data_map.loc[(last_date, index[1]),:]
    
    france_shapefile = france_shapefile.set_index('code_insee')
    france_shapefile = france_shapefile.rename(index={'69D': '69'})
    
    france = pandas.DataFrame(index=data_map.index, columns=['geometry'])
    
    for date, dpt in tqdm.tqdm(france.index):
        france.loc[(date, dpt)] = france_shapefile.loc[dpt]
    
    data_map = pandas.concat([data_map, df_local, france], axis=1)    

    data_map = geopandas.GeoDataFrame(data_map)
   
    return data_map

def maping (data_map):
    data_map = data_map.loc[[data_map.index[-1][0]]]
    month = data_map.index[-1][0].strftime("%m - %B")
    short_date = data_map.index[-1][0].strftime("%d-%m-%Y")
    
    DataSet = geoviews.Polygons(data_map, vdims=['indic_synthese', 'Département', 'ICU', 'Death', 'Hospitalized'])
    explicit_mapping = {'vert': '#91cf60', 'rouge': '#d7191c', 'orange': '#fdae61'}
    
    FinalMap = DataSet.opts(width=1000, height=560, tools=['hover'], cmap=explicit_mapping,
                xaxis=None, yaxis=None, title=f'Carte du {data_map.index[-1][0].strftime("%d-%m-%Y")}')
    
    FinalMap = FinalMap*gvts.CartoLight
    text = hv.Curve((0, 0)).opts(xaxis=None, yaxis=None) * hv.Text(0, 0, 'Source: Santé Publique France \nGraph: C.Houzard')

    MapOutput = (geoviews.Layout(FinalMap + text)).cols(1)

    renderer = geoviews.renderer('bokeh')
    file_path = creation_folder (['/4.2 - Maps', f'/4.3 - Preview/{month}'])
    
    renderer.save(FinalMap, file_path[1] + f'MapFrance_{short_date}.png')
    renderer.save(MapOutput, file_path[0] + 'MapFrance.html')

def check_date (df_main, data_map, france_shapefile):
    today_date = datetime.date.today()
    last_date =datetime.datetime.strptime(df_main.loc[:,'date'].iloc[-1], "%Y-%m-%d").date()
    
    delta = (today_date-last_date).days
    
    if delta > 1 :
        short_date = last_date.strftime("%Y-%m-%d")
        print('\a')
        print(f'Data were last updated {delta} days ago, on {short_date}')
        conti = input('Do you wish to update the data? [y/n]?')
        
        if conti == 'y':
            df_main, data_map, france_shapefile = import_df_from_I()
            print('Data updated')
            
    return df_main, data_map, france_shapefile 
    
current = os.path.dirname(os.path.realpath(__file__))

df_main, data_map, france_shapefile = import_df_from_I()
#df_main, data_map, france_shapefile = import_df_from_xlsx(current)

df_main, data_map, france_shapefile = check_date (df_main, data_map, france_shapefile)
save_df (df_main, data_map, france_shapefile)

#france_shapefile.plot()
df_global, df_local = clean_up (df_main)
df_global = delta_df(df_global)

date_ini = pandas.to_datetime('2020-03-15', format='%Y-%m-%d')
plot(df_global, date_ini)

#df_map = creation_df_map (data_map, france_shapefile, df_local)
#maping (df_map)

