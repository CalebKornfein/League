import pandas as pd
import random
from collections import defaultdict
from itertools import product
import seaborn as sns
import math

df = pd.read_csv('Data/Matches.csv')

roles = ['TOP', 'JUNGLE', 'MIDDLE', 'BOTTOM', 'UTILITY']
final = defaultdict(lambda: [])

for i, row in df.iterrows():
    
    label = random.choice([1, 0])
    final['OUTCOME'].append(label)
    
    if label == 1:
        t1, t2 = '1', '2'
    else:
        t1, t2 = '2', '1'
    
    for role in roles:
        final[f'{role}_GOLD_LOG_RATIO'].append(math.log(row[f'{role}{t1}_GOLD'] / row[f'{role}{t2}_GOLD'], 2))
    
        final[f'{role}{t1}_IMPACT'].append(sum([row[f'{r}{t2}_{role}{t1}'] for r in roles if not r == role]))
        final[f'{role}{t2}_IMPACT'].append(sum([row[f'{r}{t1}_{role}{t2}'] for r in roles if not r == role]))
    
    for r1, r2 in product(roles, roles):
        if not r1 == r2:
            final[r1 + '_' + r2].append(row[f'{r1}{t1}_{r2}{t2}'] - row[f'{r2}{t2}_{r1}{t1}'])
        
final = pd.DataFrame(final)
final.to_csv("Data/final_log_ratio.csv", index=False)


