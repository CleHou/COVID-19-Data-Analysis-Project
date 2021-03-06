#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 23:08:30 2020

@author: Clement
v2.3
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
import datetime

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
    file_path = ['/1.0 - Data']
    file_path = creation_folder(file_path)
    
    df1, df2, df3 = list_df
    df1.to_csv(os.path.normcase(file_path [0] + 'confirmed.csv'), index=False)
    df2.to_csv(os.path.normcase(file_path [0] + 'death.csv'    ), index=False)
    df3.to_csv(os.path.normcase(file_path [0] + 'recovered.csv'), index=False)
    to_replace.to_csv(os.path.normcase(file_path [0] + 'Revised_France_Data.csv'), index=False, index_label="Date")
    
    return print('Saved')

def import_df_from_xlsx (current):
    file_path = [current+'/1.0 - Data/']
    
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
        
    list_df[0].loc['World'] = list_df[0].sum()
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

def delta_df (df):
    list_date = list(df.columns)
    delta_df=df.iloc[:,:1]

    for k in range(len(list_date)-1):
        delta_df.loc[:, list_date[k+1]] = df.loc[:,list_date[k+1]] - df.loc[:,list_date[k]]
        
    return delta_df

def log_reg (list_date, list_val, indx_lim):
    end_date=list_date[-1]
    list_date, list_val = list_date[: indx_lim], list_val[: indx_lim]
    
    list_ln = []
    new_list_date = []
    
    for k in range(len(list_val)):
        if list_val[k]>10:
            list_ln.append(numpy.log(list_val[k]))
            new_list_date.append(list_date[k])
    
    list_ln = numpy.array(list_ln)
    new_list_date = numpy.array(new_list_date).reshape((-1, 1))
    
    regression =  linear_model.LinearRegression()
    regression.fit(new_list_date, list_ln)
    
    prediction = regression.predict(new_list_date)
    
    R2 = r2_score(list_ln, prediction)
    coeff = regression.coef_
    
    date_to_pred = numpy.array([new_list_date[0][0], end_date]).reshape((-1, 1))
    list_pred = regression.predict(date_to_pred)
    
    return R2, numpy.exp(coeff[0]), list_pred, date_to_pred

def graph_C_and_D (a_df, lim_date, lim_reg_cases, lim_reg_death, intv, list_country, colors, regression, type_graph, fig, axs):
    k=0
    list_coeff = []
    df_considered = a_df.loc[list_country, lim_date[0]:lim_date[1]]
    list_date = df_considered.columns
    
    for country in list_country:
        list_val = df_considered.loc[country]
        
        if regression:
            indx_lim = lim_reg_cases[k]
            R2, coeff, prediction, new_list_date = log_reg (list_date, list_val, indx_lim)
            prediction = [numpy.exp(x) for x in prediction]
            axs.plot(new_list_date, prediction, '--', color=colors[k], linewidth = 0.5)
            list_coeff.append(coeff)
            text = '$(a, r^2)=($'+ str(round(coeff, 2)) + ',' + str(round(R2,2)) + ')'
            
            axs.plot(list_date, list_val, marker="2", markersize=5, linewidth=0.75, label = text, color=colors[k])
            axs.legend()
            
        else:
            axs.plot(list_date, list_val, marker="2", markersize=5, linewidth=0.75, color=colors[k])
        
        k+=1
        
    axs.xaxis.set_major_formatter(dates.DateFormatter('%d/%m/%Y'))
    axs.xaxis.set_major_locator(dates.DayLocator(interval=intv))
    fig.autofmt_xdate()
    
    axs.semilogy()
    
    axs.set_title (f'Number of confirmed {type_graph} vs date')
    axs.set_ylabel(f'Number of {type_graph} (log scale)')
    axs.set_xlabel('Date')
    axs.grid()
    
    return list_coeff
    
    
