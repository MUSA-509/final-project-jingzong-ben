from flask import Flask, Response, render_template, escape, request, url_for
import requests
import json
import logging
from google.cloud import bigquery
import pandas as pd
import altair as alt
from altair_saver import save
import plotly.express as px
from urllib.request import urlopen

app = Flask(__name__, template_folder="templates")
bqclient = bigquery.Client.from_service_account_json('C:/Users/bennd/Documents/MUSA509/TransitPolicyApp-99838a65a6ed.json')
pd.set_option('mode.chained_assignment', None)

area_list = ['Bridgeport-Stamford', 'Buffalo', 'Charlotte', 'Chicago', 'Cincinnati', 'Cleveland', 'Columbus', 'Dallas-Fort Worth-Arlington', 'Dayton', 'Denver-Aurora', 'Detroit', 'Durham', 'Fresno', 'Hartford', 'Honolulu', 'Houston', 'Indianapolis', 'Jacksonville', 'Las Vegas-Henderson', 'Los Angeles-Long Beach-Anaheim', 'Louisville/Jefferson County', 'Miami', 'Milwaukee', 'Minneapolis-St. Paul', 'New Haven', 'New Orleans', 'New York-Newark', 'Orlando', 'Philadelphia', 'Phoenix-Mesa', 'Pittsburgh', 'Portland', 'Providence', 'Reno', 'Richmond', 'Riverside-San Bernardino', 'Rochester', 'Sacramento', 'Salt Lake City-West Valley City', 'San Antonio', 'San Diego', 'San Francisco-Oakland', 'San Jose', 'Seattle', 'Spokane', 'St. Louis', 'Tampa-St. Petersburg', 'Tucson', 'Virginia Beach', 'Washington']
month_list = ['2019-01', '2019-02', '2019-03', '2019-04', '2019-05', '2019-06', '2019-07', '2019-08', '2019-09', '2019-10', '2019-11', '2019-12', '2020-01', '2020-02', '2020-03', '2020-04', '2020-05', '2020-06', '2020-07', '2020-08', '2020-09']

# Endpoint for first time loading national view
@app.route("/national_test/")
def national():
    # Set default selection     
    selected_month = request.args.get("month")
    selected_modes = request.args.get("modes")
    selected_overlay = request.args.get("overlay")
    selected_area = request.args.get("area")
    print(selected_month)
    print(selected_modes)

    query1 = (
        'SELECT metro_area, GEOID10, month, sum(trips) as trips, classification, min(lat) as lat, min(lon) as lon'
        ' FROM transitpolicyapp.ridership.Ridership'
        ' WHERE month = "2020-04" AND classification = "Non-Rail"'
        ' GROUP BY metro_area, GEOID10, month, classification'
    )
    resp1 = bqclient.query(query1).to_dataframe()

    fig1 = px.scatter_mapbox(resp1, lat="lat", lon="lon", size="trips", 
                            color_continuous_scale=px.colors.sequential.Jet, size_max=80, 
                            zoom=3, hover_data=["trips"], hover_name='metro_area'
                            )
    fig1.update_layout(mapbox_style="open-street-map")
    fig1.update_layout(title=f'Total Transit Trips')
    fig1.write_html("templates/map.html")

    query2 = (
        'SELECT county_fips_code as fips, max(confirmed_cases) as cases, max(deaths) as deaths'
        ' FROM bigquery-public-data.covid19_nyt.us_counties'
        ' WHERE county_fips_code IS NOT NULL'
        ' GROUP BY county_fips_code'
    )
    resp2 = bqclient.query(query2).to_dataframe()
    
    with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
        counties = json.load(response)

    fig2 = px.choropleth(resp2, geojson=counties, locations='fips', color='cases',
                            color_continuous_scale="Reds",
                            color_continuous_midpoint=5000, range_color=(0,300000),
                            scope="usa")

    fig2.update_layout(mapbox_style="open-street-map")
    fig2.update_layout(title=f'Cumulative COVID-19 Cases')
    fig2.write_html("templates/map_overlay.html")

    # Change map.html in templates folder if needed
    # You can also set default selection here
    html_response = render_template(
        "national_view.html",
        month_list = month_list,
        selected_month = selected_month,
        selected_modes = selected_modes,
        selected_overlay = selected_overlay,
        selected_area = selected_area,
        area_list = area_list
    )

    # It will include map.html in templates folder
    response = Response(response=html_response, status=200, mimetype="text/html")
    return response

