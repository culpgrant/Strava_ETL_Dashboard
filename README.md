# [Strava_Dashboard](https://strava-grant-culp-plotly.herokuapp.com/)
Building a Strava Dashboard on Flask using Dash. This project involved two major parts of the data pull from the Strava API and the dashboard building using Flask/Dash. Additionally, I created a SQL Database on my local machine to demonstrate SQL skills. Link to [Dashboard](https://strava-grant-culp-plotly.herokuapp.com/) hosted on Heroku.

## Motivation:
I wanted to build a dashboard to help analyze my Strava data and continue to get experience working with APIs. Strava is a fitness app that is a semi-social media app that allows you to track your activities with your friends, it is mainly used for running/biking.

## Data Pull:
The first part of this project was to write the python code to pull the data from the Strava API and write it to a CSV file that I can read in for the dashboard. The data pull currently happens once a month as an AWS Lambda function. It creates a CSV file and Text file on my AWS S3 Bucket for my dashboard to pull the data in from. I only run it once a month with a cron job because I want to save some money :). The function takes less than 15 seconds to run on AWS. I pull the data into a CSV file for all the activities (running, weight lifting, etc...) and a text file that holds data about my account (signup date, etc...). The Strava API takes a little bit to get working in terms of pulling all activities and I would suggest watching the videos on the topic and reading their documentation. This code is located in the Strava_Data_Pull.py file.

## SQL Postgres Database:
The last piece I wanted to involve in the project was to create a SQL database that holds my data from the Strava API. This is not integrated with the dashboard or AWS lambda function but used primarily for practice of ETL Techniques with Python and SQL. Within a corporate environment with a Data Warehouse this SQL table I created would be a perfect stagging area to finally pull into the Data Warehouse. The code can be found in the Jupyter Notebook file called ""
