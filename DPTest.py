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

start_date = "2020-08-09"
end_date = "2020-08-12"
num_days = 4
num_sites = 100
num_user = 100
n_cnt = 0

class User:
    def __init__(self, id=0): #why is this = 0? ans: default 
        d_list = []
        for x in range(0, num_days):
            d_list.append(np.zeros((24, num_sites)))
        self.data = d_list
        # self.data = [np.zeros((24, 1000)), np.zeros((24, 1000)), np.zeros((24, 1000)), np.zeros((24, 1000))]
        self.id = id

user_list = []

def fill_data(data, row):
    
    month = int(row["TIME"].month)
    day = int(row["TIME"].day)
    year = int(row["TIME"].year)
    hour = int(row["TIME"].hour)         #already in military time
    minute = int(row["TIME"].minute)
    sec = int(row["TIME"].second)
    site = int(row["LOCATION"])
    duration = float(row["DURATION"])
    
  
    old_time = datetime.datetime(year, month, day, hour, minute, sec)
    new_time = old_time + datetime.timedelta(seconds = duration)
    
    print(old_time)
    print(new_time)
    
    start = start_date.split("-")
    end = end_date.split("-")
    start_time = datetime.datetime(int(start[0]),int(start[1]), int(start[2]))
    end_time = datetime.datetime(int(end[0]),int(end[1]), int(end[2]))
    day_index = (old_time - start_time).days
    print(start_time)
    
    print("day_index: " + str(day_index))

    #adds in bluetooth pings to the data array u.data
    if(day_index <= num_days):
        if(new_time.hour == old_time.hour):
            data[day_index][hour][site] = data[day_index][hour][site] + 1
            print(str(day_index)+ "-" + str(hour) + "-" + str(site))
            print(data[day_index][hour][site])
        else:      
            o_date = old_time.date()
            n_date = new_time.date()
            
            if(o_date == n_date):
                o_set = new_time.hour - old_time.hour + 1
                for x in range(hour,hour + o_set):
                    data[day_index][x][site] = data[day_index][x][site] + 1
                    print(data[day_index][x][site])
            else:
                o_set = 23 - old_time.hour + 1  
                for x in range(hour,hour + o_set):
                    data[day_index][x][site] = data[day_index][x][site] + 1
                    print(data[day_index][x][site])
                    
                if(new_time < end_time):
                    o_set = new_time.hour + 1
                    data[day_index + 1][0][site] = data[day_index + 1][0][site] + 1
                    
                    for x in range(0, o_set):
                        data[day_index + 1][x][site] = data[day_index + 1][x][site] + 1
                        print(data[day_index][x][site])
                        
                        
    
        
        
                
def noise(user_list, DP, start, limit): #possibly use start and limit to define a range, allow multiple threads to process different sections?
    h = start
    global n_cnt
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
                          
                      n_cnt = n_cnt + 1
                     
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

#d_list: data[day_index][hour][loc_id]
        

id_list = []
# Section takes CSV data and stores to 2-D per-user array (24hrsx1000loc)
#dummy.csv is a two-day compiled list of user movement logs

csv_reader = pd.read_csv('dummy.csv', parse_dates=True)        #switched to pandas dataframe for easier parsing
#sort id from smallest to largest
csv_reader.set_index(['PERSON_ID']).sort_index()
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
        id_list.append(int(csv_reader.loc[row][0]))
    else:
        if(int(csv_reader.loc[row]["PERSON_ID"]) in id_list):
            for user in user_list:
                if(user.id == int(csv_reader.loc[row]["PERSON_ID"])):
                   u = user
            
            fill_data(u.data, csv_reader.loc[row])
        else:
            print("not here")
            u = User(int(csv_reader.loc[row][0]))
            user_list.append(u)
            id_list.append(int(csv_reader.loc[row][0]))
            fill_data(u.data, csv_reader.loc[row])
           
            
        
    print("\n")
   
    line_count += 1
print(f'Processed {line_count} lines.')

old = user_list

pd.DataFrame(user_list[0].data[1]).to_csv("johnkoch.csv")

n= []
for x in range(0, num_days):
    n.append(np.zeros((24, num_sites)))

for u in user_list: #adds together all the day 1 and day 2 logs
    n[0] = n[0] + u.data[0]
    n[1] = n[1] + u.data[1]
pd.DataFrame(n[0]).to_csv("day0.csv")
pd.DataFrame(n[1]).to_csv("day1.csv")
m = [np.zeros((num_user))]

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
# pd.DataFrame(user_list[0].data[1]).to_csv("johnkochDP.csv")
test = user_list[0].data[1]
n= []
for x in range(0, num_days):
    n.append(np.zeros((24, num_sites)))

for u in user_list:
    n[0] = n[0] + u.data[0]
    n[1] = n[1] + u.data[1]
pd.DataFrame(n[0]).to_csv("day0DP.csv")
pd.DataFrame(n[1]).to_csv("day1DP.csv") 
m = [np.zeros((num_user))]

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