def graph_frate (a_df, lim_date, lim_reg_cases, lim_reg_death, intv, list_country, colors, fig, axs):
    k=0
    df_considered = a_df.loc[list_country, lim_date[0]:lim_date[1]]
    list_date = df_considered.columns
    
    for country in list_country:
        list_val = df_considered.loc[country]
        axs.plot(list_date, list_val, marker="2", markersize=5, linewidth=0.75, label = country, color = colors[k])
        k+=1
    
    axs.xaxis.set_major_formatter(dates.DateFormatter('%d/%m/%y'))
    axs.xaxis.set_major_locator(dates.DayLocator(interval=intv))
    fig.autofmt_xdate()
        
    axs.set_title ('Fatality rate vs date')
    axs.set_ylabel('Fatality rate')
    axs.set_xlabel('Date')
    axs.grid()
    
def graph_grate (a_df, lim_date, lim_reg_cases, lim_reg_death, intv, list_country, colors, list_coeff, regression, fig, axs):
    k=0
    df_considered = a_df.loc[list_country, lim_date[0]:lim_date[1]]
    list_date = df_considered.columns
    
    for country in list_country:
        list_val = df_considered.loc[country]
        
        if regression:
            coeff = (list_coeff[k]-1)*100
            axs.plot([list_date[0], list_date[-1]], [coeff, coeff], '--', color=colors[k], linewidth = 0.5)
        
        axs.plot(list_date, list_val, marker="2", markersize=5, linewidth=0.75, label = country, color = colors[k])
        
        k+=1
    
    axs.xaxis.set_major_formatter(dates.DateFormatter('%d/%m/%y'))
    axs.xaxis.set_major_locator(dates.DayLocator(interval=intv))
    fig.autofmt_xdate()
        
    axs.set_title ('Growth rate vs date')
    axs.set_ylabel('Growth rate (%)')
    axs.set_xlabel('Date')
    axs.grid()
    
def graph_delta (a_df, lim_date, lim_reg_cases, lim_reg_death, intv, list_country, colors, type_graph, fig, axs):
    k=0
    df_considered = a_df.loc[list_country, lim_date[0]:lim_date[1]]
    list_date = df_considered.columns
    
    for country in list_country:
        list_val = df_considered.loc[country]
        
        if country != 'US':
            axs.plot(list_date, list_val, marker="2", markersize=5, linewidth=0.75, label = country, color = colors[k])
        else:
            axs2 = axs.twinx()
            axs2.plot(list_date, list_val, marker="2", markersize=5, linewidth=0.75, label = country, color = colors[k])
            axs2.set_ylabel(f'$\Delta$ {type_graph} (US)', color=colors[k])
            axs2.tick_params(axis='y', labelcolor=colors[k])
        
        k+=1
    
    axs.xaxis.set_major_formatter(dates.DateFormatter('%d/%m/%y'))
    axs.xaxis.set_major_locator(dates.DayLocator(interval=intv))
    fig.autofmt_xdate()
    axs.set_xlabel('Date')
    axs.set_ylabel(f'$\Delta$ {type_graph}')
    axs.set_title (f'New {type_graph} compared to d-1')
    axs.grid()
    
def legend (list_country, colors):
    list_zip = zip(list_country, colors)
    handles, labels = [], []
    for element in list_zip:
        handles.append(mlines.Line2D([], [], color=element[1], marker = '2', linewidth=0.75))
        labels.append(element[0])
        
    return handles, labels
    
    
