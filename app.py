import pandas as pd
import numpy as np
import plotly.express as px

import dash
from dash import html
from dash import dcc, callback_context
from dash import Input, Output
import dash_bootstrap_components as dbc

# -------------------------------------------------------------------------------------------------------------------------
# read dataset
data = pd.read_csv('../Data/data_complete_with_iso.csv')
print(data.columns)

# get the year of the date
data['Order Date'] = pd.to_datetime(data['Order Date'], infer_datetime_format=True)
data['order_year'] = data['Order Date'].dt.year

# get the month of the date
data['order_month'] = data['Order Date'].dt.month

# plot revenue verse year
#sales_per_years = data.groupby(['order_year', 'order_month']).sum()

# pie chart for segment per sales
sales_per_segment = data.groupby('Segment').sum()
sales_per_segment.reset_index(inplace=True)

# colors pie
colors = ['#645565', '#ceb4b7', '#e2e0eb']
fig_pie_segment = px.pie(sales_per_segment, values='Sales', names='Segment', hole=.6, width=90, height=90,
                         template='presentation',
                         hover_data=['Segment'])

fig_pie_segment.update_traces(marker=dict(colors=colors))
fig_pie_segment.update_layout(margin=dict(l=0, r=20, t=4, b=7))

# pie chart for Cateogory per sales
sales_per_category = data.groupby('Category').sum()
sales_per_category.reset_index(inplace=True)

fig_pie_category = px.pie(sales_per_category, values='Sales', names='Category', hole=.6, width=90, height=90,
                          template='presentation',
                          hover_data=['Category'])

fig_pie_category.update_traces(marker=dict(colors=colors))
fig_pie_category.update_layout(margin=dict(l=0, r=20, t=4, b=7))


# --------------------------------------------------------------------------------------------------------#

# Function For Map Graph


# first get the orderCount and the total sales for each country
def get_country_orders(df):
    country_orders = df.groupby("Country").agg({'Order ID': 'count', 'Sales': 'sum'})
    country_orders.rename(columns={"Order ID": "OrderCount_Per_Country", "Sales": "TotalSales_Per_Country"},
                          inplace=True)
    country_orders["TotalSales_Per_Country"] = np.round(country_orders["TotalSales_Per_Country"])
    return country_orders


# then get the order counte,totalsales,total profit for each Market
def get_market_order(df):
    Markets_Order = df.groupby("Market").agg({'Order ID': 'count', 'Sales': 'sum', 'Profit': 'sum'})
    Markets_Order.rename(columns={"Order ID": "OrderCount_Per_Market", "Sales": "TotalSales_Per_Market",
                                  "Profit": "TotalProfit_Per_Market"}, inplace=True)
    Markets_Order["TotalSales_Per_Market"] = np.round(Markets_Order["TotalSales_Per_Market"])
    Markets_Order["TotalProfit_Per_Market"] = np.round(Markets_Order["TotalProfit_Per_Market"])
    return Markets_Order


# then get the iso_alpha data for each country
def get_iso_market(df):
    country_iso_Market = pd.DataFrame(df.loc[:, ['Country', 'Market', 'iso_alpha']].groupby("Country"),
                                      columns=["Country", "Market"])
    iso_alpha = []
    for index in range(country_iso_Market.shape[0]):
        Market_name = list(country_iso_Market.Market[index]['Market'].unique())[0]
        iso = list(country_iso_Market.Market[index]['iso_alpha'].unique())[0]
        iso_alpha.append(iso)
        country_iso_Market.Market[index] = Market_name
    country_iso_Market['iso_alpha'] = iso_alpha
    return country_iso_Market


# merge all the data
def Create_DataFrame_For_Map(df):
    country_order = get_country_orders(df)
    country_iso = get_iso_market(df)
    market_order = get_market_order(df)

    data1 = country_iso.join(country_order, how='inner', on='Country')
    total_data = data1.merge(market_order, how="left", on="Market")
    return total_data


