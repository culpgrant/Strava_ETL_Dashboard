import requests
import urllib3
import json
import csv
import boto3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
def lambda_handler(event = None, context = None):
    ACCESS_KEY_ID = ''
    ACCESS_SECRET_KEY = ''
    BUCKET_NAME = ''
    REGION_NAME = ''
    FILE_NAME_act = "Strava/activities_df.csv"
    FILE_NAME_ath = "Strava/athlete_dataset.txt"
    s3_client = boto3.client(
            service_name='s3',
            aws_access_key_id=ACCESS_KEY_ID,
            aws_secret_access_key=ACCESS_SECRET_KEY,
            region_name=REGION_NAME
        )

    auth_url = "https://www.strava.com/oauth/token"
    activites_url = "https://www.strava.com/api/v3/activities"

    payload = {
        'client_id': "",
        'client_secret': '',
        'refresh_token': '',
        'grant_type': "",
        'f': ''
    }

    page_number = 1
    temp_list = []
    activities_dataset = []
    while True:
        res = requests.post(auth_url, data=payload, verify=False)
        access_token = res.json()['access_token']
        header = {'Authorization': 'Bearer ' + access_token}
        param = {'per_page': 100, 'page': page_number}
        temp_list = requests.get(activites_url, headers=header, params=param).json()
        for element in temp_list:
            activities_dataset.append(element)
        page_number += 1
        if len(temp_list)==0:
            break
        temp_list.clear()
    keys = activities_dataset[0].keys()
    with open("/tmp/data.csv","w") as file:
        fieldname = ["resource_state","athlete","name","distance","moving_time","elapsed_time","total_elevation_gain",
                     "type","workout_type","id","external_id","upload_id","start_date","start_date_local",
                     "timezone","utc_offset","start_latlng","end_latlng","location_city","location_state",
                     "location_country","start_latitude","start_longitude","achievement_count",
                     "kudos_count","comment_count","athlete_count","photo_count","map","trainer",
                     "commute","manual","private","visibility","flagged","gear_id","from_accepted_tag","upload_id_str",
                     "average_speed","max_speed","has_heartrate","average_heartrate","max_heartrate","heartrate_opt_out",
                     "display_hide_heartrate_option","elev_high","elev_low","pr_count","total_photo_count",
                     "has_kudoed","device_watts","average_cadence"]
        dict_writer = csv.DictWriter(file,fieldnames = fieldname)
        dict_writer.writeheader()
        dict_writer.writerows(activities_dataset)
    with open("/tmp/data.csv","rb") as file:
        s3_client.put_object(Body=file,Bucket = BUCKET_NAME, Key = FILE_NAME_act)

    auth_url = "https://www.strava.com/oauth/token"
    athlete_url = "https://www.strava.com/api/v3/athlete"

    payload = {
        'client_id': "51756",
        'client_secret': 'c9b7b4d7eeab695cba7ccdad4803ad56f92e0e5b',
        'refresh_token': '8efc74fb2a079ec26a8e995373e1df96cb05bbb1',
        'grant_type': "refresh_token",
        'f': 'json'
    }

    res = requests.post(auth_url, data=payload, verify=False)
    access_token = res.json()['access_token']

    header = {'Authorization': 'Bearer ' + access_token}
    param = {'per_page': 10, 'page': 1}
    athlete_dataset = requests.get(athlete_url, headers=header, params=param).json()
    athlete_dataset = json.dumps(athlete_dataset)

    s3_client.put_object(Body=athlete_dataset, Bucket=BUCKET_NAME, Key=FILE_NAME_ath)
    return "Success"
