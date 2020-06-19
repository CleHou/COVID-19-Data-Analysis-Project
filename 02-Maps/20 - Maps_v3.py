#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 14 20:34:42 2020

@author: Clement
"""

import pandas
import numpy
import os
import datetime
import geoviews as gv
import geoviews.tile_sources as gvts
from geoviews import dim, opts
gv.extension('bokeh')
import holoviews as hv
import geopandas as gpd

def import_df_from_I ():
    partial_link = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_'
    df_cases_world = pandas.read_csv(partial_link+ 'confirmed_global.csv')
    df_death_world = pandas.read_csv(partial_link+ 'deaths_global.csv')  
    df_France = pandas.read_csv('https://github.com/CleHou/COVID-19-Data-Analysis-Project/raw/master/01-Graph/France_data.csv')
    df_cases_us = pandas.read_csv(partial_link + 'confirmed_US.csv')
    df_death_us = pandas.read_csv(partial_link + 'deaths_US.csv')
    df_fra = pandas.read_csv('https://raw.githubusercontent.com/opencovid19-fr/data/master/dist/chiffres-cles.csv')
    
    countries_loc = pandas.read_csv('https://github.com/CleHou/COVID-19-Data-Analysis-Project/raw/master/02-Maps/country.csv')
    us_shpe = gpd.read_file('https://www2.census.gov/geo/tiger/GENZ2019/shp/cb_2019_us_state_5m.zip')
    world_shpe = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    #fra_shpe = gpd.read_file('https://www.data.gouv.fr/fr/datasets/r/4f7e95a0-c045-4c30-8013-afb94b5876a8')
    fra_shpe = gpd.read_file('https://datanova.laposte.fr/explore/dataset/contours-geographiques-des-nouvelles-regions-metropole/download/?format=shp&timezone=Europe/Berlin&lang=fr')
    
    world_pop = pandas.read_csv('https://population.un.org/wpp/Download/Files/1_Indicators%20(Standard)/CSV_FILES/WPP2019_TotalPopulationBySex.csv')
    us_pop = pandas.read_csv('http://www2.census.gov/programs-surveys/popest/datasets/2010-2019/national/totals/nst-est2019-alldata.csv?#')
    fra_pop = pandas.read_csv('https://github.com/CleHou/COVID-19-Data-Analysis-Project/raw/master/04-French_Data/French_population.csv')
    
    return [df_cases_world, df_death_world, df_France], [df_cases_us, df_death_us], df_fra, [countries_loc, world_shpe, us_shpe, fra_shpe], [world_pop, us_pop, fra_pop] 

def creation_folder (paths):
    current = os.path.dirname(os.path.realpath(__file__))
    list_directory = [os.path.normcase(current + directory) for directory in paths]
    
    for directory in list_directory:
        if os.path.exists(directory) == False:
            print('Directory created')
            os.makedirs(directory)
    list_return = [current + x + '/' for x in paths]      
    return list_return

def save_df (list_df_world, list_df_us, df_fra, location_data, pop_data):
    file_path = ['/2.0 - Data']
    file_path = creation_folder(file_path)
 
    list_df_world[0].to_csv(os.path.normcase(file_path [0] + 'cases_world.csv'), index=False)
    list_df_world[1].to_csv(os.path.normcase(file_path [0] + 'death_world.csv'), index=False)
    list_df_world[2].to_csv(os.path.normcase(file_path [0] + 'Revised_France_Data.csv'), index=False, index_label="Date")
    list_df_us[0].to_csv(os.path.normcase(file_path [0] + 'cases_us.csv'), index=False)
    list_df_us[1].to_csv(os.path.normcase(file_path [0] + 'death_us.csv'), index=False)
    df_fra.to_csv(os.path.normcase(file_path [0] + 'fra_data.csv'), index=False)
    
    location_data[0].to_csv(os.path.normcase(file_path [0] + 'countries_loc.csv'), index=False)
    location_data[1].to_file(os.path.normcase(file_path [0] + 'world_shp.shp'), index=False)
    location_data[2].to_file(os.path.normcase(file_path [0] + 'us_shp.shp'), index=False)
    location_data[3].to_file(os.path.normcase(file_path [0] + 'fra_shp.shp'), index=False)
    
    pop_data[0].to_csv(os.path.normcase(file_path [0] + 'world_pop.csv'), index=False)
    pop_data[1].to_csv(os.path.normcase(file_path [0] + 'us_pop.csv'), index=False)
    pop_data[2].to_csv(os.path.normcase(file_path [0] + 'fra_pop.csv'), index=False)
    
    return print('Saved')

def import_df_from_xlsx (current):
    file_path = [current+'/2.0 - Data/']
    
    df_cases_world = pandas.read_csv(os.path.normcase(file_path [0] + 'cases_world.csv'))
    df_death_world = pandas.read_csv(os.path.normcase(file_path [0] + 'death_world.csv')  )
    df_France = pandas.read_csv(os.path.normcase(file_path [0] + 'Revised_France_Data.csv'))
    df_cases_us = pandas.read_csv(os.path.normcase(file_path [0] + 'cases_us.csv'))
    df_death_us = pandas.read_csv(os.path.normcase(file_path [0] + 'death_us.csv'))
    df_fra = pandas.read_csv(os.path.normcase(file_path [0] + 'fra_data.csv'))
    
    countries_loc = pandas.read_csv(os.path.normcase(file_path [0] + 'countries_loc.csv'))
    world_shpe = gpd.read_file(os.path.normcase(file_path [0] + 'world_shp.shp'))
    us_shpe = gpd.read_file(os.path.normcase(file_path [0] + 'us_shp.shp'))
    fra_shpe = gpd.read_file(os.path.normcase(file_path [0] + 'fra_shp.shp'))
    
    world_pop = pandas.read_csv(os.path.normcase(file_path [0] + 'world_pop.csv'))
    us_pop = pandas.read_csv(os.path.normcase(file_path [0] + 'us_pop.csv'))
    fra_pop = pandas.read_csv(os.path.normcase(file_path [0] + 'fra_pop.csv'))
    
    return [df_cases_world, df_death_world, df_France], [df_cases_us, df_death_us], df_fra, [countries_loc, world_shpe, us_shpe, fra_shpe], [world_pop, us_pop, fra_pop] 

def clean_up_world (list_df_world):
    list_return = []

    for a_df in list_df_world[:2]:
        a_df = a_df.drop(['Lat', 'Long'], axis=1)
        a_df = a_df.groupby("Country/Region").sum()
        a_df.columns = pandas.to_datetime(a_df.columns)
        a_df.loc['World'] = a_df.sum()
        list_return.append(a_df)
                            
    list_return.append(list_df_world[2])
    return list_return

def append_geography_world (list_df_world, countries_loc):
    list_return = []
    countries_loc[0] = countries_loc[0].set_index('name')
    countries_loc[0] = countries_loc[0].loc[:,['latitude', 'longitude']]
    
    countries_loc[1] = countries_loc[1].set_index('name')
    countries_loc[1] = countries_loc[1].rename(index={'United States of America': 'US'})
    countries_loc[1] = countries_loc[1].loc[:,['geometry']]
    
    condition_print=True
    for a_df in list_df_world:
        a_df = pandas.concat([countries_loc[0], a_df], axis=1)
        a_df = pandas.concat([countries_loc[1], a_df], axis=1, join="inner")
        if condition_print: print("\nCountries with no data")
        
        for indexG in countries_loc[1].index:
            if indexG not in (a_df.index):
                list_a = [countries_loc[1].loc[indexG, 'geometry']]
                for k in range(len(a_df.columns)-1):
                    list_a.append(numpy.nan)
                                                     
                if condition_print: print(indexG)
                a_df.loc[indexG] = list_a
                
        condition_print=False
        
        list_return.append(a_df)                               
    print('\n')
    return list_return
    
def ajusted_values_world(list_df_world):
    to_replace = list_df_world[2].set_index('Date')
    to_replace.loc[:,'Cases'] = pandas.to_numeric(to_replace.loc[:,'Cases'], downcast='float')
    to_replace.index = pandas.to_datetime(to_replace.index)
   
    for index in to_replace.index:
        list_df_world[0].loc['France', index] = to_replace.loc[index, 'Cases']
        
    list_df_world[0].loc['World'] = list_df_world[0].sum()
    return list_df_world

def df_Map3 (list_df, demographic):
    list_return = []
    demographic = demographic[(demographic.loc[:, 'Time']==2020) & (demographic.loc[:, 'Variant']=='Medium')]
    demographic = demographic.drop(['LocID', 'VarID', 'Variant', 'Time', 'MidPeriod', 'PopMale', 'PopFemale', 'PopDensity'], axis=1)
    demographic = demographic.set_index('Location')
    missing_countries = []
    
    L1 = ['United Republic of Tanzania', 'United States of America', 'Russian Federation', 'Bolivia (Plurinational State of)', 'Venezuela (Bolivarian Republic of)', "Lao People's Democratic Republic", 'Viet Nam', 
          "Dem. People's Republic of Korea", 'Republic of Korea',"Iran (Islamic Republic of)", "Syrian Arab Republic", "Republic of Moldova", "China, Taiwan Province of China", "Brunei Darussalam", 'Western Sahara', 
          'Democratic Republic of the Congo', 'Dominican Republic', 'Falkland Islands (Malvinas)',
                            'Central African Republic', 'Equatorial Guinea', 'Eswatini', 'State of Palestine', 'Solomon Islands', 'Bosnia and Herzegovina', 'North Macedonia', 'South Sudan']
    L2 = ['Tanzania', 'US', 'Russia', 'Bolivia', 'Venezuela', 'Laos', 'Vietnam', 
          'North Korea', 'Korea, South', 'Iran', 'Syria', 'Moldova', 'Taiwan', 'Brunei', 'W. Sahara', 
          'Dem. Rep. Congo', 'Dominican Rep.', 'Falkland Is.', 'Central African Rep.', 'Eq. Guinea', 'eSwatini', 'Palestine', 'Solomon Is.', 
                            'Bosnia and Herz.', 'Macedonia', 'S. Sudan']
    
    replace_dic = dict(zip(L1,L2))
    demographic = demographic.rename(index=replace_dic)
    
    new_demographic = pandas.DataFrame(index=list_df[0].index, columns=list_df[0].columns[3:])
    for a_country in new_demographic.index:
        if a_country in demographic.index:
            new_demographic.loc[a_country] = demographic.loc[a_country, 'PopTotal']
            
        else:
            missing_countries.append(a_country)
    #print(missing_countries)
    
    name = ['Cases', 'Death']
    
    for k in range (2):
        list_df[k].iloc[:,3:] =  list_df[k].iloc[:,3:]/new_demographic
        list_df[k].iloc[:,3:] = list_df[k].iloc[:,3:].astype('float64')
        
        df_Map3 = pandas.DataFrame(index=list_df[k].index, columns=['geometry', f'{name[k]}_per_1000_hab'])
        
        df_Map3.loc[:,'geometry'] = list_df[k].loc[:,'geometry']
        df_Map3.loc[:,f'{name[k]}_per_1000_hab'] = list_df[k].iloc[:,-1]
        df_Map3 = df_Map3.reset_index()
        df_Map3 = df_Map3.rename(columns={'index':'Country'})
        #df_Map3 = df_Map3.dropna()
        df_Map3 = gpd.GeoDataFrame(df_Map3, geometry='geometry')
        df_Map3.plot()
        list_return.append(df_Map3)
    
    list_return[1].iloc[:,2] = list_return[1].iloc[:,2]*1
    return list_return

def clean_up_US (list_df_us, smooth_val, location_data, pop_data):
    list_return1 = []
    list_return2 = []
    list_df_us[1] = list_df_us[1].drop(columns=['Population'])
    list_name = ['Cases', 'dC/dt', 'Death', 'dD/dt']
    
    for a_df, name in zip(list_df_us, list_name):
        a_df = a_df.groupby('Province_State').sum()
        a_df = a_df.drop(columns=['UID', 'code3', 'FIPS', 'Lat', 'Long_'])
        a_df.columns = pandas.to_datetime(a_df.columns)
        delta_df=a_df.diff(axis=1)
        #pctge_change = delta_df.pct_change(periods=7, axis='columns')
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

    global_df.loc[:,'Pctge_Change_Cases']= global_df.loc[:,'Cases'].groupby(level=0).pct_change(periods=7)*100
    global_df.loc[:,'Pctge_Change_Death']= global_df.loc[:,'Death'].groupby(level=0).pct_change(periods=7)*100
    
    us_shapefile = location_data[2].set_index('NAME')
    us_shapefile.index = us_shapefile.index.rename('States')
    us_shapefile = us_shapefile.loc[:,'geometry']
    
    global_df = global_df.join(us_shapefile)
    global_df = gpd.GeoDataFrame(global_df)
   
    us_pop = pop_data[1].set_index('NAME')
    us_pop.index = us_pop.index.rename('States')

    global_df = global_df.join(us_pop.loc[:, 'POPESTIMATE2019'], how='inner')
    global_df.loc[:,'Cases_per_1000_hab'] = global_df.loc[:,'Cases'].div(global_df.loc[:,'POPESTIMATE2019'])*1000
    global_df.loc[:,'Death_per_1000_hab'] = global_df.loc[:,'Death'].div(global_df.loc[:,'POPESTIMATE2019'])*1000
    global_df = global_df.drop(columns=['POPESTIMATE2019'])
    
    date_plot = global_df.index.get_level_values(1)[-1].strftime("%Y-%m-%d")
    
    df_Map3 = global_df.groupby(level='States').tail(1)
    df_Map3 = df_Map3.reset_index()
    df_Map3_Cases = df_Map3.loc[:,['States', 'Cases', 'Cases_per_1000_hab','geometry']]
    df_Map3_Death = df_Map3.loc[:,['States', 'Death', 'Death_per_1000_hab','geometry']]
    
    df_Map2_cases = global_df.groupby(level='States').tail(1)
    df_Map2_cases = df_Map2_cases.reset_index()
    df_Map2_cases = df_Map2_cases.loc[:,['States','Cases', 'Pctge_Change_Cases', 'dC/dt', 'geometry']]
    
    return [df_Map3_Cases, df_Map3_Death], df_Map2_cases, date_plot

def clean_up_Fra (df_fra, smooth_val, location_data, pop_data):
    df_sorted = df_fra[(df_fra.loc[:,'granularite']=='region') & (df_fra.loc[:,'source_type']=='opencovid19-fr')]
    df_sorted.loc[:,'date'] = pandas.to_datetime(df_sorted.loc[:,'date'], format='%Y-%m-%d')
    df_sorted = df_sorted.set_index(['maille_nom', 'date']).sort_index()
    
    df_local = pandas.DataFrame(index=df_sorted.index, columns=['Death'])
    df_local.loc[:,'Death'] = df_sorted.loc[:,'deces']
    df_local = df_local.rename_axis(index=['Regions', 'Date'])
    
    df_local.loc[:,'dD/dt']= df_local.loc[:,'Death'].groupby(level=0).diff()
    df_local.loc[:,'Pctge_Change_Death']= df_local.loc[:,'Death'].groupby(level=0).pct_change(periods=7)*100
    df_local = df_local.groupby(level=0).rolling(window=smooth_val, center=True).mean()
    df_local = df_local.droplevel(0)
    
    former_version = ['Ile-de-France', 'Centre-Val de Loire', 'Bourgogne-Franche-Comté', 'Hauts-de-France',
                      'Normandie', 'Grand-Est', 'Bretagne', 'Pays de la Loire',
                      'Occitanie', 'Nouvelle Aquitaine', 'Auvergne-Rhône-Alpes', "Provence-Alpes-Côte d'Azur", 'Corse']
        
    new_version = ['Île-de-France', 'Centre-Val de Loire', 'Bourgogne-Franche-Comté', 'Hauts-de-France', 
                   'Normandie', 'Grand Est', 'Bretagne', 'Pays de la Loire', 
                   'Occitanie', 'Nouvelle-Aquitaine', 'Auvergne-Rhône-Alpes', "Provence-Alpes-Côte d'Azur", 'Corse']
    replace_dic = dict(zip(former_version, new_version))
    
    location_data = location_data[3].replace(replace_dic)
    location_data = location_data.set_index('region')
    location_data.index = location_data.index.rename('Regions')
    location_data = location_data.loc[:,'geometry']
    print(location_data)
    
    df_local = df_local.join(location_data)
    df_local = gpd.GeoDataFrame(df_local)
   
    fra_pop = pop_data[2].set_index('Région')
    fra_pop.index = fra_pop.index.rename('Regions')
    
    df_local = df_local.join(fra_pop.loc[:, 'Population'], how='inner')
    df_local.loc[:, 'Death_per_1000_hab'] = df_local.loc[:,'Death'].div(df_local.loc[:,'Population'])*1000
    df_local = df_local.drop(columns=['Population'])
    df_local = df_local.dropna()
    
    date_plot = df_local.index.get_level_values(1)[-1].strftime("%Y-%m-%d")
    
    df_Map3 = df_local.groupby(level='Regions').tail(1)
    df_Map3 = df_Map3.reset_index()
    df_Map3_Death = df_Map3.loc[:,['Regions', 'Death', 'Death_per_1000_hab','geometry']]
    
    df_Map2_death = df_local.groupby(level='Regions').tail(1)
    df_Map2_death = df_Map2_death.reset_index()
    df_Map2_death = df_Map2_death.loc[:,['Regions','Death', 'Pctge_Change_Death', 'dD/dt', 'geometry']]
    
    return [df_Map3_Death], df_Map2_death, date_plot

def define_max_val (a_df, to_sort):
    grp_by_country = a_df.groupby('Country')
    # for each group, aggregate by sorting by data and taking the last row (latest date)
    latest_per_grp = grp_by_country.agg(lambda x: x.sort_values(by='Date').iloc[-1])
    # sort again by cases
    sorted_by_cases = latest_per_grp.sort_values(by=to_sort, ascending=False)
  
    k_max=11
    k=0
    
    rg = sorted_by_cases.columns.get_loc(to_sort)
    val_lim = 1.1 * sorted_by_cases.iloc[k,rg]
    while  sorted_by_cases.iloc[k,rg]//sorted_by_cases.iloc[k+1,rg] >=2 and k<k_max:
        k+=1
            
    val_lim = 1.1 * sorted_by_cases.iloc[k,rg]
    print(sorted_by_cases.index[k], sorted_by_cases.iloc[k,rg])
        
    return val_lim

def max_value_2 (df_Map3, columns):
    maxi = df_Map3.loc[:,columns].nlargest(10, keep='all')
    maxi = maxi.tolist()
    
    val_lim = maxi[0]
    k=0
    while maxi[k]//maxi[k+1] >=2 and k<9:
        k+=1
       
    val_lim = 1.1 * maxi [k]
    
    print(k)
    
    return val_lim
    

def df_Map1 (list_df):
    df_cases = list_df[0].iloc[:,3:].stack()
    df_death = list_df[1].iloc[:,3:].stack()
    
    new_df = pandas.concat([df_cases, df_death], axis=1)
    new_df = new_df.rename(columns={0:'Cases', 1:'Death'})
    new_df.index.set_names(['Country', 'Date'], inplace=True)
    
    df_Gpos = list_df[0].loc[:,['latitude', 'longitude']]
    df_Gpos.index.rename('Country', inplace=True)
   
    new_df = df_Gpos.join(new_df, how='inner')
    new_df = new_df.dropna()
    new_df = new_df.reset_index()
    new_df.loc[:,'Date'] = pandas.to_datetime(new_df.loc[:,'Date'])
    
    return new_df

def Map1 (dfMap1, date_plot):
    print('\n', dfMap1)
    val_lim = define_max_val (dfMap1, 'Cases')
      
    MapDataSet=gv.Dataset(dfMap1, kdims=['Country', 'Date'], vdims = ['Death', hv.Dimension('Cases', range=(0, +val_lim))])

    MapCases = MapDataSet.to(gv.Points, ['longitude', 'latitude'] ,['Country', 'Cases'], group=f'Number of cases on {date_plot}')
    MapDeath = MapDataSet.to(gv.Points, ['longitude', 'latitude'] ,['Country', 'Death'], group=f'Number of dead on {date_plot}')
    
    MapCases = (gvts.CartoLight * MapCases).opts(
        opts.Points(width=1000, height=560, tools=['hover'], size=0.05*numpy.sqrt(dim('Cases')), xaxis=None, yaxis=None,
                    colorbar=True, toolbar='above', color='Cases', cmap='Blues'))
    
    MapDeath= (gvts.CartoLight * MapDeath).opts(
        opts.Points(width=1000, height=560, tools=['hover'], size=0.2*numpy.sqrt(dim('Death')), xaxis=None, yaxis=None,
                    colorbar=True, toolbar='above', color='Death', cmap='OrRd'))
    
    text = hv.Curve((0, 0)).opts(xaxis=None, yaxis=None) * hv.Text(0, 0, 'Source: John Hopkins University \nGraph: C.Houzard')
    
    renderer = hv.renderer('bokeh')
    file_path = creation_folder (['/2.1 - Maps', '/2.2 - Preview'])
    renderer.save(MapCases, os.path.normcase(file_path[1] + 'MapCases.png'))
    renderer.save(MapDeath, os.path.normcase(file_path[1] + 'MapDeath.png'))

    MapOutput = (gv.Layout(MapCases + MapDeath + text)).cols(1)
    
    renderer.save(MapOutput, os.path.normcase(file_path[0] + 'MapCases-Death.html'))

   
def df_Map2 (list_df, lissage):
    combined_df = pandas.DataFrame(index = list_df[0].index, columns=['geometry', 'Cases', 'dC/dt', 'Pctge_change'])
    
    delta_df = list_df[0].iloc[:, 3:].diff(axis=1)
    
    delta_df = delta_df.rolling(window = lissage, center=True, axis=1).mean()
    pctge_df = delta_df.pct_change(periods=7, axis=1)
    
    combined_df.loc[:,'geometry'] = list_df[0].loc[:,'geometry']
    combined_df.loc[:,'Cases'] = list_df[0].iloc[:, -lissage//2]
    combined_df.loc[:,'dC/dt'] = delta_df.loc[:,delta_df.columns[-lissage//2]]
    combined_df.loc[:,'Pctge_change'] = pctge_df.loc[:,pctge_df.columns[-lissage//2]]*100

    combined_df = combined_df.replace([numpy.inf, -numpy.inf], numpy.nan)
    combined_df = combined_df.reset_index()
    combined_df = combined_df.rename(columns={'index':'Country'})
        
    combined_df= gpd.GeoDataFrame(combined_df)
   
    return combined_df

def Map2 (df_Map2_cases, list_parameters, titles, names):
    print('\n', df_Map2_cases)
    
    DataSet = gv.Polygons(df_Map2_cases, vdims=list_parameters[0])
    FinalMap = DataSet.opts(width=1000, height=560, tools=['hover'], colorbar=True, cmap='coolwarm', 
                xaxis=None, yaxis=None, title=titles[0])
    
    FinalMap = FinalMap * gvts.CartoLight
    
    text = hv.Curve((0, 0)).opts(xaxis=None, yaxis=None) * hv.Text(0, 0, 'Source: John Hopkins University \nGraph: C.Houzard')

    renderer = gv.renderer('bokeh')
    file_path = creation_folder (['/2.1 - Maps', '/2.2 - Preview'])
    
    renderer.save(FinalMap, os.path.normcase(file_path[1] + names[0]))
    
    MapOutput = (gv.Layout(FinalMap + text)).cols(1)
    renderer.save(MapOutput, os.path.normcase(file_path[0] + names[1]))
    

def Map3 (list_return, list_parameters, titles, source, names, list_cmap):
    renderer = hv.renderer('bokeh')
    file_path = creation_folder (['/2.1 - Maps', '/2.2 - Preview'])
    
    first_round = True
    list_map = []
    for a_df, parameter, a_title, a_cmap, name in zip(list_return, list_parameters, titles, list_cmap, names):
        MapDataSet = gv.Polygons(a_df, vdims=parameter)
        MapRel = MapDataSet.opts(width=1000, height=560, tools=['hover'], colorbar=True, cmap=a_cmap, 
                    xaxis=None, yaxis=None, title=a_title)
        MapRel= MapRel * gvts.CartoLight
        list_map.append(MapRel)
        renderer.save(MapRel, os.path.normcase(file_path[1] + name))
        
        if first_round:
            sum_map = MapRel
            first_round=False
            
        else:
            sum_map = sum_map + MapRel

    text = hv.Curve((0, 0)).opts(xaxis=None, yaxis=None) * hv.Text(0, 0, f'Source: John Hopkins University \n{source}\nGraph: C.Houzard')
    MapOutput = (gv.Layout(sum_map + text)).cols(1)
    
    renderer.save(MapOutput, os.path.normcase(file_path[0] + names[-1]))
    
def check_date (list_df_world, list_df_us, df_fra, location_data, pop_data):
    today_date = datetime.date.today()
    last_date =datetime.datetime.strptime(list_df_world[0].columns[-1], "%m/%d/%y").date()
    
    delta = (today_date-last_date).days
    
    if delta > 1 :
        short_date = last_date.strftime("%Y-%m-%d")
        print('\a')
        print(f'Data were last updated {delta} days ago, on {short_date}')
        conti = input('Do you wish to update the data? [y/n]?')
        
        if conti == 'y':
            list_df_world, list_df_us, df_fra, location_data, pop_data = import_df_from_I()
            print('Data updated')
            
    return list_df_world, list_df_us, df_fra, location_data, pop_data
        
    
#-- Creation DF --#
current = os.path.dirname(os.path.realpath(__file__))

list_df_world, list_df_us, df_fra, location_data, pop_data = import_df_from_I()
#list_df_world, list_df_us, df_fra, location_data, pop_data = import_df_from_xlsx(current)

list_df_world, list_df_us, df_fra, location_data, pop_data = check_date (list_df_world, list_df_us, df_fra, location_data, pop_data)
save_df (list_df_world, list_df_us, df_fra, location_data, pop_data)


#------- World -------
list_df_world = clean_up_world(list_df_world)
list_df_world = ajusted_values_world(list_df_world)
list_df_world = append_geography_world(list_df_world, location_data)
date_plot_world = (list_df_world[0].columns)[-1].strftime("%Y-%m-%d")

dfMap1 = df_Map1 (list_df_world)
Map1(dfMap1, date_plot_world)

df_Map2_cases_world = df_Map2 (list_df_world, 7)
val_lim=100
list_parameters_world=[[hv.Dimension('Pctge_change', range=(-val_lim, +val_lim)), 'Cases', 'dC/dt', 'Country']]
titles_world = [f'Evolution of the number of cases in the world on {date_plot_world}']
names_world = ['MapBalance.png', 'MapBalance.html']
Map2 (df_Map2_cases_world, list_parameters_world, titles_world, names_world)

list_dfMap3_world = df_Map3 (list_df_world, pop_data[0])
val_lim1=max_value_2 (list_dfMap3_world[0], 'Cases_per_1000_hab')
val_lim2=max_value_2 (list_dfMap3_world[1], 'Death_per_1000_hab')
list_parameters_world = [[hv.Dimension('Cases_per_1000_hab', range=(0, val_lim1)), 'Country'], [hv.Dimension('Death_per_1000_hab', range=(0, val_lim2)), 'Country']]
titles_world = [f'Number of cases per 10000 inhabitant on {date_plot_world}', f'Number of death per 10000 inhabitant on {date_plot_world}']
source_world = '& UN for demographic data'
names_world = ['Map_Relative_Cases.png', 'Map_Relative_Death.png', 'Map_Relative_Cases-Death.html']
list_cmap_world = ['Blues', 'OrRd']
Map3 (list_dfMap3_world, list_parameters_world, titles_world, source_world, names_world, list_cmap_world)

#------- US -------
list_dfMap3_us, df_Map2_cases_us, date_plot_us = clean_up_US (list_df_us, 3, location_data, pop_data)

val_lim1=max_value_2 (list_dfMap3_us[0], 'Cases_per_1000_hab')
val_lim2=max_value_2 (list_dfMap3_us[1], 'Death_per_1000_hab')
list_parameters_us = [[hv.Dimension('Cases_per_1000_hab', range=(0, val_lim1)), 'States', 'Cases'], [hv.Dimension('Death_per_1000_hab', range=(0, val_lim2)), 'States', 'Death']]
titles_us= [f'Number of cases per state and per 10000 inhabitant on {date_plot_world}', f'Number of death per state and per 10000 inhabitant on {date_plot_world}']
source_us= '& US Census Bureau'
names_us = ['Map_Relative_Cases_US.png', 'Map_Relative_Death_US.png', 'Map_Relative_Cases-Death_US.html']
list_cmap_us = ['Blues', 'OrRd']
Map3 (list_dfMap3_us, list_parameters_us, titles_us, source_us, names_us, list_cmap_us)

val_lim=100
list_parameters_us=[[hv.Dimension('Pctge_Change_Cases', range=(-val_lim, +val_lim)), 'Cases', 'dC/dt', 'States']]
titles_us= [f'Evolution of the number of cases in the US on {date_plot_world}']
names_us = ['MapBalance_US.png', 'MapBalance_US.html']
Map2 (df_Map2_cases_us, list_parameters_us, titles_us, names_us)

#------- France -------
list_dfMap3_fra, df_Map2_death_fra, date_plot_fra = clean_up_Fra (df_fra, 3, location_data, pop_data)

val_lim=max_value_2 (list_dfMap3_fra[0], 'Death_per_1000_hab')
list_parameters_fra = [[hv.Dimension('Death_per_1000_hab', range=(0, val_lim)), 'Regions', 'Death']]
titles_fra= [f'Number of death per regions and per 10000 inhabitant on {date_plot_fra}']
source_fra= '& data.gouv'
names_fra = ['Map_Relative_Death_Fra.png', 'Map_Relative_Cases-Death_Fra.html']
list_cmap_fra = ['OrRd']
Map3 (list_dfMap3_fra, list_parameters_fra, titles_fra, source_fra, names_fra, list_cmap_fra)

val_lim=100
list_parameters_fra=[[hv.Dimension('Pctge_Change_Death', range=(-val_lim, +val_lim)), 'Death', 'dD/dt', 'Regions']]
titles_fra= [f'Evolution of the number of death in France on {date_plot_fra}']
names_fra = ['MapBalance_Fra.png', 'MapBalance_Fra.html']
Map2 (df_Map2_death_fra, list_parameters_fra, titles_fra, names_fra)

