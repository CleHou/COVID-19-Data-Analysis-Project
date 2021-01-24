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
import sys
from cycler import cycler

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from gen_fct import df_fct
from gen_fct import file_fct

class Preping_data:
    def __init__ (self, df_cases, df_death, df_fra):
        self.df_cases = df_cases
        self.df_death = df_death
        self.df_fra = df_fra
        self.df_world = pandas.DataFrame()

    def clean_up_JH (self):
        list_df = [self.df_cases, self.df_death]
        name_df = ['cases', 'death']

        list_return = []
        for a_df, a_name in zip(list_df, name_df):
            a_df = a_df.drop(['Lat', 'Long'], axis=1)
            a_df = a_df.groupby("Country/Region").sum()
            a_df.loc['World'] = a_df.sum()
            a_df = pandas.melt(a_df.reset_index(), id_vars=["Country/Region"], value_vars=a_df.columns, var_name='date', value_name=a_name)
            a_df.loc[:,"date"] = pandas.to_datetime(a_df.loc[:,"date"])
            a_df = a_df.set_index(['Country/Region', 'date'])
            list_return.append(a_df)
            
        self.df_world = pandas.concat(list_return, axis=1).sort_index()

    def clean_up_Fra_gen (self):
        self.df_fra = self.df_fra.set_index('date')
        self.df_fra = self.df_fra.drop(index=['2020-11_11']).reset_index()
        
        self.df_fra = self.df_fra[(self.df_fra.loc[:,'granularite']=='pays') & (self.df_fra.loc[:,'source_type']=='ministere-sante')]
        self.df_fra = self.df_fra.set_index('date')
        self.df_fra.index = pandas.to_datetime(self.df_fra.index, format='%Y-%m-%d')
        self.df_fra['deces_ehpad'] = self.df_fra['deces_ehpad'].fillna(method='ffill')
        self.df_fra['deces_ehpad'] = self.df_fra['deces_ehpad'].fillna(0)
        self.df_fra = self.df_fra.sort_index()
        self.df_fra.loc[:,'cas_confirmes'].astype('float64').dtypes

    def ajust_values (self):
        ini_date = pandas.to_datetime('2020-04-03', format='%Y-%m-%d')
        last_date = self.df_world.index.get_level_values(1).unique('date')[-1]
        self.df_world.loc[('France', ini_date): ('France', last_date), 'cases'] = self.df_fra.loc[ini_date: last_date, ['cas_confirmes']].values
        self.df_world.loc['World'] = self.df_world.sum(level='date').values
        
    def main(self):
        self.clean_up_JH ()
        self.clean_up_Fra_gen ()
        self.ajust_values ()
        df_fct.export_df([['Fra_GenData_full', self.df_fra],['World_JH', self.df_world]], ['processed', 'processed'])
        
        return self.df_world, self.df_fra

df_cases, df_death, df_fra = df_fct.import_df(['World_JH_cases', 'World_JH_death', 'Fra_GenData'], ['raw' for x in range(3)])
df_world, df_fra = Preping_data (df_cases, df_death, df_fra).main()
#%%


def ajusted_values(list_df, to_replace):
    to_replace = to_replace.set_index('Date')
    to_replace.loc[:,'Cases'] = pandas.to_numeric(to_replace.loc[:,'Cases'], downcast='float')
    to_replace.index = pandas.to_datetime(to_replace.index)
   
    for index in to_replace.index:
        list_df[0].loc['France', index] = to_replace.loc[index, 'Cases']
    
    list_df[0] = list_df[0].drop('World')     
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

def log_reg (df, offset):
    df['days_from_start'] = (df.index - df.index[0]).days; df
    list_val = df.iloc[:,0].values
    list_date = df['days_from_start'].values
    
    list_ln = []
    
    for k in range(len(list_val)):
        if list_val[k]>10:
            list_ln.append(numpy.log(list_val[k]))
    
    list_ln = numpy.array(list_ln)
    list_date_2 = numpy.array(list_date).reshape((-1, 1))
    
    regression =  linear_model.LinearRegression()
    regression.fit(list_date_2, list_ln)
    
    prediction = regression.predict(list_date_2)
    
    R2 = r2_score(list_ln, prediction)
    coeff = regression.coef_
    
    prev_xtra_date = [x for x in range(-offset[0], 0)]
    folowing_xtra_date = [x for x in range(list_date[-1]+1, list_date[-1]+1+offset[1])]
    
    date_to_pred = numpy.array([*prev_xtra_date, *list_date, *folowing_xtra_date]).reshape((-1, 1))
    list_pred = regression.predict(date_to_pred)
    
    return R2, numpy.exp(coeff[0]), list_pred