# draw the map graph for countries
def draw_graph_Map(df):
    data_country_Market = Create_DataFrame_For_Map(df)
    fig = px.scatter_geo(data_country_Market, locations="iso_alpha", color="Market",

                         hover_name="Country",
                         hover_data={"iso_alpha": False, "TotalSales_Per_Country": True,
                                     "OrderCount_Per_Country": True, "TotalSales_Per_Market": True,
                                     "OrderCount_Per_Market": True},
                         size="TotalSales_Per_Country",  # size of markers, "pop" is one of the columns of gapminder
                         size_max=25,
                         width=800,
                         color_discrete_sequence=px.colors.qualitative.G10
                         # color_discrete_sequence=['green']
                         )
    fig.update_layout(legend=dict(
        yanchor="top",
        xanchor="right",
        y=0.98,
        x = 1,
        font=dict(size=10)
    ))
    fig.update_layout(margin=dict(l=2, r=2, t=10, b=7))
    return fig


# -----------------------------------------------------------------------------------------------------#

# Function For Profit Per Market

# use the function for order_Data for Market
# and then plot bar graph for profit

def draw_graph_Market_Profit(df):
    df_Market = get_market_order(df)
    df_Market['Market'] = df_Market.index
    fig = px.bar(df_Market, x='Market', y='TotalProfit_Per_Market',
                 color='TotalProfit_Per_Market', color_continuous_scale="Brwnyl")
    fig.update_xaxes(categoryorder='total descending')
    fig.update_layout(coloraxis_showscale=False)
    fig.update_layout(margin=dict(l=12, r=12, t=10, b=7))

    return fig