# Endpoint for refresh page
@app.route("/national_refresh/", methods=['GET'])
def refresh():
    # Get selections from user.
    selected_month = request.args.get("month")
    selected_modes = request.args.get("modes")
    selected_overlay = request.args.get("overlay")
    selected_area = request.args.get("area")
    print(selected_month)
    print(selected_modes)

    # Change the map.html in templates folder, the map in the page will be replace
    # Though I'm not sure it is the right way to do

    html_response = render_template(
        "national_view.html",
        month_list = month_list,
        selected_month = selected_month,
        selected_modes = selected_modes,
        selected_overlay = selected_overlay,
        area_list = area_list, 
        selected_area = selected_area       
    )
    response = Response(response=html_response, status=200, mimetype="text/html")
    return response

# Endpoint for first time loading metro area view
@app.route("/metro_test/", methods=['GET'])
def metro():
    selected_area = request.args.get('metroArea')

    # Modularize following sections so that they could be used in another endpoint.
    
    #Census Table
    query1 = (
         'SELECT metro_area, pop_18, hh_size, hh_income, rent_share, pt_share, service_share'
         ' FROM transitpolicyapp.ridership.top50_census'
         ' WHERE metro_area =  \''+selected_area + 
         '\' GROUP BY metro_area, pop_18, hh_size, hh_income, rent_share, pt_share, service_share'
         )
    resp1 = bqclient.query(query1).to_dataframe()
    
    table_data = pd.melt(resp1, id_vars='metro_area', value_vars=['pop_18', 'hh_size', 'hh_income', 'rent_share', 'pt_share', 'service_share'])
    table_data = table_data.replace({'pop_18': 'Population (2018)', 'hh_size': 'Avg. Household Size', 'hh_income': 'Median Household Income', 'rent_share': 'Renter-occupied housing units', 'pt_share': 'Primary Mode to Work: Public Transit', 'service_share': 'Workers in Service Occupations'})
    table_data = table_data[['variable','value']]
    table_data = table_data.to_json(orient="values")
    
    #Example of new table_data output: [["Population (2018)",944348.0],["Avg. Household Size",2.72],["Median Household Income",92969.0],["Renter-occupied housing units",0.33],["Primary Mode to Work: Public Transit",0.1],["Workers in Service Occupations",0.18]]
    #table_data = {'0': selected_area,'1':'data1','2':'data2','3':'data3','4':'data4','5':'data5'}

    #Ridership Chart
    query2 = (
         'SELECT metro_area, month, mode, trips'
         ' FROM transitpolicyapp.ridership.top50_ridership'
         ' WHERE metro_area =  \''+selected_area + 
         '\' GROUP BY metro_area, month, mode, trips')
    resp2 = bqclient.query(query2).to_dataframe()

    chart_ridership = px.area(resp2, x="month", y="trips", color="mode")
    chart_ridership.write_html("templates/chart_ridership.html")

    #Scatterplot
    query4 = (
        'SELECT r.metro_area, sum(r.trips) as trips, c.metro_area, c.cases, c.date'
        ' FROM transitpolicyapp.ridership.top50_ridership as r'
        ' JOIN transitpolicyapp.ridership.top50_covid as c'
        ' ON c.metro_area = r.metro_area'
        ' WHERE c.date = "2020-11-30"'
        ' GROUP BY r.metro_area, c.metro_area, c.cases, c.date'
    )
    resp4 = bqclient.query(query4).to_dataframe()

    chart_scatter = px.scatter(resp4, x="cases", y="trips")
    chart_scatter.write_html("templates/chart_scatter.html")

    #COVID Charts
    query3 = (
         'SELECT date, metro_area, cases, deaths'
         ' FROM transitpolicyapp.ridership.top50_covid'
         ' WHERE metro_area =  \''+selected_area + 
         '\' GROUP BY date, metro_area, cases, deaths')
    resp3 = bqclient.query(query3).to_dataframe()
    
    resp3['new_cases'] = resp3['cases'].diff()
    resp3['new_deaths'] = resp3['deaths'].diff()
    resp3['cases_avg'] = resp3.iloc[:,4].rolling(window=7).mean()
    resp3['deaths_avg'] = resp3.iloc[:,5].rolling(window=7).mean()
    
    chart_cases = px.bar(resp3, x='date', y='cases_avg')
    chart_cases.write_html("templates/chart_cases.html")

    chart_deaths = px.bar(resp3, x='date', y='deaths_avg')
    chart_deaths.write_html("templates/chart_deaths.html")

    #Response
    html_response = render_template(
        "metro_area_dashboard.html",
        area_list = area_list,
        selected_area = selected_area,
        table_data = table_data
    )
    response = Response(response=html_response, status=200, mimetype="text/html")
    return response

