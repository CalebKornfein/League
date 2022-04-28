import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import statsmodels.api as sm

roles = ["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY"]

def name(role):
    return role + '_GOLD_LOG_RATIO'

df = pd.read_csv('Data_Creation/Data/final_log_ratio.csv')
y = list(df['OUTCOME'].values)

outcomes = []

for i in range(5):
    for j in range(5):
        if i == j: continue
        
        temp = df
        
        # create contrast variable
        contrast = f'{roles[i]}_{roles[j]}'
        temp[contrast] = df[name(roles[i])] - df[name(roles[j])]
        
        roles_set = set(roles)
        roles_set.remove(roles[i])
        roles_set.remove(roles[j])
        
        # define the variables for the model
        vars = [name(x) for x in roles_set] + [contrast]
        X = temp[vars]
        
        # model
        lr = sm.Logit(y, X).fit()
        p = dict(lr.pvalues)
        estimates = pd.DataFrame(lr.conf_int()).reset_index()
        
        for k, row in estimates.iterrows():
            if row['index'] == contrast:
                outcomes.append([contrast, round((row[0] + row[1] / 2), 3), round(row[0], 3) , round(row[1], 3), round(p[contrast], 3)])
                print(contrast, row[0] + row[1] / 2, p[contrast])
                break

final = pd.DataFrame(outcomes)
final.columns = ['contrast', 'estimate', 'lower', 'upper', 'pvalue']
final.to_csv('./Data_Creation/Data/Log_Ratio_Contrasts.csv', index=False)
        