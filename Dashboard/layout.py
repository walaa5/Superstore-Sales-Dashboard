import pandas as pd
import plotly.express as px

import dash
from dash import html
from dash import dcc
from dash import Input, Output
import dash_bootstrap_components as dbc

# read dataset
data = pd.read_csv('../Data/train.csv')

# get the year of the date
data['order_year'] = pd.to_datetime(data['Order Date']).dt.year

# get the month of the date
data['order_month'] = pd.to_datetime(data['Order Date']).dt.month

# plot revenue verse year
sales_per_years = data.groupby(['order_year', 'order_month']).sum()

# pie chart for segment per sales
sales_per_segment = data.groupby('Segment').sum()
sales_per_segment.reset_index(inplace=True)

fig_pie_segment = px.pie(sales_per_segment, values='Sales', hole=.7,  width=250, height=200)
# ------------------------------------------------------------------------------------------------------- #
# create the app
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

#fig_2 = px.line(sales_per_year_2015, x='order_month', y='Sales', markers=True)


app.layout = html.Div(
        [
            dbc.Row(
                dbc.Col(
                        html.Div(children=[html.H2("Superstore Sales Dashboard", style={'margin': 'auto 6%'})])
                ),
                align='center',
                style={'height': '4em', 'background': '#ddd'}
            ),

            # ------------------------------------------------------------------------------- #
            dbc.Row(
                [
                    dbc.Col(html.Div("One of three columns"),
                            width={'size': 2, 'offset': 2},
                            style={'border': '1px solid', 'border-radius': '5px', 'height': '6em', 'margin-top': '3%'},
                            ),

                    dbc.Col(html.Div("One of three columns"),
                            width={'size': 2},
                            style={'border': '1px solid', 'border-radius': '5px', 'margin': '3% 0% 0% 5%'}
                            ),
                    dbc.Col(html.Div("One of three columns"),
                            width={'size': 2, 'offset': 1},
                            style={'border': '1px solid', 'border-radius': '5px', 'margin': '3% 0% 0% 5%'}
                            ),
                ],
                style={'margin': '2%'}
            ),

            # ------------------------------------------------------------------------------- #

            dbc.Row(
                [
                    dbc.Col(html.Div(
                        [
                            dcc.Slider(
                                min=data['order_year'].min(),
                                max=data['order_year'].max(),
                                value=data['order_year'].min(),
                                id='year-slider',
                                step=None,
                                marks={int(year): str(year) for year in data['order_year'].unique()},
                                included=False),

                            dcc.Graph(id='sales_year_graph')
                        ]),
                        width={'size': 7},
                        style={'border': '1px solid', 'border-radius': '5px', 'margin': '3% 3% 4% 2%'}
                    ),

                    dbc.Col(html.Div(
                        [
                            dbc.Row(
                            [
                                dbc.Col(html.Div(
                                    [
                                        html.P('Segment'),
                                        dcc.Checklist(list(data['Segment'].unique()),
                                                      list(data['Segment'].unique()[0:1])
                                                      ),
                                    ]
                                    ),
                                    width={'size': 5},
                                ),

                                dbc.Col(html.Div(
                                    [
                                        dcc.Graph(figure=fig_pie_segment, id='pie_segment')
                                    ]
                                ),
                                 width={'size': 6}),
                            ]),

                            dbc.Row(
                                [
                                    dbc.Col(html.Div(
                                        [
                                            html.P('Category'),
                                            dcc.Checklist(list(data['Category'].unique()),
                                                          list(data['Category'].unique()[0:1])
                                                          )
                                        ]
                                    ),
                                        width={'size': 5},
                                    ),

                                    dbc.Col(html.Div(
                                        [
                                            dcc.Graph(figure=fig_pie_segment)
                                        ]
                                    ),
                                        width={'size': 6}),
                                ])

                        ]),
                        width={'size': 3},
                        style={'border': '1px solid', 'border-radius': '5px', 'margin': '3%'}
                    )
                ],
                style={'height': '10em', 'margin': '2%'}
            )
        ]
)


@app.callback(
    Output('sales_year_graph', 'figure'),
    Input('year-slider', 'value')
)
def update_graph(year):
    # sales_per_years = data.groupby(['order_year', 'order_month']).sum()

    sales_per_year = sales_per_years.loc[year]
    sales_per_year.reset_index(inplace=True)

    fig = px.line(sales_per_year, x="order_month", y="Sales", markers=True)
    # fig.update_layout(transition_duration=500)
    # fig.show()

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
