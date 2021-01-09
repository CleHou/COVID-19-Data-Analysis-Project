#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan  9 15:56:01 2021

@author: Clement
"""
import os 
import numpy

def list_dir_files (file_path):
    file_path = os.path.normcase(file_path)
    list_subdirr = []
    list_files = []
    for root, dirs, files in os.walk(file_path):
        list_subdirr.append(dirs)
        list_files.append(files)
        
    list_files = list(numpy.concatenate(list_files).flat)
    return list_subdirr, list_files

def creation_folder (root, paths):
    list_directory = [os.path.normcase(root + directory) for directory in paths]
    
    for directory in list_directory:
        if os.path.exists(directory) == False:
            print(f'Directory created: {directory}')
            os.makedirs(directory)
    list_return = [root + x for x in paths]      
    return list_return
    
def helloworld():
    print('hello')