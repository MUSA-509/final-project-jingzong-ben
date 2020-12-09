from flask import Flask, Response, render_template, escape, request, url_for
import requests
import json
import logging

app = Flask(__name__, template_folder="templates")

area_list = ['Bridgeport-Stamford', 'Buffalo', 'Charlotte, NC-SC', 'Chicago, IL-IN', 'Cincinnati, OH-KY-IN', 'Cleveland, OH', 'Columbus, OH', 'Dallas-Fort Worth-Arlington, TX', 'Dayton, OH', 'Denver-Aurora', 'Detroit, MI', 'Durham, NC', 'Fresno, CA', 'Hartford, CT', 'Honolulu, HI', 'Houston, TX', 'Indianapolis', 'Jacksonville', 'Las Vegas-Henderson']
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