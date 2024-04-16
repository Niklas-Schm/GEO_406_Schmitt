import sqlite3

import dash
from dash import dash_table
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import pyproj
from dash import dcc, html, Input, Output


def etrs_to_latlon(etrs_x, etrs_y):
    transformer = pyproj.Transformer.from_crs("epsg:25832", "epsg:4326", always_xy=True)
    lon, lat = transformer.transform(etrs_x, etrs_y)
    return lat, lon


# Connect to the SQLite database
connection = sqlite3.connect('Geo_406_Schmitt.db')
cursor = connection.cursor()

query = "SELECT Ostwert, Nordwert, Standort, messstelle_nr FROM pegel_meta"
data = pd.read_sql(query, connection)

data['lat'], data['lon'] = zip(*data.apply(lambda row: etrs_to_latlon(row['Ostwert'], row['Nordwert']), axis=1))
data['size'] = 10
connection.close()

# Dash-App initialisieren
app = dash.Dash(__name__)
# Layout der App definieren
app.layout = html.Div([
    dcc.Graph(id='map', style={'height': '600px'}),
    html.Div(id='meta_table', style={'textAlign': 'center'}),
    dcc.Dropdown(
        id='data-type',
        options=[
            {'label': 'Pegel Q', 'value': 'q'},
            {'label': 'Pegel W', 'value': 'w'}
        ],
        value='q'
    ),
    html.Div([
        html.Button("Download CSV", id="btn_csv"),
        dcc.Download(id="download-dataframe-csv"),
    ]),
    dcc.Graph(id='plot'),
    html.Div(id='statistic_table', style={'textAlign': 'center'})
])


# Callback-Funktion für die Interaktion mit der Karte
@app.callback(
    Output('plot', 'figure'),
    [Input('map', 'clickData'),
     Input('data-type', 'value')]
)
def update_plot(clickData, data_type):
    if clickData is not None:
        # Klickposition holen
        lat = clickData['points'][0]['lat']
        lon = clickData['points'][0]['lon']
        # Finde die nächste Station basierend auf den Koordinaten
        station = data[(data['lat'] == lat) & (data['lon'] == lon)]['Standort'].values[0]
        selected_data = data[data['Standort'] == station]
        selected_station = selected_data['messstelle_nr'].values[0]

        # Connect to the SQLite database
        connection_pegel = sqlite3.connect('Geo_406_Schmitt.db')
        cursor_pegel = connection_pegel.cursor()

        query_pegel = (f"SELECT messstelle_nr, zeit, {data_type} FROM pegel_{data_type} "
                       f"WHERE messstelle_nr = '{selected_station}'")
        data_pegel = pd.read_sql(query_pegel, connection_pegel)
        connection_pegel.close()

        y_axis_name = 'Durchfluss in m³/s' if data_type == 'q' else 'Wasserstand in cm'

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data_pegel['zeit'], y=data_pegel[data_type], mode='lines+markers', name=station))
        fig.update_layout(title=f'Zeitreihe für {station}',
                          xaxis_title='Zeit',
                          yaxis_title=y_axis_name)

        return fig
    else:
        return {}


# Callback-Funktion für das Aktualisieren der Karte
@app.callback(
    Output('map', 'figure'),
    [Input('plot', 'clickData')]
)
def update_map(clickData):
    fig = px.scatter_mapbox(data,
                            lat='lat',
                            lon='lon',
                            hover_name='Standort',
                            hover_data={'messstelle_nr': True},
                            zoom=5)
    fig.update_traces(hovertemplate='Standort: %{hovertext}<br>'
                                    'lat: %{lat}<br>'
                                    'lon: %{lon}<br>'
                                    'ID: %{customdata[0]}')
    fig.update_layout(mapbox_style="open-street-map")
    return fig


