#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 11 18:29:39 2021

@author: Clement
"""
import pandas
import numpy
import os
import sys
import geopandas as gpd
import tqdm

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from gen_fct import df_fct
from gen_fct import file_fct

class WorldDataSets():
    pass #Normal + Maps

class USDataSets():
    pass #All states + Maps + Testing
class FrenchDataSets ():
    pass #Nat, reg, dpt, maps, testing, indic

class WorldDataSet:
    def __init__ (self):
        self.df_cases = pandas.DataFrame()
        self.df_death = pandas.DataFrame()
        self.df_fra = pandas.DataFrame()
        self.df_world = pandas.DataFrame()
    
    def import_db(self):
        self.df_cases, self.df_death, self.df_fra = df_fct.import_df(['World_JH_cases', 'World_JH_death', 'Fra_GenData'],
                                                                     ['raw' for x in range(3)])
        
    
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
            a_df = a_df.replace('Korea, South', 'South Korea')
            a_df = a_df.set_index(['Country/Region', 'date'])
            a_df.index = a_df.index.rename(['country', 'date'])
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
        
    def complete_data (self):
        for type_data in ['cases', 'death']:
            self.df_world.loc[:,f'delta_{type_data}'] = self.df_world.loc[:,type_data].groupby(level='country').diff()
            self.df_world.loc[:,f'growth_{type_data}'] = self.df_world.loc[:,type_data].groupby(level='country').pct_change()
            self.df_world.loc[:,f'weekly_growth_{type_data}'] = self.df_world.loc[:,type_data].groupby(level='country').pct_change(periods=7)
        
        self.df_world.loc[:,'fatality_rate'] = self.df_world.loc[:,'cases'].div(self.df_world.loc[:,'death'])
    
    def smooth (self, period, center):
        self.df_world = self.df_world.rolling(window = period, center=center).mean()
            
    def main(self, period, center):
        self.import_db()
        self.clean_up_JH ()
        self.clean_up_Fra_gen ()
        self.ajust_values ()
        self.complete_data ()
        self.smooth (period, center)
        df_fct.export_df([['Fra_GenData_full', self.df_fra],
                          ['World_JH', self.df_world]], 
                         ['processed', 'processed'])
        return self.df_world
        
    
class MapsDataSet:
    def __init__ (self):
        variables = ['World_JH', 'Fra_GenData', 'US_JH_cases', 'US_JH_death',
                          'Countries_LatLong', 'US_States_shapefile', 'Fra_Regions_shapefile', 'Fra_Departements_shapefile',
                          'World_pop', 'US_pop', 'Fra_pop', 'Dept_reg']
        
        list_prop_import = ['processed', 'raw', 'raw', 'raw',
                            'raw', 'raw', 'raw', 'raw', 
                            'raw', 'raw', 'raw', 'raw']
        for a_var , a_prop in zip(variables, list_prop_import):
             setattr(self, a_var, df_fct.import_df([a_var],[a_prop])[0])
             
        self.world_shpe = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
        self.df_us = pandas.DataFrame()
        self.df_fra = pandas.DataFrame()
        self.df_fra_dpt = pandas.DataFrame()
             
    def clean_up_CountryLatLong (self):
        self.Countries_LatLong = self.Countries_LatLong.set_index('name')
        self.Countries_LatLong.index = self.Countries_LatLong.index.rename('country')
        self.Countries_LatLong = self.Countries_LatLong.loc[:,['latitude', 'longitude']]
        
    def clean_up_WorldShp(self):
        self.world_shpe = self.world_shpe.set_index('name')
        self.world_shpe.index = self.world_shpe.index.rename('country')
        self.world_shpe = self.world_shpe.rename(index={'United States of America': 'US'})
        self.world_shpe = self.world_shpe.loc[:,['geometry']]
        
    def clean_up_USShp (self):
        self.US_States_shapefile = self.US_States_shapefile.set_index('NAME')
        self.US_States_shapefile.index = self.US_States_shapefile.index.rename('state')
        self.US_States_shapefile = self.US_States_shapefile.loc[:,'geometry']
    
    def clean_up_FraShp (self):
        self.Fra_Regions_shapefile = self.Fra_Regions_shapefile.set_index('region')
        self.Fra_Regions_shapefile = self.Fra_Regions_shapefile.loc[:,'geometry']
        
    def clean_up_pop_World (self):
        self.World_pop = self.World_pop[(self.World_pop.loc[:, 'Time']==2020) & (self.World_pop.loc[:, 'Variant']=='Medium')]
        self.World_pop = self.World_pop.drop(['LocID', 'VarID', 'Variant', 'Time', 'MidPeriod', 'PopMale', 'PopFemale', 'PopDensity'], axis=1)
        self.World_pop = self.World_pop.set_index('Location')
        self.World_pop.index = self.World_pop.index.rename('country')
        
        L1 = ['United Republic of Tanzania', 'United States of America', 'Russian Federation', 'Bolivia (Plurinational State of)', 'Venezuela (Bolivarian Republic of)', "Lao People's Democratic Republic", 'Viet Nam', 
              "Dem. People's Republic of Korea", 'Republic of Korea',"Iran (Islamic Republic of)", "Syrian Arab Republic", "Republic of Moldova", "China, Taiwan Province of China", "Brunei Darussalam", 'Western Sahara', 
              'Democratic Republic of the Congo', 'Dominican Republic', 'Falkland Islands (Malvinas)',
                                'Central African Republic', 'Equatorial Guinea', 'Eswatini', 'State of Palestine', 'Solomon Islands', 'Bosnia and Herzegovina', 'North Macedonia', 'South Sudan']
        L2 = ['Tanzania', 'US', 'Russia', 'Bolivia', 'Venezuela', 'Laos', 'Vietnam', 
              'North Korea', 'Korea, South', 'Iran', 'Syria', 'Moldova', 'Taiwan', 'Brunei', 'W. Sahara', 
              'Dem. Rep. Congo', 'Dominican Rep.', 'Falkland Is.', 'Central African Rep.', 'Eq. Guinea', 'eSwatini', 'Palestine', 'Solomon Is.', 
                                'Bosnia and Herz.', 'Macedonia', 'S. Sudan']
        
        replace_dic = dict(zip(L1,L2))
        self.World_pop = self.World_pop.rename(index=replace_dic)
        self.World_pop = self.World_pop.drop_duplicates()
        self.World_pop = self.World_pop.rename(columns={'PopTotal':'Population'})
        
    def clean_up_pop_US (self):
        self.US_pop = self.US_pop.set_index('NAME')
        self.US_pop.index = self.US_pop.index.rename('state')
        self.US_pop = self.US_pop.rename(columns={'POPESTIMATE2019':'Population'})
        
    def clean_up_pop_Fra (self):
        self.Fra_pop = self.Fra_pop.set_index('Région')
        self.Fra_pop.index = self.Fra_pop.index.rename('region')
        
    def clean_up_data_US (self):
        list_df_us = [self.US_JH_cases, self.US_JH_death]
        list_name = ['cases', 'death']
        
        list_return = []
        for a_df, a_name in zip(list_df_us, list_name):
            a_df = a_df.groupby('Province_State').sum()
            
            if 'Population' in a_df.columns:
                a_df = a_df.drop(columns=['UID', 'code3', 'FIPS', 'Lat', 'Long_', 'Population'])
            else:
                a_df = a_df.drop(columns=['UID', 'code3', 'FIPS', 'Lat', 'Long_'])
                
            a_df.columns = pandas.to_datetime(a_df.columns)
            a_df = pandas.melt(a_df.reset_index(), id_vars=["Province_State"], value_vars=a_df.columns, var_name='date', value_name=a_name)
            a_df.loc[:,"date"] = pandas.to_datetime(a_df.loc[:,"date"])
            a_df = a_df.set_index(['Province_State', 'date'])
            a_df.index = a_df.index.rename(['state', 'date'])
            list_return.append(a_df)
            
        self.df_us = pandas.concat(list_return, axis=1).sort_index()
        self.df_us = self.add_para ('df_us', 'state')
        
    def clean_up_Fra_reg (self):
        self.df_fra = self.Fra_GenData[(self.Fra_GenData.loc[:,'granularite']=='region') & (self.Fra_GenData.loc[:,'source_type']=='opencovid19-fr')]
        self.df_fra.loc[:,'date'] = pandas.to_datetime(self.df_fra.loc[:,'date'], format='%Y-%m-%d')
        self.df_fra = self.df_fra.set_index(['maille_nom', 'date']).sort_index()
        self.df_fra.index = self.df_fra.index.rename(['region', 'date'])
        self.df_fra = self.df_fra.loc[:,'deces']
        self.df_fra = self.df_fra.rename(columns={'deces':'death'})
        
    def clean_up_Fra_dpt (self):
        df_sorted2 = df_main[(df_main.loc[:,'granularite']=='departement') & (df_main.loc[:,'source_type']=='sante-publique-france-data')]
        df_sorted2.loc[:,'date'] = pandas.to_datetime(df_sorted2.loc[:,'date'], format='%Y-%m-%d')
        df_sorted2.loc[:,'maille_code'] = df_sorted2.loc[:,'maille_code'].apply(lambda dpt: dpt[4:])
        df_sorted2.set_index(['date', 'maille_code'], inplace=True)
        
    def clean_up_reg (self):
        self.Dept_reg = Dept_reg.set_index('dep_name')
    
    def add_para (self, df, level):
        df = getattr(self, df)
        for type_data in ['cases', 'death']:
            df.loc[:,f'delta_{type_data}'] = df.loc[:,type_data].groupby(level=level).diff()
            df.loc[:,f'growth_{type_data}'] = df.loc[:,type_data].groupby(level=level).pct_change()
            df.loc[:,f'weekly_growth_{type_data}'] = df.loc[:,type_data].groupby(level=level).pct_change(periods=7)
        df.loc[:,'fatality_rate'] = df.loc[:,'cases'].div(df.loc[:,'death'])
        
        return df
    
    def rel_values (self, df):
        df = getattr(self, df)
        print(df)
        for type_data in ['cases', 'death']:
            df.loc[:, f'rel_{type_data}'] = df.loc[:, type_data].div(df.loc[:, 'Population']) #cases/1000 of hab
        
        df.loc[:,'fatality_rate'] = df.loc[:,'cases'].div(df.loc[:,'death'])
        df = df.drop(columns=['Population'])
        
        return df
    
    def append_data_world(self):
        #print(self.World_JH.index.get_level_values(0).unique())
        self.World_JH = self.World_JH.join(self.Countries_LatLong)
        self.World_JH = self.World_JH.join(self.world_shpe, how='outer')
        self.World_JH = gpd.GeoDataFrame(self.World_JH)
        
        index_WorldJH = self.World_JH.index.get_level_values(0).unique()
        for indexG in self.world_shpe.index:
            if indexG not in (index_WorldJH):
                add_index = pandas.MultiIndex.from_product([[indexG],self.World_JH.index.get_level_values(1).unique()])
                temp_df = gpd.GeoDataFrame(index=add_index, columns=self.World_JH.columns)
                try:
                    temp_df.loc[indexG, 'geometry'] = self.world_shpe.loc[indexG, 'geometry']
                    self.World_JH = self.World_JH.append(temp_df)
                    print(indexG)
                    
                except ValueError:
                    print(indexG, 'not appened')
        self.World_JH = self.World_JH.sort_index(level='country')
        
        self.World_JH = self.World_JH.join(self.World_pop)
        
        self.World_JH = self.rel_values ('World_JH')
    
    def append_data (self, df_str, shp_df_str, pop_df_str):
        df, shp_df, pop_df, = getattr(self, df_str), getattr(self, shp_df_str), getattr(self, pop_df_str)
        df = df.join(shp_df)
        df = gpd.GeoDataFrame(df)

        df = df.join(pop_df.loc[:, 'Population'], how='inner')
        
        return df
    
    def clean_up_Continent (df_Map2_cases_world, list_dfMap3_world, date):
        month = date.strftime("%m - %B")
        short_date = date.strftime("%Y-%m-%d")
        
        continent_df = pandas.read_csv('https://github.com/CleHou/COVID-19-Data-Analysis-Project/raw/master/02-Maps/country_by_continent.csv')
        list_continent = continent_df.loc[:,'Continent'].unique()
        continent_df = continent_df.set_index('Country')
        
        df_Map2_cases_world = df_Map2_cases_world.set_index('Country')
        list_dfMap3_world = [list_dfMap3_world[k].set_index('Country') for k in range(len(list_dfMap3_world))]
        
        df_Map2_cases_world = df_Map2_cases_world.join(continent_df, how='inner')
        list_dfMap3_world = [list_dfMap3_world[k].join(continent_df, how='inner') for k in range(len(list_dfMap3_world))]
        
        for a_continent in list_continent[:-1]:
            file_path = creation_folder ([f'/2.1 - Maps/Continents/{month}', f'/2.2 - Preview/Continents/{month}'])
            df_Map2_cases_world_sorted = df_Map2_cases_world[df_Map2_cases_world.loc[:,'Continent']==a_continent]
            val_lim=100
            list_parameters_world=[[hv.Dimension('Pctge_change', range=(-val_lim, +val_lim)), 'Cases', 'dC/dt', 'Country']]
            titles_world = [f'Evolution of the number of cases in {a_continent} on {short_date}']
            names_world = [f'Continents/{month}/{a_continent}_MapBalance_{short_date}.png', f'Continents/{month}/{a_continent}_MapBalance_{short_date}']
            Map2 (df_Map2_cases_world_sorted, list_parameters_world, titles_world, names_world)
            print(df_Map2_cases_world_sorted.drop(columns=['geometry']))
            
            list_dfMap3_world_sorted =  [list_dfMap3_world[k][list_dfMap3_world[k].loc[:,'Continent']==a_continent] 
                                  for k in range(len(list_dfMap3_world))]
            
            val_lim1=max_value_2 (list_dfMap3_world[0], 'Cases_per_1000_hab')
            val_lim2=max_value_2 (list_dfMap3_world[1], 'Death_per_1000_hab')
            list_parameters_world = [[hv.Dimension('Cases_per_1000_hab', range=(0, val_lim1)), 'Country'], [hv.Dimension('Death_per_1000_hab', range=(0, val_lim2)), 'Country']]
            titles_world = [f'Number of cases per 10000 inhabitant on {short_date}', f'Number of death per 10000 inhabitant on {date_plot_world}']
            source_world = '& UN for demographic data'
            names_world = [f'Continents/{month}/{a_continent}_Map_Relative_Cases_{short_date}.png', f'Continents/{month}/{a_continent}_Map_Relative_Death_{short_date}.png', 
                           f'Continents/{month}/{a_continent}_Map_Relative_Cases-Death_{short_date}']
            list_cmap_world = ['Blues', 'OrRd']
            Map3 (list_dfMap3_world_sorted, list_parameters_world, titles_world, source_world, names_world, list_cmap_world)
            print(list_dfMap3_world_sorted[0].drop(columns=['geometry']))
            
    
    def world (self):
        self.clean_up_CountryLatLong ()
        self.clean_up_WorldShp()
        self.clean_up_pop_World ()
        self.append_data_world()
        #df_fct.export_df([['World_JH_map', self.World_JH]],['processed'])
        #df_fct.export_df([['World_pop', self.World_pop]], ['processed'])
        
        return self.World_JH
    
    def us (self):
        self.clean_up_USShp ()
        self.clean_up_pop_US ()
        self.clean_up_data_US ()
        self.df_us = self.append_data('df_us', 'US_States_shapefile', 'US_pop')
        self.df_us = self.rel_values ('df_us')
        print('saving')
        import time
        start = time.time()
        df_fct.export_df([['US_JH_map', self.df_us]],['processed'])
        end = time.time()
        print(end - start)
        #df_fct.export_df([['US_pop', self.US_pop]], ['processed'])
        
        return self.df_us
    
    def fra (self):
        self.clean_up_FraShp ()
        self.clean_up_pop_Fra ()
        self.clean_up_data_Fra ()
        self.df_fra = self.append_data('df_fra', 'Fra_Regions_shapefile', 'Fra_pop')
        self.df_fra = self.rel_values ('df_fra')
        #df_fct.export_df([['Fra_reg_map', self.df_fra]],['processed'])
        #df_fct.export_df([['Fra_reg_pop', self.Fra_pop]], ['processed'])
        self.df_fra = self.df_fra.drop(columns=['geometry'])
        
        return self.df_fra
    
    def main(self):
        self.world ()
        self.us()
        self.fra()
        
        return self.World_JH
        

if __name__ == '__main__':     
    #df_world = WorldDataSet().main(7, False)
    #df_world = MapsDataSet().world()
    df_us = MapsDataSet().us()
    #df_fra = MapsDataSet().fra()

    
    
    
    
    