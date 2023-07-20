import os
import pandas as pd

# convert all xlsx files into csv files
for file in os.listdir('sales_concat'):
    if file.endswith('.xlsx'):
        df = pd.read_excel(f'sales_concat/{file}')
        df.to_csv(f'sales_concat/{file[:-5]}.csv', index=False)

# concatenate all csv files into one
df = pd.concat([pd.read_csv(f'sales_concat/{file}') for file in os.listdir('sales_concat') if file.endswith('.csv')])
df.to_csv('sales_concat/output.csv', index=False)