def graph_C_and_D (a_df, lim_date, lim_reg, intv, list_country, style_cycle, type_graph, fig, axs):
    k=0
    list_coeff = []
    df_considered = a_df.loc[list_country, lim_date[0]:lim_date[1]]
    list_date = df_considered.columns
    
    for country, regression, beg_date, end_date, offset, style in zip(list_country, lim_reg[0], lim_reg [1], lim_reg [2], lim_reg [3], style_cycle()):
        list_val = df_considered.loc[country]
        
        if regression:
            df = pandas.DataFrame(a_df.loc[country, beg_date:end_date])
            R2, coeff, prediction = log_reg (df, offset)
            prediction = [numpy.exp(x) for x in prediction]
            
            previous_date = beg_date - pandas.to_timedelta(str(offset[0])+ ' day')
            folowing_date = end_date + pandas.to_timedelta(str(offset[1])+ ' day')
            list_date_reg = a_df.loc[country, previous_date:folowing_date].index
            
            axs.plot(list_date_reg, prediction, '--', linewidth = 0.5, color=style['color'])
            axs.plot([beg_date, end_date], [prediction[offset[0]], prediction[-offset[1]-1]], color=style['color'], linestyle=None, marker='2', linewidth =0)
            list_coeff.append(coeff)
            text = f'$(a, r^2)=($ {round(coeff, 2)}, {round(R2,2)})'
            
            axs.plot(list_date, list_val, label = text, **style)
            axs.legend()
            
        else:
            axs.plot(list_date, list_val, **style)
        
        k+=1
        
    axs.xaxis.set_major_formatter(dates.DateFormatter('%d/%m/%Y'))
    axs.xaxis.set_major_locator(dates.DayLocator(interval=intv))
    fig.autofmt_xdate()
    
    axs.semilogy()
    
    axs.set_title (f'Cumulated number of {type_graph} vs date')
    axs.set_ylabel(f'Number of {type_graph} (log scale)')
    axs.set_xlabel('Date')
    axs.grid()
    
    return list_coeff
    
    
def graph_frate (a_df, lim_date, lim_reg_cases, lim_reg_death, intv, list_country, style_cycle, fig, axs):
    k=0
    df_considered = a_df.loc[list_country, lim_date[0]:lim_date[1]]
    list_date = df_considered.columns
    
    for country, style in zip(list_country, style_cycle()):
        list_val = df_considered.loc[country]
        axs.plot(list_date, list_val, label = country, **style)
        k+=1
    
    axs.xaxis.set_major_formatter(dates.DateFormatter('%d/%m/%y'))
    axs.xaxis.set_major_locator(dates.DayLocator(interval=intv))
    fig.autofmt_xdate()
        
    axs.set_title ('Fatality rate vs date')
    axs.set_ylabel('Fatality rate')
    axs.set_xlabel('Date')
    axs.grid()
    
def graph_grate (a_df, lim_date, lim_reg, intv, list_country, style_cycle, list_coeff, fig, axs):
    k=0
    df_considered = a_df.loc[list_country, lim_date[0]:lim_date[1]]
    list_date = df_considered.columns
    
    for country, regression, style in zip(list_country, lim_reg[0], style_cycle()):
        list_val = df_considered.loc[country]
        
        if regression:
            """
            coeff = (list_coeff[k]-1)*100
            axs.plot([list_date[0], list_date[-1]], [coeff, coeff], '--', color=colors[k], linewidth = 0.5)
            """
            print(None)
        axs.plot(list_date, list_val, label = country, **style)
        
        k+=1
    
    axs.xaxis.set_major_formatter(dates.DateFormatter('%d/%m/%y'))
    axs.xaxis.set_major_locator(dates.DayLocator(interval=intv))
    fig.autofmt_xdate()
        
    axs.set_title ('Growth rate of cumulated cases vs date')
    axs.set_ylabel('Growth rate (%)')
    axs.set_xlabel('Date')
    axs.grid()
    