# ------------------------------------------------------------------------------------------------------- #
# create the app
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(
    [
        # ------------------------------------------- Header --------------------------------- #

        html.Div
        (
            [
                html.P("Superstore Sales Analysis",
                       style={'margin': '0% 6%', 'color': 'rgb(246 239 239)', 'font-size': '2.3vw',
                              'display': 'inline-block', 'width': '60%'}
                       ),

                html.Div
                (
                    [
                        dcc.Dropdown
                        (
                            list(data['order_year'].value_counts().sort_index().index),
                            value = None,
                            placeholder="Select a Year",
                            id='year-slider',
                            style={'width': '100%',  }
                        ),
                    ],
                    style={'display':'inline-block', 'width':'15%', 'margin':'auto 3vh auto 18vh', 'padding-top':'3vh'}
                )
            ],
            style={'min-height': '12vh', 'background': 'rgb(43 42 62)', 'width': '100%'}
        ),

        # ------------------------------------------- Kpis Pans ------------------------------#
        html.Div
            (
            [

                html.Button
                    (
                    [
                        html.H4('Total Sales', style={'margin': 'auto', 'text-align': 'center', 'font-size':'1.7vw'}),
                        html.P(id='sales_kpi', style={'text-align': 'center', 'font-size': '1.5vw', 'margin':'0vh auto 1vh '})
                    ],
                    n_clicks=0,
                    id='bt_sales',
                    style={'border-bottom': '7px solid rgb(137 186 130)', 'border-radius': '5px',
                           'height': '15vh',
                           'box-shadow': 'rgba(60, 64, 67, 0.3) 0px 1px 2px 0px, rgba(60, 64, 67, 0.15) 0px 2px 6px 2px',
                           'padding': '20px', 'width': '16%', 'margin': '0vh 13vh 0vh 10vh'
                           }
                ),

                html.Button
                    (
                    [
                        html.H4('Total Profits', style={'margin': 'auto', 'text-align': 'center', 'font-size':'1.7vw'}),
                        html.P('470', id='profits_kpi', style={'text-align': 'center', 'font-size': '1.5vw'})
                    ],
                    n_clicks=0,
                    id='bt_profits',
                    style={'border-bottom': '7px solid rgb(212 135 178)', 'border-radius': '5px',
                           'height': '15vh',
                           'box-shadow': 'rgba(60, 64, 67, 0.3) 0px 1px 2px 0px, rgba(60, 64, 67, 0.15) 0px 2px 6px 2px',
                           'padding': '20px', 'width': '16%', 'margin': '0vh 13vh 0vh 3vh'}
                ),

                html.Button
                    (
                    [
                        html.H4('Total Quantity', style={'margin': 'auto', 'text-align': 'center', 'font-size':'1.6vw'}),
                        html.P('470', id='quantity_kpi', style={'text-align': 'center', 'font-size': '1.5vw'})
                    ],
                    n_clicks=0,
                    id='bt_quantity',
                    style={'border-bottom': '7px solid rgb(205 136 72)', 'border-radius': '5px',
                           'height': '15vh',
                           'box-shadow': 'rgba(60, 64, 67, 0.3) 0px 1px 2px 0px, rgba(60, 64, 67, 0.15) 0px 2px 6px 2px',
                           'padding': '20px', 'width': '16%', 'margin': '0vh 13vh 0vh 3vh'}
                ),

                html.Button
                    (
                    [
                        html.H4('Total Discount', style={'margin': 'auto', 'text-align': 'center', 'font-size':'1.6vw'}),
                        html.P('470', id='discount_kpi', style={'text-align': 'center', 'font-size': '1.5vw'})
                    ],
                    n_clicks=0,
                    id='bt_discount',
                    style={'border-bottom': '7px solid rgb(116 156 183)', 'border-radius': '5px',
                           'height': '15vh',
                           'box-shadow': 'rgba(60, 64, 67, 0.3) 0px 1px 2px 0px, rgba(60, 64, 67, 0.15) 0px 2px 6px 2px',
                           'padding': '20px', 'width': '16%', 'margin': '0vh 0vh 0vh 0vh'}
                )
            ],
            style={'display': 'flex', 'flex-direction': 'row', 'flex-wrap': 'wrap', 'justify': 'center',
                   'min-height': '15vh', 'text-align': 'center', 'width': '100%', 'margin': '5% 10% 3% 10%'}
        ),

        # ---------------------------- sales performance with filters ----------------------------- #

        html.Div
        (
            [
                html.Div
                (
                    [
                        html.H3
                            ("Performance of Sales",
                            id='sales_title', style={'margin': '0vh 0vh 0vh 5vh', 'font-size': '1.9vw',
                                                     'color': '#444', 'width': '50%'}
                        ),
                        html.Div
                            (
                            [
                                dcc.Dropdown
                                    (
                                    data['Segment'].unique(),
                                    placeholder="Select a Segment",
                                    id='segment_checklist',
                                    style={'width': '100%', 'height': '7vh', 'font-size': '1vw'}
                                ),
                            ],
                            style={'width': '20%', 'margin-right': '5%'}
                        ),

                        html.Div
                            (
                            [
                                dcc.Dropdown
                                (
                                    data['Category'].unique(),
                                    placeholder="Select a Category",
                                    id='category_checklist',
                                    style={'width': '100%', 'height': '7vh',
                                           }
                                )
                            ],
                            style={'width': '20%'}
                        )
                    ],
                    style={'display': 'flex', 'flex-direction': 'row', 'flex-wrap': 'wrap',
                           'height': '10vh', 'width': '100%'},
                ),

                html.Div
                (
                    [
                        html.Div
                            (
                            [
                                dcc.Graph(id='sales_year_graph', responsive=True)
                            ],
                            style={'border': '1px solid #ddd', 'border-radius': '15px',
                                   'box-shadow': 'rgb(144 143 169) 1px 7px 7px 1px', 'height': '60vh',
                                   'margin': '4vh 1vh 1vh 1vh', 'background-color': 'white', 'overflow': 'hidden'}
                        ),

                    ],
                    style={'display': 'inline-block', 'height':'100%',
                           'width': '60%', 'overflow': 'hidden', 'vertical-align': 'top'}
                ),

                html.Div
                    (
                    [
                        html.Div
                            (
                            [
                                html.P('Segment', style={'margin': '1vh', 'font-size': '1.2vw',
                                                         'text-align': 'center', 'color': '#444'}),

                                html.Div
                                    (
                                    [
                                        html.Div
                                            (
                                            [
                                                dcc.Graph(figure=fig_pie_segment, id='pie_segment',
                                                          responsive=True, style={'height': '100%'})
                                            ],
                                            style={'height': '23vh'}
                                        ),

                                    ],
                                ),
                            ],
                            style={'margin': '2vh', 'border': '1px solid #ddd', 'border-radius': '15px',
                                   'box-shadow': 'rgb(144 143 169) 1px 7px 7px 1px',
                                   'background-color': 'white', 'overflow': 'hidden', 'height':'30vh'}
                        ),

                        html.Div
                            (
                            [
                                html.P('Category', style={'margin': '1vh', 'font-size': '1.2vw',
                                                          'text-align': 'center', 'color': '#444'}),

                                html.Div
                                    ([
                                    html.Div
                                        (
                                        [
                                            dcc.Graph(figure=fig_pie_category, id='pie_category',
                                                      style={'height': '100%'}, responsive=True)
                                        ],
                                        style={'height':'23vh'}
                                    ),

                                ]),
                            ],
                            style={'margin': '2vh', 'border': '1px solid #ddd', 'border-radius': '15px',
                                   'box-shadow': 'rgb(144 143 169) 1px 7px 7px 1px',
                                   'background-color': 'white', 'overflow': 'hidden', 'height': '30vh'}
                        ),

                    ],
                    style={'margin': '0% 0% 0% 2%', 'width': '38%',
                           'display': 'inline-block', 'overflow': 'hidden',
                           'vertical-align': 'top', 'height': '100%'}
                ),
            ],
            style={'margin': '0% 10%', 'position':'relevent',
                   'min-height': '70vh', 'width': '100%'}
        ),

        # --------------------------------- top 10 sub categories and cities ------------------------------- #

        html.Div
            (
            [
                html.H3("OverView to Countries and Market Sales",
                        style={'margin': '0vh 0vh 0vh 5vh', 'font-size': '1.9vw',
                                                  'color': '#444', 'width': '50%'}
                        ),
                html.Div
                (
                    [
                        html.Div(
                            [
                                html.H4(id='my_title_map', style={'margin': '1vh 3vh 1vh'}),
                            ]
                        ),

                        html.Div
                        (
                            [
                                dcc.Graph(id='map_Country_Market', responsive=True , style={'height': '100%'})
                            ],
                            style={'margin': '1vh','vertical-align': 'top'}
                        )
                    ],
                    style={'border': '1px solid white', 'border-radius': '25px', 'background-color': 'white',
                           'box-shadow': 'rgb(144 143 169) 1px 7px 7px 1px', 'height':'90%',
                           'display': 'inline-block', 'width': '60%', 'margin': '5vh 3vh 5vh 1vh', }
                ),

                html.Div
                    (
                    [
                        html.Div(
                            [
                                html.H4(id='my_title_market', style={'margin': '1vh 3vh 1vh'}),
                            ]
                        ),

                        html.Div
                        (
                            [
                                dcc.Graph(id='Map_Market_Profit', responsive=True)
                            ],
                            style={'margin': '1vh 3vh ', 'vertical-align': 'top'}
                        )
                    ],
                    style={'border': '1px solid white', 'border-radius': '25px', 'background-color': 'white',
                           'box-shadow': 'rgb(144 143 169) 1px 7px 7px 1px', 'height':'90%',
                           'display': 'inline-block', 'width': '35%', 'margin': '0% 0% 0% 2%'}
                ),

            ],
            style={'margin': '0% 10%', 'min-height': '70vh', 'width': '100%', 'padding':'10vh 0vh', 'border-top': '1px solid #ddd'}
        )
    ],
    style={'background': '#f6f5f5', 'box-sizing': 'border-box', 'min-height': '100vh', 'width': '100%',
           'display': 'flex', 'flex-wrap': 'wrap'}
)


