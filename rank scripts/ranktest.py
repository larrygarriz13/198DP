import pandas as pd
import numpy as np

df = pd.read_csv("198-20.0.csv")            #just a naming convention for saved sheets: 198-<DP value>.csv
df = df.T
out = pd.DataFrame()

real = pd.read_csv('rank_real.csv')         #1-D array of real rank answers

for row in range(30):
    print(df.loc[str(row)])
    dx = pd.DataFrame(data={'logs':df.loc[str(row)]}) 
    dx['default_rank'] = dx['logs'].rank(ascending=False,method ='first')
    print(dx)
    dx = dx.rename(columns={'default_rank':str(row)})
    out = out.append(dx[str(row)])

out = out.append(real['default_rank'])

out = out.T
out['mean'] = out.mean(axis=1)
out['stdDev'] = out.std(axis=1)
out.to_csv('unsorted_rankings20.0.csv')
out = out.sort_values(by=['default_rank'])
print(out)
out.to_csv('rankings20.0.csv')              #columns sorted by real rankings
