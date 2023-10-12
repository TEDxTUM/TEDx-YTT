from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go
import re


#def clean_label(label):
 #   # Remove special characters using regular expression
  #  if pd.isna(label):
   #     return "Unknown"  # Return a default label for NaN

    #try:
     ##   cleaned_label = re.sub(r'[^\w\s]', '', str(label))
       # return cleaned_label
    #except Exception as e:
     #   print(f"Error cleaning label '{label}': {e}")
      #  return str(label)  # Return the original label as a string




df = pd.read_csv('../all_data.csv', sep=';')
# some pre-processing of the data
# generate unique string (needed for speakers with multiple talks)
df['title_speaker'] = df['Title'].astype(str) + ' - ' + df['Speaker Name'].astype(str)
# convert all date columns to datetime, do it explicitly for Published on, since it uses a format no automatically detected
df['Date'] = pd.to_datetime(df['Date'])
df['Published on'] = pd.to_datetime(df['Published on'], format='ISO8601', errors='coerce')
# catch null values and replace them with placeholder string
df['Speaker Name'].fillna('n/a', inplace=True)

most_recent_df = df.sort_values('Date').drop_duplicates('title_speaker', keep='last')
filtered_df = most_recent_df

app = Dash(__name__)

server = app.server()

all_options = [{'label': 'Title and Speaker Name', 'value': 'title_speaker'},
               {'label': 'Title', 'value': 'Title'},
               {'label': 'Speaker Name', 'value': 'Speaker Name'}]

app.layout = html.Div([
    html.H1('TEDx Video Dashboard'),
    dcc.Dropdown(
        id='selection-dropdown',
        options=all_options,
        value='title_speaker'
    ),
    dcc.Dropdown(
        id='video-checklist',
        options=[{'label': i, 'value': i} for i in df['title_speaker'].unique()],
        value=[],  # now initialized with no videos
        multi=True
    ),
    dcc.Graph(id='youtube-views-stats'),
    dcc.Graph(id='youtube-likes-stats'),
    dcc.Graph(id='youtube-comments-stats'),
    html.H2('Table of Most Recent Data (select year published to filter)'),

    # Dropdown for Year selection
    dcc.Dropdown(
        id='year-dropdown',
        options=[{'label': i, 'value': i} for i in sorted(df['Published on'].dt.year.unique())],
        value=sorted(df['Published on'].dt.year.unique()),  # Initialize with all years
        multi=True  # Enable multi-select
    ),

    dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in  ['Title', 'Speaker Name', 'Views', 'Likes', 'Comment Count']],
        data=filtered_df.to_dict('records'),  # using filtered data
        sort_action='native',
    )
])

@app.callback(
    [Output('youtube-views-stats', 'figure'),
     Output('youtube-likes-stats', 'figure'),
     Output('youtube-comments-stats', 'figure'),
     Output('video-checklist', 'options')],
    [Input('video-checklist', 'value'),
     Input('selection-dropdown', 'value')]
)
def update_graph(selected_checkboxes, selected_option):
    options = [{'label': i, 'value': i} for i in df[selected_option].unique().tolist()]


    if not selected_checkboxes:
        return go.Figure(), go.Figure(), go.Figure(), options

    views_data = []
    likes_data = []
    comments_data = []

    for checkbox_value in selected_checkboxes:
        dff = df[df[selected_option] == checkbox_value]
        dff = dff.sort_values('Date')  # Sort data by Date

        views_data.append(
            go.Scatter(
                x=dff['Date'],
                y=dff['Views'],
                mode='lines',
                name=checkbox_value
            )
        )
        likes_data.append(
            go.Scatter(
                x=dff['Date'],
                y=dff['Likes'],
                mode='lines',
                name=checkbox_value
            )
        )
        comments_data.append(
            go.Scatter(
                x=dff['Date'],
                y=dff['Comment Count'],
                mode='lines',
                name=checkbox_value
            )
        )

    return {"data": views_data,
            "layout": go.Layout(title="Views over time", xaxis={'title': 'Date'}, yaxis={'title': 'Views'})}, \
           {"data": likes_data,
            "layout": go.Layout(title="Likes over time", xaxis={'title': 'Date'}, yaxis={'title': 'Likes'})}, \
           {"data": comments_data,
            "layout": go.Layout(title="Comments over time", xaxis={'title': 'Date'}, yaxis={'title': 'Comments'})}, \
           options

@app.callback(
    Output('table', 'data'),
    [Input('year-dropdown', 'value')]
)
def update_table(selected_years):
    global filtered_df
    # Filter rows where the year is in the list of selected years
    filtered_df = most_recent_df[most_recent_df['Published on'].dt.year.isin(selected_years)]
    return filtered_df.to_dict('records')


if __name__ == '__main__':
    app.run_server(debug=True)