# Callback-Funktion für das Aktualisieren der Metadaten-Tabelle
@app.callback(
    Output('meta_table', 'children'),
    [Input('map', 'clickData')]
)
def update_metadata_table(clickData):
    if clickData is not None:
        mess_id = clickData['points'][0]['customdata'][0]

        # Connect to the SQLite database inside the callback
        connection_meta = sqlite3.connect('Geo_406_Schmitt.db')
        cursor_meta = connection_meta.cursor()

        # Construct and execute the SQL query
        query_meta = f"SELECT * FROM pegel_meta WHERE messstelle_nr = '{mess_id}' "
        cursor_meta.execute(query_meta)
        selected_data = cursor_meta.fetchall()

        # Convert selected_data to DataFrame
        selected_df = pd.DataFrame(selected_data, columns=['messstelle_nr', 'Standort', 'Gewaesser',
                                                           'Einzugsgebiet_Oberirdisch', 'Status', 'Entfernung_Muendung',
                                                           'Messnetz_Kurzname', 'Ostwert', 'Nordwert', 'MB', 'MS1',
                                                           'MS2', 'MS3'])

        # Close the cursor and connection
        cursor_meta.close()
        connection_meta.close()

        # Convert DataFrame to DataTable
        meta_table = dash_table.DataTable(
            columns=[{'name': col, 'id': col} for col in selected_df.columns],
            data=selected_df.to_dict('records'),
            style_cell={'textAlign': 'center'},
            style_table={'margin': '20px auto'}
        )
        return meta_table
    else:
        return html.Div('No data selected', style={'margin': '20px'})


@app.callback(
    Output('statistic_table', 'children'),
    [Input('map', 'clickData'),
     Input('data-type', 'value')]
)
def update_statistic(clickData, data_type):
    if clickData is not None:
        # Klickposition holen
        lat = clickData['points'][0]['lat']
        lon = clickData['points'][0]['lon']
        # Finde die nächste Station basierend auf den Koordinaten
        station = data[(data['lat'] == lat) & (data['lon'] == lon)]['Standort'].values[0]
        selected_data = data[data['Standort'] == station]
        selected_station = selected_data['messstelle_nr'].values[0]

        # Connect to the SQLite database
        connection_pegel = sqlite3.connect('Geo_406_Schmitt.db')
        cursor_pegel = connection_pegel.cursor()

        query_pegel = (f"SELECT messstelle_nr, zeit, {data_type} FROM pegel_{data_type} "
                       f"WHERE messstelle_nr = '{selected_station}'")
        data_pegel = pd.read_sql(query_pegel, connection_pegel)
        connection_pegel.close()

        mean = round(data_pegel[data_type].mean(), 3)
        max_value = data_pegel[data_type].max()
        min_value = data_pegel[data_type].min()
        std = round(data_pegel[data_type].std(), 3)
        q25 = round(data_pegel[data_type].quantile(0.25), 3)
        q50 = round(data_pegel[data_type].quantile(0.5), 3)
        q75 = round(data_pegel[data_type].quantile(0.75), 3)

        statistic_table = dash_table.DataTable(
            data=[
                {'Statistic': 'Mean', 'Value': mean},
                {'Statistic': 'Max', 'Value': max_value},
                {'Statistic': 'Min', 'Value': min_value},
                {'Statistic': 'Std', 'Value': std},
                {'Statistic': '25%', 'Value': q25},
                {'Statistic': '50%', 'Value': q50},
                {'Statistic': '75%', 'Value': q75}
            ],
            columns=[
                {'name': 'Statistik', 'id': 'Statistic'},
                {'name': 'Wert', 'id': 'Value'}
            ],
            style_table={'width': '50%', 'margin': 'auto'},
            style_cell={'textAlign': 'center'},
        )

        return statistic_table
    else:
        return html.Div('No data selected', style={'margin': '20px'})


@app.callback(
    Output("download-dataframe-csv", "data"),
    [Input("btn_csv", "n_clicks")],
    [Input('map', 'clickData')],
    [dash.dependencies.State("data-type", "value")]
)
def download_data(n_clicks, clickData, data_type):
    if clickData:
        mess_id = clickData['points'][0]['customdata'][0]

        if n_clicks:
            # Connect to the SQLite database inside the callback
            connection_download = sqlite3.connect('Geo_406_Schmitt.db')
            cursor_download = connection_download.cursor()

            # Construct and execute the SQL query
            query_meta = f"SELECT * FROM pegel_{data_type} WHERE messstelle_nr = '{mess_id}' "
            cursor_download.execute(query_meta)
            data_download = cursor_download.fetchall()
            download_df = pd.DataFrame(data_download, columns=['messstelle_nr', 'zeit', data_type,
                                                               f'{data_type}_min', f'{data_type}_max'])

            return dcc.send_data_frame(download_df.to_csv, f"{mess_id}_{data_type}.csv")


# App starten
app.run_server(debug=True)
