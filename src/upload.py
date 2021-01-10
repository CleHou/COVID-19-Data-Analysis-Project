#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 10 01:35:41 2021

@author: Clement
"""
import pandas
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from gen_fct import gen_fct



def read_db_list (dir_name):
    db_returns_path = os.path.normcase(f'{dir_name}/reports_db.json')
    db_returns = pandas.read_json(db_returns_path, orient = "table")
    
    last_report = pandas.DataFrame(index=db_returns.index, columns=['date'])
    last_report.to_json(f'{dir_name}/last_report.json', orient = "table", indent=4)
    
    return db_returns

reports_dir = gen_fct.get_parent_dir(2, 'reports')
db_returns = read_db_list (reports_dir)