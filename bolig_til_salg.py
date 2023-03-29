import os
import requests
import pandas as pd
import time
import random
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim
import folium
import folium.plugins

#print current working directory
print(os.getcwd())

url_lst = []
rentals_lst = []
'''creates a list of urls to scrape from'''
print('hehe')
## 1. Scrape real estate adds from Finn.no ##

fetched = 0
for i in range (1, 50):
    response = requests.get(f'https://www.finn.no/realestate/homes/search.html?page={i}&sort=PUBLISHED_DESC')
    soup = BeautifulSoup(response.text, 'html.parser')

    for url in soup.find_all('a', href=True):
        soup.select('h2')[1].select('a', href=True)[0]['href']

        if 'www.finn.no/realestate/homes/' in url['href']:
            url_lst.append(url['href'])
        else:
            pass
    time.sleep(random.randint(1000, 2000)/1000)
    fetched += 1
    print(f'Fetched {fetched} pages')

# scrape rental adds from Finn.no
for i in range (1, 50):
    response1 = requests.get(f'https://www.finn.no/realestate/lettings/search.html?page={i}&sort=PUBLISHED_DESC')
    soup1 = BeautifulSoup(response1.text, 'html.parser')

    for url in soup1.find_all('a', href=True):
        soup1.select('h2')[1].select('a', href=True)[0]['href']

        if 'www.finn.no/realestate/lettings/' in url['href']:
            rentals_lst.append(url['href'])
        else:
            pass
    time.sleep(random.randint(1000, 2000)/1000)



#data frame for rental adds
df_rentals = pd.DataFrame(columns = ['address', 'price', 'area', 'url', 'lat', 'lon', 'date', 'price_per_m2'])

#extract data from rental adds
rent_counter = 0
for url in range(len(rentals_lst)):
    try:
        response1 = requests.get(rentals_lst[url])
    except:
        pass
    soup1 = BeautifulSoup(response1.text, 'html.parser')


    try:    
        adr = soup1.find_all('span', attrs={'class': 'pl-4'})[0].text
    except:
        adr = 'NA'

    try:
        rent = soup1.find('dd', attrs={'class': 'm-0 font-bold text-28'}).text.replace(' ', '').replace('kr', '')
    except:
        rent = 'NA'

    try:
        area = soup1.find_all('dd')[2].text
        area = area.split()[0]
        area = int(area)

    except: 
        area = 'NA'

    try:
        geolocator = Nominatim(user_agent="myheocoder")
        location = geolocator.geocode(adr)
        lat = location.latitude
        lon = location.longitude
    except:
        lat = 'NA'
        lon = 'NA'

    try:
        price_per_m2 = int(int(rent)/int(area))
    except:
        price_per_m2 = 'NA'
    
    date = time.strftime("%d/%m/%Y")

    url = rentals_lst[url]

    df_rentals = df_rentals.append({'address': adr, 'price': rent, 'area': area, 'url': url, 'lat' : lat, 'lon' : lon, 'date' : date, 'price_per_m2' : price_per_m2}, ignore_index=True)

    rent_counter += 1
    print(f'Extracted data from {rent_counter} rental adds')
    
    

    time.sleep(random.randint(500, 1000)/1000)




#clean rent data
df_rentals['address'] = df_rentals['address'].str.replace(',', ' ')

#extract postal code from address
df_rentals['postal_code'] = df_rentals['address'].str.extract(r'(\d{4})')

#remove postal code from address
try:
    df_rentals['address'] = df_rentals['address'].str.replace(r'(\d{4})', '')
except:
    pass

#extract city from address
df_rentals['city'] = df_rentals['address'].apply(lambda x: x.split()[-2] + ' ' + x.split()[-1] if x.split()[-1] == 'N' or x.split()[-1] == 'S' else x.split()[-1])

# Create list of unique cities
city_list_r = df_rentals['city'].unique().tolist()

# Remove city from address
df_rentals['address'] = df_rentals['address'].apply(lambda x: ' '.join(x.split()[:-2]) if x.split()[-1] == 'N' or x.split()[-1] == 'S' else ' '.join(x.split()[:-1]))

#delete rows in area if area is 'NA'
df_rentals = df_rentals[df_rentals['area'] != 'NA']

# Remove 'area' that are less than 10:
if df_rentals['area'].min() < 10:
    df_rentals = df_rentals[df_rentals['area'] > 10]

# Remove ' ' and 'kr' from 'price' column:
df_rentals['price'] = df_rentals['price'].str.replace(' kr', '')
df_rentals['price'] = df_rentals['price'].str.replace(' ', '')

#remove rows with 'Video' or 'Visning' in city column
df_rentals = df_rentals[~df_rentals['city'].str.contains('Video')]
df_rentals = df_rentals[~df_rentals['city'].str.contains('Visning')]

'''remove rows with NA in lat and lon'''
df_rentals = df_rentals[df_rentals['lat'] != 'NA']
df_rentals = df_rentals[df_rentals['lon'] != 'NA']


