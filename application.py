from flask import Flask, Response, render_template, escape, request, url_for
import requests
import json
import logging
from google.cloud import bigquery
import pandas as pd
import altair as alt
from altair_saver import save
import plotly.express as px
import plotly.graph_objects as go

#Initialize Query Connection
application = Flask(__name__, template_folder="templates")
bqclient = bigquery.Client.from_service_account_json('./TransitPolicyApp-99838a65a6ed.json')
pd.set_option('mode.chained_assignment', None)

#Specify dropdown values (top 50 metro areas by total transit trips)
area_list = ['Bridgeport-Stamford', 'Buffalo', 'Charlotte', 'Chicago', 'Cincinnati', 'Cleveland', 'Columbus', 'Dallas-Fort Worth-Arlington', 'Dayton', 'Denver-Aurora', 'Detroit', 'Durham', 'Fresno', 'Hartford', 'Honolulu', 'Houston', 'Indianapolis', 'Jacksonville', 'Las Vegas-Henderson', 'Los Angeles-Long Beach-Anaheim', 'Louisville/Jefferson County', 'Miami', 'Milwaukee', 'Minneapolis-St. Paul', 'New Haven', 'New Orleans', 'New York-Newark', 'Orlando', 'Philadelphia', 'Phoenix-Mesa', 'Pittsburgh', 'Portland', 'Providence', 'Reno', 'Richmond', 'Riverside-San Bernardino', 'Rochester', 'Sacramento', 'Salt Lake City-West Valley City', 'San Antonio', 'San Diego', 'San Francisco-Oakland', 'San Jose', 'Seattle', 'Spokane', 'St. Louis', 'Tampa-St. Petersburg', 'Tucson', 'Virginia Beach', 'Washington']
month_list = ['2019-01', '2019-02', '2019-03', '2019-04', '2019-05', '2019-06', '2019-07', '2019-08', '2019-09', '2019-10', '2019-11', '2019-12', '2020-01', '2020-02', '2020-03', '2020-04', '2020-05', '2020-06', '2020-07', '2020-08', '2020-09']

# Endpoint for first time loading national view
@application.route("/")
def national():
    # Set default selection     
    selected_month = "2020-09"
    selected_modes = "Non-Rail"

    #Query ridership
    query1 = (
        'SELECT metro_area, GEOID10, month, sum(trips) as trips, classification, min(lat) as lat, min(lon) as lon'
        ' FROM transitpolicyapp.ridership.Ridership'
        ' WHERE month =  \''+selected_month + 
         '\' AND classification =  \''+selected_modes + 
         '\' GROUP BY metro_area, GEOID10, month, classification'
    )

    resp1 = bqclient.query(query1).to_dataframe()

    #Create transit ridership map
    fig1 = px.scatter_mapbox(resp1, lat="lat", lon="lon", size="trips", 
                            color_continuous_scale=px.colors.sequential.Jet, size_max=80, 
                            zoom=3.5, hover_data=["trips"], hover_name='metro_area', width=1625, height=800
                            )

    fig1.update_layout(mapbox_style="open-street-map")
    fig1.update_layout(title=f'Total {selected_modes} Transit Trips in {selected_month}')
    fig1.write_html("templates/map.html")
               
    # Render the template
    html_response = render_template(
        "national_view.html",
        month_list = month_list,
        selected_month = selected_month,
        selected_modes = selected_modes,
        area_list = area_list
    )

    # Return html code for map
    response = Response(response=html_response, status=200, mimetype="text/html")
    return response

# Endpoint for refresh page
@application.route("/national_refresh/", methods=['GET'])
def refresh():
    # Pull variables from dropdowns    
    selected_month = str(request.args.get("month"))
    selected_modes = str(request.args.get("modes"))
    
    #Query ridership data
    query1 = (
        'SELECT metro_area, GEOID10, month, sum(trips) as trips, classification, min(lat) as lat, min(lon) as lon'
        ' FROM transitpolicyapp.ridership.Ridership'
        ' WHERE month =  \''+selected_month + 
         '\' AND classification =  \''+selected_modes + 
         '\' GROUP BY metro_area, GEOID10, month, classification'
    )

    resp1 = bqclient.query(query1).to_dataframe()

    #Create ridership map
    fig1 = px.scatter_mapbox(resp1, lat="lat", lon="lon", size="trips", 
                            color_continuous_scale=px.colors.sequential.Jet, size_max=80, 
                            zoom=3.5, hover_data=["trips"], hover_name='metro_area', width=1625, height=800
                            )

    fig1.update_layout(mapbox_style="open-street-map")
    fig1.update_layout(title=f'Total {selected_modes} Transit Trips in {selected_month}')
    fig1.write_html("templates/map.html")
               
    # Render the template
    html_response = render_template(
        "national_view.html",
        month_list = month_list,
        selected_month = selected_month,
        selected_modes = selected_modes,
        area_list = area_list
    )

    #Generate html code for map
    response = Response(response=html_response, status=200, mimetype="text/html")
    return response

