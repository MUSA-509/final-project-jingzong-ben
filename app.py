#Transport Policy App

#Packages---------------------------------------------------------------------------------------------------------------------------
import pandas as pd
import altair as alt
from google.cloud import bigquery
import geopandas as gpd
from shapely import wkt
from census import Census
from us import states
import plotly
import plotly.express as px
import plotly.graph_objects as go
from urllib.request import urlopen
import json

#Establish query connection---------------------------------------------------------------------------------------------------------
bqclient = bigquery.Client.from_service_account_json('C:/Users/bennd/Documents/MUSA509/TransitPolicyApp-99838a65a6ed.json')
pd.set_option('mode.chained_assignment', None)

#Load data--------------------------------------------------------------------------------------------------------------------------
top50 = pd.read_csv("data/top50.csv")

query_r = f"""
    SELECT metro_area, area_land, area_water, GEOID10, mode, month, trips, classification, lat, lon
    FROM `transitpolicyapp.ridership.Ridership`
    GROUP BY metro_area, area_land, area_water, GEOID10, mode, month, trips, classification, lat, lon
"""
ridership = bqclient.query(query_r).to_dataframe()

with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

#Establish query parameters---------------------------------------------------------------------------------------------------------


#Sidebar----------------------------------------------------------------------------------------------------------------------------
##get select_date from dropdown
##get select_mode from dropdown
select_date = "2020-09"
select_classification = "Non-Rail"
select_metric = (["cases"])

#Landing Page Map-------------------------------------------------------------------------------------------------------------------
ridership_agg = ridership[ridership["month"] == select_date]
ridership_agg = ridership_agg[ridership["classification"] == select_classification]
ridership_agg = ridership_agg.groupby(['GEOID10', 'metro_area'], as_index=False).agg({'trips': 'sum', 'lat': 'min', 'lon': 'min'})

fig = px.scatter_mapbox(ridership_agg,
                        lat="lat",
                        lon="lon",
                        size="trips",
                        color_continuous_scale=px.colors.sequential.Jet,
                        size_max=80,
                        zoom=3,
                        hover_data=["trips"],
                        hover_name='metro_area'
                        )
fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(
    title=f'Total Transit Trips in {select_date}',
)
fig.write_html("map.html")

select_metro = "Philadelphia, PA-NJ-DE-MD"
#Metro Detail-----------------------------------------------------------------------------------------------------------------------

#Ridership graph
ridership_s = ridership[ridership["metro_area"] == select_metro]
chart_ridership = alt.Chart(ridership_s).mark_area().encode(
    x=alt.X('month:T', axis=alt.Axis(title='Month')),
    y=alt.Y('trips:Q', axis=alt.Axis(title='Total Transit Trips')),
    color="mode:N",
    tooltip=['month','mode', 'trips']
).interactive()
chart_ridership.save('chart_ridership.html')

#search_county = "San Francisco"
#covid_s = covid[covid["county"] == search_county]
#covid_s['new_cases'] = covid_s['cases'].diff()
#covid_s['new_deaths'] = covid_s['deaths'].diff()
#covid_s['cases_avg'] = covid_s.iloc[:,6].rolling(window=7).mean()
#covid_s['deaths_avg'] = covid_s.iloc[:,7].rolling(window=7).mean()
#covid_s['DateTime'] = pd.to_datetime(covid_s['date'])

#Covid Cases graph
#chart_cases = alt.Chart(covid_s).mark_bar().encode(
#    x=alt.X('date:T', axis=alt.Axis(title='Month')),
#    y=alt.Y('cases_avg:Q', axis=alt.Axis(title='New COVID-19 Cases Reported')),
#)
#chart_cases.save('chart_cases.html')

#Covid deaths graph
#chart_deaths = alt.Chart(covid_s).mark_bar().encode(
#    x=alt.X('date:T', axis=alt.Axis(title='Month')),
#    y=alt.Y('deaths_avg:Q', axis=alt.Axis(title='New COVID-19 Deaths Reported')),
#    color=alt.value('orange'),
#)
#chart_deaths.save('chart_deaths.html')

#Comparison scatter plot
#top50_c = top50.merge(covid_l, on="fips", how='left')
#ridership_agg = ridership_agg[['GEOID10','trips']]
#top50_c = top50_c.merge(ridership_agg, on="GEOID10", how='left')

#chart_scatter = alt.Chart(top50_c).mark_circle(size=200).encode(
#    x=alt.X('cases', axis=alt.Axis(title='COVID-19 Cases (Cumulative)')),
#    y=alt.Y('trips', axis=alt.Axis(title='Total Transit Trips in September 2020')),
#    color=alt.Color('state', legend=None),
#    tooltip=['metro_area', 'cases', 'deaths', 'trips']
#).interactive()
#chart_scatter.save('scatter.html')

#Census statistics table
top50_m = pd.melt(top50, id_vars='metro_area', value_vars=['pop_18', 'hh_size', 'hh_income', 'rent_share', 'pt_share', 'service_share'])
top50_m = top50_m[top50_m["metro_area"] == "Los Angeles-Long Beach-Anaheim, CA"]
top50_m = top50_m.replace({'pop_18': 'Population (2018)', 'hh_size': 'Avg. Household Size', 'hh_income': 'Median Household Income', 'rent_share': 'Renter-occupied housing units', 'pt_share': 'Primary Mode to Work: Public Transit', 'service_share': 'Workers in Service Occupations'})
top50_m = top50_m[['variable','value']]
html = top50_m.to_html((open('metro_table.html', 'w')), header=False, index=False)