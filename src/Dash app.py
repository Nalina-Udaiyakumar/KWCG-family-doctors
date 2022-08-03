#Python 3
# libraries
import dash
from dash import dcc,html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from datetime import datetime
import plotly.graph_objects as go
from jupyter_dash import JupyterDash
import dash_table_experiments as dt

from math import sin, cos, sqrt, atan2, radians
import pgeocode
from pyproj import Geod

import os
import pandas as pd
import numpy as np

# Set working directory
os.chdir(r"---Your directory path---")
print(os.getcwd())
print("The current running version of python is: ",platform.python_version())
## this dash app filtering call back requires Python 3.8 or higher.

# Styling components
FONT_AWESOME = (
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css"
)
external_stylesheets = [dbc.themes.BOOTSTRAP, FONT_AWESOME]

# Read csv files - KWCG doctors list and distance matrix
distanceTable = pd.read_csv("UniqueKWCGcodes.csv",header=0)
print(distanceTable.shape)

KWCGpostalcodes = pd.read_csv("KWCGpostcodes_Latlong.csv",header=0)
print(KWCGpostalcodes.shape)

KWCGdoctors = pd.read_csv("Results_family doctors KWCG.csv",header=0, index_col=0)
print(KWCGdoctors.shape)

## define function to calculate distance between 2 latitude and longitude points
wgs84_geod = Geod(ellps='WGS84') #Distance will be measured on this ellipsoid - more accurate than a spherical method

#Get distance between pairs of lat-long points
def Distance(lat1,lon1,lat2,lon2):
    d1,d2,dist = wgs84_geod.inv(lon1,lat1,lon2,lat2) 
    return dist

# Remove unwanted columns from KWCGdoctors df
KWCGdoctors = KWCGdoctors.drop(['Specializations','Fax','LastName','FirstName','Former Name','LocationFlag'], axis=1)

# Check for doctor locations with null postal code values - removing them
print(KWCGdoctors[KWCGdoctors['Postal Code'].isnull()])
KWCGdoctors = KWCGdoctors.dropna(subset=['Postal Code'])
print(KWCGdoctors.shape)
print(KWCGdoctors['Postal Code'].isnull().sum()) # check again for nulls in the postal code column

# add latitude and longitude to each postal code in the KWCGdoctors dataframe
KWCGdoctors = KWCGdoctors.merge(KWCGpostalcodes.drop(['City'],axis=1), left_on='Postal Code', right_on='Postalcode', how='left')
KWCGdoctors = KWCGdoctors.drop(['Postalcode'],axis=1)
print(KWCGdoctors.shape)
print(KWCGdoctors.columns)

# Populating options for the interactive input controls
# Populting regions
region_options = KWCGdoctors['City'].unique()


# Initialise the app
app = JupyterDash(__name__, external_stylesheets=[dbc.themes.FLATLY])

