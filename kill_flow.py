import pandas as pd
from itertools import product
import numpy as np

team1 = ['TOP1', 'JUNGLE1', 'MIDDLE1', 'BOTTOM1', 'UTILITY1']
team2 = ['TOP2', 'JUNGLE2', 'MIDDLE2', 'BOTTOM2', 'UTILITY2']


df = pd.read_csv("Data_Creation/Data/Matches.csv")

roles = ["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY"]
avg_matrix = [[0] * 5 for _ in range(5)]
sizes = []
for i, r1 in enumerate(roles):
    for j, r2 in enumerate(roles):
        values = list(df[f'{r1}1_{r2}2'].values) + list(df[f'{r1}2_{r2}1'].values)
        avg = np.mean(values)
        avg_matrix[i][j] = avg
        
        sizes.append(avg)
        if avg > 0.33:
            print(f'{r1} - {r2}: {avg}')
        
        

