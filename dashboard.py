import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
import sqlite3
import os
from flask import Flask
import socket

class Dashboard:
    def __init__(self, analyzer):
        self.analyzer = analyzer
        # Initialize Dash app with minimal configuration
        self.app = dash.Dash(
            __name__,
            external_stylesheets=[dbc.themes.BOOTSTRAP]
        )
        self.db_path = os.path.join('src', 'default.db')
        
        # Initialize the dashboard layout
        self.app.layout = self._create_layout()
        self._setup_callbacks()

    def _create_layout(self):
        """Create the dashboard layout"""
        return dbc.Container([
            # Navigation bar
            dbc.Navbar(
                dbc.Container([
                    html.A(
                        dbc.Row([
                            dbc.Col(html.I(className="fas fa-chart-line mr-2")),
                            dbc.Col(dbc.NavbarBrand("Real-Time Social Media Analytics", className="ml-2")),
                        ],
                        align="center",
                        className="g-0",
                        ),
                        style={"textDecoration": "none"},
                    )
                ]),
                color="dark",
                dark=True,
                className="mb-4",
            ),

            # Main content
            dbc.Row([
                dbc.Col(html.H1("Social Media Analytics Dashboard", 
                               className="text-center mb-4"))
            ]),

            # Status Row
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-info-circle me-2"),
                            "System Status"
                        ], className="d-flex align-items-center"),
                        dbc.CardBody([
                            html.Div([
                                html.I(className="fas fa-signal me-2"),
                                html.Span("Twitter Stream Status: ", className="fw-bold"),
                                html.Span("Waiting for connection...", id='stream-status')
                            ], className="mb-2"),
                            html.Div([
                                html.I(className="fas fa-clock me-2"),
                                html.Span("Last Updated: ", className="fw-bold"),
                                html.Span("Never", id='last-update-time')
                            ])
                        ])
                    ], className="mb-4 shadow-sm")
                ], width=12),
            ]),

            # Charts Row
            dbc.Row([
                # Sentiment Analysis Card
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-smile me-2"),
                            "Sentiment Analysis"
                        ], className="d-flex align-items-center"),
                        dbc.CardBody([
                            dcc.Graph(id='sentiment-graph'),
                            dcc.Interval(id='sentiment-update', interval=5000)
                        ])
                    ], className="shadow-sm")
                ], width=6),

                # Trending Topics Card
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-fire me-2"),
                            "Trending Topics"
                        ], className="d-flex align-items-center"),
                        dbc.CardBody([
                            dcc.Graph(id='trends-graph'),
                            dcc.Interval(id='trends-update', interval=5000)
                        ])
                    ], className="shadow-sm")
                ], width=6)
            ]),

            # Tweet Volume Row
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-chart-area me-2"),
                            "Tweet Volume"
                        ], className="d-flex align-items-center"),
                        dbc.CardBody([
                            dcc.Graph(id='volume-graph'),
                            dcc.Interval(id='volume-update', interval=10000)
                        ])
                    ], className="shadow-sm mt-4")
                ], width=12)
            ]),

            # Recent Tweets Row
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.I(className="fas fa-list me-2"),
                            "Recent Tweets"
                        ], className="d-flex align-items-center"),
                        dbc.CardBody(id='recent-tweets-table'),
                        dcc.Interval(id='table-update', interval=5000)
                    ], className="shadow-sm mt-4 mb-4")
                ], width=12)
            ]),

            # Footer
            dbc.Row([
                dbc.Col(
                    html.Footer(
                        "Real-Time Social Media Analytics Dashboard © 2025",
                        className="text-center text-muted py-3"
                    ),
                    width=12
                )
            ])
        ], fluid=True)

    def _setup_callbacks(self):
        """Set up all the dashboard callbacks"""
        
        @self.app.callback(
            [Output('stream-status', 'children'),
             Output('last-update-time', 'children')],
            [Input('sentiment-update', 'n_intervals')]
        )
        def update_status(n):
            try:
                conn = sqlite3.connect(self.db_path)
                df = pd.read_sql_query("SELECT COUNT(*) as count FROM tweets", conn)
                conn.close()
                
                if df['count'].iloc[0] > 0:
                    return [
                        "Twitter Stream Status: Connected (Twitter API Error - Using Sample Data)",
                        f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    ]
                else:
                    return [
                        "Twitter Stream Status: Waiting for data...",
                        "Last Updated: Never"
                    ]
            except Exception:
                return [
                    "Twitter Stream Status: Error connecting to database",
                    "Last Updated: Never"
                ]
        
        @self.app.callback(
            Output('sentiment-graph', 'figure'),
            Input('sentiment-update', 'n_intervals')
        )
        def update_sentiment_graph(n):
            try:
                conn = sqlite3.connect(self.db_path)
                df = pd.read_sql_query(
                    """
                    SELECT timestamp, 
                           sentiment->>'polarity' as polarity,
                           sentiment->>'sentiment' as sentiment_label
                    FROM tweets 
                    ORDER BY timestamp DESC 
                    LIMIT 100
                    """, 
                    conn
                )
                conn.close()

                if len(df) == 0:
                    return self._create_empty_figure("No sentiment data available")

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df['timestamp'],
                    y=df['polarity'],
                    mode='lines+markers',
                    name='Sentiment Polarity',
                    marker=dict(
                        color=df['polarity'].apply(
                            lambda x: 'green' if x > 0 else 'red' if x < 0 else 'gray'
                        )
                    )
                ))

                fig.update_layout(
                    title='Sentiment Analysis Over Time',
                    xaxis_title='Time',
                    yaxis_title='Sentiment Polarity',
                    template='plotly_white'
                )

                return fig
            except Exception as e:
                print(f"Error updating sentiment graph: {e}")
                return self._create_empty_figure("Error loading sentiment data")

        @self.app.callback(
            Output('trends-graph', 'figure'),
            Input('trends-update', 'n_intervals')
        )
        def update_trends_graph(n):
            try:
                trends = self.analyzer.trends.most_common(10)
                if not trends:
                    return self._create_empty_figure("No trending topics available")

                df = pd.DataFrame(trends, columns=['Topic', 'Count'])

                fig = px.bar(
                    df,
                    x='Count',
                    y='Topic',
                    orientation='h',
                    title='Top Trending Topics'
                )

                fig.update_layout(
                    template='plotly_white',
                    yaxis={'categoryorder': 'total ascending'}
                )

                return fig
            except Exception as e:
                print(f"Error updating trends graph: {e}")
                return self._create_empty_figure("Error loading trending topics")

        @self.app.callback(
            Output('volume-graph', 'figure'),
            Input('volume-update', 'n_intervals')
        )
        def update_volume_graph(n):
            try:
                conn = sqlite3.connect(self.db_path)
                df = pd.read_sql_query(
                    """
                    SELECT strftime('%Y-%m-%d %H:%M', timestamp) as time_bucket,
                           COUNT(*) as tweet_count
                    FROM tweets
                    GROUP BY time_bucket
                    ORDER BY time_bucket DESC
                    LIMIT 30
                    """,
                    conn
                )
                conn.close()

                if len(df) == 0:
                    return self._create_empty_figure("No tweet volume data available")

                fig = px.line(
                    df,
                    x='time_bucket',
                    y='tweet_count',
                    title='Tweet Volume Over Time'
                )

                fig.update_layout(
                    xaxis_title='Time',
                    yaxis_title='Number of Tweets',
                    template='plotly_white'
                )

                return fig
            except Exception as e:
                print(f"Error updating volume graph: {e}")
                return self._create_empty_figure("Error loading tweet volume data")

        @self.app.callback(
            Output('recent-tweets-table', 'children'),
            Input('table-update', 'n_intervals')
        )
        def update_recent_tweets(n):
            try:
                conn = sqlite3.connect(self.db_path)
                df = pd.read_sql_query(
                    """
                    SELECT text, 
                           user,
                           sentiment->>'sentiment' as sentiment,
                           timestamp
                    FROM tweets
                    ORDER BY timestamp DESC
                    LIMIT 5
                    """,
                    conn
                )
                conn.close()

                if len(df) == 0:
                    return html.Div("No tweets available yet. Waiting for data...", 
                                  className="text-center text-muted my-4")

                return dbc.Table.from_dataframe(
                    df,
                    striped=True,
                    bordered=True,
                    hover=True,
                    responsive=True
                )
            except Exception as e:
                print(f"Error updating recent tweets table: {e}")
                return html.Div("Error loading recent tweets", 
                              className="text-center text-danger my-4")

    def _create_empty_figure(self, message="No data available"):
        """Create an empty figure with a message"""
        return {
            'data': [],
            'layout': {
                'title': message,
                'xaxis': {'visible': False},
                'yaxis': {'visible': False},
                'annotations': [{
                    'text': message,
                    'xref': 'paper',
                    'yref': 'paper',
                    'showarrow': False,
                    'font': {'size': 20}
                }]
            }
        }

    def run(self, debug=True, port=5000, host='0.0.0.0'):
        """Run the dashboard server
        
        Args:
            debug (bool): Whether to run in debug mode
            port (int): Port number to run on
            host (str): Host to bind to
        """
        # Get local IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            ip = s.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
        finally:
            s.close()
        
        print(f"\n*** Dashboard is available at: ***")
        print(f"Local URL: http://localhost:{port}")
        print(f"Network URL: http://{ip}:{port}")
        print(f"All interfaces URL: http://0.0.0.0:{port}\n")
        
        try:
            self.app.run(
                debug=debug,
                port=port,
                host=host
            )
        except Exception as e:
            print(f"Error starting dashboard: {e}") 