def plot (list_df, lim_date, lim_reg_cases, lim_reg_death, intv, list_country, colors, regression):
    long_date = lim_date[1].strftime("%d %B, %Y")
    month = lim_date[1].strftime("%m - %B")
    short_date = lim_date[1].strftime("%d-%m-%Y")
    
    if len(list_country) >1:
        fig1, axs1 = plt.subplots(2, 2, num='Covid-19 plot 1/2 on ' + long_date, figsize=(15,15)) #Grid 2x2
        fig2, axs2 = plt.subplots(2, 2, num='Covid-19 plot 2/2 on ' + long_date, figsize=(15,15)) #Grid 2x2
        
    else:
        fig1, axs1 = plt.subplots(2, 2, num=f'Covid-19 plot 1/2 {list_country[-1]}, {short_date}', figsize=(15,15)) #Grid 2x2
        fig2, axs2 = plt.subplots(2, 2, num=f'Covid-19 plot 2/2 {list_country[-1]}, {short_date}', figsize=(15,15)) #Grid 2x2
        
    fig1.text(0.87, 0.05, 'Source: John Hopkins University \nGraph: C.Houzard', fontsize=8)
    fig2.text(0.87, 0.05, 'Source: John Hopkins University \nGraph: C.Houzard', fontsize=8)
    
    list_coeff = graph_C_and_D (list_df[0], lim_date, lim_reg_cases, lim_reg_death, intv, list_country, colors, regression, 'cases', fig1, axs1[0][0])
    graph_C_and_D (list_df[1], lim_date, lim_reg_cases, lim_reg_death, intv, list_country, colors, regression, 'death', fig1, axs1[1][0])
    graph_frate(list_df[5], lim_date, lim_reg_cases, lim_reg_death, intv, list_country, colors, fig1, axs1[0][1])
    graph_grate(list_df[6], lim_date, lim_reg_cases, lim_reg_death, intv, list_country, colors, list_coeff, regression, fig1, axs1[1][1])
    
    graph_C_and_D (list_df[0], lim_date, lim_reg_cases, lim_reg_death, intv, list_country, colors, regression, 'cases', fig2, axs2[0][0])
    graph_C_and_D (list_df[1], lim_date, lim_reg_cases, lim_reg_death, intv, list_country, colors, regression, 'death', fig2, axs2[1][0])
    graph_delta (list_df[3], lim_date, lim_reg_cases, lim_reg_death, intv, list_country, colors, 'cases', fig2, axs2[0][1])
    graph_delta (list_df[4], lim_date, lim_reg_cases, lim_reg_death, intv, list_country, colors, 'death', fig2, axs2[1][1])
    
    handles, labels = legend (list_country, colors)
    
    fig1.legend(handles, labels, loc="center right", borderaxespad=0)
    fig1.subplots_adjust(right=0.87)
    fig2.legend(handles, labels, loc="center right", borderaxespad=0)
    fig2.subplots_adjust(right=0.87)
    
    
    logo = image.imread('https://raw.githubusercontent.com/CleHou/COVID-19-Data-Analysis-Project/master/99-Other/99.1-Logo/Logo2_200px.png')
    fig1.figimage(logo, 30, 20, zorder=3)
    fig2.figimage(logo, 30, 30, zorder=3)
    
    if len(list_country) >1:
        fig1.suptitle(f'Covid-19 situation on {long_date}', fontsize=16)
        fig2.suptitle(f'Covid-19 situation on {long_date}', fontsize=16)
        
        file_paths = creation_folder ([f'/1.1 - Daily/{month}', f'/1.5 - Previews/{month}'])
        
        fig2.savefig(os.path.normcase(file_paths[0] + f'{short_date}.pdf'), format='pdf', dpi=200)
        fig2.savefig(os.path.normcase(file_paths[1] + f'{short_date}_preview.png'), format='png', dpi=300) #Preview for publishing
    
        """
        pdf = matplotlib.backends.backend_pdf.PdfPages(os.path.normcase(f'01 - Graph/Daily/{month}/{short_date}.pdf'))
        pdf.savefig(fig1)
        pdf.savefig(fig2)
        pdf.close()
        """
        
    else:
        if list_country==['World']:
            fig1.suptitle(f'Covid-19 situation worldwide\n{long_date}', fontsize=16)
            fig2.suptitle(f'Covid-19 situation worldwide\n{long_date}', fontsize=16)
            
            file_paths =creation_folder ([f'/1.2 - World/{month}', f'/1.5 - Previews/{month}'])
            fig2.savefig(os.path.normcase(file_paths[0] + f'{short_date}_World.pdf'), format='pdf', dpi=200)
            fig2.savefig(os.path.normcase(file_paths[1] + f'{short_date}_preview_world.png'), format='png', dpi=300) #Preview for publishing
        
            """
            pdf = matplotlib.backends.backend_pdf.PdfPages(os.path.normcase(f'01 - Graph/World/{month}/{short_date}_World.pdf'))
            pdf.savefig(fig1)
            pdf.savefig(fig2)
            pdf.close()
            """
            
        else:
            file_paths = creation_folder ([f'/1.4 - Country'])
            
            fig1.suptitle(f'Covid-19 situation for {list_country[-1]}', fontsize=16)
            fig2.suptitle(f'Covid-19 situation for {list_country[-1]}', fontsize=16)
            
            fig2.savefig(os.path.normcase(file_paths[0] +f'/{list_country[-1]}.pdf'), format='pdf', dpi=200)
    
    plt.show()
            
    
