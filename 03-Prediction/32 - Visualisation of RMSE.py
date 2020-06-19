#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 25 13:20:57 2020

@author: Clement
"""


import pandas
import os
import numpy
import matplotlib.pyplot as plt
from matplotlib import dates
import scipy
import datetime
import tqdm
from sklearn.metrics import r2_score
from matplotlib import cm
#from matplotlib.ticker import LinearLocator, FormatStrFormatter
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.image as image

def import_df_from_I ():
    partial_link = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_'
    df1 = pandas.read_csv(partial_link+ 'confirmed_global.csv')
    df2 = pandas.read_csv(partial_link+ 'deaths_global.csv')  
    df3 = pandas.read_csv(partial_link+ 'recovered_global.csv')
    to_replace = pandas.read_csv('https://github.com/CleHou/COVID-19-Data-Analysis-Project/raw/master/01-Graph/France_data.csv')
    
    return [df1, df2, df3], to_replace

def creation_folder (paths):
    current = os.path.dirname(os.path.realpath(__file__))
    list_directory = [os.path.normcase(current + directory) for directory in paths]
    
    for directory in list_directory:
        if os.path.exists(directory) == False:
            print('Directory created')
            os.makedirs(directory)
    list_return = [current + x + '/' for x in paths]      
    return list_return

def save_df (list_df, to_replace):
    file_path = ['/3.0 - Data']
    file_path = creation_folder(file_path)
    
    df1, df2, df3 = list_df
    df1.to_csv(os.path.normcase(file_path [0] + 'confirmed.csv'), index=False)
    df2.to_csv(os.path.normcase(file_path [0] + 'death.csv'    ), index=False)
    df3.to_csv(os.path.normcase(file_path [0] + 'recovered.csv'), index=False)
    to_replace.to_csv(os.path.normcase(file_path [0] + 'Revised_France_Data.csv'), index=False, index_label="Date")
    
    return print('Saved')

def import_df_from_xlsx (current):
    file_path = [current+'/3.0 - Data/']
    
    df1 = pandas.read_csv(os.path.normcase(file_path [0] + 'confirmed.csv'))
    df2 = pandas.read_csv(os.path.normcase(file_path [0] + 'death.csv')  )
    df3 = pandas.read_csv(os.path.normcase(file_path [0] + 'recovered.csv'))
    to_replace = pandas.read_csv(os.path.normcase(file_path [0] + 'Revised_France_Data.csv'))
    
    return [df1, df2, df3], to_replace

def clean_up (list_df):
    list_return = []
    for a_df in list_df:
        a_df = a_df.drop(['Lat', 'Long'], axis=1)
        a_df = a_df.groupby("Country/Region").sum()
        a_df.columns = pandas.to_datetime(a_df.columns)
        a_df.loc['World'] = a_df.sum()
        
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


def delta_df (df):
    list_date = list(df.columns)
    delta_df=df.iloc[:,:1]

    for k in range(len(list_date)-1):
        delta_df.loc[:, list_date[k+1]] = df.loc[:,list_date[k+1]] - df.loc[:,list_date[k]]
        
    return delta_df

def reg_log (t, a,b,c):
    y = a/(1+numpy.exp(-(b+c*t)))
    
    return y

def RMSE_fun (para, data, list_t): 
    RSS = 0
    for k in range(len(list_t)):
        y_mod = reg_log(list_t[k], para[0], para[1], para[2])
        y = data[k]
        RSS += (y - y_mod)**2
        
    MSE = RSS / len(list_t)
    RMSE = numpy.sqrt(MSE)
    
    return RMSE

def mini_RMSE (data, list_t, val_ini):
    #result= scipy.optimize.least_squares (RMSE_fun, x0=numpy.array([150000, -4, 0.1]),args=(data, list_t) )
    result= scipy.optimize.minimize (RMSE_fun, x0=val_ini, args=(data, list_t) )
 
    a,b,c = result.x
    
    y_mod = reg_log (list_t, a,b,c)
    R2 = (r2_score(data, y_mod))
    #print(R2)
    return a,b,c, R2
        
        
def plot_3D (list_val, list_1, list_2, list_short, country, order):
    cmaps = ['RdGy', 'bwr','RdBu',
            'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm',  'seismic']
    
    Y, X = numpy.meshgrid(list_2, list_1)
    
    fig1 = plt.figure(country, figsize=(15,15))
    ax1 = fig1.gca(projection='3d')
    
    for k in range(len(list_short)):
        surf=ax1.plot_surface(X, Y,  numpy.array(list_val[k]),  cmap=plt.get_cmap(cmaps[k]), antialiased=False) #(X, Y)=(split, leaf)
        
    fig1.colorbar(surf, shrink=0.5, aspect=5)
        
    ax1.set_xlabel(order[2])
    ax1.set_ylabel(order[1])
    ax1.set_zlabel('RMSE')
    Title = f'RMSE at {order[0]}={list_short[-1]} fixed'
        
    plt.title(Title)
    logo = image.imread('https://raw.githubusercontent.com/CleHou/COVID-19-Data-Analysis-Project/master/99-Other/99.1-Logo/Logo2_200px.png')
    fig1.figimage(logo, 30, 20, zorder=3)

def create_values_A (list_df, country, list_a, list_b, list_c):
    data = numpy.array(list_df[0].loc[country])
    list_t = numpy.arange(1, len(dates.date2num(list_df[0].columns))+1, 1)
    
    list_val = []
    k=1
    for a in list_a:
        list_val_country = []
        for c in tqdm.tqdm(list_c, desc=f"c: {k}/" + str(len(list_a))):
            list_temp=[]
            for b in list_b: 
                list_temp.append(RMSE_fun([a,b,c], data, list_t))
            list_val_country.append(list_temp)
        list_val.append(list_val_country)
        k+=1
        
    return list_val, (r'$\alpha$', r'$\beta$', r'$\gamma$')

def create_values_B (list_df, country, list_a, list_b, list_c):
    data = numpy.array(list_df[0].loc[country])
    list_t = numpy.arange(1, len(dates.date2num(list_df[0].columns))+1, 1)
    
    list_val = []
    k=1
    for b in list_b:
        list_val_country = []
        for a in tqdm.tqdm(list_a, desc=f"a: {k}/" + str(len(list_b))):
            list_temp=[]
            for c in list_c: 
                list_temp.append(RMSE_fun([a,b,c], data, list_t))
            list_val_country.append(list_temp)
        list_val.append(list_val_country)
        k+=1
        
    return list_val, (r'$\beta$', r'$\gamma$', r'$\alpha$')

def create_values_C (list_df, country, list_a, list_b, list_c):
    data = numpy.array(list_df[0].loc[country])
    list_t = numpy.arange(1, len(dates.date2num(list_df[0].columns))+1, 1)
    
    list_val = []
    k=1
    for c in list_c:
        list_val_country = []
        for b in tqdm.tqdm(list_b, desc=f"b: {k}/" + str(len(list_c))):
            list_temp=[]
            for a in list_a: 
                list_temp.append(RMSE_fun([a,b,c], data, list_t))
            list_val_country.append(list_temp)
        list_val.append(list_val_country)
        k+=1
        
    return list_val, (r'$\gamma$', r'$\beta$', r'$\alpha$')
    
    

#Creation des DB
current = os.path.dirname(os.path.realpath(__file__))

#list_df, to_replace = import_df_from_I()
list_df, to_replace = import_df_from_xlsx(current)
save_df (list_df, to_replace)

list_df= clean_up(list_df)
list_df = ajusted_values(list_df, to_replace) #list_df[0] to list_df[2]

list_df.append(delta_df (list_df[0])) #list_df[3]

list_df[0] = smoothed_fun_2(list_df[0], 2)
list_df[3] = smoothed_fun_2(list_df[3], 2)
list_country = ['France'
                #, 'US'
                #, 'Italy'
                #, 'Germany'
                ]
                
country = 'France'

list_a = numpy.linspace(10000, 250000, 200)
#list_a = [110000, 122260]
list_b = numpy.linspace(-14, -5, 200)
#list_b = [-11]
#list_c=numpy.linspace(0.05, 0.9, 200)
list_c = [0.15]

list_val, ordre = create_values_C (list_df, country, list_a, list_b, list_c)
plot_3D (list_val, list_a, list_b, list_c, country, ordre) #Dernière liste = plus petite


#print(data, '\n')



