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

from .functions_variables import PROJECT_DIR, FILES_PATH, WEBSITE_URL, fields, fields_mapping
from .functions_variables import create_worldmap, write_map_file
from .countries_mapping import countries_dict

# Create your views here.
def index(request):

    website_content = requests.get(WEBSITE_URL).text
    website_soup = BeautifulSoup(website_content, "html5lib")

    table_id = 'main_table_countries_today'
    table_content = website_soup.find("table", attrs={"id": table_id})

    table_body_content = table_content.find("tbody")
    table_body_rows = table_body_content.find_all('tr')

    stats_max = {}
    stats_min = {}
    countries_data = []

    for row_content in table_body_rows:
        if row_content.td.a is not None:
            country_name = row_content.td.a.text.strip()
            if country_name in countries_dict:
                country_name = countries_dict[country_name]

            country_data = {}
            country_data['country'] = country_name
            statistics_rows = row_content.find_all('td')

            for ind, statistic_tag in enumerate(statistics_rows[1:-1]):
                statistic = statistic_tag.text
                if re.match('(\s+)', statistic) or statistic == '':
                    statistic = '0.0'
                elif statistic == 'N/A':
                    statistic = "Nan"
                elif statistic[0] == '+':
                    statistic = statistic[1:]

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

    geojson_file = os.path.join(FILES_PATH, 'countries_complete_geo.json')
    with open(geojson_file) as countries_file:
        countries_geodata = json.load(countries_file)

    countries_geodata_df = gpd.GeoDataFrame.from_features(countries_geodata, crs='EPSG:4326')
    columns_to_keep = ['geometry', 'admin', 'continent']
    countries_geodata_df = countries_geodata_df[columns_to_keep]

    merged_data = countries_geodata_df.merge(countries_data, left_on='admin', right_on='country', how='left')

    statistics = ['total_cases', 'new_cases', 'total_deaths', 'new_deaths', 'active_cases', 'serious_critical', 'total_recovered']

    for statistic in statistics[0:2]:
        statistic_map = create_worldmap(statistic, statistics, merged_data, stats_max)
        statistic_map_code = statistic_map._repr_html_()
        write_map_file(statistic_map_code, '{}_map'.format(statistic))

    print('map for {} is generated'.format(statistic))

    return render(request, 'dashboard/index.html')
