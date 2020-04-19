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

def import_df_from_I ():
    partial_link = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_'
    df1 = pandas.read_csv(partial_link+ 'confirmed_global.csv')
    df2 = pandas.read_csv(partial_link+ 'deaths_global.csv')  
    df3 = pandas.read_csv(partial_link+ 'recovered_global.csv')

    return df1, df2, df3

def creation_folder (paths):
    current = os.path.dirname(os.path.realpath(__file__))
    list_directory = [os.path.normcase(current + directory) for directory in paths]
    
    for directory in list_directory:
        if os.path.exists(directory) == False:
            os.makedirs(directory)

def save_df (list_df, current):
    creation_folder(['/00 - Data'])
    
    df1, df2, df3 = list_df
    df1.to_csv(os.path.normcase(current + '/00 - Data/confirmed.csv'), index=False)
    df2.to_csv(os.path.normcase(current + '/00 - Data/death.csv'    ), index=False)
    df3.to_csv(os.path.normcase(current + '/00 - Data/recovered.csv'), index=False)
    
    return print('Saved')

def import_df_from_xlsx (current):
    df1 = pandas.read_csv(current + '/00 - Data/confirmed.csv')
    df2 = pandas.read_csv(current + '/00 - Data/death.csv')  
    df3 = pandas.read_csv(current + '/00 - Data/recovered.csv')  
    
    return df1, df2, df3

def clean_up (list_df):
    list_return = []
    for a_df in list_df:
        a_df = a_df.drop(['Lat', 'Long'], axis=1)
        a_df = a_df.groupby("Country/Region").sum()
        a_df.columns = pandas.to_datetime(a_df.columns)
        a_df.loc['World'] = a_df.sum()
        
        list_return.append(a_df)

    return list_return

