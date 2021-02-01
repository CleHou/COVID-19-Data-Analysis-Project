#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 00:56:55 2021

@author: Clement
"""
import pandas
from matplotlib import dates
import matplotlib.pyplot as plt
import numpy
from sklearn import linear_model
from sklearn.metrics import r2_score
import os
import matplotlib.lines as mlines
import matplotlib.image as image
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from gen_fct import df_fct
from gen_fct import file_fct

class LinearRegression():
    def __init__ (self, prop_df):
        pass
    
class GeneralSituationGraph ():
    def __init__ (self, prop_df, plotting_dates, style_cycle, intv):
        self.world_df = df_fct.import_df(['World_JH'],['processed'])[0]
        self.prop_df = prop_df
        self.list_countries = self.prop_df.index
        self.intv = intv
        self.plotting_dates = [pandas.to_datetime(plotting_dates[0])]
        self.style_cycle = style_cycle
        self.root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        
        if plotting_dates[1] == 'last':
            self.plotting_dates.append(self.world_df.index.get_level_values('date').unique()[-1])
            
        else:
            self.plotting_dates[1].append(pandas.to_datetime(plotting_dates[0]))
            
            
    def graph_C_and_D (self, type_graph, fig, axs):
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
        
        
    def graph_frate (self fig, axs):
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
        
    def graph_grate (self, list_coeff, fig, axs):
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
        
    def graph_delta (self, type_graph, fig, axs):
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
        
    def legend (self):
        handles, labels = [], []
        for label, style in zip(list_country, style_cycle):
            handles.append(mlines.Line2D([], [], **style))
            labels.append(label)
            
        return handles, labels
        
        
    def plot (self):
        long_date = self.plotting_dates[1].strftime("%B, %d %Y")
        month = self.plotting_dates[1].strftime("%m - %B")
        year = self.plotting_dates[1].strftime("%Y")
        short_date = self.plotting_dates[1].strftime("%d-%m-%Y")
        
        if len(self.list_countries) >1:
            fig1, axs1 = plt.subplots(2, 2, num='Covid-19 plot 1/2 on ' + long_date, figsize=(15,15)) #Grid 2x2
            fig2, axs2 = plt.subplots(2, 2, num='Covid-19 plot 2/2 on ' + long_date, figsize=(15,15)) #Grid 2x2
            
        else:
            fig1, axs1 = plt.subplots(2, 2, num=f'Covid-19 plot 1/2 {self.list_countries[-1]}, {short_date}', figsize=(15,15)) #Grid 2x2
            fig2, axs2 = plt.subplots(2, 2, num=f'Covid-19 plot 2/2 {self.list_countries[-1]}, {short_date}', figsize=(15,15)) #Grid 2x2
            
        fig1.text(0.87, 0.05, 'Source: John Hopkins University \nGraph: C.Houzard', fontsize=8)
        fig2.text(0.87, 0.05, 'Source: John Hopkins University \nGraph: C.Houzard', fontsize=8)
        
        list_coeff = graph_C_and_D ('cases', fig1, axs1[0][0])
        graph_C_and_D ('death', fig1, axs1[1][0])
        graph_frate(fig1, axs1[0][1])
        graph_grate(list_coeff, fig1, axs1[1][1])
        
        graph_C_and_D ('cases', fig2, axs2[0][0])
        graph_C_and_D ('death', fig2, axs2[1][0])
        graph_delta ('cases', fig2, axs2[0][1])
        graph_delta ('death', fig2, axs2[1][1])
        
        handles, labels = legend (self)
        
        fig1.legend(handles, labels, loc="center right", borderaxespad=0.5)
        fig1.subplots_adjust(right=0.87)
        fig2.legend(handles, labels, loc="center right", borderaxespad=0.5)
        fig2.subplots_adjust(right=0.87)
        
        
        logo = image.imread('{current}/data/logo/Logo2_200px.png')
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
        
    def main (self):
        print(self.world_df)
    
class StackGraph ():
    def __init__(self):
        pass
    
prop_df = pandas.DataFrame(index=['France', 'US', 'Italy', 'Germany'],
                             columns=['Reg', 'Start_reg', 'End_reg'],
                             data=[[False, numpy.nan, numpy.nan] for k in range (4)])

plotting_dates = ['2020-03-15', 'last']
GeneralSituationGraph(prop_df, plotting_dates, 21).main()
