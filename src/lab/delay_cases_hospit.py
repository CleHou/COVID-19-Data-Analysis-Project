#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 25 10:34:40 2021

@author: Clement
Lab #1: delay between cases and hospti / ICU
"""
import pandas
import os
import matplotlib.pyplot as plt
import matplotlib.image as image
import matplotlib.ticker as ticker
from matplotlib import dates
import numpy
import datetime
import tqdm
import sys
from cycler import cycler

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from gen_fct import df_fct
from gen_fct import file_fct

class Cycler:
    def __init__ (self, type_style):
        self.color = cycler(color=['#386cb0', '#D45050', '#7fc97f', '#9A46C4', '#F08328', '#a6cee3', 'k'])
        self.color_fill = cycler(color=['#4cdc2f', '#ffb266', '#e72705'])
        self.color_fill_BW = cycler(color=['#f5f5f5', '#d6d6d6', '#808080'])
        self.alpha = cycler(alpha=[0.8, 0.2])
        self.markevery = cycler(markevery=[0.1])
        self.linewidth = cycler(linewidth=[0.75])
        self.marker = cycler(marker=['2', 4, 'o', 'x', 's', None])
        self.line = cycler(linestyle=['solid', 'dashed'])
        self.type_style=type_style

    def main(self):
        if self.type_style == 'color':
            style_cycle = self.line * self.linewidth * self.marker[-1:] * self.color
            
        else:
            style_cycle = self.color[-1:] * self.markevery_c * self.linewidth
        
        return style_cycle
    
    
class PlotCHI:
    def __init__ (self, intv, fig_size, plotting_dates, style_cycle, para_to_plot, sub_dates):
        self.french_df= df_fct.import_df(['Fra_Nat'],['processed'])[0]
        self.french_df = self.french_df.rolling(window = 7, center=False).mean()
        
        self.intv = intv
        self.plotting_dates = [pandas.to_datetime(plotting_dates[0])]
        self.style_cycle = style_cycle
        self.root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        self.fig_size = fig_size
        self.para_to_plot = para_to_plot
        
        if plotting_dates[1] == 'last':
            self.plotting_dates.append(self.french_df.index.get_level_values('date').unique()[-1])
            
        else:
            self.plotting_dates.append(pandas.to_datetime(plotting_dates[0]))
            
        self.sub_dates = [[pandas.to_datetime(date) for date in element] for element in sub_dates]
            
            
    def plot_3 (self):
        long_date = self.plotting_dates[-1].strftime("%d %B, %Y")
        month = self.plotting_dates[-1].strftime("%m - %B")
        short_date = self.plotting_dates[-1].strftime("%Y-%m-%d")
        
        fig, axs = plt.subplots(1,2, figsize=self.fig_size, num=f'Correlation cases / hospit on {short_date}')
        
        list_df = [self.french_df, self.df_derivate]
        
        for df, axes in numpy.ravel(axs):
            for para, style in zip(self.para_to_plot, self.style_cycle()):
                #axes.plot(self.french_df.loc[self.plotting_dates[0]:self.plotting_dates[-1], para], label=para, **style)
                axes.plot(df.loc[self.plotting_dates[0]:self.plotting_dates[-1], para], label=para, **style)
            
            axes.set_title(f'Corrélation cas / hospit / réa on {short_date}')
            axes.set_ylabel('Nombre')
            axes.set_xlabel('Date')
            axes.grid()
            axes.xaxis.set_major_formatter(dates.DateFormatter('%d/%m/%Y'))
            axes.xaxis.set_major_locator(dates.DayLocator(interval=self.intv))
            
        fig.autofmt_xdate()
        handles, labels = axs[0].get_legend_handles_labels()
        fig.legend(handles, labels, loc="center right", borderaxespad=0.5)
        #plt.subplots_adjust(right=0.90)
        #fig.suptitle(f"French data on\n{long_date}", size=16)
        fig.autofmt_xdate()
        
        fig.text(0.83, 0.05, 'Data source: Santé Publique France \nAnalysis: C.Houzard', fontsize=8)
        
        #file_fct.save_fig (fig, 'France_Gen_Situation', self.plotting_dates[1])
        
    def plot_as_fct_of (self):
        for set_of_date in self.sub_dates:
            short_date_st = set_of_date[0].strftime("%Y-%m-%d")
            short_date_en = set_of_date[1].strftime("%Y-%m-%d")
            
            fig, axs = plt.subplots(1,1, figsize=self.fig_size, num=f'Correlation cases / hospit btw \n {short_date_st}-{short_date_en}')
            
            list_para = [['delta_cases', 'hospitalises']]
            
            for para, style in zip(list_para, self.style_cycle()):
                axs.plot(self.french_df.loc[self.plotting_dates[0]:self.plotting_dates[-1], para[0]],
                         self.french_df.loc[self.plotting_dates[0]:self.plotting_dates[-1], para[1]],
                         label=para, **style)
                
    def find_max (self):
        df_max = pandas.DataFrame(index=[element[0] for element in self.sub_dates],
                                  columns = self.para_to_plot)
        
        for set_of_date in self.sub_dates:
            for a_col in df_max.columns:
                df_max.loc[set_of_date[0], a_col] = self.french_df.loc[set_of_date[0]:set_of_date[1], a_col].idxmax()
        print(df_max)
        
    def derivate (self):
        self.df_derivate = self.french_df.loc[:,self.para_to_plot].diff()
        self.df_derivate = self.df_derivate.rolling(window = 7, center=True).mean()
        self.df_derivate.plot()
        
        
        
    def main (self):
        self.derivate ()
        self.plot_3()
        #self.plot_as_fct_of()
        #self.find_max()
        
        
        
        
if __name__ == "__main__":
    fig_size = (14,7)
    intv=21
    cycle = Cycler('color').main()
    para_to_plot = ['reanimation', 'hospitalises', 'delta_cases']
    plotting_dates = ['2020-03-15', 'last']
    sub_dates = [['2020-08-15', '2020-12-31']]
    
    PlotCHI(intv, fig_size, plotting_dates, cycle, para_to_plot, sub_dates).main()
            
        
                                        
            
    
