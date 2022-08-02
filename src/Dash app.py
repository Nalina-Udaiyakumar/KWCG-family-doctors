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

# Read csv files - KWCG doctors list and distance matrix
distanceTable = pd.read_csv("UniqueKWCGcodes.csv",header=0)
print(distanceTable.shape)

KWCGpostalcodes = pd.read_csv("KWCGpostcodes_Latlong.csv",header=0)
print(KWCGpostalcodes.shape)

KWCGdoctors = pd.read_csv("Results_family doctors KWCG.csv",header=0, index_col=0)
print(KWCGdoctors.shape)

## define function to calculate distance between 2 latitude and longitude points
wgs84_geod = Geod(ellps='WGS84') #Distance will be measured on this ellipsoid - more accurate than a spherical method

#Get distance between pairs of lat-lon points
def Distance(lat1,lon1,lat2,lon2):
    az12,az21,dist = wgs84_geod.inv(lon1,lat1,lon2,lat2) #Yes, this order is correct
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


# Initialise the app
app = JupyterDash(__name__, external_stylesheets=[dbc.themes.FLATLY])

# Define sidebar and content styles
SIDEBAR_STYLE = {
    'position': 'fixed',
    'top': 0,
    'left': 0,
    'bottom': 0,
    'width': '12rem',
    'padding': '2rem 1rem',
    'background-color': 'lightgray',
}
CONTENT_STYLE = {
    'margin-left': '15rem',
    'margin-right': '2rem',
    'padding': '2rem' '1rem',
}

app.layout = dbc.Container([
        dbc.Row(
            dbc.Col(html.H2('Family Doctor Search - KW region', className='text-center text-primary, mb-3'))),  # header row
            
        dbc.Row([  # start of second row 
            dbc.Col([   # first column on second row - side bar
            dbc.Row([
                dbc.Label("Show number of rows:"),
                row_drop := dcc.Dropdown(value=15, clearable=False, style={'width':'35%'},
                                        options=[10,15,20,30]),
                html.Hr()]),
            dbc.Row([
                dbc.Label('Search by:'), #html.H4
                mode_radio := dcc.RadioItems(
                                        options = ['Location ', 'Distance '], 
                                        value = 'Location ',
                                        inline = False),
                html.Hr()]),
            dbc.Row([    
                dbc.Label('Select location'), #html.H6
                location_radio := dcc.RadioItems(
                                        options = ['Kitchener ', 'Waterloo ', 'Cambridge ', 'Guelph '], 
                                        value = 'Kitchener ',
                                        inline = False),
                html.Hr()]),
            dbc.Row([
                dbc.Label('Enter postal code (ex. N2M0A1)'),  #html.H6
                postalcode_input := dcc.Input(
                    #                   id = 'postalcode_input',  # if Python 3.7 or lower, add this instead of using the walrus (:=) operator
                                        type="text", 
                                        placeholder="", 
                                        debounce=True),
                dbc.Label('Select radius of search'),  #html.H6
                radius_slider := dcc.Slider( 
                           min=5, max=50, step=None,
                           marks={5:"5", 10:"10", 15:"15", 20:"20", 30:"30", 50:"50"},
                           value=0)]),
#             html.Button('Search doctors', id='search_button', n_clicks=0)
            ], width={'size': 2, 'offset': 0, 'order': 1}),  # width first column on second row
            
            dbc.Col([  # second column on second row - data table
            html.H5('List of doctors', className='text-left'),
            dt.DataTable(
                id='doctors-datatable',
                data=KWCGdoctors.to_dict('records'),
                columns = [{'name':i, 'id':i} for i in KWCGdoctors.columns],
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
    ])

# # # Define callbacks
@callback(
    Output('doctors-datatable', 'data'),
    Output('doctors-datatable', 'page_size'),       
    Input('mode_radio','value'),
    Input('location_radio', 'value'),
    Input('postalcode_input', 'value'),
    Input('radius_slider', 'value'),
    Input('row_drop', 'value')
)
def updateDoctorsTable(mode_v,location_v,postalcode_v,radius_v,row_v):
    doctordf = KWCGdoctors.copy()
    
    if location_v:
        doctordf = doctordf[doctordf['City'].isin(location_v)]

    if postlcode_v:
      doctordf = doctordf[doctordf['Postal Code'].isin(postalcode_v)]
        
    return doctordf.to_dict('records'), row_v

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True, port=8058)
    
