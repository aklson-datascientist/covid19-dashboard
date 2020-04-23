import os
import sys
import requests
import pandas as pd
import geopandas as gpd
import re
import json

from django.shortcuts import render
from django.http import HttpResponse

from bs4 import BeautifulSoup

from .functions_variables import PROJECT_DIR, FILES_PATH, WEBSITE_URL
from .functions_variables import misspelled_countries_dict, fields, fields_mapping
from .functions_variables import create_worldmap, write_map_file

# Create your views here.
def index(request):

    website_content = requests.get(WEBSITE_URL).text
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

    geojson_file = os.path.join(FILES_PATH, 'countries_complete_geo.json')

    with open(geojson_file) as countries_file:
        countries_geodata = json.load(countries_file)

    countries_oi = []
    for country_geodata in countries_geodata['features']:
        countries_oi.append(country_geodata['properties']['admin'])

    countries_dict = {}
    for country in countries_names:
        if country in countries_oi:
            countries_dict[country] = country

    countries_dict.update(misspelled_countries_dict)

    stats_max = {}
    stats_min = {}
    countries_data = []
    for country in countries_dict:

        country_row_data = countries_row_data[country]
        statistics_rows = country_row_data.find_all('td')

        country_data = {}
        country_data['country'] = countries_dict[country]

        for ind, statistic_tag in enumerate(statistics_rows[1:-1]):

            statistic = statistic_tag.text

            if re.match('(\s+)', statistic) or statistic == '':
                statistic = '0.0'
            elif statistic == 'N/A':
                statistic = 'No Data'
            elif statistic[0] == '+':
                statistic = statistic[1:]

            if statistic != 'No Data':
                statistic = float(statistic.replace(',', ''))

                # add statistic to stats_max
                if fields[ind] not in stats_max:
                    stats_max[fields[ind]] = statistic
                else:
                    if statistic > stats_max[fields[ind]]:
                        stats_max[fields[ind]] = statistic

                # add statistic to stats_min
                if fields[ind] not in stats_min:
                    stats_min[fields[ind]] = statistic
                else:
                    if statistic < stats_min[fields[ind]]:
                        stats_min[fields[ind]] = statistic

            country_data[fields[ind]] = statistic
        countries_data.append(country_data)

    countries_data = pd.json_normalize(countries_data)

    countries_geodata_df = gpd.GeoDataFrame.from_features(countries_geodata, crs='EPSG:4326')
    columns_to_keep = ['geometry', 'admin', 'continent']
    countries_geodata_df = countries_geodata_df[columns_to_keep]

    merged_data = countries_geodata_df.merge(countries_data, left_on='admin', right_on='country', how='left')

    statistics = ['total_cases', 'total_deaths', 'new_cases', 'new_deaths', 'active_cases', 'serious_critical', 'total_recovered']

    for statistic in statistics[0:5]:
        statistic_map = create_worldmap(statistic, statistics, merged_data, stats_max)
        statistic_map_code = statistic_map._repr_html_()
        write_map_file(statistic_map_code, '{}_map'.format(statistic))

    print('map for {} is generated'.format(statistic))

    return render(request, 'dashboard/index.html')
