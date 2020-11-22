import urllib3
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import pandas as pd
import datetime
import plotly.graph_objects as go
import json
import numpy as np
from dash.dependencies import Input, Output, State
from dateutil.relativedelta import relativedelta
from scipy import stats
import boto3
import io

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
pd.options.mode.chained_assignment = None  # default='warn'

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
app.title = 'Strava Dashboard - Grant Culp'

#Reading in the data activites, athlete
ACCESS_KEY_ID = ''
ACCESS_SECRET_KEY = ''
BUCKET_NAME = ''
REGION_NAME = ''
FILE_NAME_act = ""
FILE_NAME_ath = ""
s3_client = boto3.client(
        service_name='s3',
        aws_access_key_id=ACCESS_KEY_ID,
        aws_secret_access_key=ACCESS_SECRET_KEY,
        region_name=REGION_NAME
    )
#activities
obj = s3_client.get_object(Bucket=BUCKET_NAME, Key=FILE_NAME_act)
activities_df = pd.read_csv(io.BytesIO(obj['Body'].read()))
activities_df.sort_values(by=['start_date_local'], ascending=False)
#athlete
athlete_dataset = json.loads(s3_client.get_object(Bucket = BUCKET_NAME, Key = FILE_NAME_ath)['Body'].read())

# # notes
# # number of total koodos/average
# # Do a running cumulative run of total miles run
# # Do a trend of average time per mile
# # Do best mile average trended out over time so its only showing my best time
# # Look to see if there is a drilldown feature in plotly like Power BI
#getting total count of total actitivities
total_count_activities = activities_df['id'].count()
#getting last date of activities
last_date_activity = activities_df['start_date_local'].max().split("T")[0]

#helper functions
def meters_to_miles(dataframe_column):
    dataframe_column = dataframe_column/1609
    dataframe_column = dataframe_column.round(2)
    return dataframe_column
def seconds_frmt_hh_mm_ss(dataframe_column):
    dataframe_column = dataframe_column.apply(lambda x: datetime.timedelta(seconds=x))
    return dataframe_column
def meters_to_km(dataframe_column):
    dataframe_column = dataframe_column/1000
    dataframe_column = dataframe_column.round(2)
    return dataframe_column
def seconds_mins(dataframe_column):
    return (dataframe_column/60).round(2)



#CLEANING THE DATASET
#cleaning up type of workouts
activities_df = activities_df.replace({'type': {'Workout': 'WeightTraining', 'EBikeRide': 'Ride'}})
#add column with just one in it
activities_df['POO'] = 1


#CHART - Activities by Count
#getting my aggregation columns and creating a new dataframe for ease of use
act_type_agg = activities_df.groupby(['type']).agg({'POO': 'sum', 'moving_time': 'mean'})
act_type_agg = act_type_agg.reset_index()
#formating the seconds into hours, mins and seconds
act_type_agg['moving_time_formated'] = act_type_agg['moving_time'].apply(lambda x: datetime.timedelta(seconds =x))
#rounding to the nearest second
act_type_agg['moving_time_formated'] = act_type_agg['moving_time_formated'].dt.round('S')
data_workout_type = go.Bar(
            x=act_type_agg.type, y=act_type_agg.POO,
            text=act_type_agg.POO,
            textposition='auto'
        )
layout_workout_type = go.Layout(
    title = "Count of Activities by Workout Type", title_x=0.5,
    xaxis=dict(
        title='Workout Types'
    ),
    yaxis= dict(
        title = 'Count of Activities'),
)
fig_bar_chart_wktype = go.Figure(data = data_workout_type, layout = layout_workout_type)
fig_bar_chart_wktype.update_layout(xaxis={'categoryorder':'total descending'})

#CHART DISTRIBUTION - Distance
distribution_df = activities_df[['id','type','distance']]
distribution_df = distribution_df.query('type == "Run"')
distribution_df['distance'] = meters_to_miles(distribution_df['distance'])
distribution_df.sort_values(by=["distance"],ascending = True)
data_histogram = go.Histogram(x=distribution_df['distance'], histnorm='probability')
layout_histogram =go.Layout(
    title = "Run Distance Distribution Normalized",title_x=0.5,
    xaxis=dict(
        title='Run Distance (Miles)'
    ),
    yaxis = dict(
        title = "Count of Activities (Normalized)"
    )
)
fig_histogram = go.Figure(data=data_histogram,layout = layout_histogram)