@app.callback(
    Output('sales_year_graph', 'figure'),
    Output('sales_title', 'children'),

    Input('segment_checklist', 'value'),
    Input('category_checklist', 'value'),
    Input('bt_sales', 'n_clicks'),
    Input('bt_profits', 'n_clicks'),
    Input('bt_quantity', 'n_clicks'),
    Input('bt_discount', 'n_clicks'),
    Input('year-slider', 'value'),
)
def update_graph(segment_options, category_options, bts, btp, btq, btd, year):

    month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'June', 'Jul',
             'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    if year == None:
        filter_data = data

    else:
        year = int(year)
        filter_data = data[data['order_year'] == year]

    # filter data based on segment and category
    if(segment_options == None) and (category_options == None):
        filter_data = filter_data

    elif segment_options == None:
        filter_data = filter_data[filter_data['Category'] == category_options]

    elif category_options == None:
        filter_data = filter_data[filter_data['Segment'] == segment_options]

    else:
        filter_data = filter_data[(filter_data['Segment'] == segment_options) & (filter_data['Category'] == category_options)]


    #print(filter_data.columns)
    filter_data = filter_data.groupby(['order_month']).sum()
    filter_data.reset_index(inplace=True)
    print(filter_data)

    #sales_per_years = data.groupby(['order_year', 'order_month']).sum()
    #sales_per_year = sales_per_years.loc[year]
    #sales_per_year.reset_index(inplace=True)

    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if 'bt_sales' in changed_id:
        y = 'Sales'
        fig = px.line(filter_data, x=month, y=y, markers=True, template='presentation',)
        fig.update_traces(marker_color='rgb(137,186, 130)', line_color='rgb(137,186, 130)')

    elif 'bt_profits' in changed_id:
        y = 'Profit'
        fig = px.line(filter_data, x=month, y=y, markers=True, template='presentation',)
        fig.update_traces(marker_color='rgb(212, 135,178)', line_color='rgb(212, 135,178)')

    elif 'bt_quantity' in changed_id:
        y = 'Quantity'
        fig = px.line(filter_data, x=month, y=y, markers=True, template='presentation',)
        fig.update_traces(marker_color='rgb(205, 136, 72)', line_color='rgb(205 ,136, 72)')
    elif 'bt_discount' in changed_id:
        y = 'Discount'
        fig = px.line(filter_data, x=month, y=y, markers=True, template='presentation',)
        fig.update_traces(marker_color='rgb(116, 156 ,183)', line_color='rgb(116, 156 ,183)')
    else:
        y = 'Sales'
        fig = px.line(filter_data, x=month, y=y, markers=True, template='presentation',)
        fig.update_traces(marker_color='rgb(137,186, 130)', line_color='rgb(137,186, 130)')


    title = 'Performance of {}'.format(y)

    # fig.update_layout(transition_duration=500)
    fig.update_layout(xaxis=dict(showgrid=False, title='Months'),
                      yaxis=dict(showgrid=True))

    #fig.update_traces(marker_color='rgb(144,143,169)', line_color='rgb(144,143,169)')
    # fig.show()

    return fig, title