def graph_delta (a_df, lim_date, lim_reg_cases, lim_reg_death, intv, list_country, style_cycle, type_graph, fig, axs):
    df_considered = a_df.loc[list_country, lim_date[0]:lim_date[1]]
    list_date = df_considered.columns
    
    for country, style in zip(list_country, style_cycle()):
        list_val = df_considered.loc[country]
        
        if country != 'US':
            axs.plot(list_date, list_val, label = country, **style)
        else:
            axs2 = axs.twinx()
            axs2.plot(list_date, list_val, label = country, **style)
            axs2.set_ylabel(f'$\Delta$ {type_graph} (US)', color=style['color'])
            axs2.tick_params(axis='y', labelcolor=style['color'])

    
    axs.xaxis.set_major_formatter(dates.DateFormatter('%d/%m/%y'))
    axs.xaxis.set_major_locator(dates.DayLocator(interval=intv))
    fig.autofmt_xdate()
    axs.set_xlabel('Date')
    axs.set_ylabel(f'$\Delta$ {type_graph}')
    axs.set_title (f'New {type_graph} compared to d-1')
    axs.grid()
    
def legend (list_country, style_cycle):
    handles, labels = [], []
    for label, style in zip(list_country, style_cycle):
        handles.append(mlines.Line2D([], [], **style))
        labels.append(label)
        
    return handles, labels
    
    
def plot (list_df, lim_date, lim_reg_cases, lim_reg_death, intv, list_country, style_cycle):
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
    
    list_coeff = graph_C_and_D (list_df[0], lim_date, lim_reg_cases, intv, list_country, style_cycle, 'cases', fig1, axs1[0][0])
    graph_C_and_D (list_df[1], lim_date, lim_reg_death, intv, list_country, style_cycle, 'death', fig1, axs1[1][0])
    graph_frate(list_df[5], lim_date, lim_reg_cases, lim_reg_death, intv, list_country, style_cycle, fig1, axs1[0][1])
    graph_grate(list_df[6], lim_date, lim_reg_cases, intv, list_country, style_cycle, list_coeff, fig1, axs1[1][1])
    
    graph_C_and_D (list_df[0], lim_date, lim_reg_cases, intv, list_country, style_cycle, 'cases', fig2, axs2[0][0])
    graph_C_and_D (list_df[1], lim_date, lim_reg_death, intv, list_country, style_cycle, 'death', fig2, axs2[1][0])
    graph_delta (list_df[3], lim_date, lim_reg_cases, lim_reg_death, intv, list_country, style_cycle, 'cases', fig2, axs2[0][1])
    graph_delta (list_df[4], lim_date, lim_reg_cases, lim_reg_death, intv, list_country, style_cycle, 'death', fig2, axs2[1][1])
    
    handles, labels = legend (list_country, style_cycle)
    
    fig1.legend(handles, labels, loc="center right", borderaxespad=0.5)
    fig1.subplots_adjust(right=0.87)
    fig2.legend(handles, labels, loc="center right", borderaxespad=0.5)
    fig2.subplots_adjust(right=0.87)
    
    
    logo = image.imread('https://raw.githubusercontent.com/CleHou/COVID-19-Data-Analysis-Project/master/99-Other/99.1-Logo/Logo2_200px.png')
    fig1.figimage(logo, 30, 20, zorder=3)
    fig2.figimage(logo, 30, 30, zorder=3)
    
    if len(list_country) >1:
        fig1.suptitle(f'Covid-19 situation on {long_date}', fontsize=16)
        fig2.suptitle(f'Covid-19 situation on {long_date}', fontsize=16)
        
        file_paths = creation_folder ([f'/1.1 - Daily/{month}', f'/1.5 - Previews/{month}'])
        
        fig1.savefig(os.path.normcase(file_paths[0] + f'{short_date}_GR.pdf'), format='pdf', dpi=200)
        fig1.savefig(os.path.normcase(file_paths[1] + f'{short_date}_preview_GR.png'), format='png', dpi=300) #Preview for publishing
        
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
            fig1.suptitle(f'Covid-19 situation for {list_country[-1]}\n{long_date}', fontsize=16)
            fig2.suptitle(f'Covid-19 situation for {list_country[-1]}\n{long_date}', fontsize=16)
            
            file_paths = creation_folder ([f'/1.4 - Country/{list_country[-1]}/{month}', f'/1.5 - Previews/{month}'])
        
            fig1.savefig(os.path.normcase(file_paths[0] + f'{short_date}_{list_country[-1]}_GR.pdf'), format='pdf', dpi=200)
            fig1.savefig(os.path.normcase(file_paths[1] + f'{short_date}_{list_country[-1]}_preview_GR.png'), format='png', dpi=300) #Preview for publishing
        
            fig2.savefig(os.path.normcase(file_paths[0] + f'{short_date}_{list_country[-1]}.pdf'), format='pdf', dpi=200)
            fig2.savefig(os.path.normcase(file_paths[1] + f'{short_date}_{list_country[-1]}_preview.png'), format='png', dpi=300) #Preview for publishing
    
    plt.show()
            
    
