from flask import Flask, Response, render_template, escape, request, url_for
import requests
import json
import logging
from google.cloud import bigquery
import pandas as pd
import altair as alt

app = Flask(__name__, template_folder="templates")
bqclient = bigquery.Client.from_service_account_json('C:/Users/bennd/Documents/MUSA509/TransitPolicyApp-99838a65a6ed.json')
pd.set_option('mode.chained_assignment', None)

area_list = ['Bridgeport-Stamford', 'Buffalo', 'Charlotte', 'Chicago', 'Cincinnati', 'Cleveland', 'Columbus', 'Dallas-Fort Worth-Arlington', 'Dayton', 'Denver-Aurora', 'Detroit', 'Durham', 'Fresno', 'Hartford', 'Honolulu', 'Houston', 'Indianapolis', 'Jacksonville', 'Las Vegas-Henderson', 'Los Angeles-Long Beach-Anaheim', 'Louisville/Jefferson County', 'Miami', 'Milwaukee', 'Minneapolis-St. Paul', 'New Haven', 'New Orleans', 'New York-Newark', 'Orlando', 'Philadelphia', 'Phoenix-Mesa', 'Pittsburgh', 'Portland', 'Providence', 'Reno', 'Richmond', 'Riverside-San Bernardino', 'Rochester', 'Sacramento', 'Salt Lake City-West Valley City', 'San Antonio', 'San Diego', 'San Francisco-Oakland', 'San Jose', 'Seattle', 'Spokane', 'St. Louis', 'Tampa-St. Petersburg', 'Tucson', 'Virginia Beach', 'Washington']
month_list = ['2019-01', '2019-02', '2019-03', '2019-04', '2019-05', '2019-06', '2019-07', '2019-08', '2019-09', '2019-10', '2019-11', '2019-12', '2020-01', '2020-02', '2020-03', '2020-04', '2020-05', '2020-06', '2020-07', '2020-08', '2020-09']

# Endpoint for first time loading national view
@app.route("/national_test/")
def national():
    # Set default selection     
    selected_date = '2019-02'
    selected_area = request.args.get("selectedArea")

    # Change map.html in templates folder if needed    

    # You can also set default selection here
    html_response = render_template(
        "national_view.html",
        month_list = month_list,
        selected_month = selected_date,
        selected_modes = "Rail",
        selected_overlay = "no",
        area_list = area_list,
        selected_area = selected_area
    )
    # It will include map.html in templates folder
    response = Response(response=html_response, status=200, mimetype="text/html")
    return response

# Endpoint for refresh page
@app.route("/national_refresh/", methods=['POST'])
def refresh():
    # Get selections from user.
    selected_month = request.form.get("month")    
    selected_mode = request.form.get("modes")
    selected_overlay = request.form.get("overlay")

    selected_area = 'Buffalo'

    # Change the map.html in templates folder, the map in the page will be replace
    # Though I'm not sure it is the right way to do

    html_response = render_template(
        "national_view.html",
        month_list = month_list,
        selected_month = selected_month,
        selected_modes = selected_mode,
        selected_overlay = selected_overlay,
        area_list = area_list, 
        selected_area = selected_area       
    )
    response = Response(response=html_response, status=200, mimetype="text/html")
    return response

# Endpoint for first time loading metro area view
@app.route("/metro_test/", methods=['POST'])
def metro():
    selected_area = request.form.get('metroArea')

    # Modularize following sections so that they could be used in another endpoint.
    # Query data
    table_data = {'0': selected_area,'1':'data1','2':'data2','3':'data3','4':'data4','5':'data5'}

    # Create charts
    query = (
         'SELECT metro_area, month, mode, trips'
         ' FROM transitpolicyapp.ridership.top50_ridership'
         ' WHERE metro_area =  \''+selected_area + 
         '\' GROUP BY metro_area, month, mode, trips')
    resp = bqclient.query(query).to_dataframe()
    
    chart_ridership = alt.Chart(resp).mark_area().encode(
        x=alt.X('month:T', axis=alt.Axis(title='Month')),
        y=alt.Y('trips:Q', axis=alt.Axis(title='Total Transit Trips')),
        color="mode:N",
        tooltip=['month','mode', 'trips']
        ).interactive()

    html_chart = chart_ridership.save('templates/chart_ridership.html')

    html_response = render_template(
        "metro_area_dashboard.html",
        area_list = area_list,
        selected_area = selected_area,
        table_data = table_data
    )
    response = Response(response=html_response, status=200, mimetype="text/html")
    return response

# Endpoint for changing area
@app.route("/metro", methods=['POST'])
def change_area():
    selected_area = request.form.get('metroArea')

    # Query data 
    table_data = {'0': selected_area,'1':'newdata1','2':'newdata2','3':'newdata3','4':'newdata4','5':'newdata5'}

    # Create charts
    query = (
         'SELECT metro_area, month, mode, trips'
         ' FROM transitpolicyapp.ridership.top50_ridership'
         ' WHERE metro_area =  \''+selected_area + 
         '\' GROUP BY metro_area, month, mode, trips')
    resp = bqclient.query(query).to_dataframe()
    
    chart_ridership = alt.Chart(resp).mark_area().encode(
        x=alt.X('month:T', axis=alt.Axis(title='Month')),
        y=alt.Y('trips:Q', axis=alt.Axis(title='Total Transit Trips')),
        color="mode:N",
        tooltip=['month','mode', 'trips']
        ).interactive()

    html_chart = chart_ridership.save('templates/chart_ridership.html')

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