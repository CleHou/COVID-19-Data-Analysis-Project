#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 23 20:48:02 2020

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
import matplotlib.image as image
import matplotlib.ticker as ticker

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


def mini_RMSE (data, list_t, val_ini):
    #result= scipy.optimize.least_squares (RMSE_fun, x0=numpy.array([150000, -4, 0.1]),args=(data, list_t) )
    result= scipy.optimize.minimize (RMSE_fun, x0=val_ini, args=(data, list_t) )
 
    a,b,c = result.x
    
    y_mod = reg_log (list_t, a,b,c)
    R2 = (r2_score(data, y_mod))
    #print(R2)
    return a,b,c, R2

    
def RMSE_fun (para, data, list_t): 
    RSS = 0
    for k in range(len(list_t)):
        y_mod = reg_log(list_t[k], para[0], para[1], para[2])
        y = data[k]
        RSS += (y - y_mod)**2
        
    MSE = RSS / len(list_t)
    RMSE = numpy.sqrt(MSE)
    
    return RMSE
        
def reg_log (t, a,b,c):
    y = a/(1+numpy.exp(-(b+c*t)))
    
    return y

def reg_log_der (t, a,b,c):
    
    y = a*c*numpy.exp(-(b+c*t))/((1+numpy.exp(-(b+c*t)))**2)
    
    return y

def try_start (data_to_fit, list_t, country, end, val_ini):
    start_range = numpy.arange(30, len(data_to_fit)-30)
    df_result = pandas.DataFrame(columns=['α', 'ß', 'γ', 'r2'])
    
    for start in tqdm.tqdm(start_range, desc = country):
        new_list_t = list_t [start:end]
        new_data_to_fit = data_to_fit[start:end]
        
        val_ini = numpy.array(val_ini)
        
        list_res = mini_RMSE (new_data_to_fit, new_list_t, val_ini)
        df_result.loc[start] = list_res
        
    #print(df_result)
    return df_result

def try_start2 (data_to_fit, list_t, country, end, val_ini):
    start_range = numpy.arange(30, len(data_to_fit)-30)
    df_result = pandas.DataFrame(columns=['α', 'ß', 'γ', 'r2'])
    
    for start in start_range:
        new_list_t = list_t [start:end]
        new_data_to_fit = data_to_fit[start:end]
        
        val_ini = numpy.array(val_ini)
        
        list_res = mini_RMSE (new_data_to_fit, new_list_t, val_ini)
        df_result.loc[start] = list_res
        
    #print(df_result)
    return df_result

def plot_para (df_result, country, date):
    long_date = date.strftime("%d %B, %Y")
    month = date.strftime("%m - %B")
    short_date = date.strftime("%d-%m-%Y")
    colors = ['#3E86E8', '#D45050', '#58C446', '#9A46C4', '#F0D735', '#6BB482', '#013BD2', '#F08328', '#04979C' ,"#00000"]

    
    fig, axs = plt.subplots(1,2, num=f'Parameter {country} {short_date}', figsize=(15,15))
    index = ['α', 'r2']
    titles = [r'$\alpha$', r'$r^2$']
    
    list_x = list(df_result.index)
    k=0
    for element, title in zip(index, titles):
        axs[k].plot(list_x, df_result.loc[:,element], color=colors[k], linewidth=0.75)
        axs[k].set_title(title)
        axs[k].grid()
        axs[k].set_ylabel(title)
        axs[k].set_xlabel('Time ($j_0=$22/01/2020)')
        k+=1
        
    fig.suptitle(f'Parameters for {country} on\n{long_date}')
    
    logo = image.imread('https://raw.githubusercontent.com/CleHou/COVID-19-Data-Analysis-Project/master/99-Other/99.1-Logo/Logo2_200px.png')
    fig.figimage(logo, 30, 20, zorder=3)
    
    fig.text(0.85, 0.05, 'Data source: John Hopkins University \nAnalysis: C.Houzard', fontsize=8)
    
    file_path = creation_folder ([f'/3.1 - Modelisation/{country}/{month}/Parameters',f'/3.1 - Modelisation/{country}/{month}/Previews'])
    fig.savefig(file_path[0] + f'Parameters_{country}_{short_date}.pdf', dpi=200)
    fig.savefig(file_path[1] + f'PREVParameters_{country}_{short_date}.png', dpi=300)
        
def get_mM (df_result, list_t, type_mM, rang):
    if type_mM=='max':
        index = df_result.idxmax(axis=0)[rang]
        
    else:
        index = df_result.idxmin(axis=0)[rang]
        
    a,b,c, r2 = df_result.loc[index]
    list_t = numpy.linspace (0, len(list_t)+30, 200)
    y_mod = reg_log(list_t, a,b,c)
    
    return list_t, y_mod, a, b,c, r2
        
        