def graph_stack (new_df, lim_date, intv, style_cycle_stack, type_graph, incrementxy, fig, axs):
    df_considered = new_df.loc[:, lim_date[0]:lim_date[1]]
    list_date = df_considered.columns

    prev_val = 0
    for country in df_considered.index:
        final_val = int(df_considered.loc[country, lim_date[1]])
        new_val = final_val + prev_val
        #axs.annotate('+'+str(final_val), xy=(list_date[-1], new_val), xytext = (list_date[-32], new_val-incrementxy),
         #  arrowprops=dict(facecolor='black', arrowstyle="->"))
        prev_val += final_val
    
    axs.grid(alpha=0.4, zorder=4)    
    stacks = axs.stackplot(list_date, df_considered, labels = new_df.index, colors = style_cycle_stack[0][:len(new_df.index)])
    for stack, hatch in zip(stacks, style_cycle_stack[1]):
        stack.set_hatch(hatch)
    
    axs.xaxis.set_major_formatter(dates.DateFormatter('%d/%m/%y'))
    axs.xaxis.set_major_locator(dates.DayLocator(interval=intv))
    fig.autofmt_xdate()
    
    axs.set_title (f'Number of confirmed {type_graph} vs date')
    axs.set_ylabel(f'Number of {type_graph}')
    axs.set_xlabel('Date')
    
    
def plot_stack (list_df, lim_date, intv, list_country, style_cycle_stack):
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
    
    graph_stack (new_cases_df, lim_date, intv, style_cycle_stack, 'cases', 50000, fig, axs[0])
    graph_stack (new_death_df, lim_date, intv, style_cycle_stack, 'death', 500  , fig, axs[1])
    
    handles, labels = axs[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="center right", borderaxespad=0.5)
    plt.subplots_adjust(right=0.86)
    
    fig.suptitle(f'Covid-19 situation on {long_date}', fontsize=16)
    
    logo = image.imread('https://raw.githubusercontent.com/CleHou/COVID-19-Data-Analysis-Project/master/99-Other/99.1-Logo/Logo2_200px.png')
    fig.figimage(logo, 30, 20, zorder=3)
    
    file_paths = creation_folder ([f'/1.3 - Stack/{month}', f'/1.5 - Previews/{month}'])
    fig.savefig(os.path.normcase(file_paths[0] + f'{short_date}_stack.pdf'), format='pdf', dpi=200)
    fig.savefig(os.path.normcase(file_paths[1] + f'{short_date}_preview_stack.png'), format='png', dpi=300) #Preview for publishing
    
    
def to_print (list_df, list_country):
    
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
    last_date = datetime.datetime.strptime(list_df[0].columns[-1], "%m/%d/%y").date()
    
    delta = (today_date-last_date).days
    
    if delta > 1 :
        short_date = last_date.strftime("%Y-%m-%d")
        print('\a')
        print(f'Data were last updated {delta} days ago, on {short_date}')
        conti = input('Do you wish to update the data? [y/n/c]?')
        
        if conti == 'y':
            list_df, to_replace = import_df_from_I()
            last_date =datetime.datetime.strptime(list_df[0].columns[-1], "%m/%d/%y").date()
            delta2 = (today_date-last_date).days
            
            if delta2 > 1 :
                short_date = last_date.strftime('%Y-%m-%d')
                print(f'Latest data published on {short_date}, i.e. {delta2} days ago')
                stop = input('Do you wish to continue ? [y/n]?')
                    
                if stop == 'n':
                    sys.exit('Script stoped')
            else:
                print('Data updated')
 
        elif conti == 'c':
            sys.exit('Script stoped')
            
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
delta_df11 = smoothed_fun (delta_df11, 7)
list_df.append(delta_df11) #list_df[3]

delta_df12 = delta_df(list_df[1])
delta_df12 = smoothed_fun (delta_df12, 7)
list_df.append(delta_df12) #list_df[4]

frate = fatality_rate (list_df)
list_df.append(frate) #list_df[5]

grate = growth_rate (list_df[0])
grate2 = smoothed_fun (grate, 2)
list_df.append(grate2) #list_df[6]
list_df.append(grate)

