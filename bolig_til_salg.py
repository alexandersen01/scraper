import requests
import pandas as pd
import time
import random
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim
import folium
import folium.plugins

url_lst = []
'''creates a list of urls to scrape from'''

for i in range (1, 15):
    response = requests.get(f'https://www.finn.no/realestate/homes/search.html?page={i}&sort=PUBLISHED_DESC')
    soup = BeautifulSoup(response.text, 'html.parser')

    for url in soup.find_all('a', href=True):
        soup.select('h2')[1].select('a', href=True)[0]['href']

        if 'www.finn.no/realestate/homes/' in url['href']:
            url_lst.append(url['href'])
        else:
            pass
    time.sleep(random.randint(1000, 2000)/1000)

counter = 0

'''create empty dataframe with specified columns '''

df = pd.DataFrame(columns=['address', 'price', 'area', 'rooms', 'year', 'type', 'url', 'price_per_m2', 'lat', 'lon', 'date'])
adr_lst = []
for url_i in range(len(url_lst)):
    response = requests.get(url_lst[url_i])
    soup = BeautifulSoup(response.text, 'html.parser')

    try:
        adr = soup.find_all('span', attrs={'class': 'pl-4'})[0].text
    except:
        adr = 'NA'

    try:
        geolocator = Nominatim(user_agent="myGeocoder")
        location = geolocator.geocode(adr)
        lat = location.latitude
        lon = location.longitude
    except:
        lat = 'NA'
        lon = 'NA'

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

    #add todays date
    date = time.strftime("%d/%m/%Y")


    df = df.append({'address': adr, 'price' : price, 'area' : area, 'rooms' : rooms, 'year' : year, 'type' : type, 'url' : url, 'price_per_m2' : price_per_m2, 'lat' : lat, 'lon' : lon, 'date' : date}, ignore_index=True)

    time.sleep(random.randint(500, 1000)/1000)

    counter += 1
    print(counter)


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

# Save df as excel with today's date:
df.to_excel('price_data_norway_' + str(time.strftime("%Y%m%d")) + '.xlsx', index=False)

'''remove rows with NA in lat and lon'''
df = df[df['lat'] != 'NA']
df = df[df['lon'] != 'NA']

'''display locations as circle map with folium'''
map1 = folium.Map(location = [59.940077, 10.764767], tiles = 'CartoDB dark_matter', zoom_start = 7)
df.apply(lambda row : folium.CircleMarker(location = [row['lat'], row['lon']]).add_to(map1), axis = 1)
cluster = folium.plugins.MarkerCluster().add_to(map1)

'''add info to popups on map'''

for (index, row) in df.iterrows():
    iframe = folium.IFrame('Address: ' + str(row['address']) + '<br>' + 'Price: ' + str(row['price']) + ' kr' + '<br>' + 'Price per m2: ' + str(row['price_per_m2']) + ' kr' + '<br>' + 'Area: ' + str(row['area']) + '<br>' + 'Rooms: ' + str(row['rooms']) + '<br>' + 'Year: ' + str(row['year']) + '<br>' + 'Type: ' + str(row['type']) + '<br>' + 'URL: ' + str(row['url']) + '<br>' + 'Date fetched: ' + str(row['date']))
    popup = folium.Popup(iframe, min_width = 300, max_width = 400, min_height = 300, max_height = 400)
    folium.Marker([row['lat'], row['lon']], popup = popup).add_to(cluster)

#save map as html file with today's date
map1.save('map_' + str(time.strftime("%Y%m%d")) + '.html')

print(df)

# To do:

# 3. Add column with number of bathrooms

# Overall goal: 
# Calculate estimated gross yield for each property 