def plot_max_min (data, data_der, df_result, list_t, country, date):
    long_date = date.strftime("%d %B, %Y")
    month = date.strftime("%m - %B")
    short_date = date.strftime("%d-%m-%Y")

    list_t_max, y_mod_max, a_max, b_max,c_max, r2_max = get_mM (df_result, list_t, 'max', 0)
    y_mod_der = reg_log_der(list_t_max, a_max,b_max,c_max)
    
    colors = ['#3E86E8', '#D45050', '#58C446', '#9A46C4', '#F0D735', '#6BB482', '#013BD2', '#F08328', '#04979C' ,"#00000"]

    fig, axs = plt.subplots(1,2, num=f'Cases {country} {short_date}', figsize=(15,15))
    
    axs[0].plot(list_t, data, '.', marker='2', color = colors[0], label = 'Data')
    axs[0].plot(list_t_max, y_mod_max, linewidth=0.75, color = colors[1], label = fr"Modélisation $r^2=$ {round(r2_max, 3)}")
    axs[0].axhline(y=a_max, linestyle='--', color='#1C1C1C', linewidth=0.75)
    
    axs[0].set_xlabel('Time ($j_0=$22/01/2020)')
    axs[0].set_ylabel('Cases')
    axs[0].set_title('Cases vs time')
    
    axs[1].plot(list_t, data_der, '.', marker='2', color = colors[0], label = 'Data')
    axs[1].plot(list_t_max, y_mod_der, linewidth=0.75, color = colors[1], label = 'Derivate')
    axs[1].set_xlabel('Time ($j_0=$22/01/2020)')
    axs[1].set_ylabel(r'$\frac{dC}{dt}$')
    axs[1].set_title('Delta cases vs time')
    axs[1].grid()
    
    fig.suptitle(f'COVID-19 estimation {country}\n{long_date}',  fontsize=16)
    
    handles, labels = axs[0].get_legend_handles_labels()
    
    fig.legend(handles, labels, loc="center right", borderaxespad=0)
    fig.subplots_adjust(right=0.82)
    axs[0].grid()
    axs[0].text(0.05*list_t_max[-1], a_max/2, r'$\hat{c}_{\alpha, \beta, \gamma}(t)=\frac{\alpha}{1+e^{-(\beta+\gamma t)}}$', fontsize=15)
    axs[0].text(-4, 1.01*a_max, fr'$c_{{max}}={int(a_max)}$', fontsize=10)
    
    logo = image.imread('https://raw.githubusercontent.com/CleHou/COVID-19-Data-Analysis-Project/master/99-Other/99.1-Logo/Logo2_200px.png')
    fig.figimage(logo, 30, 20, zorder=3)
    
    fig.text(0.85, 0.05, 'Data source: John Hopkins University \nAnalysis: C.Houzard', fontsize=8)
    
    file_paths = creation_folder ([f'/3.1 - Modelisation/{country}/{month}/Predictions', f'/3.1 - Modelisation/{country}/{month}/Previews'])
    fig.savefig(file_paths[0] + f'Predictions_{country}_{short_date}.pdf', dpi=200)
    fig.savefig(file_paths[1] + f'Preview_{country}_{short_date}.png', format='png', dpi=300)
    
def modelisation (list_df, list_country, coeff_a_ini):
    df_para = pandas.DataFrame(columns=['α', 'ß', 'γ', 'r2'])
    df_propreties = pandas.DataFrame(columns=['α', 'τ', 'Δt_99'])
    df_end_epidemic = pandas.DataFrame(columns=[' % cas', 't_99', 'date_99', 'dC/dt_99'])
    for coeff, country in zip(coeff_a_ini, list_country):
        #print(country)
        data_to_fit = numpy.array(list_df[0].loc[country])
        data_to_fit_der = numpy.array(list_df[3].loc[country])
        list_t = numpy.arange(1, len(dates.date2num(list_df[0].columns))+1, 1)
        
        val_ini=[coeff*data_to_fit[-1], -14, 0.01]
        df_result = try_start (data_to_fit, list_t, country, -1, val_ini)
        
        plot_para (df_result, country, list_df[0].columns[-1])
        plot_max_min(data_to_fit, data_to_fit_der, df_result, list_t, country, list_df[0].columns[-1])
        
        list_t_max, y_mod_max, a_max, b_max,c_max, r2_max = get_mM (df_result, list_t, 'max', 0)
        
        tau, t_99, DeltaT_99, pctge_cas, date_99, dCdt_99  = parameters (a_max, b_max,c_max, 
                                                                       (list_df[0].columns)[-1], list_t[-1], 
                                                                       data_to_fit[-1])
        date_99 = date_99.strftime("%d/%m/%Y")
        
        df_para.loc[country] = [int(a_max), round(b_max, 3), round(c_max,3), r2_max]
        df_propreties.loc[country]= [int(a_max), tau, DeltaT_99]
        df_end_epidemic.loc[country]=[pctge_cas, t_99, date_99, dCdt_99]
    
    print('\n', df_para)
    print('\n', df_propreties)
    print('\n', df_end_epidemic)
    month = (list_df[0].columns[-1]).strftime("%m - %B")
    short_date = (list_df[0].columns[-1]).strftime("%d-%m-%Y")
    file_paths = creation_folder ([f'/3.1 - Modelisation/Output Data/{month}'])
    writer=pandas.ExcelWriter(file_paths[0]+f'Data_{short_date}.xlsx', engine='xlsxwriter')
    df_para.to_excel(writer, sheet_name='Parameters')
    df_propreties.to_excel(writer, sheet_name='Properties')
    df_end_epidemic.to_excel(writer, sheet_name='End epidemic')
    writer.save()

