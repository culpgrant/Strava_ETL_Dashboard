# Strava ETL and Dashboard
Building an ETL out of Strava API and a dashboard on Flask using Dash. This project involved two major parts of the data pull from the Strava API and the dashboard building using Flask/Dash. Additionally, I created a SQL Database on my local machine to demonstrate SQL skills. Link to [Dashboard](https://strava-grant-culp-plotly.herokuapp.com/) hosted on Heroku. Strava is a workout app you can download on your phone to track your running and other activities

## Tools:
AWS(Lambda, S3), Python (Pandas, Dash/Plotly, Requests), SQL (Postgres)

## Motivation:
I wanted to build a dashboard to help analyze my Strava data and continue to get experience working with APIs. Strava is a fitness app that is a semi-social media app that allows you to track your activities with your friends, it is mainly used for running/biking.

## Extracting Strava Data:
The first part of this project was to write the python code to pull the data from the Strava API and write it to a CSV file that I can read in for the dashboard. The data pull currently happens once a month as an AWS Lambda function. It creates a CSV file and Text file on my AWS S3 Bucket for my dashboard to pull the data in from. I only run it once a month with a cron job because I want to save some money :). The function takes less than 15 seconds to run on AWS. I pull the data into a CSV file for all the activities (running, weight lifting, etc...) and a text file that holds data about my account (signup date, etc...). The Strava API takes a little bit to get working in terms of pulling all activities and I would suggest watching the videos on the topic and reading their documentation. This code is located in the [Extracting_Strava_Data.py file](https://github.com/culpgrant/Strava_Dashboard/blob/main/Extracting_Strava_Data.py).

## Load: SQL Postgres Database:
The second piece I wanted to involve in the project was to create a SQL database that holds my data from the Strava API. The dashboard does not use the data from the Postgres SQL database. This databse was primarily created for practice the of ETL Techniques with Python and SQL. Within a corporate environment, with a Data Warehouse, this SQL table I created would be a perfect stagging area to finally pull into the Data Warehouse. The code can be found in the Jupyter Notebook file called ["Creating_Postgres_Database"](https://github.com/culpgrant/Strava_Dashboard/blob/main/Creating_Postgres_Database.ipynb).

## Dashboard/Analyzing Strava Data:
The last piece of this project was to create a [dasboard](https://strava-grant-culp-plotly.herokuapp.com/) that I can access at anytime. I decided to use Ploty/Dash to buld a dashboard using all python and host it on the free service Heroku. You can see I host a lot of my websites/dashboards on Heroku, its a great service to use.
There is a lot you can do with this data but this basic dashboard gives me a lot of insights and a great website to check every couple weeks to see how I am trending with my running distance.

