#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 16:46:41 2020

@author: ejreidelbach

:DESCRIPTION: This script visualizes the results of the Eagle 
    Dynamics' 2020 F-18 roadmap survey in more visually pleasing manner.
    
    Actual survey link: https://docs.google.com/forms/d/e/1FAIpQLSfKuQ53phRBCLQT03QFLX18UcA2UiibvZO6uvGeosGRPhpYrg/viewanalytics
    
:REQUIRES: N/A

:NOTES: N/A
   
:TODO: N/A
"""
#==============================================================================
# Package Import
#==============================================================================
import glob
import numpy as np
import os  
import pandas as pd
import pathlib
import plotly.express as px
import plotly.graph_objects as go
import time

from scrape_f18_poll import scrape_f18_poll
from plotly.offline import plot # plot graphs in web browser if using Spyder

#==============================================================================
# Reference Variables
#==============================================================================
# set the category each question belongs to
dict_categories = {
    'ATFLIR':'A2G',
    'New and updated HOTAS functions':'Navigation/Avionics',
    'AG radar. EXP modes (1-2-3), GMT and GMTT modes, and SEA search mode':'A2G',
    'Azimuth / Elevation air-to-air radar mode with AUTO IFF modes':'A2A',
    'Coupled autopilot modes':'Navigation/Avionics',
    'ACLS mode':'Navigation/Avionics',
    'Datalink symbols, EW symbols, and AG mode for JHMCS':'Navigation/Avionics',
    'Correct possible flare number loaded':'Countermeasures',
    'ASPJ ECM jammer':'Countermeasures',
    'Adjust countermeasure programs when on ground':'Countermeasures',
    'Mark points':'Navigation/Avionics',
    'Offset waypoints':'Navigation/Avionics',
    'SLAM-ER air-to-surface missile':'Weapon',
    'Harpoon, SEA radar directed mode (FTT)':'Weapon',
    'Update flight model for ground effect, takeoff pitch effects, auto-pilot based on FPM, touch and go handling, and other remaining flight model issues':'Navigation/Avionics',
    'Jamming targets not displayed on radar, should be in dugout':'A2A',
    'Aircraft Setup Card in Options':'Flight Planning/Misc',
    'Mission Card for 60 waypoints with properties (Sequence 1, 2, 3, PP, PB, Initial, etc.)':'Flight Planning/Misc',
    'RWS RAID air-to-air radar sub-mode missing':'A2A',
    'Radar SPOT mode':'A2A',
    'AG radar interleaved mode (SEA and GMT)':'A2G',
    'AG radar. AGR (air to ground ranging) mode':'A2G',
    'HARM Pre-Briefed mode':'Weapon',
    'GBU-32 JDAM':'Weapon',
    'Select AA and AG on ground':'Flight Planning/Misc',
    'TALD decoy':'Weapon',
    'AIM-7P':'Weapon',
    'Mk-77 firebomb':'Weapon',
    'GBU-24 Paveway III LGB':'Weapon',
    'IN LAR cue is missing': 'A2A',
    'The missing function of WIDE radar auto acquisition mode, cannot slew it':'A2A',
    'UFC BU page':'Flight Planning/Misc',
    'Flight member TGT ground target SA page symbol missing':'A2G',
    'Fuel BIT (FLBIT) Page':'Navigation/Avionics',
    'MUMI Page':'Flight Planning/Misc',
    'Gun sparks at night':'Flight Planning/Misc',
    'INS / GPS full simulation and alignment (carrier and ground)':'Navigation/Avionics',
    'LOFT modes, ARM, JPF, and other JDAM and JSOW remaining functions':'Weapon',
    'BDU-45 Training Bomb':'Weapon',
    'GEN-X decoy':'Weapon',
    'S/A and AUTO countermeasure modes':'Countermeasures',
    }

# set the category each question belongs to
dict_questions_short = {
    'ATFLIR':'ATFLIR',
    'New and updated HOTAS functions':'HOTAS Update',
    'AG radar. EXP modes (1-2-3), GMT and GMTT modes, and SEA search mode':'AG Radar Modes',
    'Azimuth / Elevation air-to-air radar mode with AUTO IFF modes':'AUTO IFF',
    'Coupled autopilot modes':'Coupled A/P',
    'ACLS mode':'ACLS Mode',
    'Datalink symbols, EW symbols, and AG mode for JHMCS':'JHMCS Symbology',
    'Correct possible flare number loaded':'Flare # Correction',
    'ASPJ ECM jammer':'ASPJ ECM Jammer',
    'Adjust countermeasure programs when on ground':'Adjust CM on Ground',
    'Mark points':'Mark points',
    'Offset waypoints':'Offset W/P',
    'SLAM-ER air-to-surface missile':'SLAM-ER',
    'Harpoon, SEA radar directed mode (FTT)':'Harpoon FTT',
    'Update flight model for ground effect, takeoff pitch effects, auto-pilot based on FPM, touch and go handling, and other remaining flight model issues':'Flight Model Issues',
    'Jamming targets not displayed on radar, should be in dugout':'Jamming on Radar',
    'Aircraft Setup Card in Options':'A/C Setup Card',
    'Mission Card for 60 waypoints with properties (Sequence 1, 2, 3, PP, PB, Initial, etc.)':'60 Waypoints',
    'RWS RAID air-to-air radar sub-mode missing':'RWS RAID A2A',
    'Radar SPOT mode':'A2A SPOT Mode',
    'AG radar interleaved mode (SEA and GMT)':'AG SEA/GTM Mode',
    'AG radar. AGR (air to ground ranging) mode':'AGR Mode',
    'HARM Pre-Briefed mode':'HARM Pre-Briefed',
    'GBU-32 JDAM':'GBU-32 JDAM',
    'Select AA and AG on ground':'AA/AG on Ground',
    'TALD decoy':'TALD Decoy',
    'AIM-7P':'AIM-7P',
    'Mk-77 firebomb':'MK-77 Firebomb',
    'GBU-24 Paveway III LGB':'GBU-27 Paveway',
    'IN LAR cue is missing': 'A2A LAR gun cue',
    'The missing function of WIDE radar auto acquisition mode, cannot slew it':'WIDE Radar mode',
    'UFC BU page':'UFC B/U Page',
    'Flight member TGT ground target SA page symbol missing':'TGT SA Symbology',
    'Fuel BIT (FLBIT) Page':'Fuel BIT Page',
    'MUMI Page':'MUMI Page',
    'Gun sparks at night':'Gun Sparks',
    'INS / GPS full simulation and alignment (carrier and ground)':'INS/GPS Alignment',
    'LOFT modes, ARM, JPF, and other JDAM and JSOW remaining functions':'JDAM/JSOW Modes',
    'BDU-45 Training Bomb':'BDU-45 Train. Bomb',
    'GEN-X decoy':'GEN-X Decoy',
    'S/A and AUTO countermeasure modes':'S/A & AUTO CM Modes',
    }
#==============================================================================
# Classes
#==============================================================================

#==============================================================================
# Functions
#==============================================================================
def function(var):
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
''' Step 1. Ingest the latest version of the data by scraping a new set. 
'''

# scrape the newest batch of data
df_latest_results = scrape_f18_poll()
df_latest_results = df_latest_results.set_index('vote')

# # find the most up-to-date results
list_of_files = glob.glob(r'C:\Users\reideej1\Projects\dcs\data\*')
latest_file = pathlib.Path('data', max(list_of_files, key = os.path.getctime))
df_latest_results = pd.read_csv(latest_file)
''' Step 2. Reshape the dataset such that each row contains information about
            the specific poll question and the index is the value of each vote.
'''
df_latest_results = df_latest_results.set_index('vote')
df_latest_results = df_latest_results.T

''' Step 3. Create a new score variable based on ranking groups.
               - Must Have:  10 or 9
               - Nice to Have: 8 or 7 
               - Meh: 6, 5, 4
               - Pass: 3, 2, 1
'''
list_range_scores = []
for index, row in df_latest_results.iterrows():
    list_range_scores.append({
        "Implement it today!" : (row[10] + row[9]),
        "I'm interested." : (row[8] + row[7]),
        "Meh." : (row[6] + row[5] + row[4]),
        "Don't waste your time." : (row[3] + row[2] + row[1])
        })
# add the grouped scores to their down dataframe
df_scores_groups = pd.DataFrame(list_range_scores)
df_scores_groups = df_scores_groups.set_index(df_latest_results.index)

# add the the new groups to the dataframe
df_latest_results = pd.concat([df_latest_results, 
                               df_scores_groups],
                              axis = 1, sort = False)

''' Step 4. Add a weighted score to the dataset. 
            Votes are weighted based on their value, so a 10 is worth 
            10 points, a 9 is worth 9, etc... 
'''
list_weighted_scores = []
for index, row in df_latest_results.iterrows():
    weighted_score = 0
    for score, num_votes in row.iteritems():
        if type(score) == str:
            break
        weighted_score = weighted_score + score*num_votes
    list_weighted_scores.append(weighted_score)

# add the weighted scores to the dataframe
df_latest_results['score_weighted'] = list_weighted_scores

''' Step 5. Add question categories to the dataset.
'''
# retrieve the category for each question in the dataframe
list_categories = []
for question in df_latest_results.index:
    list_categories.append(dict_categories[question])
# add the category column to the dataframe
df_latest_results['category'] = list_categories

''' Step 6. Calculate a score based on the groups defined in step 3.
'''
list_grouped_scores = []
for index, row in df_latest_results.iterrows():
    list_grouped_scores.append(row["Implement it today!"]*3 + row["I'm interested."]*2 + row["Meh."]*1)
df_latest_results['score_grouped'] = list_grouped_scores

''' Step 7. Add shorter question names to dataframe
'''
df_latest_results['question_short'] = df_latest_results.apply(lambda row: dict_questions_short[row.name], axis = 1)

''' Step 8. Save the updated scores to disk
'''
# create a timestamp for naming purposes when writing to disk
timestamp = time.strftime('%d_%m_%Y_%H_%M_%S')   
# save a copy of the data to disk
df_latest_results.to_csv(f'data\poll_results_{timestamp}_with_additional_data.csv')

''' Step 9. Visualize the grouped scores as a bar chart.
'''
# sort from biggest weighted vote getter to smallest
df_latest_results = df_latest_results.sort_values(
    by = 'score_weighted', ascending = False)

fig = px.bar(df_latest_results, 
             x = df_latest_results.index, 
             y = 'score_grouped', 
             color = 'category')
fig.update_layout(xaxis={'categoryorder':'total descending'})
#fig.show()
plot(fig)
    
''' Step 10. Visualize the data in a stacked bar chart to highlight the various
        changes in voting scores across each question
'''
fig = go.F

def px_stacked_bar(df, color_name='category', y_name='y', **pxargs):
    '''Row-wise stacked bar using plot-express.
       Equivalent of `df.T.plot(kind='bar', stacked=True)`
       `df` must be single-indexed
    '''
    idx_col = df.index.name
    m = pd.melt(df.reset_index(), id_vars=idx_col, var_name=color_name, value_name=y_name)
    return px.bar(m, x=idx_col, y=y_name, color=color_name, **pxargs)

''' Step 11. Group results by category
'''
num_votes = 3607
df_ctgy = df_latest_results.groupby(['category'])[10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 'Implement it today!', 'Meh.', "I'm interested.", "Don't waste your time."].sum()
df_ctgy['num_questions'] = df_latest_results.groupby(['category'])[10].count()
df_ctgy['Score (weighted)'] = df_ctgy.apply(
    lambda row: sum([row[10]*10, row[9]*9, row[8]*8, row[7]*7, row[6]*6, row[5]*5, 
                    row[4]*4, row[3]*3,row[2]*2, row[1]*1])/(num_votes*row['num_questions']), axis = 1)
df_ctgy.to_csv('data\poll_results_by_category.csv')