def parameters (a, b, c, date, j_n, c_n):
    t_99=1/c * numpy.log(0.99/0.01) - b/c
    pctge_cas = c_n/a
    dCdt_99 = reg_log_der (t_99, a, b ,c)
    tau = 2*numpy.log(2+numpy.sqrt(3))/c
    DeltaT_99 = numpy.log(99**2/0.01**2)/c
    
    date_99 = date + datetime.timedelta(days=t_99-j_n)
    
    return [tau, t_99, DeltaT_99, pctge_cas, date_99, dCdt_99]
      
def test_end (list_df, list_country, coeff_a_ini):
    list_end =  numpy.arange(len(list_df[0].columns)-10, len(list_df[0].columns), 1)
    list_df_result = []
    list_df_para = [] 
    for coeff, country in zip(coeff_a_ini, list_country):
        a_df = pandas.DataFrame(columns=['α (r_max)', 'α (α_max)', 'r (r_max)', 'r (α_max)'])
        df_para = pandas.DataFrame(columns=['τ', 't_99', 'Δt_99', '% cas', 'date_99', 'dC/dt_99', 'α', 'r2'])
        for an_end in tqdm.tqdm(list_end, desc=country):
            data_to_fit = numpy.array(list_df[0].loc[country])[:an_end]
            list_t = numpy.arange(1, an_end+1, 1)
            
            val_ini = [coeff*data_to_fit[-1], -14, 0.01]
            df_result = try_start2 (data_to_fit, list_t, country, an_end, val_ini)
            res1 = get_mM (df_result, list_t, 'max', 3)
            res2 = get_mM (df_result, list_t, 'max', 0)

            date = (list_df[0].columns)[an_end].strftime("%d-%m-%Y")
            a_df.loc[date] = [res1[2], res2[2], res1[5], res2[5]]
            
            L = parameters(res2[2], res2[3], res2[4], (list_df[0].columns)[an_end], list_t[-1], data_to_fit[-1])
            L.extend([res2[2], res2[5]])
            df_para.loc[date] = L
            
        list_date = pandas.to_datetime(a_df.index, format='%d-%m-%Y')
        #plot2 (a_df, country, list_date)
        list_df_result.append(a_df)
        list_df_para.append(df_para)
        
        print('\n', a_df)
        print(df_para, '\n')
    plot3 (list_df_para, list_date, list_country)
        
    return list_df_result
    
def plot2 (a_df, country, list_date) :
    long_date = list_date[-1].strftime("%d %B, %Y")
    month = list_date[-1].strftime("%m - %B")
    short_date = list_date[-1].strftime("%d-%m-%Y")
    
    colors = ['#3E86E8', '#D45050', '#58C446', '#9A46C4', '#F0D735', '#6BB482', '#013BD2', '#F08328', '#04979C' ,"#00000"]

    fig, axs = plt.subplots(1,2, figsize=(15,15), num=f'Test des paramètres {country}')
    
    axs[0].plot(list_date, a_df.loc[:,'α (r_max)'],label=r'Selected curve: $\max(r^2)$', color=colors[0], linewidth=0.75)
    axs[0].plot(list_date, a_df.loc[:,'α (α_max)'],label=r'Selected curve: $\max(\alpha)$', color=colors[1], linewidth=0.75)
    axs[0].grid()
    axs[0].set_title(r'Predicted $\alpha$ as a function of time')
    axs[0].set_xlabel('Date of prediction')
    axs[0].set_ylabel(r'Predicted $\alpha$')
    
    axs[1].plot(list_date, a_df.loc[:,'r (r_max)'],label='$r_{max}$', color=colors[0], linewidth=0.75)
    axs[1].plot(list_date, a_df.loc[:,'r (α_max)'],label='$a_{max}$', color=colors[1], linewidth=0.75)
    axs[1].set_title(r'Values of $r^2$ as a functin of time')
    axs[1].set_xlabel('Date of prediction')
    axs[1].set_ylabel(r'Values of $r^2$')
    axs[1].yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:.3f}"))
    axs[1].grid()
    
    handles, labels = axs[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="center right", borderaxespad=0)
    plt.subplots_adjust(right=0.85)
    fig.suptitle(f"Evolution of the model prediction as a function of time\n {country} - {long_date}", size=16)
    fig.autofmt_xdate()
    
    logo = image.imread('https://raw.githubusercontent.com/CleHou/COVID-19-Data-Analysis-Project/master/99-Other/99.1-Logo/Logo2_200px.png')
    fig.figimage(logo, 30, 20, zorder=3)
    
    fig.text(0.85, 0.05, 'Data source: John Hopkins University \nAnalysis: C.Houzard', fontsize=8)
    
    file_path = creation_folder ([f'/3.2 - Prediction study/Prediction evolution/{country}/{month}'])
    fig.savefig(file_path[0] + f'Pred_evol_{country}_{short_date}.pdf', dpi=200)
    #fig.savefig(f'01 - Modelisation/{country}/{month}/Previews/Preview_{short_date}', format='png', dpi=300)


