import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns

roles = ["Top", "Jungle", "Middle", "Bottom", "Utility"]

df = pd.read_csv("Data_Creation/Data/Final.csv")

def hplot(role, df):
    fig = sns.histplot(data = df, x = f'{role.upper()}_GOLD_DIFF', hue='OUTCOME')
    if role == 'Utility':
        fig.set(xlabel = 'Support Gold Difference')
    else:
        fig.set(xlabel = f'{role} Gold Difference')
    return fig

for role in roles:
    plt.figure()
    fig = sns.histplot(data = df, x = f'{role.upper()}_GOLD_DIFF', hue='OUTCOME')
    if role == 'Utility':
        fig.set(xlabel = 'Support Gold Difference')
    else:
        fig.set(xlabel = f'{role} Gold Difference')
    plt.legend(title='Match Outcome', loc='upper right', labels=['Win', 'Loss'])
    plt.savefig(f'Figures/{role}_histplot.png')
        
        

