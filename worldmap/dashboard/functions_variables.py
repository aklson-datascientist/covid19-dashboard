import os
import sys
import numpy as np
import pandas as pd
import geopandas as gpd
import branca.colormap as cm

import folium
from folium.features import GeoJson, GeoJsonTooltip

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_DIR)
FILES_PATH = os.path.join(PROJECT_DIR, 'dashboard/templates/dashboard/files')
WEBSITE_URL = 'https://www.worldometers.info/coronavirus/'

fields = [
    'total_cases', 'new_cases', 'total_deaths',
    'new_deaths', 'total_recovered', 'active_cases',
    'serious_critical', 'tot_cases_1M', 'deaths_1M',
    'total_tests', 'tests_1M'
    ]

fields_mapping = {
    'total_cases': 'Total Cases',
    'new_cases': 'New Cases',
    'total_deaths': 'Total Deaths',
    'new_deaths': 'New Deaths',
    'total_recovered': 'Total Recovered',
    'active_cases': 'Active Cases',
    'serious_critical': 'Serious or Critical',
    'tot_cases_1M': 'Total Cases / 1M Population',
    'deaths_1M': 'Deaths / 1M Population',
    'total_tests': 'Total Tests',
    'tests_1M': 'Total Test / 1M Population'
}


# a function to create world map for a given statistic
def create_worldmap(statistic, statistics, merged_data, stats_max):

    statistics = statistics.copy()
    if statistic in statistics:
        statistics.remove(statistic)
    statistics.insert(0, statistic)

    colormap = cm.linear.YlOrRd_03.scale(0, stats_max[statistic]).to_step(6)
    colormap.caption = 'World Map of COVID-19 {}'.format(fields_mapping[statistic])

    world_map = folium.Map(location=[42, 0], zoom_start=2, tiles='cartodbpositron')

    for i in range(merged_data.shape[0]):
        country_row_data = merged_data.iloc[i:i+1]

        country_name = country_row_data['admin'].item()
        display_values = []
        for statistic_to_display in statistics:
            statistic_value = merged_data.iloc[i][statistic_to_display]

            if country_row_data[statistic_to_display].isna().bool() or statistic_value == 'No Data':
                display_value = 'No Data'
            else:
                statistic_value = float(statistic_value)
                if statistic_value < 1 and statistic_value > 0:
                    display_value = str(statistic_value)
                else:
                    display_value = format(int(statistic_value), ',')
                    if statistic_to_display in ['new_cases', 'new_deaths'] and display_value != '0':
                        display_value = '+{}'.format(display_value)
            display_values.append(display_value)

        gs = folium.GeoJson(
            merged_data.iloc[i:i+1],
            style_function = lambda x: {
                        "fillColor": colormap(x['properties'][statistic])
                        if x['properties'][statistic] is not None
                        else "grey",
                        "color": "black",
                        "weight": 0.5,
                        "fillOpacity": 0.7,
                    },
            tooltip = folium.Tooltip(
                '''
                <div style="font-weight:bold; display: inline-block;">
                    <p>Country: </p>
                    <p>{}: </p>
                    <p>{}: </p>
                    <p>{}: </p>
                    <p>{}: </p>
                    <p>{}: </p>
                    <p>{}: </p>
                </div>
                <div style="display: inline-block;">
                    <p>{}</p>
                    <p>{}</p>
                    <p>{}</p>
                    <p>{}</p>
                    <p>{}</p>
                    <p>{}</p>
                    <p>{}</p>
                </div>
                '''.format(
                        fields_mapping[statistics[0]],
                        fields_mapping[statistics[1]],
                        fields_mapping[statistics[2]],
                        fields_mapping[statistics[3]],
                        fields_mapping[statistics[4]],
                        fields_mapping[statistics[5]],
                        country_name,
                        display_values[0],
                        display_values[1],
                        display_values[2],
                        display_values[3],
                        display_values[4],
                        display_values[5],
                    ),
                style="""
                    background-color: #F0EFEF;
                    border: 1px solid black;
                    border-radius: 1px;
                    box-shadow: 3px;
                    padding: 10px;
                    """,
                ),
            highlight_function = lambda x: {
                    "fillColor": colormap(x["properties"][statistic])
                    if x["properties"][statistic] is not None
                    else "grey",
                    'color':'black',
                    'fillOpacity': 0.7,
                    'weight': 2}
            ).add_to(world_map)

    colormap.add_to(world_map)
    return world_map

def write_map_file(map_code_file, file_name):
    map_file_path = os.path.join(FILES_PATH, '{}.html'.format(file_name))

    if os.path.exists(map_file_path):
        os.remove(map_file_path)

    with open(map_file_path, 'w') as map_html_file:
        map_html_file.write(map_code_file)