#getting YTD and LYTD - Building KPI Chart
dist_time_trend = activities_df[['id','distance','moving_time','type','start_date_local']]
dist_time_trend = dist_time_trend.query('type =="Run"')
dist_time_trend = dist_time_trend.sort_values(by=["start_date_local"])
dist_time_trend['distance'] = meters_to_miles(dist_time_trend['distance'])
dist_time_trend['moving_time'] = seconds_mins(dist_time_trend['moving_time'])
dist_time_trend['Start_Year'] = pd.DatetimeIndex(dist_time_trend['start_date_local']).year
dist_time_trend['Start_Month'] = pd.DatetimeIndex(dist_time_trend['start_date_local']).month
dist_time_trend['Start_Day'] = pd.DatetimeIndex(dist_time_trend['start_date_local']).day
distance_kpi_df = dist_time_trend[['id','distance','start_date_local','Start_Year','Start_Month',"Start_Day"]]
distance_kpi_df["start_date_local"] = pd.to_datetime(distance_kpi_df["start_date_local"]).dt.tz_localize(None)
year_distance_df = distance_kpi_df.groupby(["Start_Year"]).agg({"distance":"sum"})
year_month_index_df = distance_kpi_df.set_index("start_date_local")
year_month_index_df = year_month_index_df[["distance"]]
year_month_index_df = year_month_index_df.groupby(pd.Grouper(freq = "M")).sum()
year_month_index_df = year_month_index_df.reset_index()
distance_kpi_df = distance_kpi_df.append(pd.DataFrame({'start_date_local': pd.date_range(distance_kpi_df.start_date_local.min(), distance_kpi_df.start_date_local.max())}))
expanding = distance_kpi_df.groupby([
    distance_kpi_df["start_date_local"].dt.month, distance_kpi_df["start_date_local"].dt.day, distance_kpi_df["start_date_local"].dt.year
    ]).distance.sum().unstack(fill_value=0).cumsum()
pd.set_option('display.max_rows', None)
expanding.index.names = ["Month","Day"]
expanding = expanding.reset_index()
today = datetime.date.today()
today_month = today.month
today_day = today.day
today_year = today.year
today_last_year = today_year - 1
#getting ytd number
ytd_running_miles = expanding[["Month","Day",today_year]]
ytd_running_miles = ytd_running_miles[today_year][(ytd_running_miles["Month"] == today_month) &(ytd_running_miles["Day"] == today_day)]
ytd_running_miles = ytd_running_miles.values[0].round(0)
#getting lytd number
lytd_running_miles = expanding[["Month","Day",today_last_year]]
lytd_running_miles = lytd_running_miles[today_last_year][(lytd_running_miles["Month"] == today_month) &(lytd_running_miles["Day"] == today_day)]
lytd_running_miles = lytd_running_miles.values[0].round(0)
#getting total miles ran
total_miles = year_month_index_df['distance'].sum()
total_miles = total_miles.round(0)
#getting yoy rate
yoy_miles = (ytd_running_miles - lytd_running_miles)/lytd_running_miles
yoy_percent_miles = "{:.0%}".format(yoy_miles)
#getting max miles ran in a year
year_distance_df = year_distance_df.reset_index()
max_distance_year = year_distance_df.loc[year_distance_df['distance'].idxmax()]
year_max_miles = int(max_distance_year[0])
max_miles_in_a_year = int(max_distance_year[1])

#Getting Personal Bests


#KPI Figure
kpi_fig = go.Figure(go.Indicator(
    mode = "number+delta",
    value = ytd_running_miles,
    delta = {"reference": lytd_running_miles, "valueformat": ".0f"},
    title = {"text": "Running Miles YTD vs. LYTD"},
    domain = {'y': [0, 1], 'x': [0, 1]}))

kpi_fig.add_trace(go.Scatter(x = year_month_index_df["start_date_local"], y = year_month_index_df["distance"]))
kpi_fig.update_layout(autosize = True)

#Run distance trend line chart
data_trend = go.Scatter(x = year_month_index_df['start_date_local'],
                 y = year_month_index_df['distance'])
layout_trend =go.Layout(
    title = "Running Distance Trend",title_x=0.5,
    xaxis=dict(
        title='Date'
    ),
    yaxis = dict(
        title = 'Run Distance (Miles)'
    )
)
fig_distance_trend = go.Figure(data=data_trend, layout = layout_trend)

#scatter plot of distance vs. time
scatter_df = activities_df[['id','distance','moving_time','type']]
scatter_df = scatter_df.query('type =="Run"')
scatter_df['distance'] = meters_to_miles(scatter_df['distance'])
scatter_df['moving_time'] = seconds_mins(scatter_df['moving_time'])
scatter_df = scatter_df.reset_index()
#need to identify outliers
z = np.abs(stats.zscore(scatter_df[['distance','moving_time']]))
z = np.where(z>3)
z_df = pd.DataFrame(z).transpose()
z_df = z_df.drop(columns= [1])
z_df = z_df.rename(columns = {0:'Index_Merge'})
z_df = z_df.drop_duplicates()
z_df["Outlier"] = "Outlier"
z_df = z_df.set_index('Index_Merge')
merged_df = pd.merge(z_df,scatter_df,right_index = True, left_index = True,how = 'right')

