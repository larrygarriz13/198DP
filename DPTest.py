# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 22:26:19 2020

@author: Larry
"""

import numpy as np
import csv
import pandas as pd
import datetime
import random 
import math
import threading
import matplotlib.pyplot as plt
import time

import multiprocessing as mp
from itertools import repeat
from multiprocessing import Process, Manager
from multiprocessing import Pool

#system info
num_processes = mp.cpu_count()
print("Number of cpu : ", num_processes)




# yyyy-mm-dd
start_date = "2020-08-09"
end_date = "2020-08-12"
num_days = 4
num_sites = 100
num_user = 600

noise_count = []
real_count = []
n_cnt = 0

e = 5
DP = 1/(math.exp(e/2)+1)
    

class User:
    def __init__(self, id=0): #why is this = 0? ans: default 
        d_list = []
        for x in range(0, num_days):
            d_list.append(np.zeros((24, num_sites)))
        d_list = np.array(d_list)
        self.data = d_list
        # self.data = [np.zeros((24, 1000)), np.zeros((24, 1000)), np.zeros((24, 1000)), np.zeros((24, 1000))]
        self.id = id



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
    
    # print(old_time)
    # print(new_time)
    
    start = start_date.split("-")
    end = end_date.split("-")
    start_time = datetime.datetime(int(start[0]),int(start[1]), int(start[2]))
    end_time = datetime.datetime(int(end[0]),int(end[1]), int(end[2]))
    day_index = (old_time - start_time).days
    # print(start_time)
    
    # print("day_index: " + str(day_index))

    #adds in bluetooth pings to the data array u.data
    if(day_index <= num_days):
        if(new_time.hour == old_time.hour):
            data[day_index][hour][site] = data[day_index][hour][site] + 1
            # print(str(day_index)+ "-" + str(hour) + "-" + str(site))
            # print(data[day_index][hour][site])
        else:      
            o_date = old_time.date()
            n_date = new_time.date()
            
            if(o_date == n_date):
                o_set = new_time.hour - old_time.hour + 1
                for x in range(hour,hour + o_set):
                    data[day_index][x][site] = data[day_index][x][site] + 1
                    # print(data[day_index][x][site])
            else:
                o_set = 23 - old_time.hour + 1  
                for x in range(hour,hour + o_set):
                    data[day_index][x][site] = data[day_index][x][site] + 1
                    # print(data[day_index][x][site])
                    
                if(new_time < end_time):
                    o_set = new_time.hour + 1
                    data[day_index + 1][0][site] = data[day_index + 1][0][site] + 1
                    
                    for x in range(0, o_set):
                        data[day_index + 1][x][site] = data[day_index + 1][x][site] + 1
                        # print(data[day_index][x][site])
                        
                        
    
        
        
                
def noise(data, DP): #possibly use start and limit to define a range, allow multiple threads to process different sections?
    global n_cnt
    
    #sol 4 init
    # percent = int(0.3*num_sites)
    # choices = list(range(num_sites))
    # random.shuffle(choices)
    # res = choices[-percent:] 
    
    
    
    for a in range(len(data)): #day 
        for b in range(len(data[a])): #hour
            l = 0
            #for g in range(len(user_list[u].data[a][b])): #check if an entry is present in a given hour
                #l = l + user_list[u].data[a][b][g] #will equate to 1 if this entry exists
            #if(l==1):    
            #above section commented out; current implementation is to noise all hours wether log is present or not
            for c in range(len(data[a][b])): #site
                d = int(np.random.binomial(1, DP, 1))
                if(d==1):
                 
                  #[solution 1]: 50% noise negative 
                 
                   f = int(np.random.binomial(1, 0.5, 1))
                   if(f==1):
                       data[a][b][c] = data[a][b][c] + 1
                   else:
                       data[a][b][c] = data[a][b][c] - 1
                      
                n_cnt = n_cnt + 1                     
                 
                #[solution 2]: flip the bit (majority of noise will be flips to 1)
    
                  # if(data[a][b][c]==0):
                  #    data[a][b][c] = 1
                  # else:
                  #    data[a][b][c] = 0
                     
                #[solution 3]: Laplace distribution      
                # data[a][b][c] = data[a][b][c] + np.random.laplace(0, DP)
                
                #[solution 4]: only noise certain parts of data
                # p = 0.4
                # q = 0.6
                # num= q*(1-p)
                # denom = p*(1-q)
                # e = (math.log(num/denom))


               
                # if(data[a][b][c] >= 1):
                #     if(c in res):
                #         data[a][b][c] += np.random.binomial(1,q)
                #         # data[a][b][c] += -1
                # else:
                #     data[a][b][c] -= np.random.binomial(1,p)
                    
                #     if(data[a][b][c] < 0):
                #         data[a][b][c] = 0
                
                # data[a][b][c] = data[a][b][c]
                                    
                        
                    
    return data

def work(data, DP, user_no):
    print("Worker has processed # " + str(user_no))
    noised_data = noise(data, DP)
    return noised_data


if __name__ == "__main__":
        

    
    start = time.time()
    
    #real_count: data[day_index][hour][loc_id]
    for x in range(0, num_days):
        real_count.append(np.zeros((24, num_sites))) 
        
    real_count = np.array(real_count)
    noise_count = np.array(real_count)
    
    # Section takes CSV data and stores to 2-D per-user array (24hrsx1000loc)
    #dummy.csv is a two-day compiled list of user movement logs
    
    csv_reader = pd.read_csv('dummy.csv', parse_dates=True)        #switched to pandas dataframe for easier parsing
    #sort id from smallest to largest
    csv_reader = csv_reader.set_index(['PERSON_ID']).sort_index()
    print(csv_reader)
    csv_reader['TIME'] = pd.to_datetime(csv_reader.TIME)
    csv_reader.to_csv('sorted_dummy.csv')
    
    
    csv_reader = pd.read_csv('sorted_dummy.csv', parse_dates=True)   
    csv_reader['TIME'] = pd.to_datetime(csv_reader.TIME)
    
    line_count = 0
    name = ""
    noise_cnt = 0
    
    #MULTI-processing part
    import concurrent.futures 
    
    
    
                
    
    user_processing_no = 0
    
    list_of_users_processed = []
    mylist = []
    users_remaining = num_user
    
    with concurrent.futures.ProcessPoolExecutor() as executor:
        #f1 = executor.submit(noise, u.data)
        for row in range(len(csv_reader)):
            print(row)
            if(line_count == 0):
                print(csv_reader.loc[row])
                u = User(int(csv_reader.loc[row][0]))
                name = str(csv_reader.loc[row][1])
                fill_data(u.data, csv_reader.loc[row])
            else:
                if(csv_reader.loc[row][1] != name):
                    print("Processing User # " + str(user_processing_no) )
                    user_processing_no += 1    
                
                    noise_cnt += 1
                    
                    #add real value to total
                    real_count = real_count + u.data
                    
                    #schedule a worker to work on the noising of this user's logs
                    mylist.append(executor.submit(work, u.data, DP, user_processing_no))    

                    
                    del u
                    
                    u = User(int(csv_reader.loc[row][0]))
                    name = str(csv_reader.loc[row][1])
                    fill_data(u.data, csv_reader.loc[row])
                else:
                    name = str(csv_reader.loc[row][1])
                    fill_data(u.data, csv_reader.loc[row])
                    
                    
                    if(len(csv_reader) -1 == line_count):
                        print("Processing User # " + str(user_processing_no) )
                        user_processing_no += 1    
                        #add real value to total
                        real_count = real_count + u.data
                        
                        #schedule a worker to work on the noising of this user's logs
                        mylist.append(executor.submit(work, u.data, DP, user_processing_no))       
                        

                        
                                   
            # print("\n")
            line_count += 1
        print("Printing results...")
        for result in concurrent.futures.as_completed(mylist):
            #list_of_users_processed.append(result.result())
            users_remaining = users_remaining - 1
            print("1 Work finished, Users remaining: ." + str(users_remaining))
            noise_count += result.result()
    
        
    print(f'Processed {line_count} lines.')
    
    
    # pd.DataFrame(real_count[0]).to_csv("day0.csv")
    # pd.DataFrame(real_count[1]).to_csv("day1.csv") 
    # pd.DataFrame(noise_count[0]).to_csv("day0DP.csv")
    # pd.DataFrame(noise_count[1]).to_csv("day1DP.csv") 
    
    #real counts
    n= []
    for x in range(0, num_days):
        n.append(np.zeros((24, num_sites)))
    n = np.array(n)
    n = n + real_count[0]
    
    m = [np.zeros((num_sites))]
    for row in n[0]:
        m = m + row
    
    ts = pd.Series(m[0])
    ts = np.transpose(ts)
    
    #dp counts
    n= []
    for x in range(0, num_days):
        n.append(np.zeros((24, num_sites)))
    
    n = np.array(n)
    n = n + noise_count[0]
    
    m = [np.zeros((num_sites))]
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
    
    # end time
    end = time.time()
    
    # total time taken
    print(f"Runtime of the program is {end - start}")
    