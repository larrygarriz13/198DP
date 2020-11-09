import pandas as pd 
import numpy as np
import weightgen
from numpy.random import choice
Population = []

PopSize = 17316             #SCALABILITY PARAMETERS
Beacons = 625               #TO BE VARIED DURING TESTING
                            #Note: weightgen.py reads these values from the CSV based on amount of people and beacons. Could pass the info back to markov.py during init to remove need to hard code these values here

#PERSON CLASS STRUCTURE
class Person:
    def __init__(self,pid):                                 
        self.pid = pid                                      #PID taken from index
        self.locs = np.array(list(range(Beacons)))              #List of locations represented by index
        self.weights, self.home = weightgen.weight(pid)     #weight distribution, id of home building
        self.prev = -1                                      #initialize previous location to none
        self.stay = 0                                       #Tells us how long an individual has stayed in a building
        self.date = 9                                       #[TEMPORARY REQUIREMENT:] Hard code the start date of the dataset
        self.lastLog = 0
        self.currentBldg = -1                               #allows us to force exit at end of day

# INITIALIZATION OF LOCATION-WEIGHT PAIR (and other parameters)
#NOTE: Observed RAM consumption: 1.8GB for 17316 students
for x in range(PopSize):
    print(f"generating person: id = {x}")
    Population.append(Person(x))

df = pd.read_csv('output/example1/dummy.csv', parse_dates=True)         #dummy.csv: sample.py Trumania output 
print(df)       #access the trumania output

df['TIME'] = pd.to_datetime(df.TIME)


for x in range(len(df.index)):
    pid = int(df.loc[x][0])
    print(x)


    if df.loc[x]["TIME"].day != Population[pid].date:
        #print("cleaning")
        if Population[pid].currentBldg == Population[pid].home:
            mult = 2
        else:
            mult = 1
        Population[pid].weights = weightgen.weight(pid, out=True, multiplier = mult, skip = Population[pid].currentBldg)
        Population[pid].weights[Population[pid].currentBldg] = 0
        Population[pid].date = df.loc[x]["TIME"].day
        #here we 'repair' the previous log by ensuring the student leaves school at the end of the day
        df.at[Population[pid].lastLog,'LOCATION'] = Population[pid].currentBldg                     #takes the last log and sets it to bldg exit
        Population[pid].prev = -1
    #print(f"Drawing Person: {df.loc[x][1]}")
    draw = choice(Population[pid].locs, size=1,p=np.ndarray.tolist(Population[pid].weights))        #Core of the script; randomly selects the visited location
    df.at[x,'LOCATION'] = draw                                                                         #write location back to dataframe
    #print(f"Person: {df.loc[x][1]} Visited location: {draw}")

    Population[pid].weights, Population[pid].stay, Population[pid].currentBldg = weightgen.visit(Population[pid].pid, int(draw), Population[pid].weights, Population[pid].prev, Population[pid].home, Population[pid].stay, Population[pid].currentBldg) #provides updated weights based on movement
    Population[pid].prev = draw                         #save previous location for memory
    Population[pid].lastLog = x                         #save CSV index of last log



    #print(df) 

df.to_csv('dummy.csv', index=False)
