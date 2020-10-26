# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 22:26:19 2020

@author: Larry
"""

import numpy as np
import csv
import pandas as pd
import datetime
import random as rd
import math
import threading

import matplotlib.pyplot as plt
def fill_data(data, row):

    month = row["TIME"].month
    day = row["TIME"].month - 9     #current dataset starts aug 9 so -9
    year = row["TIME"].year
    hour = row["TIME"].hour         #already in military time
    minute = row["TIME"].minute
    sec = row["TIME"].second
    site = int(row["LOCATION"])
    
    #temporarily commented out the duration elements coz this was rebuilt with the duration column missing
    
    #duration = row["DURATION"].split('.')
    #dur_min = int(duration[0])
    #dur_sec = int(duration[1])
    
    #pandas library could simplify this? 
    #old_time = datetime.datetime(year, month, day, hour, minute, sec)
    #new_time = old_time + datetime.timedelta(minutes = dur_min)
    
    #adds in bluetooth pings to the data array u.data
    #if(new_time.hour == old_time.hour):
    data[day][hour][site] = 1
    #else:
        #o_set = new_time.hour - old_time.hour + 1
        #for x in range(hour,hour + o_set):
            #if(hour + o_set < 24):
                #data[day_new][x][site] = 1
                
                
def noise(user_list, DP, start, limit): #possibly use start and limit to define a range, allow multiple threads to process different sections?
    h = start
    for u in range(start,limit):
        for a in range(len(user_list[u].data)): #day 
            for b in range(len(user_list[u].data[a])): #hour
                l = 0
                #for g in range(len(user_list[u].data[a][b])): #check if an entry is present in a given hour
                    #l = l + user_list[u].data[a][b][g] #will equate to 1 if this entry exists
                #if(l==1):    
                #above section commented out; current implementation is to noise all hours wether log is present or not
                for c in range(len(user_list[u].data[a][b])): #site
                    d = int(np.random.binomial(1, DP, 1))
                    if(d==1):
                     
                     #[solution 1]: 50% noise negative 
                     
                     f = int(np.random.binomial(1, 0.5, 1))
                     if(f==1):
                         user_list[u].data[a][b][c] = user_list[u].data[a][b][c] + 1
                     else:
                         user_list[u].data[a][b][c] = user_list[u].data[a][b][c] - 1
                         
                     
                    #[solution 2]: flip the bit (majority of noise will be flips to 1)

                     #if(user_list[u].data[a][b][c]==0):
                         #user_list[u].data[a][b][c] = 1
                     #else:
                         #user_list[u].data[a][b][c] = 0
                         
                    #[solution 3]: Laplace distribution      
                    #user_list[u].data[a][b][c] = user_list[u].data[a][b][c] + np.random.laplace()
                            
                        
        h = h+1 
        print(h)      #progress tracking in terminal
    return user_list


class User:
    def __init__(self, id=0): #why is this = 0? ans: default 
        self.data = [np.zeros((24, 1000)), np.zeros((24, 1000)), np.zeros((24, 1000)), np.zeros((24, 1000))]
        self.id = id
user_list = []
# Section takes CSV data and stores to 2-D per-user array (24hrsx1000loc)
#dummy.csv is a two-day compiled list of user movement logs

csv_reader = pd.read_csv('dummy.csv', parse_dates=True)        #switched to pandas dataframe for easier parsing
csv_reader['TIME'] = pd.to_datetime(csv_reader.TIME)
line_count = 0
name = ""
for row in range(len(csv_reader)):
    print(row)
    if line_count == 0:
        #print(f'Column names are {", ".join(row)}')
        line_count += 1
    if(len(user_list) == 0):
        u = User(int(csv_reader.loc[row][0]))
        user_list.append(u)
        name = csv_reader.loc[row][1]
        fill_data(u.data, csv_reader.loc[row])
    else:

        if(csv_reader.loc[row]["NAME"] != name): #CSV data needs to be manually organized ALPHABETICALLY. Fills up a users' info until next user in list is reached.
            u = User(int((csv_reader.loc[row]["PERSON_ID"])))
            user_list.append(u)
            name = (csv_reader.loc[row]["NAME"])
            fill_data(u.data, csv_reader.loc[row])
        else:
            fill_data(u.data, csv_reader.loc[row])
    line_count += 1
print(f'Processed {line_count} lines.')

pd.DataFrame(user_list[0].data[1]).to_csv("johnkoch.csv")


n =  [np.zeros((24, 1000)), np.zeros((24, 1000)), np.zeros((24, 1000)), np.zeros((24, 1000))]
for u in user_list: #adds together all the day 1 and day 2 logs
    n[0] = n[0] + u.data[0]
    n[1] = n[1] + u.data[1]
pd.DataFrame(n[0]).to_csv("day0.csv")
pd.DataFrame(n[1]).to_csv("day1.csv")
m = [np.zeros((1000))]

for row in n[0]:
    m = m + row
ts = pd.Series(m[0])
ts = np.transpose(ts)
#DP Noising
scores = []

e = 0.1
DP = 1/(math.exp(e/2)+1)


#insert threads here? call noise function

noise(user_list, DP,  0, int(len(user_list)))

#producing noised output CSVs
pd.DataFrame(user_list[0].data[1]).to_csv("johnkochDP.csv")
test = user_list[0].data[1]
n =  [np.zeros((24, 1000)), np.zeros((24, 1000)), np.zeros((24, 1000)), np.zeros((24, 1000))]
for u in user_list:
    n[0] = n[0] + u.data[0]
    n[1] = n[1] + u.data[1]
pd.DataFrame(n[0]).to_csv("day0DP.csv")
pd.DataFrame(n[1]).to_csv("day1DP.csv") 
m = [np.zeros((1000))]
for row in n[0]:
    m = m + row
ds = pd.Series(m[0])
ds = np.transpose(ds)
fig, axs = plt.subplots(2,1)
fig.suptitle(F"DP value: {e}")
axs[0].plot(ts)
axs[0].set_xlabel('Location')
axs[0].set_ylabel('Visits (clean)')
axs[1].plot(ds)
axs[1].set_xlabel('Location')
axs[1].set_ylabel('Visits (noised)')
plt.show()     

### SORTING ALGORITHM (CLEAN) ###       
dict_ts = {0:1}
for v in range(len(ts)):
        dict_ts[v] = ts[v]
dicts_ts = sorted(dict_ts.items(), key = lambda kv:kv[1], reverse = True)
x = 0 
print("top 10 max occupancies (CLEAN):")
while (x<10):
    print(f'{x+1}: loc: {dicts_ts[x][0]} pop: {dicts_ts[x][1]}')
    x = x + 1        
    
### SORTING ALGORITHM (NOISED) ###
dict_ds = {0:1}
for v in range(len(ds)):
        dict_ds[v] = ds[v]
dicts_ds = sorted(dict_ds.items(), key = lambda kv:kv[1], reverse = True)
x = 0 
print("top 10 max occupancies (NOISED):")
while (x<10):
    print(f'{x+1}: loc: {dicts_ds[x][0]} pop: {dicts_ds[x][1]}')
    x = x + 1        
y = 0
for w in range(10):
    for x in range(10):
        if (dicts_ts[w][0] == dicts_ds[x][0]):
            y = y + 1 
print(f'score: {y}')