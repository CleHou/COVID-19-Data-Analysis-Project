#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan  9 15:56:01 2021

@author: Clement
"""
import os 
import numpy
import pandas
import datetime
import holoviews as hv
import matplotlib.image as image
import matplotlib.backends.backend_pdf
import matplotlib.pyplot as plt

from gen_fct import df_fct

def list_dir_files (file_path):
    file_path = os.path.normcase(file_path)
    list_subdirr = []
    list_files = []
    for root, dirs, files in os.walk(file_path):
        list_subdirr.append(dirs)
        list_files.append(files)
        
    list_files = list(numpy.concatenate(list_files).flat)
    return list_subdirr, list_files

def get_parent_dir (n, suffix=''):
    dir_name = os.path.dirname(os.path.realpath(__file__))
    for k in range(n):
        dir_name = os.path.dirname(dir_name)
        
    dir_name = f'{dir_name}/{suffix}'       
    return dir_name

def creation_folder (root, paths):
    list_directory = [os.path.normcase(root + directory) for directory in paths]
    
    for directory in list_directory:
        if os.path.exists(directory) == False:
            print(f'Directory created: {directory}')
            os.makedirs(directory)
    list_return = [root + x for x in paths]      
    return list_return

def save_fig (an_object, name, date, **kwargs):
    db_file, db_file_date = df_fct.write_db_files (name, date, kwargs)

    date_str = date.strftime("%Y-%m-%d")
    year = date.strftime("%Y")
    month = date.strftime("%m - %B")
    
    if db_file.loc[name, 'add_date']:
        file_dir = f"{get_parent_dir(2)}/{db_file.loc[name, 'local_path']}/{year}/{month}"
        file_dir_prev = f"{get_parent_dir(2)}/{db_file.loc[name, 'local_path_prev']}/{year}/{month}"
        file_name = f"{db_file.loc[name, 'pref']}{date_str}{db_file.loc[name, 'suf']}"

    else:
        file_dir = f"{get_parent_dir(2)}/{db_file.loc[name, 'local_path']}"
        file_dir_prev = f"{get_parent_dir(2)}/{db_file.loc[name, 'local_path_prev']}"
        file_name = f"{db_file.loc[name, 'pref']}{db_file.loc[name, 'suf']}"

    root = get_parent_dir(2, 'reports')
    creation_folder ('', [file_dir, file_dir_prev])

    if db_file.loc[name, 'type_file'] == 'Graph':
        root_img = get_parent_dir(2, 'data')
        logo = image.imread(f'{root_img}/logo/Logo2_200px.png')
        an_object.figimage(logo, 30, 20, zorder=3)

        an_object.savefig(os.path.normcase(f'{file_dir}/{file_name}.pdf'), format='pdf', dpi=200)
        an_object.savefig(os.path.normcase(f'{file_dir_prev}/{file_name}_preview.png'), format='png', dpi=300)
        #fig.savefig(os.path.normcase(f'{file_dir}/{file_name}.svg'), format='svg', dpi=300)
        print(f'Graph {name} saved')

    elif db_file.loc[name, 'type_file'] == 'Map':
        print('\n\nSaving Map...\r')
        renderer = hv.renderer('bokeh')
        renderer.save(an_object, os.path.normcase(f'{file_dir}/{file_name}'))
        print(f'Map {name} saved')

    elif db_file.loc[name, 'type_file'] == 'MapPrev':
        hv.save(an_object, os.path.normcase(f'{file_dir}/{file_name}.png'))
        print(f'Map Preview {name} saved')

    df_fct.save_db_files (db_file, db_file_date)

def save_multi_fig (list_objects, name, date, **kwargs):
    #list_objects = list_objects[1:]
    #preview_fig = list_objects[0]

    db_file, db_file_date = df_fct.write_db_files (name, date, kwargs)

    date_str = date.strftime("%Y-%m-%d")
    year = date.strftime("%Y")
    month = date.strftime("%m - %B")
    
    if db_file.loc[name, 'add_date']:
        file_dir = f"{get_parent_dir(2)}/{db_file.loc[name, 'local_path']}/{year}/{month}"
        file_dir_prev = f"{get_parent_dir(2)}/{db_file.loc[name, 'local_path_prev']}/{year}/{month}"
        file_name = f"{db_file.loc[name, 'pref']}{date_str}{db_file.loc[name, 'suf']}"

    else:
        file_dir = f"{get_parent_dir(2)}/{db_file.loc[name, 'local_path']}"
        file_dir_prev = f"{get_parent_dir(2)}/{db_file.loc[name, 'local_path_prev']}"
        file_name = f"{db_file.loc[name, 'pref']}{db_file.loc[name, 'suf']}"

    creation_folder ('', [file_dir, file_dir_prev])

    list_objects[0].savefig(os.path.normcase(f'{file_dir_prev}/{file_name}_preview.png'), format='png', dpi=300)

    pdf = matplotlib.backends.backend_pdf.PdfPages(os.path.normcase(f'{file_dir}/{file_name}.pdf'))

    for a_fig in list_objects[1:]:
        root_img = get_parent_dir(2, 'data')
        logo = image.imread(f'{root_img}/logo/Logo2_200px.png')
        a_fig.figimage(logo, 30, 20, zorder=3)
        pdf.savefig(a_fig, dpi=200)
        plt.close(a_fig)

    pdf.close()
    print(f'Graph {name} saved')


    df_fct.save_db_files (db_file, db_file_date)

def save_pdf (pdf_object, date, **kwargs):
    name = 'daily_brief'
    db_file, db_file_date = df_fct.write_db_files (name, date, kwargs)
    
    date_str = date.strftime("%Y-%m-%d")
    year = date.strftime("%Y")
    month = date.strftime("%m - %B")

    file_dir = f"{get_parent_dir(2)}/{db_file.loc[name, 'local_path']}/{year}/{month}"
    file_name = f"{db_file.loc[name, 'pref']}{date_str}{db_file.loc[name, 'suf']}"
    
    creation_folder ('', [file_dir])
    full_path = os.path.normcase(f'{file_dir}/{file_name}.pdf')

    pdf_output = open(full_path, 'wb')
    pdf_object.write(pdf_output)
    pdf_output.close()
    
    df_fct.save_db_files (db_file, db_file_date)
    

    print('Daily brief saved')