# ------------------------------------------------------------------------------ #

@app.callback(
    Output('sales_kpi', 'children'),
    Output('profits_kpi', 'children'),
    Output('quantity_kpi', 'children'),
    Output('discount_kpi', 'children'),
    Input('year-slider', 'value'),
    Input('segment_checklist', 'value'),
    Input('category_checklist', 'value')
)
def update_kpi(year, segment_options, category_options):

    if year == None:
        filter_data = data

    else:
        year = int(year)
        filter_data = data[data['order_year'] == year]


    # filter data based on segment and category
    if (segment_options == None) and (category_options == None):
        filter_data = filter_data

    elif segment_options == None:
        filter_data = filter_data[filter_data['Category'] == category_options]

    elif category_options == None:
        filter_data = filter_data[filter_data['Segment'] == segment_options]

    else:
        filter_data = filter_data[
            (filter_data['Segment'] == segment_options) & (filter_data['Category'] == category_options)]

    # group by year and month
    filter_data = filter_data.groupby(['order_month']).sum()
    filter_data.reset_index(inplace=True)

    sales = "${:,}".format(round(filter_data['Sales'].sum()))
    profits = '${:,}'.format(round(filter_data['Profit'].sum()))
    quantity = '{:,}'.format(round(filter_data['Quantity'].sum()))
    discount = '${:,}'.format(round(filter_data['Discount'].sum()))

    return sales, profits, quantity, discount


# ------------------------------------------------------------------ #
@app.callback(
    Output('map_Country_Market', 'figure'),
    Output('my_title_map', 'children'),
    Output('Map_Market_Profit', 'figure'),
    Output('my_title_market', 'children'),
    Input('year-slider', 'value'),
)
def update_graph_screen2(year):
    if year == None:
        title1 = f"Sales Per Country from 2011 to 2014"
        title2 = f"Profit Per Market from 2011 to 2014"

        data_graph = data.copy()
    else:
        year = int(year)
        title1 = f"Sales Per Country in {year} Year"
        title2 = f"Profit Per Market in{year} Year"

        data_graph = data[data['order_year'] == year].copy()

    print(data_graph.columns)
    fig1 = draw_graph_Map(data_graph)
    fig2 = draw_graph_Market_Profit(data_graph)

    return fig1, title1, fig2, title2

if __name__ == '__main__':
    app.run_server(debug=True)
