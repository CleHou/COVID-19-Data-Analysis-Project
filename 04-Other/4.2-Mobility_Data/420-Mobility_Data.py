#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 10:00:15 2020

@author: Clement
"""

import pandas
import matplotlib.pyplot as plt
from matplotlib import dates
import numpy
import matplotlib.lines as mlines
import os

def import_df_from_I ():
    partial_link = 'https://covid19-static.cdn-apple.com/covid19-mobility-data/2006HotfixDev7/v1/en-us/applemobilitytrends-2020-04-16.csv'
    df = pandas.read_csv(partial_link)
    df.to_csv(os.path.normcase('applemobilitytrends.csv'), index=False)

    return df

def simport_df_from_csv ( ):
    df = pandas.read_csv('applemobilitytrends.csv')
    return df

def csv_to_df (df):
    df = df.loc[df['geo_type']== 'country/region']

    df_D = df.loc[df['transportation_type'] == 'driving']
    df_D = df_D.drop(columns=['transportation_type', 'geo_type'])
    df_D = df_D.set_index('region')
    df_D.columns = pandas.to_datetime(df_D.columns)
    df_D = df_D-100
    
    df_W = df.loc[df['transportation_type'] == 'walking']
    df_W = df_W.drop(columns=['transportation_type', 'geo_type'])
    df_W = df_W.set_index('region')
    df_W.columns = pandas.to_datetime(df_W.columns)
    df_W = df_W-100
    
    df_T = df.loc[df['transportation_type'] == 'transit']
    df_T = df_T.drop(columns=['transportation_type', 'geo_type'])
    df_T = df_T.set_index('region')
    df_T.columns = pandas.to_datetime(df_T.columns)
    df_T = df_T-100
    
    return df_D, df_T

def smoothed_fun_2 (df, nb_val): #Moving average smoothing on the 2 previous values and 2 values after
    list_date = list(df.columns.values)
    df_smoothed = df.iloc[:, :nb_val]
    for k in range(nb_val, len(list_date)-nb_val):
        df_smoothed [list_date[k]] = 0

        for j in range(-nb_val, nb_val+1):
            df_smoothed [list_date[k]] += df[list_date[k-j]] /(2*nb_val+1)                  

    return df_smoothed

def plot (list_df, list_graph, list_country, colors, date_confinement):
    fig, axs = plt.subplots(1,2, figsize=(15,15), num='Evolution déplacement')
    
    k=0
    
    for a_df in list_df:
        j=0
        for a_country in list_country:
            axs[k].grid(True)
            list_date = list(a_df.columns.values)
            axs[k].plot(list_date, a_df.loc[a_country], color=colors[j], marker=None, markersize=5, linewidth=0.75, label = a_country)
            axs[k].axhline(0, axs[k].get_xlim()[0], axs[k].get_xlim()[1], linestyle='--', color='red', linewidth=0.75)
            axs[k].axvline(x=date_confinement[j], linestyle='--', color=colors[j], linewidth=0.75)
            axs[k].set_xlabel('Date')
            axs[k].set_ylabel(f'Evolution (%)')
            axs[k].set_title (f'Deplacement {list_graph[k]}')
            axs[k].xaxis.set_major_formatter(dates.DateFormatter('%d/%m/%Y'))
            axs[k].xaxis.set_major_locator(dates.DayLocator(interval=7))
            
            j+=1
            
        k+=1
        
    fig.autofmt_xdate()  
    
    handles, labels = axs[0].get_legend_handles_labels()
    handles.append(mlines.Line2D([], [], color='#1C1C1C', linestyle='--', linewidth=0.75))
    labels.append('Début confinement')
    
    fig.legend(handles, labels, loc="center right", borderaxespad=0)
    fig.subplots_adjust(right=0.87)
    fig.suptitle(f'Evolution relative des déplacements dans le monde \n(avant confinement=0)', fontsize=16)
    fig.text(0.85, 0.05, 'Source: apple.com/covid19/mobility \nGraph: C.Houzard', fontsize=8)
    
    fig.savefig('Evolution deplacement.pdf', format='pdf')    
    

colors = ['#3E86E8', '#D45050', '#58C446', '#9A46C4', '#F0D735', '#6BB482', '#013BD2', '#F08328', '#04979C' ,"#00000"]
list_country = ['France', 'United States', 'Italy', 'Germany']
date_confinement = numpy.array(['2020-03-17', 'NaT', '2020-03-10', '2020-03-22'], dtype='datetime64')
print(date_confinement)

df = import_df_from_I()
#sdf = import_df_from_csv()

list_df = csv_to_df(df)

list_df = [smoothed_fun_2(df, 3) for df in list_df]
list_df = [df.iloc[:,9:] for df in list_df] 

list_graph = ['en voiture', 'en transport']

plot (list_df, list_graph, list_country, colors, date_confinement)
        
