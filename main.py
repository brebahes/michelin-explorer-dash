from dash import Dash, html, dcc, callback, Output, Input, State, ctx
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import dash_bootstrap_components as dbc
import helpers as hl
from geopy.geocoders import Nominatim
import plots as pl

# Used for the search bar
geolocator = Nominatim(user_agent="maps")

# Load the data
df  = hl.load_data()

# Create the app
app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP])

# ------------
# --SIDEBAR---
# ------------

text_input = dbc.InputGroup(
    [
        dbc.Input(placeholder="Search for a location...", type="text", id='location-search'),
        dbc.Button('L', id='geolocation-button', n_clicks=0,color='primary'),
        dbc.Button('Search', id='location-button', n_clicks=0, color="secondary"),
        dcc.Geolocation(id="geolocation"),
    ]
)

michelin_checklist = dbc.Card(
    [
        dbc.CardHeader("Michelin Category"),
        dbc.CardBody(
            [

                dbc.Checklist(
                    options=[
                        {"label": hl.michelin_star_list(3), "value": '3 Stars'},
                        {"label": hl.michelin_star_list(2), "value": '2 Stars'},
                        {"label": hl.michelin_star_list(1), "value": '1 Star'},
                        {"label": hl.bib_gourmand(), "value": 'Bib Gourmand'},
                        {"label": 'SL', "value": 'Selected Restaurants'},
                    ],
                    value=['3 Stars', '2 Stars', '1 Star', 'Bib Gourmand', 'Selected Restaurants'],
                    id="checklist-michelin",
                    inline=True,
                ),
            ]
        )

    ]
)

euro_checklist = dbc.Card(
    [
        dbc.CardHeader("Price point"),
        dbc.CardBody(
            [
                dbc.Checklist(
                    options=[
                        {"label": hl.euro(4), "value": 4},
                        {"label": hl.euro(3), "value": 3},
                        {"label": hl.euro(2), "value": 2},
                        {"label": hl.euro(1), "value": 1},
                    ],
                    value=[4, 3, 2, 1],
                    id="checklist-euro",
                    inline=True,
                ),
            ]
        )

    ]
)

valid_cuisine = list(pd.unique(df.Cuisine.str.split(', ',expand=True).stack()))
cuisine_checklist = dbc.Card(
    [
        dbc.CardHeader("Cuisine Type"),
        dbc.CardBody(
            [
                dcc.Dropdown(
                    valid_cuisine,
                    [],
                    multi=True,
                    id="checklist-cuisine",
                )
            ]
        )
    ]
)

valid_services = list(pd.unique(df.FacilitiesAndServices.str.split(',',expand=True).stack()))
services_checklist = dbc.Card(
    [
        dbc.CardHeader("Facilities & Services"),
        dbc.CardBody(
            [
                dcc.Dropdown(
                    valid_services,
                    [],
                    multi=True,
                    id="checklist-services"
                )
            ]
        )
    ]
)

sidebar =  html.Div(
    [
        text_input,
        html.Hr(),
        michelin_checklist,
        html.Br(),
        euro_checklist,
        html.Br(),
        cuisine_checklist,
        html.Br(),
        services_checklist,
        html.Br()
    ]
)

# ------------
# ---TAB 1 ---
# ------------

settings_popover = html.Div(
    [
        dbc.Button(
            id="popover-target",
            n_clicks=0,
            className="bi bi-gear"
        ),
        dbc.Popover(
            [
                dbc.PopoverHeader("Map Settings"),
                dbc.PopoverBody(
                    dcc.Dropdown(
                        hl.map_styles(),
                        id='map-style'
                    )
                ),
            ],
            style={'width':'500px'},
            target="popover-target",
            trigger="legacy",
        ),
    ]
)

map = html.Div(
    [
        dcc.Graph(figure=pl.map(df,4, (47.6, 2.5), 'basic'), id='graph-content',style={'height': '90%'}),
        settings_popover,

    ], style={'height': '100vh'}
)

# ------------
# ---TAB 2 ---
# ------------

first_card = html.Div(
    [
        dcc.Graph(figure=pl.barplot(df, 10), id='insights-fig-left',style={'height': '90%'})
    ], style={'height': '50vh'}
)

second_card = html.Div(
    [
        dcc.Graph(figure=pl.barplot(df, 10), id='insights-fig-right',style={'height': '90%'})
    ], style={'height': '50vh'}
)

third_card = html.Div(
    [
        dcc.Graph(figure=pl.makeImage(pl.category_wordcloud(df)), id='insights-fig-bottom',style={'height': '90%'})
    ], style={'height': '50vh'}
)

insights = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(first_card, width=6),
                dbc.Col(second_card, width=6),
            ]),
        dbc.Row(
            [
                dbc.Col(third_card, width=12),
            ]),
    ]
)

# ------------
# ----MAIN----
# ------------

main = dbc.Tabs(
    [
            dbc.Tab(map, label="🗺️ Map", activeTabClassName="fw-bold"),
            dbc.Tab(insights, label="🤔 Insights", activeTabClassName="fw-bold"),
    ]
)

# ------------
# ----OTHER---
# ------------

