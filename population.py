import pandas as pd
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go

# Load the dataset
data = pd.read_csv('world_population.csv')

# Extract the years dynamically from the column names
years = [int(col.split(' ')[0]) for col in data.columns if 'Population' in col and 'Percentage' not in col]
years = sorted(years)

# Initialize the Dash app with Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

# Layout with Bootstrap
app.layout = dbc.Container(
    fluid=True,
    children=[
        html.H1("World Population Dashboard", className="text-center mt-4 text-light"),
        
        # Dropdowns and Sliders
        dbc.Row([
            dbc.Col([
                html.Label("Select a Country:", className="text-light"),
                dcc.Dropdown(
                    id='country-dropdown',
                    options=[{'label': country, 'value': country} for country in data['Country/Territory']],
                    value='India',
                    style={'width': '100%', 'color': '#333'},
                )
            ], width=6),
            dbc.Col([
                html.Label("Select a Year:", className="text-light"),
                dcc.Slider(
                    id='year-slider',
                    min=min(years),
                    max=max(years),
                    step=1,
                    marks={year: str(year) for year in years},
                    value=max(years),
                )
            ], width=6)
        ], className="mb-4"),
        
        # Map and Graphs
        dbc.Row([
            dbc.Col([dcc.Graph(id='world-map', style={'height': '70vh'})], width=12)
        ]),
        dbc.Row([
            dbc.Col([dcc.Graph(id='population-graph', style={'height': '45vh'})], width=6),
            dbc.Col([dcc.Graph(id='growth-rate-graph', style={'height': '45vh'})], width=6),
        ], className="mt-4"),
        
        # Density Area Graph (Animated)
        dbc.Row([
            dbc.Col([dcc.Graph(id='density-area-graph', style={'height': '45vh'})], width=12),
        ], className="mt-4"),

        # Stats Card
        dbc.Row([
            dbc.Col([
                dbc.Card(
                    dbc.CardBody([
                        html.H4("Statistics Summary", className="card-title text-light"),
                        html.Div(id='stats-output', className="text-light")
                    ]),
                    color="dark"
                )
            ])
        ], className="mt-4"),
    ]
)

