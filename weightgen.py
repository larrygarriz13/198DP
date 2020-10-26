# 1000 Locations, 100 participants

import numpy as np
import pandas as pd
entrances = [0, 20, 40, 60, 80] #Declare building entrances here

BldgInfo = [[0,20,2000],[20,40,8000],[40,60,8500],[60,80,9000],[80,100,10000]]    #index 0: bldg entrance, index 1: max index of bldg beacon, index 2: max pid of assigned population

BldgData = {0:20,20:40,40:60,60:80,80:100}
#will simplify BldgInfo and BldgData into one in next commit

def membership(pid):
    for x in range(len(BldgInfo)):
        #print(x)
        if pid < BldgInfo[x][2]:
            home = BldgInfo[x][0]
            return home

#also hard coded for varying building sizes?

def building(loc):
    for x in range(len(BldgInfo)):
        print(x)
        if loc < BldgInfo[x][1]:
            home = BldgInfo[x][0]
            return home

def weight(pid, multiplier=1, out=False):                      # [WEIGHT]: Sets default start-of-day weights for an individual
    weights = np.zeros( (100) )                                # generate empty weights for each person
    Home = membership(pid)
    for x in entrances:
        weights[x] = (0.5/(len(BldgInfo)-1))*multiplier
        if x == Home:
            weights[x] = 0.5
    if out == True:
        return weights
    else:
        return weights, Home                                    #pass back weights list (and home address for future reference)

def visit(pid, loc, new_weight, prev, home, stay, currentBldg):
    if loc in entrances:
        if prev in entrances or prev == -1:                     #[SCENARIO 1] They're entering a building for the first time 
            for x in range(loc,BldgData[loc]): 
                new_weight[x] = 1/(BldgData[loc]-loc-1)
            for x in entrances:                                 #zero out all entrance weights since they've entered a building
                new_weight[x] = 0
            stay = 1                                            #initialize stay counter
            currentBldg = loc
            return new_weight, stay, currentBldg                #update current building info
        else:                                                   #[SCENARIO 2] They're exiting the building
            if loc == home: 
                weights = weight(pid,2,True)                    #for exit: weight reassignment dependent on what building you're exiting from
            else:
                weights = weight(pid,(len(BldgData)-1)/(len(BldgData)-2),True)
            weights[loc] = 0                                    #zero out current location
            stay = 0                                            #reset counter
        return weights, stay, currentBldg

    else:                                                       #[SCENARIO 3] moving around the building

        if currentBldg == home:                                        #determine exit likelihood (greatly increased for non-home dep)
            ext = 0.2
        else:
            ext = 0.7

        new_weight[currentBldg] = ext * stay                              #set chance of exiting; exit probability * duration of stay
        if new_weight[currentBldg] > 1:
            new_weight[currentBldg] = 1                                   #if product manages to exceed 1, set upper limit

        for x in range(currentBldg+1,BldgData[currentBldg]):                          
            
            new_weight[x] = (1-new_weight[currentBldg])/(BldgData[currentBldg]-currentBldg-2)        

        new_weight[loc] = 0
        stay = stay + 1

        return new_weight, stay, currentBldg

