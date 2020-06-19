#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 14 07:43:50 2020

@author: Clement
v1.0
"""

import pandas
from matplotlib import dates
import matplotlib.pyplot as plt
import numpy
from sklearn import linear_model
from sklearn.metrics import r2_score
import os
import matplotlib.lines as mlines
import matplotlib.backends.backend_pdf
import matplotlib.image as image
import tqdm
import datetime

def import_df_from_I ():
    partial_link = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_'
    df1 = pandas.read_csv(partial_link+ 'confirmed_global.csv')
    df2 = pandas.read_csv(partial_link+ 'deaths_global.csv')  
    to_replace = pandas.read_csv('https://github.com/CleHou/COVID-19-Data-Analysis-Project/raw/master/01-Graph/France_data.csv')
    df_main = pandas.read_csv('https://raw.githubusercontent.com/opencovid19-fr/data/master/dist/chiffres-cles.csv')
    df_case_us = pandas.read_csv('https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv')
    df_death_us = pandas.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv')
    
    return [df1, df2], to_replace, df_main, df_case_us, df_death_us

def creation_folder (paths):
    current = os.path.dirname(os.path.realpath(__file__))
    list_directory = [os.path.normcase(current + directory) for directory in paths]
    
    for directory in list_directory:
        if os.path.exists(directory) == False:
            print('Directory created')
            os.makedirs(directory)
    list_return = [current + x + '/' for x in paths]      
    return list_return

def save_df (list_df, to_replace, df_main, df_case_us, df_death_us):
    file_path = ['/5.0 - Data']
    file_path = creation_folder(file_path)
    
    df1, df2= list_df
    df1.to_csv(os.path.normcase(file_path [0] + 'confirmed.csv'), index=False)
    df2.to_csv(os.path.normcase(file_path [0] + 'death.csv'    ), index=False)
    to_replace.to_csv(os.path.normcase(file_path [0] + 'Revised_France_Data.csv'), index=False, index_label="Date")
    df_main.to_csv(os.path.normcase(file_path [0] + 'France_Data.csv'), index=False, index_label="Date")
    df_case_us.to_csv(os.path.normcase(file_path [0] + 'cases_us.csv'), index=False)
    df_death_us.to_csv(os.path.normcase(file_path [0] + 'death_us.csv'), index=False)
    
    return print('Saved')

def import_df_from_xlsx (current):
    file_path = [current+'/5.0 - Data/']
    
    df1 = pandas.read_csv(os.path.normcase(file_path [0] + 'confirmed.csv'))
    df2 = pandas.read_csv(os.path.normcase(file_path [0] + 'death.csv')  )
    to_replace = pandas.read_csv(os.path.normcase(file_path [0] + 'Revised_France_Data.csv'))
    df_main = pandas.read_csv(os.path.normcase(file_path [0] + 'France_Data.csv'))
    df_case_us = pandas.read_csv(os.path.normcase(file_path [0] + 'cases_us.csv'))
    df_death_us = pandas.read_csv(os.path.normcase(file_path [0] + 'death_us.csv'))
    
    return [df1, df2], to_replace, df_main, df_case_us, df_death_us

def clean_up_1 (list_df):
    list_return = []
    for a_df in list_df:
        a_df = a_df.drop(['Lat', 'Long'], axis=1)
        a_df = a_df.groupby("Country/Region").sum()
        a_df.columns = pandas.to_datetime(a_df.columns)
        a_df.loc['World'] = a_df.sum()
        a_df = a_df.stack().to_frame()
        list_return.append(a_df)
        
    list_return[0] = list_return[0].rename(columns={0: 'Cases'})
    list_return[1] = list_return[1].rename(columns={0: 'Death'})
    
    df_world = pandas.concat([list_return[0], list_return[1]], axis=1)
    df_world = df_world.rename_axis(index=['countries', 'date'])
    
    list_df[0].loc['World'] = list_df[0].sum()
    return df_world

def clean_up_2 (df_main):
    df_sorted2 = df_main[(df_main.loc[:,'granularite']=='region') & (df_main.loc[:,'source_type']=='opencovid19-fr')]
    df_sorted2.loc[:,'date'] = pandas.to_datetime(df_sorted2.loc[:,'date'], format='%Y-%m-%d')
    df_sorted2 = df_sorted2.set_index(['maille_nom', 'date']).sort_index()
    
    df_local = pandas.DataFrame(index=df_sorted2.index, columns=['Death', 'ICU', 'Hospitalized'])
    df_local.loc[:,'Death']=df_sorted2.loc[:,'deces']
    df_local.loc[:,'ICU']=df_sorted2.loc[:,'reanimation']
    df_local.loc[:,'Hospitalized']=df_sorted2.loc[:,'hospitalises']
    df_local = df_local.rename_axis(index=['regions', 'date'])
    
    return df_local

def clean_up_3 (df_cases_us, df_death_us, smooth_val):
    list_df = [df_cases_us, df_death_us]
    list_return1 = []
    list_return2 = []
    list_df[1] = list_df[1].drop(columns=['Population'])
    list_name = ['Cases', 'Delta_Cases', 'Death', 'Delta_Death', ]
    
    for a_df, name in zip(list_df, list_name):
        a_df = a_df.groupby('Province_State').sum()
        a_df = a_df.drop(columns=['UID', 'code3', 'FIPS', 'Lat', 'Long_'])
        a_df.columns = pandas.to_datetime(a_df.columns)
        delta_df=a_df.diff(axis=1)
        list_return1.extend([a_df, delta_df]) 
    
    for a_df, name in zip(list_return1, list_name):
        a_df = a_df.rolling(window=smooth_val, center=True, axis=1).mean()
        a_df = pandas.DataFrame(a_df.stack())
        a_df = a_df.rename(columns={0:name})
        a_df.index = a_df.index.set_names(['States', 'Date'])
        list_return2.append(a_df)
        
    global_df =  list_return2[0] 
    for a_df in list_return2[1:]:
        global_df = global_df.join(a_df, how='outer')
    
    return global_df

def select_countries (df_world, pctg):
    last_date = df_world.index[-1][1]
    cut_off_val = df_world.loc[('World', last_date), 'Cases'] * pctg
    print(cut_off_val)
    list_countries = df_world.index.levels[0]
    
    df_val = pandas.DataFrame()
   
    for a_country in list_countries:
        if df_world.loc[(a_country, last_date), 'Cases'] < cut_off_val:
            df_world = df_world.drop(index=a_country)
    """        
        else:
            df_val.loc[a_country, 'Cases'] = df_world.loc[(a_country, last_date), 'Cases']
          
    df_world.index = df_world.index.remove_unused_levels()
    df_val = df_val.sort_values(by='Cases', ascending=False)   
    df_val = df_val.drop(index='World')
    print(df_val)
    """
    return df_world

def sort_countries(df, idx1, idx2, para, drop):
    grp_by_country = df.groupby(idx1)
    # for each group, aggregate by sorting by data and taking the last row (latest date)
    latest_per_grp = grp_by_country.agg(lambda x: x.sort_values(by=idx2).iloc[-1])
    # sort again by cases
    sorted_by_cases = latest_per_grp.sort_values(by=para, ascending=False)
    
    if drop[0]:
        sorted_by_cases = sorted_by_cases.drop(index=drop[1])
    
    return sorted_by_cases.index

 
def num_countries (df_world):
    list_len = []
    list_pctge = numpy.logspace(-3, -1, 30)
    for a_pctge in tqdm.tqdm(list_pctge):
        df_world = select_countries (df_world, a_pctge)
        list_len.append(len(df_world.index.levels[0]))
    
    plt.figure('Test pctge')
    plt.plot(list_pctge, list_len, linewidth=0.75, marker='2')
    plt.xlabel('% of total world cases')
    plt.ylabel('Number of countries matching criteria')
    plt.grid()
    plt.show()       

def ajusted_values(df_world, to_replace):
    to_replace = to_replace.set_index('Date')
    to_replace.loc[:,'Cases'] = pandas.to_numeric(to_replace.loc[:,'Cases'], downcast='float')
    to_replace.index = pandas.to_datetime(to_replace.index)
   
    for index in to_replace.index:
        df_world.loc[('France', index),'Cases'] = to_replace.loc[index,'Cases']

    return df_world

def delta_df_1 (df_world):
    delta_df = df_world.groupby(level=0).diff()
    delta_df=delta_df.rename(columns={'Cases': 'Delta_Cases', 'Death':'Delta_Death'})
    df_world = pandas.concat([df_world, delta_df], axis=1)
    
    return df_world

def delta_df_2 (df_local):
    delta_df = df_local.loc[:,'Death'].groupby(level=0).diff()
    df_local.loc[:,'Delta_Death'] = delta_df
    
    return df_local

def smoothed_fun_2 (df, win_size): #Moving average smoothing on the 2 previous values and 2 values after

    df_smoothed = df.groupby(level=0).rolling(window=win_size, center=True).mean()
    df_smoothed = df_smoothed.reset_index(level=0, drop=True)
    
    return df_smoothed

    
def legend (list_country, colors):
    list_zip = zip(list_country, colors)
    handles, labels = [], []
    for element in list_zip:
        handles.append(mlines.Line2D([], [], color=element[1], marker = '2', linewidth=0.75))
        labels.append(element[0])
        
    return handles, labels

    
def chunks_list (list_countries, val):
    tot_len = len(list_countries)
    list_chunks = []
  
    for j in range(tot_len//val):
        list_chunks.append([list_countries[k+val*j] for k in range(val)])

    if val*tot_len//val < tot_len:     
        list_chunks.append([list_countries[k] for k in range(tot_len//val *val, tot_len)])
        
    return list_chunks

def plot_everyone (df, region_to_plot, para_to_plot, lim_date, title_graph, colors, intv, titre_pdf, titre_preview, tqdm_name, logo):
    long_date = lim_date[1].strftime("%d %B, %Y")
    
    num_pages = len(region_to_plot)
    pdf = matplotlib.backends.backend_pdf.PdfPages(os.path.normcase(titre_pdf))
    
    preview=True
   
    for a_chunk, page in tqdm.tqdm(list(zip(region_to_plot, range(num_pages+1))), desc=tqdm_name):
        sub_title = title(a_chunk)
        fig, axs = plt.subplots(2, 2, num=f'{titre_pdf} {page+1}/{num_pages}', figsize=(11.7, 8.3))
      
        for an_axs, a_para in zip(numpy.ravel(axs), para_to_plot):
            scd_axes, scd_axes_country = axes_or_not (df, a_chunk, a_para)
                
            for a_country, a_color in zip(a_chunk, colors):
                a_df = df.loc[(a_country, lim_date[0]): (a_country, lim_date[1]), a_para[0]]
                a_df.index = a_df.index.remove_unused_levels()
                list_date = a_df.index.levels[1]

                if scd_axes and a_country == scd_axes_country:
                    axs2 = an_axs.twinx()
                    axs2.plot(list_date, a_df, linewidth=0.75, label = a_country, color = a_color)
                    axs2.set_ylabel(f'{a_para[0]} ({a_country})', color=a_color)
                    axs2.tick_params(axis='y', labelcolor=a_color)
                        
                else:
                    an_axs.plot(list_date, a_df, linewidth=0.75, color = a_color)
                    
            an_axs.xaxis.set_major_formatter(dates.DateFormatter('%d/%m/%y'))
            an_axs.xaxis.set_major_locator(dates.DayLocator(interval=intv))
            an_axs.set_xlabel('Date')
            an_axs.set_ylabel(a_para[0])
            an_axs.set_title (title_graph.loc[a_para[0], 'Title'])
            an_axs.grid()
            
            if a_para[1] and df.loc[(a_chunk[0], lim_date[-1]), a_para[0]]>10:
                an_axs.semilogy()
                an_axs.set_ylabel(f'{a_para[0]} (log scale)')
                
        handles, labels = legend (a_chunk, colors)
        
        fig.autofmt_xdate()
        fig.suptitle(f'Covid-19 situation on {long_date}\n{sub_title}', fontsize=16)
        fig.legend(handles, labels, loc="center right")
        fig.subplots_adjust(right=0.85)
        fig.figimage(logo, 30, 20, zorder=3)
        fig.text(0.83, 0.05, f'Source: John Hopkins University \nGraph: C.Houzard\nPage {page+1}/{num_pages}', fontsize=8)
        #plt.tight_layout()
        pdf.savefig(fig, dpi=200)
        
        if preview:
            fig.savefig(os.path.normcase(titre_preview), format='png', dpi=300)
            preview=False
            #fig.savefig(os.path.normcase(titre_preview + a_chunk[0]+'.png'), format='png', dpi=300)
        plt.close(fig)
            
    pdf.close()
                
def axes_or_not (df_world, a_chunk, a_para):
    scd_axes = False
    scd_axes_country = a_chunk[0]

    if len(a_chunk)>1:
        val1 = df_world.loc[(a_chunk[0], lim_date[1]), a_para[0]]
        val2 = df_world.loc[(a_chunk[1], lim_date[1]), a_para[0]]
        
        if val1 > 5*val2:
                scd_axes=True
                
    return scd_axes, scd_axes_country

def title (a_chunk):
    title = a_chunk[0]
    
    if len(a_chunk)>1:
        for a_country in a_chunk:
            title += f', {a_chunk}'
        
    return title
               
def check_date (list_df, to_replace, df_main, df_case_us, df_death_us):
    today_date = datetime.date.today()
    last_date =datetime.datetime.strptime(list_df[0].columns[-1], "%m/%d/%y").date()
    
    delta = (today_date-last_date).days
    
    if delta > 1 :
        short_date = last_date.strftime("%Y-%m-%d")
        print('\a')
        print(f'Data were last updated {delta} days ago, on {short_date}')
        conti = input('Do you wish to update the data? [y/n]?')
        
        if conti == 'y':
            list_df, to_replace, df_main, df_case_us, df_death_us = import_df_from_I()
            print('Data updated')
            
    return list_df, to_replace, df_main, df_case_us, df_death_us
    

#Creation des DB
current = os.path.dirname(os.path.realpath(__file__))

list_df, to_replace, df_main, df_case_us, df_death_us = import_df_from_I()
#list_df, to_replace, df_main, df_case_us, df_death_us = import_df_from_xlsx(current)

list_df, to_replace, df_main, df_case_us, df_death_us = check_date (list_df, to_replace, df_main, df_case_us, df_death_us)
save_df (list_df, to_replace, df_main, df_case_us, df_death_us)

colors = ['#3E86E8', '#D45050', '#58C446', '#9A46C4', '#F0D735', '#6BB482', '#013BD2', '#F08328', '#04979C' ,"#00000"]
logo = image.imread('https://raw.githubusercontent.com/CleHou/COVID-19-Data-Analysis-Project/master/99-Other/99.1-Logo/Logo2_200px.png')

#---- World ----#
df_world= clean_up_1(list_df)
df_world = ajusted_values(df_world, to_replace)
df_world = delta_df_1(df_world)
#num_countries (df_world)
df_world = select_countries (df_world, 0.005)
list_countries = sort_countries(df_world, 'countries', 'date', 'Cases', (True, 'World'))
df_world_smoothed = smoothed_fun_2(df_world, 7)
list_chunks1=chunks_list(list_countries, 1)

para_to_plot = [('Cases', True), ('Delta_Cases', False), ('Death', True), ('Delta_Death', False)]

start_date=pandas.to_datetime('2020-03-15', format='%Y-%m-%d')
end_date =df_world_smoothed.index.levels[1][-4]

lim_date = [start_date, end_date]

title_graph = pandas.DataFrame(columns=['Title'], 
                               index=['Cases', 'Death', 'Delta_Cases', 'Delta_Death'],
                               data = ['Number of cases', 'Number of dead', 'Daily number of cases', 'Daily number of death'])

intv=10

month = lim_date[1].strftime("%m - %B")
short_date = lim_date[1].strftime("%d-%m-%Y")
file_paths = creation_folder ([f'/5.1 - Graph World/{month}', f'/5.4 - Preview/{month}'])
pdf_name = file_paths[0] + f'All_Countries_{short_date}.pdf'
preview_name = file_paths[1] + f'All_Countries_{short_date}_Preview.png'
#preview_name = file_paths[1] + f'All_Countries_{short_date}_Preview_'
tqdm_name = 'World'

plot_everyone (df_world_smoothed, list_chunks1, para_to_plot, lim_date, title_graph, colors, intv, pdf_name, preview_name, tqdm_name, logo)

#---- Region ----#
df_local=clean_up_2(df_main)
df_local=delta_df_2(df_local)
#df_local= select_countries (df_local, 0.0001)
list_countries = sort_countries(df_local, 'regions', 'date', 'Death', (False,''))
df_local_smoothed = smoothed_fun_2(df_local, 5)
print(df_local_smoothed)
list_chunks2=chunks_list(list_countries, 1)

para_to_plot = [('ICU', False), ('Hospitalized', False), ('Death', True), ('Delta_Death', False)]

start_date=pandas.to_datetime('2020-03-15', format='%Y-%m-%d')
end_date =df_local_smoothed.index.levels[1][-3]

lim_date = [start_date, end_date]

title_graph = pandas.DataFrame(columns=['Title'], 
                               index=['ICU', 'Hospitalized', 'Death', 'Delta_Death'],
                               data = ['Nombre en réa', 'Nombre hospitalisés', 'Nombre de décès', 'Nombre journalier de décès'])

month = lim_date[1].strftime("%m - %B")
short_date = lim_date[1].strftime("%d-%m-%Y")
file_paths = creation_folder ([f'/5.2 - Graph France/{month}', f'/5.4 - Preview/{month}'])
pdf_name = file_paths[0] + f'All_Regions_{short_date}.pdf'
preview_name = file_paths[1] + f'All_Regions_{short_date}_Preview.png'
tqdm_name = 'France'

plot_everyone (df_local_smoothed, list_chunks2, para_to_plot, lim_date, title_graph, colors, intv, pdf_name, preview_name, tqdm_name, logo)

#---- US States ----#
df_us = clean_up_3(df_case_us, df_death_us, 3)
list_states = sort_countries(df_us, 'States', 'Date', 'Cases', (False, ''))
list_chunks3=chunks_list(list_states, 1)

para_to_plot = [('Cases', True), ('Delta_Cases', False), ('Death', True), ('Delta_Death', False)]

start_date=pandas.to_datetime('2020-03-15', format='%Y-%m-%d')
end_date =df_us.index.levels[1][-1]

lim_date = [start_date, end_date]

title_graph = pandas.DataFrame(columns=['Title'], 
                               index=['Cases', 'Death', 'Delta_Cases', 'Delta_Death'],
                               data = ['Number of cases', 'Number of dead', 'Daily number of cases', 'Daily number of death'])

intv=10

month = lim_date[1].strftime("%m - %B")
short_date = lim_date[1].strftime("%d-%m-%Y")
file_paths = creation_folder ([f'/5.3 - Graph US/{month}', f'/5.4 - Preview/{month}'])
pdf_name = file_paths[0] + f'All_States_{short_date}.pdf'
preview_name = file_paths[1] + f'All_States_{short_date}_Preview.png'
tqdm_name = 'US'

plot_everyone (df_us, list_chunks3, para_to_plot, lim_date, title_graph, colors, intv, pdf_name, preview_name, tqdm_name, logo)
