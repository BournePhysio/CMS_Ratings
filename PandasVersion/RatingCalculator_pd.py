#!/usr/bin/env python
# coding: utf-8

# In[443]:


import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


# In[444]:


results_directory = 'Processed'
file_name = 'Processed//201109_231143_R2_proc.json'
events_name = 'events_pd.json'
ratings_name = 'RatingData_pd.json'


# In[445]:


results = pd.read_json(file_name)
events = pd.read_json(events_name)
ratings = pd.read_json(ratings_name)


# In[446]:


# pull event data
# Create the event and add to events file
event = pd.DataFrame({ 'race_id': results['race_id'], 'race_type': results['race_type'], 'sessionType': results['sessionType'], 'track': results['track'], 'useRating': results['useRating']})


# In[447]:


events = pd.concat([events, event])
events.drop_duplicates(subset = ['race_id'], keep='first', inplace=True)

# add new results to old results
ratings_data = pd.concat([ratings, results])
ratings.head(4)
events


# In[448]:


# drop ratings from ratings file then merge event data
ratings_data.drop(['useRating'], axis=1)
# sort by laptime then drop duplicates (i.e. worse rating)
ratings_data = ratings_data.sort_values(by=['laptime'])


# In[449]:


ratings_data.drop_duplicates(subset = ['steamId', 'GT3','race_id'], keep='first', inplace=True)
# remove where useRating = false
filt = (ratings_data['useRating'] == True)
ratings_data = ratings_data.loc[filt]


# In[450]:


# Add the best time per event and per class
ratings_data['best_times']  = ratings_data.groupby(['race_id', 'GT3'])['laptime'].transform('min')


# In[451]:


def rating_calc(x):
    zero_cut = 1.10
    rating = (1 - (x['laptime'] - x['best_times'])/ (x['best_times']* zero_cut - x['best_times'])) * 100
    if rating < 0:
        rating = 0
    return rating


# In[452]:


# Calculate the rating
# ratings_data['rating']= (1 - (ratings_data['laptime'] - ratings_data['best_times'])/(ratings_data['best_times']*1.07 - ratings_data['best_times'])) * 100
ratings_temp = ratings_data.apply(rating_calc, axis = 1)
ratings_data.head(5)


# In[453]:


overall_rating = ratings_data.groupby(['lastName'])['rating'].mean()
overall_rating


# In[454]:


ratings_data.to_json(ratings_name, orient='records')
events.to_json(events_name, orient='records')

