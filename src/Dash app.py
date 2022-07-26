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

import os
import pandas as pd
import numpy as np

# Set working directory
os.chdir(r"---Your directory path---")
print(os.getcwd())

# Read csv files - KWCG doctors list and distance matrix
uniqueKWCGcodes = pd.read_csv("UniqueKWCGcodes.csv",header=0)
print(uniqueKWCGcodes.shape)

KWCGdoctors = pd.read_csv("Results_family doctors KWCG.csv",header=0)
print(KWCGdoctors.shape)

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
    
