import pandas as pd


df = pd.read_csv('/Users/jakobalexandersen/scraper/ML model/output.csv', low_memory=False)

#remove url column
df = df.drop(['url'], axis=1)
df = df.drop(['lat'], axis=1)
df = df.drop(['lon'], axis=1)
df = df.drop(['date'], axis=1)

try:
    df['postal_code'] = df['postal_code'].astype(str).str.split('.').str[0]

# Convert 'postal_code' column to integers
    df['postal_code'] = df['postal_code'].astype(str)
    #add leading zero to postal codes with 3 digits
    df['postal_code'] = df['postal_code'].apply(lambda x: '0' + x if len(x) == 3 else x)

    #if floor is nan or empty, set to 0
    df['floor'] = df['floor'].fillna(0)

    #convert price_per_sqm to str
    df['price_per_sqm'] = df['price_per_sqm'].astype(int)


except:
    pass

#save to csv
df.to_csv('/Users/jakobalexandersen/scraper/ML model/output_clean.csv', index=False)
