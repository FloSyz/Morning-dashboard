# CS50 Final project: Morning dashboard with Siri

from google.transit import gtfs_realtime_pb2
import requests
from protobuf_to_dict import protobuf_to_dict
import json
from datetime import date, timedelta, datetime
from flask import Flask, jsonify
import re

app = Flask(__name__)

def get_data(topic):

    # Definition of URL's to be used to get the data from various websites/API's
    # Note: these URL's are not used in the published project because of private API keys included. Hardcoded data in json files are used instead

    # url_train = "xxx"
    # url_weather = "xxx"
    # url_maps = "xxx"

    # Get request
    match topic:
        case "t":

            # ----- Code to be used only with real URL's ------

            # response = requests.get(url_train)

            # # Creation of the object feed, call of the get_data function and convertion to dictionnary
            # feed = gtfs_realtime_pb2.FeedMessage()
            # feed.ParseFromString(response.content)

            # # Print feed in a json file
            # dict_feed = protobuf_to_dict(feed)
            # with open('train2.json', 'w') as convert_file:
            #     convert_file.write(json.dumps(dict_feed,indent=2))

            # ----------------------------------------------------

            with open("train.json") as file:
                response = json.load(file)

        case "m":

            # ----- Code to be used only with real URL's ------

            # response = requests.get(url_maps)

            # # Print answer in a txt file
            # with open('maps.json', 'w') as convert_file:
            #     convert_file.write(json.dumps(response,indent=2))

            # ----------------------------------------------------

            with open("maps.json") as file:
                response = json.load(file)

        case "w":

            # ----- Code to be used only with real URL's ------

            # response = requests.get(url_weather)

            # # Print answer in a txt file
            # with open('weather.json', 'w') as convert_file:
            #     convert_file.write(json.dumps(response,indent=2))

            # ----------------------------------------------------

            with open("weather.json") as file:
                response = json.load(file)

    return response

@app.route('/train')
def train():

    # ID's of station stops of the train relevant for this application
    stops = {
    "8811007" : "Schaerbeek",
    "8821907" : "Turnhout",
    "8883006" : "Braine-Le-Comte",
    "8814308" : "Halle"
    }

    # Date of today for further comparison (to be used in code with real URL)
    # dateNow = datetime.now()

    # Fake date in the range of the example data (used for the published code)
    dateNow = datetime.fromtimestamp(1702272900)

    # Creation of the object feed, call of the get_data function and convertion to dictionnary
    # feed = gtfs_realtime_pb2.FeedMessage()
    # feed.ParseFromString(get_data("t").content)

    dict_train = get_data("t")

    # Base string, to be completed with data
    string = f"Les prochains trains pour Schaerbeek sont:\n"

    # Search for preferred destinations (included in stops) - in the dictionnary, entity is a list, so we take its length
    length_entity =  len(dict_train["entity"])
    for i in range(length_entity):

        trip_id = dict_train["entity"][i]["trip_update"]["trip"]["trip_id"]

        # Search for preferred stops (=keys) in the dictionnary
        for k in stops.keys():

            # Regex expression to be searched in the trip_id
            if matches := re.search(r".+[0-9]:("+ k +"):.+", trip_id):

                # Search for stop(s) in Ecaussinnes (stop_id = 8883212)
                stop_times_list = len(dict_train["entity"][i]["trip_update"]["stop_time_update"])
                for j in range(stop_times_list):
                    stop_id = dict_train["entity"][i]["trip_update"]["stop_time_update"][j]["stop_id"]

                    if  stop_id == "8883212":
                        stop_times = dict_train["entity"][i]["trip_update"]["stop_time_update"][j]

                        # Explore the list and store relevant data into variables
                        destination = stops[matches.group(1)]
                        departure = datetime.fromtimestamp(stop_times["departure"]["time"])
                        delay = int(int(stop_times["departure"]["delay"])/60)
                        timedelta = departure - dateNow
                        delta = int(timedelta.total_seconds()/60)

                        # Construction of the string to be read by Siri (take only trains foreseen in time interval)
                        if 2 < (timedelta.total_seconds()/60) < 100:
                            string += f"à {str(departure.hour)} heure {str(departure.minute)}, dans {delta} minute vers {destination} avec un retard probable de {delay} minute,\n"

    string = string[:-2] + "."
    return string

@app.route('/maps')
def maps():
    # Call of the get_data function and convert to dictionnary
    dict_maps = get_data("m")

    # Explore the dictionnary and store relevant data into variables
    distance = dict_maps["resourceSets"][0]["resources"][0]["travelDistance"]
    congestion = dict_maps["resourceSets"][0]["resources"][0]["trafficCongestion"]
    time = dict_maps["resourceSets"][0]["resources"][0]["travelDurationTraffic"]

    # Translation of English to French for congestion
    match congestion:
        case "None":
            traffic = "fluide"
        case _:
            traffic = "non identifié"

    # Construction of the string to be read by Siri
    string = (f'Trajet Ecaussinnes Schaerbeek en voiture:\n'
                f'Distance: {int(distance)} km.\n'
                f'Traffic: {traffic}.\n'
                f'Temps de route actuellement: {int(time/60)} minute'
                )
    return string


@app.route('/weather')
def weather():
    # Call of the get_data function and convert to dictionnary format
    dict_weather = get_data("w")

    # Explore the dictionnary and store relevant data into variables
    description = dict_weather["weather"][0]["description"]
    temp_min = dict_weather["main"]["temp_min"]
    temp_max = dict_weather["main"]["temp_max"]
    humidity = dict_weather["main"]["humidity"]
    wind = int(dict_weather["wind"]["speed"]/1000*3600)

    # Construction of the string to be read by Siri
    string = (f'Meteo a Ecaussinnes:\n'
               f'{description}.\n'
               f'Les temperatures sont comprises entre {int(temp_min)} et {int(temp_max)} degres.\n'
               f'Le taux d\'hygrometrie est de {humidity} pourcent.\n'
               f'Le vent a une vitesse moyenne de {wind} kilometre par heure.')

    # Rain information is not always present in data, so we take it if present and we pass if not
    try:
        rain = f'\nIl a plu {dict_weather["rain"]["speed"]} mm sur la dernière heure.\n'
        string += rain
    except KeyError:
        pass

    return string

def main():
    app.run(host='0.0.0.0', port=8000, use_reloader=True)
    # print(train())
    # print(weather())
    # print(maps())

if __name__ == '__main__':
    main()