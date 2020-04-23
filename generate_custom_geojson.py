import numpy as np
import requests
import json

import shapefile

from bs4 import BeautifulSoup

website_url = 'https://www.worldometers.info/coronavirus/'
website_content = requests.get(website_url).text

website_soup = BeautifulSoup(website_content, "html5lib")

table_id = 'main_table_countries_today'
table_content = website_soup.find("table", attrs={"id": table_id})

table_body_content = table_content.find("tbody")
table_body_rows = table_body_content.find_all('tr')

countries_row_data = {}
countries_names = []
for row_content in table_body_rows:
    try:
        country_name = row_content.td.a.text.strip()
        countries_row_data[country_name] = row_content
        countries_names.append(country_name)
    except:
        pass

with open('custom.geo.json') as countries_file:
    countries_geodata = json.load(countries_file)

countries_oi = []
for country_geodata in countries_geodata['features']:
    countries_oi.append(country_geodata['properties']['admin'])

countries_dict = {}
for country in countries_names:
    if country in countries_oi:
        countries_dict[country] = country

misspelled_countries_dict = {
    'USA': 'United States of America',
    'UK':  'United Kingdom',
    'S. Korea': 'South Korea',
    'Czechia': 'Czech Republic',
    'UAE': 'United Arab Emirates',
    'Serbia': 'Republic of Serbia',
    'North Macedonia': 'Macedonia',
    'Hong Kong': 'Hong Kong S.A.R.',
    'DRC': 'Democratic Republic of the Congo',
    'Faeroe Islands': 'Faroe Islands',
    'Tanzania': 'United Republic of Tanzania',
    'Congo': 'Republic of Congo',
    'Cabo Verde': 'Cape Verde',
    'Bahamas': 'The Bahamas',
    'Guinea-Bissau': 'Guinea Bissau',
    'Macao': 'Macao S.A.R',
    'Eswatini': 'Swaziland',
    'Timor-Leste': 'East Timor',
    'CAR': 'Central African Republic',
    'St. Vincent Grenadines':  'Saint Vincent and the Grenadines',
    'Turks and Caicos': 'Turks and Caicos Islands',
    'Vatican City': 'Vatican',
    'St. Barth': 'Saint Barthelemy',
    'Saint Pierre Miquelon':  'Saint Pierre and Miquelon',
}

countries_dict.update(misspelled_countries_dict)

missing_countries = ['Mauritius', 'Seychelles', 'Maldives']

keys_ref = countries_geodata['features'][0]['properties'].keys()

filename = 'ne_10m_admin_0_map_units/ne_10m_admin_0_map_units.shp'

with shapefile.Reader(filename) as shp:
    fields = shp.fields
    keys = [field[0].lower() for field in fields if field[0].lower() in keys_ref]

    missing_geodata = []
    for sr in shp.shapeRecords():
        atr = dict(zip(keys, sr.record))
        if atr['admin'] in missing_countries:
            geom = sr.shape.__geo_interface__
            missing_geodata.append(dict(type="Feature", properties=atr, geometry=geom))

countries_geodata['features'].extend(missing_geodata)

countries_dict = {}
for country in countries_names:
    if country in countries_oi:
        countries_dict[country] = country

countries_dict.update(misspelled_countries_dict)
print(countries_dict)


countries_to_delete = [
    'United States Virgin Islands',
    'Northern Cyprus',
    'Indian Ocean Territories',
    'Siachen Glacier',
    'Aland',
    'Guernsey',
    'Jersey',
    'Ashmore and Cartier Islands',
    'American Samoa',
    'Cook Islands',
    'Kiribati',
    'Guam',
    'Northern Mariana Islands',
    'Norfolk Island',
    'Niue',
    'Pitcairn Islands',
    'Tonga',
    'Samoa',
    'Wallis and Futuna'
]

for country_geodata in countries_geodata['features']:
    if country_geodata['properties']['admin'] in countries_to_delete:
        countries_geodata['features'].remove(country_geodata)

with open('countries_complete_geo.json', 'w') as outfile:
    json.dump(countries_geodata, outfile)
