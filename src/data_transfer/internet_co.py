#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug  1 11:10:59 2021

@author: Clement
Internet connection
"""
import requests
import time
import sys
  
def check_internet (tot_trials):
    url = 'https://www.google.fr'
    timeout = 5
    
    connection = False
    nb_try = 0
    wait_time = 6 #time between 2 trials
    
    while not connection and nb_try < tot_trials:
        try:
            requests.get(url, timeout=timeout)
            connection = True
            wait=0
            
        except (requests.ConnectionError, requests.Timeout):
            nb_try += 1
            print(f'\rTry {nb_try}: no internet connection')
            
            if nb_try < tot_trials :
                wait = wait_time
                print(f'Trying again in {wait}s', end='')
                
                while wait > 0:
                    wait -= 1
                    time.sleep(1)
                    print(f"\rTrying again in {wait}s", end='')
                
    
    if connection:
        print("\r" + " "*len(f"Trying again in {wait}s"))
        print('Connected to the internet!\n\n')
        
    else:
        print("\r" + " "*len(f"Trying again in {wait}s"))
        print('Not connected to the internet. Please check internet connection and try again')
        sys.exit()
        
if __name__ == '__main__':
    check_internet (10)
                
                