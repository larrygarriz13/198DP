import numpy as np
import pandas as pd
from scipy.stats import poisson
import statistics as st

df = pd.read_csv('loc.csv')

#three different global data structures for the methods to access for info on beacons and users
#yeeeah it's not super optimized :(

BldgInfo = []
entrances = []
BldgData = {}

for x in range(len(df.index)):      #Collects user and beacon data from given CSV file
    BldgInfo.append([int(df.loc[x]['FIRST']), df.loc[x]['BEACONDEX'], int(df.loc[x]['POPNDEX'])])
    entrances.append(df.loc[x]['FIRST'])
    BldgData[df.loc[x]['FIRST']] = int(df.loc[x]['BEACONDEX'])

num_loc = BldgData[df.loc[x]['FIRST']]  #takes the last location index to know max number of locations


def roomWeight(s):          #adjust the number of weights to be assigned based on the number of rooms in the given building
    weightDist = []
    mu = s/2
    sum = 0
    for x in range(s):
        z = poisson.pmf(x,mu)
        weightDist.append(z)
        sum = sum + z

    sum2 = 0                                        #for normalizing outputs; probabilities must sum to 1
    for x in range(s):
        weightDist[x] = weightDist[x]/sum
        sum2 = sum2 + weightDist[x]
    weightDist[x] = weightDist[x] + (1-sum2)

    return weightDist, sum


def membership(pid):                                                    #determines where a person belongs to given their ID
    for x in range(len(BldgInfo)):
        if pid < BldgInfo[x][2]:
            home = BldgInfo[x][0]
            return home

def building(loc):                                                      #determines the building you're in given the pinged beacon
    for x in range(len(BldgInfo)):
        if loc < BldgInfo[x][1]:
            home = BldgInfo[x][0]
            return home

def weight(pid, multiplier=1, out=False, skip=999):                      # [WEIGHT]: Sets default (or exiting) entrance weights for an individual
    weights = np.zeros( num_loc )                                          # generate empty weights for each person [TO DO] Make location total variable?
    Home = membership(pid)                                               #temp value for skip is arbitrary, big enough to be out of the way of number of locations

    if out == True and multiplier == 1:
        length = len(entrances) - 2
    else:
        length = len(entrances) - 1
    weightDist, sum = roomWeight(length)
    newsum = 0
    for x in range(len(entrances)):                          
        z = x
        if entrances[x] >= Home or entrances[x] >= skip:            #shift indexes to skip locations that have other probabilities (to be set later in code)
            z = x - 1
        if entrances[x] >= Home and entrances[x] >= skip:
            z = x - 2
        weights[entrances[x]] = (weightDist[z])*0.5*multiplier
        if x != Home:
            if x != skip:
                newsum = newsum + weights[entrances[x]]
        if entrances[x] == Home:
            weights[entrances[x]] = 0.5

    if skip < num_loc:                              #if skip is actual location: exited from building other than home: zero out that probability
        weights[skip] = 0 

    if out == True:
        return weights
    else:
        return weights, Home                                    #pass back weights list (and home address for future reference)

def visit(pid, loc, new_weight, prev, home, stay, currentBldg):
    if loc in entrances:
        if prev in entrances or prev == -1:                     #[SCENARIO 1] They're entering a building for the first time 
            length = BldgData[loc]-loc-1
            weightDist, sum = roomWeight(length)
            newsum = 0
            for x in range(loc+1,BldgData[loc]): 
                new_weight[x] = weightDist[x-loc-1]
                newsum = newsum + new_weight[x]

            newsumcheck = newsum - new_weight[x]
            new_weight[x] = new_weight[x] + (1-newsum)
            newsumcheck = newsumcheck + new_weight[x]

            for x in entrances:                                 #zero out all entrance weights since they've entered a building
                new_weight[x] = 0
            stay = 1                                            #initialize duration of stay counter (longer stay, greater likelihood of leaving)
            currentBldg = loc
            return new_weight, stay, currentBldg                #update current building info
        else:                                                   #[SCENARIO 2] They're exiting the building
            if loc == home: 
                weights = weight(pid,2,True)                    #for exit: weight reassignment dependent on what building you're exiting from
            else:
                weights = weight(pid,1,True,skip=loc)
            weights[loc] = 0                                     #zero out current location
            stay = 0                                            #reset duration of stay counter
        return weights, stay, currentBldg

    else:                                                       #[SCENARIO 3] moving around the building
        if currentBldg == home:                                        #determine exit likelihood (greatly increased for non-home dep, aribtrarily set values)
            ext = 0.2
        else:
            ext = 0.4                                                      #THESE PARAMETERS CAN BE VARIED TO adjust tendency of students to transfer buildings

        new_weight[currentBldg] = ext * stay                              #set chance of exiting; exit probability * duration of stay
        if new_weight[currentBldg] > 1:
            new_weight[currentBldg] = 1                                   #if product manages to exceed 1, set upper limit to maintain integrity of probabilities
        length = BldgData[currentBldg]-currentBldg-2
        weightDist, sum = roomWeight(length)
        newsum = 0
        for x in range(currentBldg+1,BldgData[currentBldg]):                          
            z = x
            if x >= loc:
                z = x - 1
            new_weight[x] = (weightDist[z-currentBldg-1])
            new_weight[x] = (weightDist[z-currentBldg-1])*(1-new_weight[currentBldg])
            if x != loc:
                newsum = newsum + new_weight[x]
        newsumcheck = newsum - new_weight[x]                                    #re-normalize probabilities
        new_weight[x] = (new_weight[x] + ((1-new_weight[currentBldg])-newsum))
        newsumcheck = newsumcheck + new_weight[x]

        new_weight[loc] = 0
        stay = stay + 1

        return new_weight, stay, currentBldg