@app.callback(
    [Output('population-graph', 'figure'),
     Output('growth-rate-graph', 'figure'),
     Output('world-map', 'figure'),
     Output('density-area-graph', 'figure'),
     Output('stats-output', 'children')],
    [Input('country-dropdown', 'value'),
     Input('year-slider', 'value')]
)
def update_dashboard(selected_country, selected_year):
    # Filter data for the selected country
    country_data = data[data['Country/Territory'] == selected_country]

    # Historical population data
    historical_population = [
        country_data[f'{year} Population'].values[0] for year in years
    ]

    # Population for the selected year
    selected_population = country_data[f'{selected_year} Population'].values[0]

    # Compute growth rates
    growth_rates = [
        ((historical_population[i] - historical_population[i - 1]) / historical_population[i - 1]) * 100
        if i > 0 else 0 for i in range(len(historical_population))
    ]

    # Line graph: Historical population trend
    population_fig = go.Figure()
    population_fig.add_trace(go.Scatter(
        x=years, y=historical_population, mode='lines+markers', name='Population',
        line=dict(color='#FFA500')
    ))
    population_fig.update_layout(
        title=f"Population Trend for {selected_country}",
        xaxis_title="Year",
        yaxis_title="Population",
        template="plotly_dark",
    )

    # Bar graph: Growth rate comparison over years
    growth_rate_fig = go.Figure()
    growth_rate_fig.add_trace(go.Bar(
        x=years, y=growth_rates, name='Growth Rate (%)', marker_color='#00FF00'
    ))
    growth_rate_fig.update_layout(
        title=f"Growth Rate Trend for {selected_country}",
        xaxis_title="Year",
        yaxis_title="Growth Rate (%)",
        template="plotly_dark",
    )

    # Choropleth map: World population
    world_map = px.choropleth(
        data_frame=data,
        locations="CCA3",
        color=f"{selected_year} Population",
        hover_name="Country/Territory",
        title=f"World Population Distribution in {selected_year}",
        template="plotly_dark",
        color_continuous_scale=px.colors.sequential.Plasma
    )
    world_map.update_traces(
        selector=dict(type="choropleth"),
        marker_line_color="white"
    )
    world_map.update_layout(
        margin={"r":0,"t":30,"l":0,"b":0},
    )

    # Calculate Population Density (Population / Area)
    data['Density'] = data[f'{selected_year} Population'] / data['Area (km²)']

    # Animated line graph: Population Density over the years
    density_fig = go.Figure()
    for year in years:
        density_fig.add_trace(go.Scatter(
            x=data['Country/Territory'], 
            y=data[f'{year} Population'] / data['Area (km²)'],
            mode='lines+markers',
            name=str(year),
            visible='legendonly' if year != selected_year else True
        ))
    
    density_fig.update_layout(
        title=f"Population Density for {selected_country}",
        xaxis_title="Country/Territory",
        yaxis_title="Density (per km²)",
        updatemenus=[dict(
            type="buttons",
            showactive=False,
            buttons=[dict(
                label="Play",
                method="animate",
                args=[None, dict(frame=dict(duration=500, redraw=True), fromcurrent=True, mode="immediate")],
            )]
        )],
        template="plotly_dark",
    )

    # Statistics output
    stats = [
        f"Population in {selected_year}: {selected_population:,}",
        f"Country: {selected_country}"
    ]

    return population_fig, growth_rate_fig, world_map, density_fig, html.Ul([html.Li(stat) for stat in stats])


if __name__ == '__main__':
    app.run_server(debug=True)
import pandas as pd
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go

# Load the dataset
data = pd.read_csv('world_population.csv')

# Extract the years dynamically from the column names
years = [int(col.split(' ')[0]) for col in data.columns if 'Population' in col and 'Percentage' not in col]
years = sorted(years)

# Initialize the Dash app with Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

# Layout with Bootstrap
app.layout = dbc.Container(
    fluid=True,
    children=[
        html.H1("World Population Dashboard", className="text-center mt-4 text-light"),
        
        # Dropdowns and Sliders
        dbc.Row([
            dbc.Col([
                html.Label("Select a Country:", className="text-light"),
                dcc.Dropdown(
                    id='country-dropdown',
                    options=[{'label': country, 'value': country} for country in data['Country/Territory']],
                    value='India',
                    style={'width': '100%', 'color': '#333'},
                )
            ], width=6),
            dbc.Col([
                html.Label("Select a Year:", className="text-light"),
                dcc.Slider(
                    id='year-slider',
                    min=min(years),
                    max=max(years),
                    step=1,
                    marks={year: str(year) for year in years},
                    value=max(years),
                )
            ], width=6)
        ], className="mb-4"),
        
        # Map and Graphs
        dbc.Row([
            dbc.Col([dcc.Graph(id='world-map', style={'height': '70vh'})], width=12)
        ]),
        dbc.Row([
            dbc.Col([dcc.Graph(id='population-graph', style={'height': '45vh'})], width=6),
            dbc.Col([dcc.Graph(id='growth-rate-graph', style={'height': '45vh'})], width=6),
        ], className="mt-4"),
        
        # Density Area Graph (Animated)
        dbc.Row([
            dbc.Col([dcc.Graph(id='density-area-graph', style={'height': '45vh'})], width=12),
        ], className="mt-4"),

        # Stats Card
        dbc.Row([
            dbc.Col([
                dbc.Card(
                    dbc.CardBody([
                        html.H4("Statistics Summary", className="card-title text-light"),
                        html.Div(id='stats-output', className="text-light")
                    ]),
                    color="dark"
                )
            ])
        ], className="mt-4"),
    ]
)

