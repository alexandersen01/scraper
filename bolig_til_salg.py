import requests
import pandas as pd
import time
import random
from bs4 import BeautifulSoup

url_lst = []
'''creates a list of urls to scrape from'''

for i in range (1, 5):
    response = requests.get(f'https://www.finn.no/realestate/homes/search.html?page={i}&sort=PUBLISHED_DESC')
    soup = BeautifulSoup(response.text, 'html.parser')

    for url in soup.find_all('a', href=True):
        soup.select('h2')[1].select('a', href=True)[0]['href']

        if 'www.finn.no/realestate/homes/' in url['href']:
            url_lst.append(url['href'])
        else:
            pass
    time.sleep(random.randint(1000, 2000)/1000)

'''create empty dataframe with specified columns '''

df = pd.DataFrame(columns=['address', 'price', 'area', 'rooms', 'year', 'type', 'url', 'price_per_m2'])

for url_i in range(len(url_lst)):
    response = requests.get(url_lst[url_i])
    soup = BeautifulSoup(response.text, 'html.parser')

    try:
        adr = soup.find_all('span', attrs={'class': 'pl-4'})[0].text
    except:
        adr = 'NA'

    try:
        price = soup.find_all('span', attrs={'class': 'text-28 font-bold'})[0].text.replace(' ', '').replace('kr', '')
    except:
        price = 'NA'

    try:
        area = soup.find_all('div', attrs={'data-testid': 'info-usable-area'})[0].text
        area = area.replace('m²', '').replace('Bruksareal', '')
    except:
        area = 'NA'

    try:
        rooms = soup.find_all('div', attrs={'data-testid': 'info-rooms'})[0].text
        rooms = rooms.replace('Rom', '')
    except:
        rooms = 'NA'
    
    try:
        year = soup.find_all('div', attrs={'data-testid': 'info-construction-year'})[0].text
        year = year.replace('Byggeår', '')
    except:
        year = 'NA'
    
    try:    
        type = soup.find_all('div', attrs={'data-testid': 'info-property-type'})[0].text
        type = type.replace('Boligtype', '')
    except:
        type = 'NA'

    try:
        price_per_m2 = int(int(price)/int(area))
    except:
        price_per_m2 = 'NA'
    
    url = url_lst[url_i]


    df = df.append({'address': adr, 'price' : price, 'area' : area, 'rooms' : rooms, 'year' : year, 'type' : type, 'url' : url, 'price_per_m2' : price_per_m2}, ignore_index=True)

    time.sleep(random.randint(500, 1000)/1000)



'''clean data'''

df['address'] = df['address'].str.replace(',', ' ')

df['postal_code'] = df['address'].str.extract('(\d{4})')

try:
    df['address'] = df['address'].str.replace('\d{4}', '')
except:
    pass


df['city'] = df['address'].apply(lambda x: x.split()[-2] + ' ' + x.split()[-1] if x.split()[-1] == 'N' or x.split()[-1] == 'S' else x.split()[-1])


city_list = df['city'].unique().tolist()

'''remove city from address'''

df['address'] = df['address'].apply(lambda x: ' '.join(x.split()[:-2]) if x.split()[-1] == 'N' or x.split()[-1] == 'S' else ' '.join(x.split()[:-1]))


#clean area column and keep just numbers
df['area'] = df['area'].str.replace(str(), '')



# Delete rows in 'area' that dont contain numbers:
df = df[df['area'].str.contains('\d')]

try:
    df['area'] = df['area'].str.replace('\.', '')
except:
    pass

# Convert 'area' to integer: 
df['area'] = df['area'].astype(int)

# Remove 'area' that are less than 10:
if df['area'].min() < 10:
    df = df[df['area'] > 10]

# Remove ' ' and 'kr' from 'price' column:
df['price'] = df['price'].str.replace(' kr', '')
df['price'] = df['price'].str.replace(' ', '')

#remove rows with 'Video' or 'Visning' in city column
df = df[~df['city'].str.contains('Video')]
df = df[~df['city'].str.contains('Visning')]

# Save df as csv with today's date:
df.to_excel('price_data_norway_' + str(time.strftime("%Y%m%d")) + '.xlsx', index=False)



print(df)

# To do: 
# 1. Add date column
# 2. Add column with number of rooms
# 3. Add column with number of bathrooms

# Overall goal: 
# Calculate estimated gross yield for each property 