def plot3 (list_df_para, list_date, list_country):
    long_date = list_date[-1].strftime("%d %B, %Y")
    month = list_date[-1].strftime("%m - %B")
    short_date = list_date[-1].strftime("%d-%m-%Y")
    
    list_para_plot = ['α', 'τ', 'r2', 'date_99']
    list_title = ['Final number of cases α', 'Caracteristic time τ', 'Corrolation coefficient $r^2$', 'Date at which 99% of cases will be obtained']
    
    colors = ['#3E86E8', '#D45050', '#58C446', '#9A46C4', '#F0D735', '#6BB482', '#013BD2', '#F08328', '#04979C' ,"#00000"]

    fig, axs = plt.subplots(2,2, figsize=(15,15), num=f'Evolution of prediction on {short_date}')
    
    for axes, para, title in zip(numpy.ravel(axs), list_para_plot, list_title):
        for k in range(len(list_df_para)):
            if list_country[k] == 'US' and para == 'α':
                axs2 = axes.twinx()
                axs2.plot(list_date, list_df_para[k].loc[:, para], label=list_country[k], color=colors[k], linewidth=0.75, marker='2')
                axs2.set_ylabel('', color=colors[k])
                axs2.tick_params(axis='y', labelcolor=colors[k])
                axs2.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
            else:
                 axes.plot(list_date, list_df_para[k].loc[:, para], label=list_country[k], color=colors[k], linewidth=0.75, marker='2')
  
        axs[0][0].ticklabel_format(axis='y', style='sci', scilimits=(0,0))
        axs[1][0].yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:.3f}"))    
        axes.set_title(title)
        axes.set_ylabel(para)
        axes.set_xlabel('Date of the prediction')
        axes.grid()
        
    axs[1][1].yaxis.set_major_formatter(dates.DateFormatter('%d-%m'))
    
    fig.autofmt_xdate()
    handles, labels = axs[0][1].get_legend_handles_labels()
    fig.legend(handles, labels, loc="center right", borderaxespad=0)
    plt.subplots_adjust(right=0.90)
    fig.suptitle(f"Evolution of the model parameters as a function of time\n{long_date}", size=16)
    fig.autofmt_xdate()
    
    logo = image.imread('https://raw.githubusercontent.com/CleHou/COVID-19-Data-Analysis-Project/master/99-Other/99.1-Logo/Logo2_200px.png')
    fig.figimage(logo, 30, 20, zorder=3)
    
    fig.text(0.85, 0.05, 'Data source: John Hopkins University \nAnalysis: C.Houzard', fontsize=8)
    
    file_path = creation_folder ([f'/3.2 - Prediction study/Parameters evolution/Graph/{month}', f'/3.2 - Prediction study/Parameters evolution/Preview/{month}'])
    fig.savefig(file_path[0] + f'Evol_para_{short_date}.pdf', dpi=200)
    fig.savefig(file_path[1] + f'Preview_Evol_para_{short_date}.png', format='png', dpi=300)

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

list_df.append(delta_df (list_df[0])) #list_df[3]

list_df[0] = smoothed_fun_2(list_df[0], 2)
list_df[3] = smoothed_fun_2(list_df[3], 2)

list_country = ['France', 
                'US', 
                'Italy', 
                'Germany'
                ]

coeff_a_ini = [1.7, 
               1.5, 
               1.5, 
               1.7]

#list_country=['France', 'US']

test_end (list_df, list_country, coeff_a_ini)
modelisation (list_df, list_country, coeff_a_ini)