merged_df = merged_df[['index', 'id', 'distance', 'moving_time','type','Outlier']]

data_scatter= go.Scatter(x = merged_df['distance'],
                 y = merged_df['moving_time'],
                 mode = 'markers',
                 text=merged_df['Outlier'])
layout_scatter =go.Layout(
    title = "Run Distance vs. Run Time",title_x=0.5,
    xaxis=dict(
        title='Run Distance (Miles)'
    ),
    yaxis = dict(
        title = "Time of Run (Mins)"
    )
)

scatter_fig = go.Figure(data = data_scatter, layout = layout_scatter)

#Creating function to get my best times at any distance
milestone_best_time_df = activities_df[['id','distance','moving_time','type','start_date_local']]
milestone_best_time_df = milestone_best_time_df.query('type == "Run"')
milestone_best_time_df['distance'] = meters_to_miles(milestone_best_time_df['distance'])
def best_run_time_mile(distance_miles):
    milestone_df = milestone_best_time_df.query('distance >= @distance_miles')
    milestone_df = milestone_df[milestone_df.moving_time == milestone_df.moving_time.min()]
    milestone_df['avg_time_per_mile'] = (milestone_df['moving_time']/ milestone_df['distance'])
    milestone_df['moving_time'] = seconds_frmt_hh_mm_ss(milestone_df['moving_time'])
    milestone_df['avg_time_per_mile'] = seconds_frmt_hh_mm_ss(milestone_df['avg_time_per_mile']).dt.round('S')
    best_time = str(milestone_df.iloc[0]['moving_time'])
    best_time = best_time[7:].strip()
    return best_time
best_5k_time = best_run_time_mile(3.10)
best_10k_time = best_run_time_mile(6.21)
best_half_marathon_time = best_run_time_mile(13.1)
best_marathon_time = best_run_time_mile(26.2)
longest_run = milestone_best_time_df.distance.max()

#getting athlete data saved into variables
city = athlete_dataset["city"]
state = athlete_dataset["state"]
country = athlete_dataset["country"]
sex = athlete_dataset["sex"]
first_name = athlete_dataset["firstname"]
last_name = athlete_dataset["lastname"]
created_at = athlete_dataset["created_at"]
follower_count = athlete_dataset["follower_count"]
friend_count = athlete_dataset["friend_count"]
profile_id = athlete_dataset["id"]
profile_link = f"https://www.strava.com/athletes/{profile_id}"
full_name = first_name + " " + last_name
shoes = athlete_dataset["shoes"]
active_shoes = next(item for item in shoes if item['primary'] is True)
active_shoes_name = active_shoes["name"]
active_shoes_name = " ".join(active_shoes_name.split(" ", 3)[:3])
active_shoes_distance = int(round(((active_shoes["distance"])/1609),0))
created_at = created_at.replace("Z", "")
created_at_dt = datetime.datetime.fromisoformat(created_at).date()
today = datetime.datetime.today().date()
diff_y_m_d = relativedelta(today, created_at_dt)
account_age = f'{diff_y_m_d.years} years {diff_y_m_d.months} months and {diff_y_m_d.days} days'
account_age_days = (today - created_at_dt).days
activities_per_day = (total_count_activities/account_age_days).round(2)

# building the app components - bootstrap

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
app.title = 'Strava Dashboard - Grant Culp'

#navbar
nav_item = dbc.NavItem(dbc.NavLink("Google Maps Heat Map", href="https://www.google.com/webhp?hl=en&gws_rd=ssl"))
drop_down = dbc.DropdownMenu(children=[
    dbc.DropdownMenuItem("LinkedIn", href = "https://www.linkedin.com/in/grantculp/"),
    dbc.DropdownMenuItem("Personal Website", href = "http://grantculp.strikingly.com/"),
    dbc.DropdownMenuItem("Other Projects",href = "http://grantculp.mystrikingly.com/#projects")
], nav=True, in_navbar= True, label = "Links")


navbar = dbc.Navbar(
    dbc.Container(
    [
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(dbc.NavbarBrand(f'Strava - {full_name} - Last Updated: {last_date_activity}', className="ml-2")),
                ],
                align="center",
                no_gutters=True,
            )
        ),
        dbc.NavbarToggler(id="navbar-toggler"),
        dbc.Collapse(dbc.Nav([nav_item, drop_down],className='ml-auto',navbar=True), id="navbar-collapse", navbar=True),
    ],
    ),
    color="dark",
    dark=True,
        className='mb-5'
)