def graph_stack (new_df, lim_date, intv, colors, type_graph, incrementxy, fig, axs):
    df_considered = new_df.loc[:, lim_date[0]:lim_date[1]]
    list_date = df_considered.columns

    prev_val = 0
    for country in df_considered.index:
        final_val = int(df_considered.loc[country, lim_date[1]])
        new_val = final_val + prev_val
        axs.annotate('+'+str(final_val), xy=(list_date[-1], new_val), xytext = (list_date[-32], new_val-incrementxy),
           arrowprops=dict(facecolor='black', arrowstyle="->"))
        prev_val += final_val
    
    axs.grid(alpha=0.4)    
    axs.stackplot(list_date, df_considered, labels = new_df.index, colors = colors[:len(new_df.index)])
    axs.xaxis.set_major_formatter(dates.DateFormatter('%d/%m/%y'))
    axs.xaxis.set_major_locator(dates.DayLocator(interval=intv))
    fig.autofmt_xdate()
    
    axs.set_title (f'Number of confirmed {type_graph} vs date')
    axs.set_ylabel(f'Number of {type_graph}')
    axs.set_xlabel('Date')
    
    
def plot_stack (list_df, lim_date, intv, list_country, colors):
    long_date = lim_date[1].strftime("%d %B, %Y")
    month = lim_date[1].strftime("%m - %B")
    short_date = lim_date[1].strftime("%d-%m-%Y")
    
    list_country_extanded = list_country[:]
    list_country_extanded.append('World')

    new_cases_df = list_df[0].loc[list_country]
    new_cases_df.loc['Other'] = list_df[0].drop(list_country_extanded).sum()
    
    new_death_df = list_df[1].loc[list_country]
    new_death_df.loc['Other'] = list_df[1].drop(list_country_extanded).sum()
    
    fig, axs = plt.subplots(1, 2, num=f'Covid-19 plot on {long_date}\nStacked plot', figsize=(15,15)) #Grid 2x2
    fig.text(0.87, 0.05, 'Source: John Hopkins University \nGraph: C.Houzard', fontsize=8)
    
    graph_stack (new_cases_df, lim_date, intv, colors, 'cases', 50000, fig, axs[0])
    graph_stack (new_death_df, lim_date, intv, colors, 'death', 500  , fig, axs[1])
    
    handles, labels = axs[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="center right", borderaxespad=0)
    plt.subplots_adjust(right=0.9)
    
    fig.suptitle(f'Covid-19 situation on {long_date}', fontsize=16)
    
    logo = image.imread('https://raw.githubusercontent.com/CleHou/COVID-19-Data-Analysis-Project/master/99-Other/99.1-Logo/Logo2_200px.png')
    fig.figimage(logo, 30, 20, zorder=3)
    
    file_paths = creation_folder ([f'/1.3 - Stack/{month}', f'/1.5 - Previews/{month}'])
    fig.savefig(os.path.normcase(file_paths[0] + f'{short_date}_stack.pdf'), format='pdf', dpi=200)
    fig.savefig(os.path.normcase(file_paths[1] + f'{short_date}_preview_stack.png'), format='png', dpi=300) #Preview for publishing
    
    
