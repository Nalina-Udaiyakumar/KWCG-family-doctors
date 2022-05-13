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

app.layout = dbc.Container(
    [
        dbc.Row(dbc.Col(html.H2('Family Doctor Search - KW region', className='text-center text-primary, mb-3'))),  # header row
        
        dbc.Row([  # start of second row 
            dbc.Col([  # first column on second row - side bar
            dbc.Row([
                html.H4('Search by:'),
                dcc.RadioItems(
                    id = 'mode_radio',
                    options = ['Location ', 'Distance '], 
                    value = 'Location ',
                    inline = False),
                html.Hr()]),
            dbc.Row([    
                html.H6('Select location'),
                dcc.RadioItems(
                    id = 'location_radio',
                    options = ['Kitchener ', 'Waterloo ', 'Cambridge ', 'Guelph '], 
                    value = 'Kitchener ',
                    inline = False),
                html.Hr()]),
            dbc.Row([
                html.H6('Enter postal code (ex. N2M0A1)'),
                dcc.Input(
                    id = 'postalcode_input',
                    type="text", 
                    placeholder="", 
                    debounce=True),
                html.H6('Select radius of search'),
                dcc.Slider(id="radius_slider", 
                           min=5, max=50, step=None,
                           marks={5:"5", 10:"10", 15:"15", 20:"20", 30:"30", 50:"50"},
                           value=0)]),
            html.Button('Search doctors', id='search_button', n_clicks=0)
            ], width={'size': 2, 'offset': 0, 'order': 1}),  # width first column on second row
            
            dbc.Col([  # second column on second row - data table
            html.H5('List of doctors', className='text-center'),
            dt.DataTable(
                id='doctors-datatable',
                rows=KWCGdoctors.to_dict('records'),
                editable=False,
                row_selectable=True,
                filterable=True,
                sortable=True,
                selected_row_indices=[]
                )
            ], width={'size': 9, 'offset': 0, 'order': 2}),  # width second column on second row
        ])  # end of second row        
    ], fluid=True)

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True, port=8058)
    
@app.callback(Output('doctors-datatable', 'selected_row_indices'),
[Input('doctors-datatable', 'clickData')],
[State('doctors-datatable', 'selected_row_indices')])
def updated_selected_row_indices(clickData, selected_row_indices):
  if clickData:
    for point in clickData['points']:
      if point['pointNumber'] in selected_row_indices:
        selected_row_indices.remove(point['pointNumber'])
      else:
        selected_row_indices.append(point['pointNumber'])
        return selected_row_indices