'''create empty dataframe with specified columns '''
counter = 0
df = pd.DataFrame(columns=['address', 'price', 'area', 'rooms', 'year', 'type', 'url', 'price_per_m2', 'lat', 'lon', 'date', 'floor', 'ownership'])
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
        floor = soup.find_all('div', attrs={'data-testid': 'info-floor'})[0].text
        floor = floor.replace('Etasje', '')
    except:
        floor = 'NA'

    try:
        price_per_m2 = int(int(price)/int(area))
    except:
        price_per_m2 = 'NA'
    
    try:
        ownership = soup.find_all('div', attrs = {'data-testid' : 'info-ownership-type'})[0].text
        ownership = ownership.replace('Eieform', '')
    except:
        ownership = 'NA'

    url = url_lst[url_i]

    #add todays date
    date = time.strftime("%d/%m/%Y")


    df = df.append({
        'address': adr, 
        'price' : price, 
        'area' : area, 
        'rooms' : rooms, 
        'year' : year, 
        'type' : type, 
        'url' : url, 
        'price_per_m2' : price_per_m2, 
        'lat' : lat, 
        'lon' : lon, 
        'date' : date, 
        'floor' : floor,
        'ownership' : ownership}, ignore_index=True)

    time.sleep(random.randint(500, 1000)/1000)

    counter += 1
    print(counter)


'''clean data'''
# Replace ' ' with ',' in 'address' column:
df['address'] = df['address'].str.replace(',', ' ')

# Extract postal code from address
df['postal_code'] = df['address'].str.extract('(\d{4})')

# Remove postal code from address
try:
    df['address'] = df['address'].str.replace('\d{4}', '')
except:
    pass

# Extract city from address
df['city'] = df['address'].apply(lambda x: x.split()[-2] + ' ' + x.split()[-1] if x.split()[-1] == 'N' or x.split()[-1] == 'S' else x.split()[-1])

# Create list of unique cities
city_list = df['city'].unique().tolist()

'''remove city from address'''
# Remove city from address
df['address'] = df['address'].apply(lambda x: ' '.join(x.split()[:-2]) if x.split()[-1] == 'N' or x.split()[-1] == 'S' else ' '.join(x.split()[:-1]))

# Clean area column and keep just numbers
df['area'] = df['area'].str.replace(str(), '')

# Delete rows in 'area' that dont contain numbers:
df = df[df['area'].str.contains('\d')]

# Remove '.' from 'area' column:
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



'''remove rows with NA in lat and lon'''
df = df[df['lat'] != 'NA']
df = df[df['lon'] != 'NA']

'''display locations as circle map with folium'''
map1 = folium.Map(location = [59.940077, 10.764767], tiles = 'CartoDB dark_matter', zoom_start = 7)
df.apply(lambda row : folium.CircleMarker(location = [row['lat'], row['lon']]).add_to(map1), axis = 1)
df_rentals.apply(lambda row : folium.CircleMarker(location = [row['lat'], row['lon']], color = 'red').add_to(map1), axis = 1)
cluster = folium.plugins.MarkerCluster().add_to(map1)

'''add info to popups on map'''
for (index, row) in df.iterrows():

    # Create details to be displayed in popup:
    iframe = folium.IFrame('Address: ' + str(row['address']) + '<br>' + 
    'Price: ' + str(row['price']) + ' kr' + '<br>' + 
    'Price per m2: ' + str(row['price_per_m2']) + ' kr' + '<br>' + 
    'Area: ' + str(row['area']) + '<br>' + 
    'Rooms: ' + str(row['rooms']) + '<br>' + 
    'Year: ' + str(row['year']) + '<br>' + 
    'Type: ' + str(row['type']) + '<br>' + 
    'URL: ' + str(row['url']) + '<br>' + 
    'Date fetched: ' + str(row['date']) + '<br>' + 
    'Floor: ' + str(row['floor']) + '<br>' + 
    'Ownership: ' + str(row['ownership']))
    
    # Create a popup for each marker on the map:
    popup = folium.Popup(iframe, min_width = 300, max_width = 400, min_height = 300, max_height = 400)

    # Add marker to map:
    folium.Marker([row['lat'], row['lon']], popup = popup, color = '#000000', fill_color = 'white').add_to(cluster)

'''add rental info to popups on map'''
for (index, row) in df_rentals.iterrows():

    # Create details to be displayed in popup:
    iframe = folium.IFrame('Address: ' + str(row['address']) + '<br>' + 
    'Price: ' + str(row['price']) + ' kr' + '<br>' + 
    'Price per m2: ' + str(row['price_per_m2']) + ' kr' + '<br>' + 
    'Area: ' + str(row['area']) + '<br>' + 
    'URL: ' + str(row['url']) + '<br>' + 
    'Date fetched: ' + str(row['date']) + '<br>')
    
    # Create a popup for each marker on the map:
    popup = folium.Popup(iframe, min_width = 300, max_width = 400, min_height = 300, max_height = 400)

    # Add marker to map:
    folium.Marker([row['lat'], row['lon']], popup = popup, color = '#000000', fill_color = 'orange').add_to(cluster)

#save map as html file with today's date
map1.save('map_' + str(time.strftime("%Y%m%d")) + '.html')

# Save df as excel with today's date:
df.to_excel('price_data_norway_' + str(time.strftime("%Y%m%d")) + '.xlsx', index=False)
df_rentals.to_excel('rental_data_norway_' + str(time.strftime("%Y%m%d")) + '.xlsx', index=False)

print(df)
print(df_rentals)

#sleep for 10 seconds
time.sleep(10)
#make computer go to sleep after code is done running
#os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

# To do:
# 3. Add column with number of bathrooms
# 4. Add stories to map - DONE :D
# 5. Add commute time to Nationaltheatret
# 6. Add regression model to predict price
# 7. Add average rent price in the postal code

# Overall goal: 
# Calculate estimated gross yield for each property 
