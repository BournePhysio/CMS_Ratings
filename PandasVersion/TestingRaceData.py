#!/usr/bin/env python
# coding: utf-8

# In[395]:


# Install a pip package in the current Jupyter kernel
import sys
import json
from json import JSONEncoder
import numpy as np
import pandas as pd
# !{sys.executable} -m pip install flatten_json
from flatten_json import flatten
# !{sys.executable} -m pip install seaborn
import seaborn as sns
# !{sys.executable} -m pip install MatplotLib
import matplotlib.pyplot as plt


# In[396]:


race_id = "MisanoR1"
race_type = "sprint"
file_name = 'NewData//201109_211704_R.json'


# In[397]:


results_file = open(file_name, 'rb')
results_file_stringify = results_file.read()
results_file.close()
results_json = json.loads(results_file_stringify, strict=False)
leader_board_lines = results_json["sessionResult"]["leaderBoardLines"]
laps = results_json["laps"]


# In[398]:


df_laps = pd.DataFrame(laps)
filt3 = df_laps['isValidForBest'] == True
df_laps = df_laps.loc[filt3]
filt = (df_laps['laptime'] < 200000)
df_laps = df_laps.loc[filt]
df_laps


# In[399]:


# Create the event
event = pd.DataFrame({ 'race_id':[race_id], 'race_type': [race_type], 'sessionType': [results_json['sessionType']], 'track':[results_json['trackName']], 'useRating': [True]})


# In[400]:


lead_flat = [flatten(d) for d in leader_board_lines]


# In[401]:


df_leader = pd.json_normalize(lead_flat)
# list(df_leader.columns)
df_leader = df_leader[['car_carId', 'car_drivers_0_firstName','car_drivers_0_lastName','car_drivers_0_playerId','car_carModel']]
df_leader = df_leader.rename(columns={"car_carId": "carId", "car_drivers_0_firstName": "firstName", "car_drivers_0_lastName": "lastName", "car_drivers_0_playerId" : "steamId"})
df_leader['GT3'] = df_leader['car_carModel'].apply(lambda x: 'GT4' if (x >50 and x < 62) else 'GT3')


# In[402]:


lap_data = pd.merge(df_laps, df_leader)
lap_data['Name'] = lap_data['firstName'] + " " + lap_data['lastName']


# In[403]:


lap_data['laptime'] = lap_data['laptime'] / 1000
lap_data2 = lap_data.sort_values(by=['laptime'])
lap_data3 = lap_data2.groupby('Name').head(10).reset_index(drop=True)
lap_data3
#list(lap_data2.columns)


# In[404]:


sns.set_context('poster')
sns.set_style("darkgrid")
plt.figure(figsize=(16,20))

sns.boxplot(y='Name', x = 'laptime', data = lap_data3)


# In[405]:


def filter_func(x):
    return x['isValidForBest'].count() > 9


# In[429]:


lp = lap_data3.groupby(['steamId']).filter(filter_func)

# lp2 = lp.groupby(['carId', 'driverIndex', 'isValidForBest','GT3','steamId' ,'Name']).mean()
lp2 = lp.groupby(['steamId' ]).mean()
lp2.insert(0, 'race_id', event['race_id'][0])

final_data = pd.merge(lp2, df_leader)
final_data = pd.merge(final_data, event)

results_file_json = 'test_results_pd.json'
final_data.to_json(r'test_results_pd3.json', orient='records')

# idea for dropping duplicate values. first sort by laptime then drop dublicates keeping the first. Should just drop lower rating
# users.duplicated(subset = ['age', 'zip_code']) to look for subset duplication