modal = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Title", id='restaurant-title')),
                dbc.ModalBody(id='restaurant-description'),
                dbc.ModalFooter(
                    dbc.Button(
                        "Open Michelin URL",
                        id="restaurant-url-michelin",
                        className="ms-auto",
                        n_clicks=0,
                        href='',
                        target="_blank"
                    )
                ),
            ],
            id="modal-body-scroll",
            scrollable=True,
            is_open=False,
        ),
    ]
)

# ------------
# ---LAYOUT---
# ------------

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(sidebar, width=3, className='bg-light', style={'padding': '25px'}),
                dbc.Col(main, width=9, style={'padding': '25px'}),
                modal,
                dcc.Store(id='filtered-df')
                ],
            style={"height": "100vh"}
            ),
        ],
    fluid=True
    )

# Callback to update the dataframe based on the filters
@callback(
    Output('filtered-df', 'data'),
    Input('checklist-euro', 'value'),
    Input('checklist-michelin', 'value'),
    Input('checklist-cuisine', 'value'),
    Input('checklist-services', 'value'),
    prevent_initial_call=True
)
def filter_df(price, stars, cuisine, services):
    dff = hl.apply_filters(df, price, stars, cuisine, services)
    return dff.to_dict('records')

# TODO: Rethink and add the right-plot
# Callback to update the insights left-plot
@callback(
    Output('insights-fig-left', 'figure'),
    Input('filtered-df', 'data'),
    prevent_initial_call=True
)
def update_insights_figures(data):
    dff = pd.DataFrame(data)
    fig1 = pl.barplot(dff, 10)
    return fig1


# TODO: Separate the location-search on another callback
# Callback to update the scatter map
@callback(
    Output('graph-content', 'figure'),
    Input('filtered-df', 'data'),
    Input('map-style', 'value'),
    Input('location-search', 'value'),
    State('graph-content', 'figure'),
    prevent_initial_call=True
)
def update_graph(data, mapstyle, location_search, fig):
    # Detect what triggered the graph update
    if 'location-search'== ctx.triggered_id: # If it was triggered by the search button
        zoom = hl.zoom_from_location(location_search) * 0.85
        location = geolocator.geocode(location_search)
        fig['layout']['map']['center'] = {"lat": location.latitude, "lon": location.longitude}
        fig['layout']['map']['zoom'] = zoom
        return fig
    elif 'map-style'== ctx.triggered_id: # If it was triggered by the map-style button
        fig = go.Figure(fig)
        fig.update_layout(map_style=mapstyle)
        return fig
    else: # If it was triggered by the filters
        dff = pd.DataFrame(data)
        # Get the current zoom and center of the map
        zoom = fig['layout']['map']['zoom']
        center = (fig['layout']['map']['center']['lat'], fig['layout']['map']['center']['lon'])
        fig = pl.map(dff, zoom, center, mapstyle)
        return fig

@callback(Output("geolocation", "update_now"), Input("geolocation-button", "n_clicks"),
    prevent_initial_call=True)
def update_now(click):
    return True if click and click > 0 else False

# Callback to update the location search value
@callback(
    Output('location-search', 'value'),
    Input('location-button', 'n_clicks'),
    Input("geolocation", "position"),
    State('location-search', 'value'),
    prevent_initial_call=True
)
def update_location(nclicks1, pos, location_search):
    if 'location-button' == ctx.triggered_id:
        location = geolocator.geocode(location_search)
        return location.address
    else:
        location = geolocator.reverse(f'{pos["lat"]}, {pos["lon"]}')
        return location.address

# TODO: Add the webpage of the restaurant and some more details (street, country, etc...)
# Callback to show a modal with the details of the restaurant upon clicking on the map
@app.callback(
    Output("modal-body-scroll", "is_open"),
    Output('restaurant-title', 'children'),
    Output('restaurant-description', 'children'),
    Output("restaurant-url-michelin", 'href'),
    [Input('graph-content', 'clickData')],
    prevent_initial_call=True)
def update_figure(clickData):
    # Get the name of the restaurant that was clicked on
    name = clickData["points"][0]["customdata"][0]
    # Get the entry of the restaurant
    df_name = df.loc[df['Name']==name].iloc[0]
    # Create the title of the modal
    title = html.Span([name + ' '] + hl.michelin_star_list(3) + [' '] + [dbc.Badge(df_name['Price'], pill=True, color='primary', className="me-1")])
    # Create badges for the types of cuisine of the restaurant
    badges_cuisine = html.Span(
        [dbc.Badge(cuisine, pill=True, color='primary', className="me-1") for cuisine in df_name['Cuisine'].split(',')]
    )
    # Create badges for the services of the restaurant
    badges_services = html.Span(
        [dbc.Badge(cuisine, pill=True, color='secondary', className="me-1") for cuisine in df_name['FacilitiesAndServices'].split(',')]
    )
    # Create the modal body, with the description and the badges
    body = [
        badges_cuisine,
        html.Div([html.Br(), df_name['Description']]),
        html.Br(),
        badges_services
    ]
    return True, title, body, df_name['Url']

if __name__ == '__main__':
    # app.run_server(host="0.0.0.0", port="8050")
    app.run(debug=True)