#end of navbar

# App Body

#Cards
athlete_cards = dbc.CardGroup(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Athlete Profile", className="card-title"),
                    html.P(
                        f"{full_name} is a runner in {city}, {state}. "
                        f"MY account is {account_age} old. "
                        f"I have recorded a total of {total_count_activities} activities. "
                        f"That is {activities_per_day} activities per day. "
                        f"I have a follower count of {follower_count}. "
                        ,
                        className="card-text"),
                    dbc.Button(
                        "View Full Strava Profile",
                       href = f"https://www.strava.com/athletes/{profile_id}",
                       target='_blank',
                       style={"background-color":"#fc4c02","outline-stle":"#fc4c02"}
                    ),
                ]
            ),style= {"margin-left":"5px", "margin-right":"5px"}
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Running Miles", className="card-title"),
                    html.P(
                        f"I have {int(total_miles)} amount of total running miles and {int(ytd_running_miles)} amount of miles this year. "
                        f"Last year at this time I had {int(lytd_running_miles)}. "
                        f"That is a YoY rate  of {yoy_percent_miles}. "
                        f"I am currently running in {active_shoes_name} shoe with {active_shoes_distance} miles. "
                        "I also does weight training in addition to running.",
                        className="card-text",
                    ),
                ]
            ),style= {"margin-left":"5px", "margin-right":"5px"}
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Personal Bests:", className="card-title"),
                    html.P(
                        f"The most miles I have ran in a year are {max_miles_in_a_year} miles "
                        f"in the year {year_max_miles}. "
                        f"The fastest 5k I have run is: {best_5k_time}. "
                        f"The fastest 10K I have run is:  {best_10k_time}. "
                        f"The fastest half marathon I have run is: {best_half_marathon_time}. "
                        f"The fastest full marathon I have run is: {best_marathon_time}. "
                        f"The longest run I have is: {longest_run} miles. "
                        ,
                        className="card-text",
                    ),
                ]
            ),style= {"margin-left":"5px", "margin-right":"5px"}
        ),
    ]
)



#Graphs
activity_bar_chart = dcc.Graph(figure=fig_bar_chart_wktype,
                               style={"height":"500px","margin-left":"5px",
                                      "margin-right":"2px","margin-top":"5px",
                                      "box-shadow": "2px 2px 2px lightgrey",
                                      "border-radius":"5px",
                                      "padding":"1px"})
histogram_run_distance = dcc.Graph(figure = fig_histogram,
                                   style={"height": "500px", "margin-left": "2px",
                                          "margin-right": "5px", "margin-top": "5px",
                                          "box-shadow": "2px 2px 2px lightgrey",
                                          "border-radius": "5px",
                                          "padding": "1px"})
kpi_chart = dcc.Graph(figure = kpi_fig,
                      style={"height": "500px", "margin-left": "5px",
                                          "margin-right": "5px",
                                          "box-shadow": "2px 2px 2px lightgrey",
                                          "padding": "1px"})
line_chart_trend = dcc.Graph(figure = fig_distance_trend,
                      style = {"height": "500px", "margin-left": "5px",
                                 "margin-right": "2px","margin-top":"5px",
                                 "box-shadow": "2px 2px 2px lightgrey",
                                 "padding": "1px"})
scatter_chart = dcc.Graph(figure = scatter_fig,
                          style={"height": "500px", "margin-left": "2px",
                                 "margin-right": "5px", "margin-top": "5px",
                                 "box-shadow": "2px 2px 2px lightgrey",
                                 "padding": "1px"}
                          )
#App Layout
row_one = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(athlete_cards, width={"size": 12, "order": "first"}),
                #dbc.Col(kpi_chart, width={"size":8})
            ]
            ),
    ]
)

row_two = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(activity_bar_chart,width={"size": 6, "order":"first"}),
                dbc.Col(histogram_run_distance, width={"size": 6, "order":"second"}),
            ]
        )
    ]
)

row_three = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(line_chart_trend,width={"size": 6, "order":"first"}),
                dbc.Col(scatter_chart,width={"size": 6, "order":"second"})
            ]
        )
    ]
)
row_four = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(" ")
            ]
        )
    ]
)

app.layout =  html.Div([
    navbar,row_one, row_two, row_three,row_four
],style={'backgroundColor':'#f2f2f2'})


#App Callback
# add callback for toggling the collapse on small screens
#navbar
@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

if __name__ == '__main__':
    app.run_server(debug=True)