color_c = cycler(color=['#386cb0', '#D45050', '#7fc97f', '#9A46C4', '#F08328', '#a6cee3', 'k'])
marker_c = cycler(marker=['2', 4, 'o', 'x', 's'])
line_c = cycler(linestyle=['solid', 'dashed'])
markevery_c = cycler(markevery=[0.3])
linewidth_c = cycler(linewidth=[0.75])
list_hatches = ['-', '+', 'x', '\\', '*', 'o', 'O', '.']
cycle_BW = color_c[-1:] * markevery_c * linewidth_c *line_c * marker_c
cycle_color = line_c[:1] * markevery_c * linewidth_c * cycler(marker=[None]) * color_c
cycle_BW_stack = [['#d6d6d6' for h in list_hatches],list_hatches]
cycle_color_stack = [color_c.by_key()['color'],[None for h in list_hatches]]

style_cycle = cycle_color
style_stack = cycle_color_stack

#For a list of country 4 graphs
start_date=pandas.to_datetime('2020-03-15', format='%Y-%m-%d')
end_date = list_df[0].columns[-1]
#end_date=pandas.to_datetime('2020-05-07', format='%Y-%m-%d')
len_tot = len(list(list_df[0].columns.values))-1

lim_date = [start_date, end_date]

reg_cases = [False, False, False, False]
beg_reg_cases = [pandas.to_datetime(x, format='%Y-%m-%d') for x in ['2020-10-15', '2020-03-15', '2020-03-15', '2020-03-15']]
end_reg_cases = [pandas.to_datetime('2020-11-09', format='%Y-%m-%d'), end_date, end_date, end_date]
offset_plot_cases = [[20,7] for k in range(len(reg_cases))]
lim_reg_cases = [reg_cases, beg_reg_cases, end_reg_cases, offset_plot_cases]

reg_death = [False, False, False, False] 
beg_reg_death = [pandas.to_datetime(x, format='%Y-%m-%d') for x in ['2020-03-15', '2020-03-15', '2020-03-15', '2020-03-15']]
end_reg_death = [end_date, end_date, end_date, end_date]
offset_plot_death = [[20,7] for k in range(len(reg_cases))]
lim_reg_death = [reg_death, beg_reg_death, end_reg_death, offset_plot_death]

intv = 21
list_country = ['France', 'US', 'Italy', 'Germany']

plot (list_df, lim_date, lim_reg_cases, lim_reg_death, intv, list_country, style_cycle)
to_print (list_df, list_country)

#For a list of country Stacked graph
start_date = pandas.to_datetime('2020-01-20', format='%Y-%m-%d')
lim_date = [start_date, end_date]
intv = 21
list_country = ['United Kingdom', 'Italy', 'Spain', 'France', 'US']

plot_stack (list_df, lim_date, intv, list_country, style_stack)

#One Country or worldwide
start_date = pandas.to_datetime('2020-01-20', format='%Y-%m-%d')
end_date = list_df[0].columns[-1]
lim_date = [start_date, end_date]

reg_cases = [False]
beg_reg_cases = [pandas.to_datetime(x, format='%Y-%m-%d') for x in ['2020-03-15']]
end_reg_cases = [end_date]
offset_plot_cases = [[20,7]]
lim_reg_cases = [reg_cases, beg_reg_cases, end_reg_cases, offset_plot_cases]

reg_death = [False] 
beg_reg_death = [pandas.to_datetime(x, format='%Y-%m-%d') for x in ['2020-03-15']]
end_reg_death = [end_date]
offset_plot_death = [[20,7]]
lim_reg_death = [reg_death, beg_reg_death, end_reg_death, offset_plot_death]

intv = 21
list_country = ['World']

plot (list_df, lim_date, lim_reg_cases, lim_reg_death, intv, list_country, style_cycle)

start_date = pandas.to_datetime('2020-06-05', format='%Y-%m-%d')
lim_date = [start_date, end_date]
reg_cases = [True]
beg_reg_cases = [pandas.to_datetime(x, format='%Y-%m-%d') for x in ['2020-10-15']]
end_reg_cases = [pandas.to_datetime(x, format='%Y-%m-%d') for x in ['2020-11-09']]
offset_plot_cases = [[20,7]]
lim_reg_cases = [reg_cases, beg_reg_cases, end_reg_cases, offset_plot_cases]

reg_death = [False] 
beg_reg_death = [pandas.to_datetime(x, format='%Y-%m-%d') for x in ['2020-03-11']]
end_reg_death = [end_date]
offset_plot_death = [[20,7]]
lim_reg_death = [reg_death, beg_reg_death, end_reg_death, offset_plot_death]

intv = 14
list_country_fr = ['France']
plot (list_df, lim_date, lim_reg_cases, lim_reg_death, intv, list_country_fr, style_cycle)
to_print (list_df, list_country)

#print (list(list_df[0].index)) #Liste des pays