app.layout = dbc.Container([
        dbc.Row(
            dbc.Col(html.H2('Family Doctor Search - Kitchener Waterloo region', className='text-center text-primary, mb-3'))),  # header row
            
        dbc.Row([  # start of second row 
            dbc.Col([   # first column on second row - side bar
            dbc.Row([
                dbc.Label("Show number of rows:"),
                dcc.Dropdown(id="row_drop",value=15, clearable=False, style={'width':'35%'},
                                        options=[10,15,20,30]),
                html.Hr()]),
            dbc.Row([
                dbc.Label('Search by:'), #html.H4
                dcc.RadioItems(
                    id="mode_radio", 
                    options = ['Location', 'Distance'], 
                    value = 'Location',
                    inline = True   #style={'width': '35%'}
                    ),
                html.Hr()]),
            dbc.Row([    
                dbc.Label('Select location'), #html.H6
                dcc.Dropdown(   #location_dropdown :=
                    id="location_dropdown",
                    options = region_options, 
                    value = 'Kitchener',
                    clearable = False),
                html.Hr()]),
            dbc.Row([
                dbc.Label('Enter postal code (ex. N2M 0A1)'),  #html.H6
                dcc.Input( #postalcode_input := 
                    id = 'postalcode_input',  # if Python 3.8 or higher, add the walrus (:=) operator instead of defining id attribute
                    type="text", 
                    placeholder="N2M 0A1", 
                    debounce=True),
                dbc.Label('Select radius of search'),  #html.H6
                dcc.Slider( #radius_slider := 
                   id="radius_slider",
                   min=5, max=50, step=None,
                   marks={5:"5", 10:"10", 15:"15", 20:"20", 30:"30", 50:"50"},
                   value=0)]),
                dbc.Button(id='download_button',
                          children=["Download"],
                          color="info",
                          className="mt-1"),
                dcc.Download(id="download-component")
            ], width={'size': 2, 'offset': 0, 'order': 2}),  # width first column on second row
            
            dbc.Col([  # second column on second row - data table
            html.H5('List of doctors', className='text-left'),
            dt.DataTable(
                id='doctors-datatable',
                data=KWCGdoctors.to_dict('records'),
                columns = [{'name':i, 'id':i} for i in KWCGdoctors.columns[0:7]],
                editable=False,
                page_size=15,
                page_action='native',
                style_data = {
                    'width': '150px', 'minWidth': '150px', 'maxWidth': '150px',
                    'overflow': 'hidden',
                    'textoverflow': 'ellipsis',
                }
                )
            ], width={'size': 9, 'offset': 0, 'order': 2}),  # width second column on second row
        ])  # end of second row        
    ], fluid=True)

# Define callbacks

## Callback for filtering serch of doctors
@app.callback(
    Output('doctors-datatable', 'data'),
    Output('doctors-datatable', 'page_size'),
    Input('mode_radio','value'),
    Input('location_dropdown', 'value'),
    Input('postalcode_input', 'value'),
    Input('radius_slider', 'value'),
    Input('row_drop', 'value')
)
def updateDoctorsTable(mode_v,location_v,postalcode_v,radius_v,row_v): #,num_clicks
    global doctordf   # define doctordf as a global variable so the download option can access the filetered search list of doctors
    
    doctordf = KWCGdoctors.copy()
    
    if mode_v=="Location":
        if location_v:
            doctordf = doctordf[doctordf['City'] == location_v]

    if mode_v=="Distance":
        if postalcode_v:
            # Gather latitude and longitude of the given postal code from the postal code database 
            latgiven = KWCGpostalcodes[KWCGpostalcodes['Postalcode']==postalcode_v]['Latitude']
            longgiven = KWCGpostalcodes[KWCGpostalcodes['Postalcode']==postalcode_v]['Longitude']

            # Calculate distance of each doctor's location from the given postal code
            KWCGdoctors['LatGiven'] = float(latgiven.values)
            KWCGdoctors['LongGiven'] = float(longgiven.values)                                                                      
            KWCGdoctors['DistanceCol'] =  Distance(KWCGdoctors['Latitude'].tolist(),KWCGdoctors['Longitude'].tolist(),
                                            KWCGdoctors['LatGiven'].tolist(),KWCGdoctors['LongGiven'].tolist())
            # floor and sort KWCGdoctors in ascending order of DistanceCol
            KWCGdoctors["DistanceCol"] = (KWCGdoctors["DistanceCol"]/1000).apply(np.floor)
            KWCGdoctors.sort_values(by="DistanceCol",ascending=True)

            doctordf = KWCGdoctors[KWCGdoctors['DistanceCol']<=radius_v]
            doctordf.sort_values(by="DistanceCol", ascending=True)

    return doctordf.to_dict('records'), row_v

## Callback for download option
@app.callback(
    Output('download-component', 'data'),
    Input('download_button', 'n_clicks'),
    prevent_initial_call=True,
)
def enableDownload(n_clicks): 
    if n_clicks>0:
        return dcc.send_data_frame(doctordf.to_excel, "Family doctor search_excel.xlsx", sheet_name="Sheet_name_1")


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True, port=8058)
