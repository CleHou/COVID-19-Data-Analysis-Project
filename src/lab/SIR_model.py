#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 26 17:53:26 2022

@author: Clement
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
    
    
class PlotIRS:
    def __init__ (self, I_para, R_para, intv, fig_size, plotting_dates, style_cycle, para_to_plot, legend_name):
        self.french_df= df_fct.import_df(['Fra_Nat_v2'],['processed'])[0]
        self.I_para = I_para
        self.R_para = R_para
        
        self.intv = intv
        self.plotting_dates = [pandas.to_datetime(plotting_dates[0])]
        self.style_cycle = style_cycle
        self.root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        self.fig_size = fig_size
        self.para_to_plot = para_to_plot
        self.legend_name = [legend_name[key] for key in self.para_to_plot]
        
        self.pop = 67114995
        
        if plotting_dates[1] == 'last':
            self.plotting_dates.append(self.french_df.index.get_level_values('date').unique()[-1])
            
        else:
            self.plotting_dates.append(pandas.to_datetime(plotting_dates[0]))
            
    def pre_processing (self):
        self.french_df['I'] = self.french_df['cases'].rolling(window=self.I_para, min_periods=1).sum()
        self.french_df['R'] = self.french_df['cases'].rolling(window=self.R_para+self.I_para, min_periods=1).sum() - self.french_df['I']
        self.french_df['S'] = self.pop - (self.french_df['I'] + self.french_df['R'])
        print(self.french_df)
        
    def plot_ov (self):
        long_date = self.plotting_dates[-1].strftime("%d %B, %Y")
        month = self.plotting_dates[-1].strftime("%m - %B")
        short_date = self.plotting_dates[-1].strftime("%Y-%m-%d")
        
        fig, axs = plt.subplots(1,1, figsize=self.fig_size, num=f'SIR model for France on {short_date}')
        
        
        axes=axs
        stacks = axs.stackplot(self.french_df.index, self.french_df[self.para_to_plot].T.values, labels = self.legend_name)
        
        axes.set_title(f'SIR model for France on\n{short_date}')
        axes.set_ylabel('Nombre de cas')
        axes.set_xlabel('Date')
        axes.grid()
        axes.xaxis.set_major_formatter(dates.DateFormatter('%d/%m/%Y'))
        axes.xaxis.set_major_locator(dates.DayLocator(interval=self.intv))
        
        
        prop_axs = axes.secondary_yaxis('right', functions=(self.nb_to_prop, self.prop_to_nb))
        prop_axs.set_ylabel('Prop. de la population (%)')
        
        
        fig.autofmt_xdate()
        handles, labels = axes.get_legend_handles_labels()
        fig.legend(handles, labels, loc="center right", borderaxespad=0.5)
        plt.subplots_adjust(right=0.85)
        #fig.suptitle(f"French data on\n{long_date}", size=16)
        fig.autofmt_xdate()
        
        fig.text(0.83, 0.05, 'Data source: Santé Publique France \nAnalysis: C.Houzard', fontsize=8)
        
        file_fct.save_fig (fig, 'French_SIR', self.plotting_dates[1])
        
    def nb_to_prop (self, nb):
        return nb/self.pop * 100
    
    def prop_to_nb (self, prop):
        return prop * self.pop * 0.01
        
        
        
    def main (self):
        self.pre_processing()
        self.plot_ov()
        #self.derivate ()
        #self.plot_3()
        #self.plot_as_fct_of()
        #self.find_max()
        
if __name__ == "__main__":
    fig_size = (14,7)
    intv=21
    cycle = Cycler('color').main()
    para_to_plot = ['S', 'I', 'R']
    para_to_plot = ['I', 'R', 'S']
    plotting_dates = ['2020-05-13', 'last']
    sub_dates = [['2020-08-15', '2020-12-31']]
    legend = {'S': 'Suspected', 'I':'Infected', 'R':'Recovered'}
    
    I_para = 7
    R_para = 30*4
    
    A = PlotIRS(I_para, R_para, intv, fig_size, plotting_dates, cycle, para_to_plot, legend)
    B = A.main()
    C = A.french_df
        