# Endpoint for changing area
@app.route("/metro", methods=['GET'])
def change_area():
    selected_area = request.args.get('metroArea')

    # Modularize following sections so that they could be used in another endpoint.
    
    #Census Table
    query1 = (
         'SELECT metro_area, pop_18, hh_size, hh_income, rent_share, pt_share, service_share'
         ' FROM transitpolicyapp.ridership.top50_census'
         ' WHERE metro_area =  \''+selected_area + 
         '\' GROUP BY metro_area, pop_18, hh_size, hh_income, rent_share, pt_share, service_share'
         )
    resp1 = bqclient.query(query1).to_dataframe()
    
    table_data = pd.melt(resp1, id_vars='metro_area', value_vars=['pop_18', 'hh_size', 'hh_income', 'rent_share', 'pt_share', 'service_share'])
    table_data = table_data.replace({'pop_18': 'Population (2018)', 'hh_size': 'Avg. Household Size', 'hh_income': 'Median Household Income', 'rent_share': 'Renter-occupied housing units', 'pt_share': 'Primary Mode to Work: Public Transit', 'service_share': 'Workers in Service Occupations'})
    table_data = table_data[['variable','value']]
    table_data = table_data.to_json(orient="values")
    
    #Example of new table_data output: [["Population (2018)",944348.0],["Avg. Household Size",2.72],["Median Household Income",92969.0],["Renter-occupied housing units",0.33],["Primary Mode to Work: Public Transit",0.1],["Workers in Service Occupations",0.18]]
    #table_data = {'0': selected_area,'1':'data1','2':'data2','3':'data3','4':'data4','5':'data5'}

    #Ridership Chart
    query2 = (
         'SELECT metro_area, month, mode, trips'
         ' FROM transitpolicyapp.ridership.top50_ridership'
         ' WHERE metro_area =  \''+selected_area + 
         '\' GROUP BY metro_area, month, mode, trips')
    resp2 = bqclient.query(query2).to_dataframe()

    chart_ridership = px.area(resp2, x="month", y="trips", color="mode")
    chart_ridership.write_html("templates/chart_ridership.html")

    #Scatterplot
    query4 = (
        'SELECT r.metro_area, sum(r.trips) as trips, c.metro_area, c.cases, c.date'
        ' FROM transitpolicyapp.ridership.top50_ridership as r'
        ' JOIN transitpolicyapp.ridership.top50_covid as c'
        ' ON c.metro_area = r.metro_area'
        ' WHERE c.date = "2020-11-30"'
        ' GROUP BY r.metro_area, c.metro_area, c.cases, c.date'
    )
    resp4 = bqclient.query(query4).to_dataframe()

    chart_scatter = px.scatter(resp4, x="cases", y="trips")
    chart_scatter.write_html("templates/chart_scatter.html")

    #COVID Charts
    query3 = (
         'SELECT date, metro_area, cases, deaths'
         ' FROM transitpolicyapp.ridership.top50_covid'
         ' WHERE metro_area =  \''+selected_area + 
         '\' GROUP BY date, metro_area, cases, deaths')
    resp3 = bqclient.query(query3).to_dataframe()
    
    resp3['new_cases'] = resp3['cases'].diff()
    resp3['new_deaths'] = resp3['deaths'].diff()
    resp3['cases_avg'] = resp3.iloc[:,4].rolling(window=7).mean()
    resp3['deaths_avg'] = resp3.iloc[:,5].rolling(window=7).mean()
    
    chart_cases = px.bar(resp3, x='date', y='cases_avg')
    chart_cases.write_html("templates/chart_cases.html")

    chart_deaths = px.bar(resp3, x='date', y='deaths_avg')
    chart_deaths.write_html("templates/chart_deaths.html")

    #Response
    html_response = render_template(
        "metro_area_dashboard.html",
        area_list = area_list,
        selected_area = selected_area,
        table_data = table_data
    )
    response = Response(response=html_response, status=200, mimetype="text/html")
    return response


if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.run(debug=True)