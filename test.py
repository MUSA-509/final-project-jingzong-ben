from flask import Flask, Response, render_template, escape, request, url_for
import requests
import json
import logging

app = Flask(__name__, template_folder="templates")

area_list = ['Bridgeport-Stamford, CT-NY', 'Buffalo, NY', 'Charlotte, NC-SC', 'Chicago, IL-IN', 'Cincinnati, OH-KY-IN', 'Cleveland, OH', 'Columbus, OH', 'Dallas-Fort Worth-Arlington, TX', 'Dayton, OH', 'Denver-Aurora, CO', 'Detroit, MI', 'Durham, NC', 'Fresno, CA', 'Hartford, CT', 'Honolulu, HI', 'Houston, TX', 'Indianapolis, IN', 'Jacksonville, FL', 'Las Vegas-Henderson, NV', 'Los Angeles-Long Beach-Anaheim, CA', 'Louisville/Jefferson County, KY-IN', 'Miami, FL', 'Milwaukee, WI', 'Minneapolis-St. Paul, MN-WI', 'New Haven, CT', 'New Orleans, LA', 'New York-Newark, NY-NJ-CT', 'Orlando, FL', 'Philadelphia, PA-NJ-DE-MD', 'Phoenix-Mesa, AZ', 'Pittsburgh, PA', 'Portland, OR-WA', 'Providence, RI-MA', 'Reno, NV-CA', 'Richmond, VA', 'Riverside-San Bernardino, CA', 'Rochester, NY', 'Sacramento, CA', 'Salt Lake City-West Valley City, UT', 'San Antonio, TX', 'San Diego, CA', 'San Francisco-Oakland, CA', 'San Jose, CA', 'Seattle, WA', 'Spokane, WA', 'St.Louis, MO-IL', 'Tampa-St. Petersburg, FL', 'Tucson, AZ', 'Virginia Beach, VA', 'Washington, DC-VA-MD', 'Buffalo']

#test
@app.route("/national_test/")
def nationalTest():
    selected_date = request.args.get("selectedDate")
    selected_date = '2019-02'
    month_list = ['2019-01', '2019-02', '2019-03', '2019-04', '2019-05', '2019-06', '2019-07', '2019-08', '2019-09', '2019-10', '2019-11', '2019-12', '2020-01', '2020-02', '2020-03', '2020-04', '2020-05', '2020-06', '2020-07', '2020-08', '2020-09']

    selected_area = request.args.get("selectedArea")

    html_response = render_template(
        "national_view.html",
        month_list = month_list,
        selected_month = selected_date,
        area_list = area_list,
        selected_area = selected_area
    )
    response = Response(response=html_response, status=200, mimetype="text/html")
    return response

@app.route("/metro_view_test/")
def metroTest():
    selected_area = 'Buffalo'
    table_data = {'0':'data0','1':'data1','2':'data2','3':'data3','4':'data4','5':'data5'}

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