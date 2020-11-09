Values to be varied for testing:

no. logs per user per day -> sample.py
no. logs per user per hour -> sample.py
no. users -> edit loc.csv file input
no. locations -> edit loc.csv file input
DP parameters -> DPTest.py
DP method -> DPTest.py


loc.CSV columns: 

BUILDINGS:  Name of given building

POPULATION: number of users with given building as 'home'

POPNDEX: index of last student assigned to given building (when concatenated sequentially)

BEACONS: number of beacons in given building

BEACONDEX: index of last beacon assigned to given building (when concatenated sequentially)

FIRST: index of beacon assigned as entrance/choke point of given building
