import pandas as pd

df = pd.read_csv('m_data.csv')

benefits = df['benefits']

for ind, item in enumerate(df['benefits']):
    new = '<p>' + item.replace('\n', '</p><p>') + '</p>'
    print(new)
    if ind == 3:
        break