def ajusted_values(list_df):
    to_replace = numpy.array([65202, 69500, 71412, 75343, 79163, 83057, 87366, 91738, 94863, 
                  96482, 99172, 104481, 107318, 109978, 109252, 111821], dtype=float)
    
    for k in range(len(list_df[0].columns)-72):
        list_df[0].iloc[list_df[0].index.get_loc('France'), 72+k]=to_replace[k]
        
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
    
    for country in list_country:
        list_date = list(a_df.columns.values) [lim_date[0]: lim_date[-1]]
        list_val = list(a_df.loc[country])[lim_date[0]: lim_date[-1]]
        
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
    
    for country in list_country:
        list_date = list(a_df.columns.values) [lim_date[0]: lim_date[-1]]
        list_val = list(a_df.loc[country])[lim_date[0]: lim_date[-1]]
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
    
    for country in list_country:
        list_date = list(a_df.columns.values) [lim_date[0]: lim_date[-1]]
        list_val = list(a_df.loc[country])[lim_date[0]: lim_date[-1]]
        
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
    
    for country in list_country:
        list_date = list(a_df.columns.values) [lim_date[0]: lim_date[-1]]
        list_val = list(a_df.loc[country])[lim_date[0]: lim_date[-1]]
        
        if country != 'US':
            axs.plot(list_date, list_val, marker="2", markersize=5, linewidth=0.75, label = country, color = colors[k])
        else:
            axs2 = axs.twinx()
            axs2.plot(list_date, list_val, marker="2", markersize=5, linewidth=0.75, label = country, color = colors[k])
            axs2.set_ylabel(f'$\Delta$ {type_graph} (US)', color=colors[k])  # we already handled the x-label with ax1
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
    long_date = (list_df[0].columns)[lim_date[-1]].strftime("%d %B, %Y")
    month = (list_df[0].columns)[lim_date[-1]].strftime("%m - %B")
    short_date = (list_df[0].columns)[lim_date[-1]].strftime("%d-%m-%Y")
    
    if len(list_country) >1:
        fig1, axs1 = plt.subplots(2, 2, num='Covid-19 plot 1/2 on ' + long_date, figsize=(15,15)) #Grid 2x2
        fig2, axs2 = plt.subplots(2, 2, num='Covid-19 plot 2/2 on ' + long_date, figsize=(15,15)) #Grid 2x2
        
    else:
        fig1, axs1 = plt.subplots(2, 2, num='Covid-19 plot 1/2 '+list_country[-1], figsize=(15,15)) #Grid 2x2
        fig2, axs2 = plt.subplots(2, 2, num='Covid-19 plot 2/2 '+list_country[-1], figsize=(15,15)) #Grid 2x2
        
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
    
    
    if len(list_country) >1:
        creation_folder ([f'/01 - Graph/Daily/{month}'])
        
        fig1.suptitle(f'Covid-19 situation on {long_date} \n1/2', fontsize=16)
        fig2.suptitle(f'Covid-19 situation on {long_date} \n', fontsize=16)
        fig2.savefig(os.path.normcase(f'01 - Graph/Daily/{month}/{short_date}.pdf'), format='pdf')
        
        """
        pdf = matplotlib.backends.backend_pdf.PdfPages(os.path.normcase(f'01 - Graph/Daily/{month}/{short_date}.pdf'))
        pdf.savefig(fig1)
        pdf.savefig(fig2)
        pdf.close()
        """
        
    else:
        if list_country==['World']:
            creation_folder ([f'/01 - Graph/World/{month}'])
            
            fig1.suptitle('Covid-19 situation worldwide \n1/2', fontsize=16)
            fig2.suptitle('Covid-19 situation worldwide \n', fontsize=16)
            
            fig2.savefig(os.path.normcase(f'01 - Graph/World/{month}/{short_date}_World.pdf'), format='pdf')
            """
            pdf = matplotlib.backends.backend_pdf.PdfPages(os.path.normcase(f'01 - Graph/World/{month}/{short_date}_World.pdf'))
            pdf.savefig(fig1)
            pdf.savefig(fig2)
            pdf.close()
            """
            
        else:
            creation_folder ([f'/01 - Graph/Country/'])
            
            fig1.suptitle(f'Covid-19 situation for {list_country[-1]} \n1/2', fontsize=16)
            fig2.suptitle('Covid-19 situation for {list_country[-1]} \n', fontsize=16)
            
            fig2.savefig(os.path.normcase(f'01 - Graph/Country/{list_country[-1]}.pdf'), format='pdf')
    
    plt.show()
            
    
def graph_stack (new_df, lim_date, intv, colors, type_graph, incrementxy, fig, axs):
    list_date = list(new_df.columns.values) [lim_date[0]: lim_date[-1]]
    list_val = [list(new_df.loc[country])[lim_date[0]: lim_date[-1]] for country in new_df.index]
    
    prev_val = 0
    for a_list in list_val:
        final_val = a_list[-1]
        new_val = final_val + prev_val
        axs.annotate('+'+str(round(final_val)), xy=(list_date[-1], new_val), xytext = (list_date[-17], new_val-incrementxy),
           arrowprops=dict(facecolor='black', arrowstyle="->"))
        prev_val += final_val
    
    axs.grid(alpha=0.4)    
    axs.stackplot(list_date, list_val, labels = new_df.index, colors = colors[:len(new_df.index)])
    axs.xaxis.set_major_formatter(dates.DateFormatter('%d/%m/%y'))
    axs.xaxis.set_major_locator(dates.DayLocator(interval=intv))
    fig.autofmt_xdate()
    
    axs.set_title (f'Number of confirmed {type_graph} vs date')
    axs.set_ylabel(f'Number of {type_graph}')
    axs.set_xlabel('Date')
    
   
    