# Endpoint for first time loading metro area view
@application.route("/metro_test/", methods=['GET'])
def metro():
    selected_area = request.args.get('metroArea')

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
    census_data = table_data[['variable','value']]

    fig = go.Figure(data=[go.Table(header=dict(values=['Census Variable', 'Value']),
                 cells=dict(values=[census_data.variable, census_data.value]))
                     ])
    fig.write_html("templates/table.html")
    
    #Ridership Chart
    query2 = (
         'SELECT metro_area, month, mode, trips'
         ' FROM transitpolicyapp.ridership.top50_ridership'
         ' WHERE metro_area =  \''+selected_area + 
         '\' GROUP BY metro_area, month, mode, trips')
    resp2 = bqclient.query(query2).to_dataframe()

    chart_ridership = px.area(resp2, x="month", y="trips", color="mode", title="Total Transit Trips by Mode", labels={'month':'Month', 'trips':'Total Transit Trips'})
    chart_ridership.write_html("templates/chart_ridership.html")

    #Scatterplot
    query4 = (
        'SELECT r.metro_area, sum(r.trips) as trips, c.metro_area, c.cases, c.date, r.month'
        ' FROM transitpolicyapp.ridership.top50_ridership as r'
        ' JOIN transitpolicyapp.ridership.top50_covid as c'
        ' ON c.metro_area = r.metro_area'
        ' WHERE c.date = "2020-11-30"'
        ' AND r.month = "2020-09"'
        ' GROUP BY r.metro_area, c.metro_area, c.cases, c.date, r.month'
    )
    resp4 = bqclient.query(query4).to_dataframe()

    chart_scatter = px.scatter(resp4, x="cases", y="trips", hover_data=['metro_area'], title="Relationship Between COVID and Transit Trips", labels={'cases':'Cumulative COVID-19 Cases', 'trips':'Total Transit Trips in Sep 2020'})
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
    
    chart_cases = px.bar(resp3, x='date', y='cases_avg', color_discrete_sequence=["orange"], labels={'cases_avg':'New COVID-19 Cases', 'date':'Date'}, title="COVID-19 Cases")
    chart_cases.write_html("templates/chart_cases.html")

    chart_deaths = px.bar(resp3, x='date', y='deaths_avg', color_discrete_sequence=["red"], labels={'deaths_avg':'New COVID-19 Deaths', 'date':'Date'}, title="COVID-19 Deaths")
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
@application.route("/metro", methods=['GET'])
def change_area():
    selected_area = request.args.get('metroArea')

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
    census_data = table_data[['variable','value']]

    fig = go.Figure(data=[go.Table(header=dict(values=['Census Variable', 'Value']),
                 cells=dict(values=[census_data.variable, census_data.value]))
                     ])
    fig.write_html("templates/table.html")
    
    #Ridership Chart
    query2 = (
         'SELECT metro_area, month, mode, trips'
         ' FROM transitpolicyapp.ridership.top50_ridership'
         ' WHERE metro_area =  \''+selected_area + 
         '\' GROUP BY metro_area, month, mode, trips')
    resp2 = bqclient.query(query2).to_dataframe()

    chart_ridership = px.area(resp2, x="month", y="trips", color="mode", title="Total Transit Trips by Mode", labels={'month':'Month', 'trips':'Total Transit Trips'})
    chart_ridership.write_html("templates/chart_ridership.html")

    #Scatterplot
    query4 = (
        'SELECT r.metro_area, sum(r.trips) as trips, c.metro_area, c.cases, c.date, r.month'
        ' FROM transitpolicyapp.ridership.top50_ridership as r'
        ' JOIN transitpolicyapp.ridership.top50_covid as c'
        ' ON c.metro_area = r.metro_area'
        ' WHERE c.date = "2020-11-30"'
        ' AND r.month = "2020-09"'
        ' GROUP BY r.metro_area, c.metro_area, c.cases, c.date, r.month'
    )
    resp4 = bqclient.query(query4).to_dataframe()

    chart_scatter = px.scatter(resp4, x="cases", y="trips", hover_data=['metro_area'], title="Relationship Between COVID and Transit Trips", labels={'cases':'Cumulative COVID-19 Cases', 'trips':'Total Transit Trips in Sep 2020'})
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
    
    chart_cases = px.bar(resp3, x='date', y='cases_avg', color_discrete_sequence=["orange"], labels={'cases_avg':'New COVID-19 Cases', 'date':'Date'}, title="COVID-19 Cases")
    chart_cases.write_html("templates/chart_cases.html")

    chart_deaths = px.bar(resp3, x='date', y='deaths_avg', color_discrete_sequence=["red"], labels={'deaths_avg':'New COVID-19 Deaths', 'date':'Date'}, title="COVID-19 Deaths")
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