@app.callback(
    [Output('population-graph', 'figure'),
     Output('growth-rate-graph', 'figure'),
     Output('world-map', 'figure'),
     Output('density-area-graph', 'figure'),
     Output('stats-output', 'children')],
    [Input('country-dropdown', 'value'),
     Input('year-slider', 'value')]
)
def update_dashboard(selected_country, selected_year):
    # Filter data for the selected country
    country_data = data[data['Country/Territory'] == selected_country]

    # Historical population data
    historical_population = [
        country_data[f'{year} Population'].values[0] for year in years
    ]

    # Population for the selected year
    selected_population = country_data[f'{selected_year} Population'].values[0]

    # Compute growth rates
    growth_rates = [
        ((historical_population[i] - historical_population[i - 1]) / historical_population[i - 1]) * 100
        if i > 0 else 0 for i in range(len(historical_population))
    ]

    # Line graph: Historical population trend
    population_fig = go.Figure()
    population_fig.add_trace(go.Scatter(
        x=years, y=historical_population, mode='lines+markers', name='Population',
        line=dict(color='#FFA500')
    ))
    population_fig.update_layout(
        title=f"Population Trend for {selected_country}",
        xaxis_title="Year",
        yaxis_title="Population",
        template="plotly_dark",
    )

    # Bar graph: Growth rate comparison over years
    growth_rate_fig = go.Figure()
    growth_rate_fig.add_trace(go.Bar(
        x=years, y=growth_rates, name='Growth Rate (%)', marker_color='#00FF00'
    ))
    growth_rate_fig.update_layout(
        title=f"Growth Rate Trend for {selected_country}",
        xaxis_title="Year",
        yaxis_title="Growth Rate (%)",
        template="plotly_dark",
    )

    # Choropleth map: World population
    world_map = px.choropleth(
        data_frame=data,
        locations="CCA3",
        color=f"{selected_year} Population",
        hover_name="Country/Territory",
        title=f"World Population Distribution in {selected_year}",
        template="plotly_dark",
        color_continuous_scale=px.colors.sequential.Plasma
    )
    world_map.update_traces(
        selector=dict(type="choropleth"),
        marker_line_color="white"
    )
    world_map.update_layout(
        margin={"r":0,"t":30,"l":0,"b":0},
    )

    # Calculate Population Density (Population / Area)
    data['Density'] = data[f'{selected_year} Population'] / data['Area (km²)']

    # Animated line graph: Population Density over the years
    density_fig = go.Figure(
        data=[go.Scatter(
            x=data['Country/Territory'],
            y=data[f'{year} Population'] / data['Area (km²)'],
            mode='lines+markers',
            name=str(year),
            visible='legendonly' if year != selected_year else True
        ) for year in years]
    )

    density_fig.update_layout(
        title=f"Population Density for {selected_country}",
        xaxis_title="Country/Territory",
        yaxis_title="Density (per km²)",
        updatemenus=[dict(
            type="buttons",
            showactive=False,
            buttons=[dict(
                label="Play",
                method="animate",
                args=[None, dict(frame=dict(duration=500, redraw=True), fromcurrent=True, mode="immediate")],
            )]
        )],
        template="plotly_dark",
    )

    # Creating frames for animation
    frames = [go.Frame(
        data=[go.Scatter(
            x=data['Country/Territory'],
            y=data[f'{year} Population'] / data['Area (km²)'],
            mode='lines+markers',
            name=str(year),
        )],
        name=str(year)
    ) for year in years]

    density_fig.frames = frames

    # Statistics output
    stats = [
        f"Population in {selected_year}: {selected_population:,}",
        f"Country: {selected_country}"
    ]

    return population_fig, growth_rate_fig, world_map, density_fig, html.Ul([html.Li(stat) for stat in stats])


if __name__ == '__main__':
    app.run_server(debug=True)
