#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 12:49:03 2020

@author: ejreidelbach

:DESCRIPTION: This script attempts to visualize the results of the Eagle 
    Dynamics' 2020 F-18 roadmap survey in more visually pleasing manner.
    
    Actual survey link: https://docs.google.com/forms/d/e/1FAIpQLSfKuQ53phRBCLQT03QFLX18UcA2UiibvZO6uvGeosGRPhpYrg/viewanalytics
    
:REQUIRES:
    - Refer to the Package Import section of the script

:NOTES:
    
    NOTE 1: For the Selenium driver to function properly on Ubuntu, I had to 
            download the most up-to-date geckodriver found at:
            https://github.com/mozilla/geckodriver/releases
                
            Once that is complete, extract the driver and place it in the
            /us/local/bin folder
           
    NOTE 2: An effective selenium guide can be found here:
            https://automatetheboringstuff.com/chapter11/
            
            The relevant contents begin roughly 3/4 down the page.

:TODO: N/A
"""
#==============================================================================
# Package Import
#==============================================================================
import numpy as np
import os  
import pandas as pd
import pathlib
import plotly.express as px
import plotly.graph_objects as go
import requests
import time

from bs4 import BeautifulSoup
from plotly.offline import plot # plot graphs in web browser if using Spyder
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

#==============================================================================
# Reference Variables
#==============================================================================

#==============================================================================
# Classes
#==============================================================================

#==============================================================================
# Functions
#==============================================================================
def scrape_data(url):
    '''
    Purpose: N/A
        
    Inputs
    ------
        name : type
            description
    
    Outputs
    -------
        name : type
            description
    '''  
    # initialize the geckodriver
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(executable_path=r'C:\Users\reideej1\Projects\chromedriver.exe',
                               options=options)
    # Scrape the page 
    driver.get(url)
    # Parse the new request with BeautifulSoup
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    driver.quit()
    # Extract the question in the poll
    html_poll = soup.find('div', {'jsname':'cAPHHf'})
    html_questions = html_poll.find_all('span',{'class':'freebirdAnalyticsViewQuestionTitle'})
    list_questions = [x.text for x in html_questions]
    # Extract the results for each poll question
    html_results = html_poll.find_all('div',{'aria-label':'A tabular representation of the data in the chart.'})
    list_results = [pd.read_html(str(x.find('table')))[0].set_index(
            'Unnamed: 0').T.to_dict('records')[0] for x in html_results]
    
    # merge all results into a dataframe
    df_poll = pd.DataFrame()
    col_count = 0
    for question, result in zip(list_questions, list_results):
        # initialize dataframe
        if col_count == 0:
            df_poll = pd.DataFrame.from_dict(result, orient='index')
            df_poll.columns = [question]
        # insert column into master dataframe
        else:
            df_poll.insert(col_count,question, result.values(), True)
        col_count = col_count + 1
    # reset the df index and save the votes column
    df_poll = df_poll.reset_index().rename(columns={'index':'vote'})
    # create a timestamp for naming purposes when writing to disk
    timestamp = time.strftime('%d_%m_%Y_%H_%M_%S')   
    df_poll.to_csv(f'data/poll_results_{timestamp}.csv', index = False)

    return df_poll

def plot_data(df_poll):
    fig = px.parallel_coordinates(df_poll)
    plot(fig)
    #fig = px.parallel_categories(df)
    #plot(fig)

    return
    
#=============================================================================
# Working Code
#==============================================================================

# Set the project working directory
path_dir = pathlib.Path(r'C:\Users\reideej1\Projects\dcs')
os.chdir(path_dir)

# specify the url to the DCS results
url = 'https://docs.google.com/forms/d/e/1FAIpQLSfKuQ53phRBCLQT03QFLX18UcA2UiibvZO6uvGeosGRPhpYrg/viewanalytics'
# scrape the results
df_poll = scrape_data(url, path_dir)
#dict_poll = scrape_data(url_form)

# create totl sco