def graph_death_stack (new_df12, list_date, start_index, end_index, list_colors, fig, axs, intv):
    list_val = []
    list_country_full = list(new_df12.index)
    
    for country in list_country_full:
        list_val.append(list(new_df12.loc[country])[2 + start_index:end_index])
        
    prev_val = 0
    for L in list_val:
        axs[1].annotate('+'+str(round(L[-1])), xy=(list_date[-1], L[-1]+prev_val), xytext = (list_date[-17], L[-1]+prev_val-500),
           arrowprops=dict(facecolor='black', arrowstyle="->"))
        prev_val += L[-1]
    
    axs[1].grid(alpha=0.4)
    axs[1].stackplot(list_date, list_val, labels = list_country_full, colors = list_colors[:len(list_country_full)])
    axs[1].xaxis.set_major_formatter(dates.DateFormatter('%d/%m/%y'))
    axs[1].xaxis.set_major_locator(dates.DayLocator(interval=intv))
    fig.autofmt_xdate()
    
    axs[1].set_title ('Number of death vs date')
    axs[1].set_ylabel('Number of cases')
    axs[1].set_xlabel('Date')
    
    
    
def plot_stack (list_df, lim_date, intv, list_country, colors):
    long_date = (list_df[0].columns)[lim_date[-1]].strftime("%d %B, %Y")
    month = (list_df[0].columns)[lim_date[-1]].strftime("%m - %B")
    short_date = (list_df[0].columns)[lim_date[-1]].strftime("%d-%m-%Y")
    
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
  
    creation_folder ([f'/01 - Graph/Stack/{month}'])
    plt.savefig(os.path.normcase(f'01 - Graph/Stack/{month}/{short_date}.pdf'), format='pdf')
    
    
def to_print (list_df):
    
    for country in list_country:
        print('\n'+country)
        mod_list_df = [list_df[0], list_df[3], list_df[1], list_df[4], list_df[5], list_df[6]]
        list_index = ['Cases', 'Delta Cases', 'Death',  'Delta Death' , 'Fatality rate', 'Growth rate averaged']
        list_col = [(list_df[0].columns)[x].strftime("%d-%m-%Y") for x in range(-3, 0, 1)]
        list_concat = []
        
        for a_df in mod_list_df:
            list_concat.append(list(a_df.loc[country])[-3:])
            
        df_to_print = pandas.DataFrame(list_concat, index=list_index, columns=list_col)
   
        print (df_to_print)
        
    

#Creation des DB
current = os.path.dirname(os.path.realpath(__file__))

list_df = import_df_from_I()
#list_df = import_df_from_xlsx(current)
save_df (list_df, current)

list_df= clean_up(list_df)
list_df = ajusted_values(list_df) #list_df[0] to list_df[2]

delta_df11 = delta_df(list_df[0])
delta_df11 = smoothed_fun (delta_df11, 2)
list_df.append(delta_df11) #list_df[3]

delta_df12 = delta_df(list_df[1])
delta_df12 = smoothed_fun (delta_df12, 2)
list_df.append(delta_df12) #list_df[4]

frate = fatality_rate (list_df)
list_df.append(frate) #list_df[5]

grate = growth_rate (list_df[0])
grate = smoothed_fun (grate, 2)
list_df.append(grate) #list_df[6]


colors = ['#3E86E8', '#D45050', '#58C446', '#9A46C4', '#F0D735', '#6BB482', '#013BD2', '#F08328', '#04979C' ,"#00000"]

#For a list of country 4 graphs
len_tot = len(list(list_df[0].columns.values))-1

lim_date = [50, len_tot]
lim_reg_cases = [22, len_tot, 22, 24] 
lim_reg_death = [len_tot, len_tot,24, len_tot]
intv = 2
list_country = ['France', 'US', 'Italy', 'Germany']

plot (list_df, lim_date, lim_reg_cases, lim_reg_death, intv, list_country, colors, regression=False)
to_print (list_df)

#For a list of country Stacked graph
lim_date = [1, len_tot]
intv = 5
list_country = ['China', 'Italy', 'US', 'Spain', 'France']

plot_stack (list_df, lim_date, intv, list_country, colors)


#One Country or worldwide
im_date = [1, len_tot]
lim_reg_cases = [15]
lim_reg_death = [24] 
intv = 5
list_country = ['World']

plot (list_df, lim_date, lim_reg_cases, lim_reg_death, intv, list_country, colors, regression=False)
to_print (list_df)

#print (list(df11.index)) #Liste des pays


