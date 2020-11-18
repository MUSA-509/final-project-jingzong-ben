# Final Project Proposal
#### Ben Dodson & Jingzong Wang
#### MUSA 509 | Fall 2020
<br>

<img src="https://github.com/MUSA-509/final-project-jingzong-ben/blob/master/Images/logo.png" style="width:200px;"/>

## Abstract
Almost overnight, travel patterns shifted as lockdown measures were put in place. As conditions continue to fluctuate, public transit has seen an unprecedented drop off in ridership. Policymakers need reliable and current data to make decisions about what services to prioritize. Examining public transit ridership through a demographic and public health lens can identify connections between these trends. Comparing how ridership shifted as cases rose can help policymakers plan for future breakouts and predict recovery scenarios. Our app uses the Federal Transit Administration's (FTA) National Transit Database (NTD). All public transit agencies submit monthly ridership to the FTA who cleans and publishes the data for public use. This dataset currently lacks an API to make the data accessible, however it is generally regarded as high quality. Users can view trends across the country, broken down by month and mode. Using a drop-down, users can focus in on a single metro area to view ridership trends as well as existing conditions from the ACS 1-year estimates to get a profile of a pre-pandemic baseline. Bringing in public health data on the local COVID-19 breakouts will also align with the ridership trends. Having these three datasets would be an asset to transit policymakers on how best to distribute limited resources while maintaining services for essential travel.

## Data
<b>National Transit Database</b> 
<br> <a href="https://www.transit.dot.gov/ntd/data-product/monthly-module-adjusted-data-release"> Data Source </a> | <a href="https://github.com/MUSA-509/final-project-jingzong-ben/blob/master/Data/NTD_ridership.csv"> View Dataset </a>
<br> Publisher: Federal Transit Administration
<br> Units: Total transit trips per month, by agency and transit mode
<br> Size: 0.7MB - 17,395 rows (Filtered to Jan 2019-Sep 2020)
<br> Hosting: Plan to host on Google Big Query
<br> Access: Publicly available 

<b>American Community Survey 1-year Estimates (2019)</b> 
<br> <a href="https://www.census.gov/data/developers/data-sets/acs-1year.html"> API Documentation </a>
<br> Publisher: Census Bureau
<br> Units: Various (Units or shares); aggregated to UZA metro area
<br> Hosting: N/A; api call on a per request basis
<br> Access: Publicly available

<b>COVID-19 Data Repo</b>
<br> <a href="https://github.com/CSSEGISandData/COVID-19"> Data Source </a> | <a href="https://pipedream.com/@pravin/http-api-for-latest-covid-19-data-p_G6CLVM/edit"> API Documentation </a>
<br> Publisher: Johns Hopkins University Center for Science and Engineering (CSSE)
<br> Units: Daily cases by reporting geography
<br> Hosting: N/A; api call on a per request basis
Access: Publicly available with Creative Commons Attribution (CC BY 4.0) License

## <a href="https://www.figma.com/file/0PVeefNnvioodWHnQWbDJa/Transport-Policy-APP?node-id=0%3A1">Wireframe</a>
<img src="https://github.com/MUSA-509/final-project-jingzong-ben/blob/master/TransportPolicyWireframe.png" style="width:800px;"/>