def to_print (list_df):
    
    for country in list_country:
        print('\n'+country)
        mod_list_df = [list_df[0], list_df[3], list_df[1], list_df[4], list_df[5], list_df[6], list_df[7]]
        list_index = ['Cases', 'Delta Cases', 'Death',  'Delta Death' , 'Fatality rate', 'Growth rate averaged', 'Growth rate']
        list_col = [(list_df[0].columns)[x].strftime("%d-%m-%Y") for x in range(-3, 0, 1)]
        list_concat = []
        
        for a_df in mod_list_df:
            list_concat.append(list(a_df.loc[country])[-3:])
            
        df_to_print = pandas.DataFrame(list_concat, index=list_index, columns=list_col)
   
        print (df_to_print)
        
def check_date (list_df, to_replace):
    today_date = datetime.date.today()
    last_date =datetime.datetime.strptime(list_df[0].columns[-1], "%m/%d/%y").date()
    
    delta = (today_date-last_date).days
    
    if delta > 1 :
        short_date = last_date.strftime("%Y-%m-%d")
        print('\a')
        print(f'Data were last updated {delta} days ago, on {short_date}')
        conti = input('Do you wish to update the data? [y/n]?')
        
        if conti == 'y':
            list_df, to_replace = import_df_from_I()
            print('Data updated')
            
    return list_df, to_replace
    

#Creation des DB
current = os.path.dirname(os.path.realpath(__file__))

list_df, to_replace = import_df_from_I()
#list_df, to_replace = import_df_from_xlsx(current)

list_df, to_replace = check_date (list_df, to_replace)
save_df (list_df, to_replace)

list_df= clean_up(list_df)
list_df = ajusted_values(list_df, to_replace) #list_df[0] to list_df[2]



delta_df11 = delta_df(list_df[0])
delta_df11 = smoothed_fun (delta_df11, 2)
list_df.append(delta_df11) #list_df[3]

delta_df12 = delta_df(list_df[1])
delta_df12 = smoothed_fun (delta_df12, 2)
list_df.append(delta_df12) #list_df[4]

frate = fatality_rate (list_df)
list_df.append(frate) #list_df[5]

grate = growth_rate (list_df[0])
grate2 = smoothed_fun (grate, 2)
list_df.append(grate2) #list_df[6]
list_df.append(grate)


colors = ['#3E86E8', '#D45050', '#58C446', '#9A46C4', '#F0D735', '#6BB482', '#013BD2', '#F08328', '#04979C' ,"#00000"]


#For a list of country 4 graphs
start_date=pandas.to_datetime('2020-03-15', format='%Y-%m-%d')
end_date = list_df[0].columns[-1]
#end_date=pandas.to_datetime('2020-05-07', format='%Y-%m-%d')
len_tot = len(list(list_df[0].columns.values))-1

lim_date = [start_date, end_date]
lim_reg_cases = [22, len_tot, 22, 24] 
lim_reg_death = [len_tot, len_tot,24, len_tot]
intv = 7
list_country = ['France', 'US', 'Italy', 'Germany']

plot (list_df, lim_date, lim_reg_cases, lim_reg_death, intv, list_country, colors, regression=False)
to_print (list_df)

#For a list of country Stacked graph
start_date = pandas.to_datetime('2020-01-20', format='%Y-%m-%d')
lim_date = [start_date, end_date]
intv = 10
list_country = ['China', 'Italy', 'Spain', 'France', 'US']

plot_stack (list_df, lim_date, intv, list_country, colors)

#One Country or worldwide
start_date = pandas.to_datetime('2020-01-20', format='%Y-%m-%d')
lim_date = [start_date, end_date]
lim_reg_cases = [15]
lim_reg_death = [24] 
intv = 10
list_country = ['World']

plot (list_df, lim_date, lim_reg_cases, lim_reg_death, intv, list_country, colors, regression=False)
to_print (list_df)

#print (list(list_df[0].index)) #Liste des pays

