import pandas as pd 
import folium 
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import dash 
import base64
from dash import dcc 
from dash import html 
from dash.dependencies import Input, Output, State
from app import *
from dash_bootstrap_templates import ThemeSwitchAIO # Theme switch library - day/night mode

# Instantiating the server
FONT_AWESOME = ["https://use.fontawesome.com/releases/v5.10.2/css/all.css"]
app = dash.Dash(__name__, external_stylesheets=FONT_AWESOME)
app.scripts.config.serve_locally = True
server = app.server


# ========== Styles ============ #
tab_card = {'height': '100%'} # to occupy 100% of the column

# Templates usados com ThemeSwitchAIO
template_theme1 = "flatly"
template_theme2 = "darkly"
url_theme1 = dbc.themes.FLATLY
url_theme2 = dbc.themes.DARKLY


# Read the clean CSV file
data = pd.read_csv('peace_index.csv', sep=';')

# Comma replacement with periods in numeric columns before converting to numeric type using pd.to_numeric, with error handling as NaN.
numeric_columns = data.columns[2:] 
data[numeric_columns] = data[numeric_columns].apply(lambda x: x.str.replace(',', '.')).apply(pd.to_numeric, errors='coerce')

data['Country'] = data['Country'].astype(str)
data['iso3c'] = data['iso3c'].astype(str)

# Consider only the years 2011-2021
year_columns = [ str (year) for year in  range ( 2011 , 2022 )]

#Filter the dataset for the selected years
data = data[[ 'Country' , 'iso3c' ] + year_columns]

# Calculate global safety averages for each year
global_avg_safety = data[year_columns].mean(numeric_only=True)

# Calculate global safety averages for each year
global_avg_safety = data[year_columns].mean(numeric_only=True)

# Loading the image as a binary file
with open('C:\\Users\\User\\Desktop\\DataMind\\1.jpg', 'rb') as img_file:
    encoded_image = base64.b64encode(img_file.read()).decode('utf-8')


# Create the Dash app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div([
    ThemeSwitchAIO(aio_id="theme", themes=[url_theme1, url_theme2]), # Stations the URls already created + Day/Night Theme Change
    html.Img(src='data:image/jpg;base64,{}'.format(encoded_image), style={'width': '8%', 'float': 'left'}), # DataMind company symbol
    html.H1('Travel Safety Analysis', style={'text-align': 'center', 'font-size': '62px', 'font-weight': 'bold'}),
    html.A("Visit the webpage", href="https://datamind.dev.br/", target="_blank", className="button", style={'clear': 'both', 'display': 'block', 'text-align': 'left'}), # Text = Box with button to select Web
    dcc.Dropdown(
        id='year-dropdown',
        options=[{'label': year, 'value': year} for year in year_columns],
        value=year_columns[0],  # Default to the first year in the dataset
        style={'backgroundColor': '#f5f5f5'}
    ),
    html.Div(
        children=[
            html.Div(id='map-container', style={'width': '65%', 'display': 'inline-block', 'height': '600px'}),
            html.Div(id='charts-container', style={'width': '34%', 'float': 'right', 'height': '600px'}),
        ],
        style={'width': '100%'}
    ), 
])


# Callback function
@app.callback(
    [Output('map-container', 'children'),
     Output('charts-container', 'children')],
    [Input('year-dropdown', 'value')]
)
def update_map_and_charts(year):
    # Update the map
    m = folium.Map(zoom_start=2, tiles='CartoDB dark_matter')
    folium.Choropleth(
        geo_data='https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/world-countries.json',
        name='choropleth',
        data=data,
        columns=['iso3c', year],
        key_on='feature.id',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Safety Score'
    ).add_to(m)
    map_container = html.Iframe(srcDoc=m._repr_html_(), width='100%', height='600px')
    # Update the charts
    worst_10_countries = data.nlargest(10, year)
    bar_chart = px.bar(worst_10_countries, x=year, y='Country', orientation='h',
                       title=f'10 Least Safe Countries in {year}', template='plotly_dark')
    bar_chart.update_traces(marker_color='darkred')
    line_chart = px.line(global_avg_safety.reset_index(), x='index', y=0, title='Global Safety Average Over Time',
                         template='plotly_dark')
    line_chart.update_traces(line_color='red')
    charts_container = html.Div([
        html.Div([dcc.Graph(figure=bar_chart, style={'height': '300px'})]),
        html.Div([dcc.Graph(figure=line_chart, style={'height': '300px'})]),
    ])
    return map_container, charts_container


if __name__ == '__main__':
    app.run_server(debug=True, port=8080)