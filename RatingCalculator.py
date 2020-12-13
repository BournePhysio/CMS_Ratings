import json
import csv
import gspread
from oauth2client.service_account import ServiceAccountCredentials

import numpy
from json import JSONEncoder


def add_racer(driver, result):
    pass


def main(arg):
    # key variables
    lap_time_zero = 1.10

    # first load in the Rating Files
    ratings_file = open('RatingData.json', 'rb')
    ratings_file_stringify = ratings_file.read()

    events_file = open('events.json', 'rb')
    events_file_stringify = events_file.read()

    ratings_json = json.loads(ratings_file_stringify, strict=False)
    events_json = json.loads(events_file_stringify, strict=False)
    # load in data files currently using temp file
    results_file = open(arg[0], 'rb')
    results_file_stringify = results_file.read()

    results_json = json.loads(results_file_stringify, strict=False)
    events_file.close()
    results_file.close()
    ratings_file.close()

    # rating_event = results_json[0]["race_id"]
    # check if the event is already in events_json and if not, add it
    for f in results_json:
        first_key = f
        break

    if not any(d.get('race_id', 'blue') == results_json[first_key]['race_id'] for d in events_json["events"]):
        event = {}
        event["race_id"] = results_json[first_key]["race_id"]
        event["race_type"] = results_json[first_key]["race_type"]
        event["track"] = results_json[first_key]["track_name"]
        event["rating"] = True
        if results_json[first_key]["gt3"] == "GT3":
            event["GT3Best"] = results_json[first_key]["average_ten"]
            event["GT4Best"] = 5000
        else:
            event["GT4Best"] = results_json[first_key]["average_ten"]
            event["GT3Best"] = 5000
        events_json["events"].append(event)

    # get the event key
    iteration = 0
    while iteration < len(events_json['events']):
        if events_json['events'][iteration]['race_id'] == results_json[first_key]['race_id']:
            event_key_index = iteration
        iteration += 1

    # get best GT4 and GT3 times
    gt3_best = events_json["events"][event_key_index]['GT3Best']
    gt4_best = events_json["events"][event_key_index]['GT4Best']
    # Cycle through drivers to populate best times
    for driver in results_json:
        if results_json[driver]["gt3"] == "GT3":
            if results_json[driver]["average_ten"] < gt3_best:
                gt3_best = results_json[driver]["average_ten"]
        if results_json[driver]["gt3"] == "GT4":
            if results_json[driver]["average_ten"] < gt4_best:
                gt4_best = results_json[driver]["average_ten"]
    events_json["events"][event_key_index]['GT3Best'] = gt3_best
    events_json["events"][event_key_index]['GT4Best'] = gt4_best

    # Cycle through drivers to see if already in Rating Data, if not, add
    for driver in results_json:
        steam_id = results_json[driver]['steam_id']
        if not any(d.get('steam_id', 'blue') == results_json[driver]['steam_id'] for d in ratings_json['Racers']):
            racer_to_add = {}
            racer_to_add["name"] = results_json[driver]["name"]
            racer_to_add["steam_id"] = results_json[driver]["steam_id"]
            racer_to_add["events"] = {}
            event_to_add = {}
            event_to_add["race_id"] = results_json[driver]["race_id"]
            event_to_add["model"] = results_json[driver]["model"]
            event_to_add["average_ten"] = results_json[driver]["average_ten"]
            event_to_add["laps_std"] = results_json[driver]["laps_std"]
            event_to_add["gt3"] = results_json[driver]["gt3"]
            event_to_add["race_type"] = results_json[driver]["race_type"]
            racer_to_add["events"] = []
            racer_to_add['events'].append(event_to_add)
            ratings_json["Racers"].append(racer_to_add)

        else:
            # if they do exist, check for the event if it isn't there, add it
            # first need to find the correct ratings_json record
            iteration = 0
            while iteration < len(ratings_json['Racers']):
                if ratings_json['Racers'][iteration]['steam_id'] == steam_id:
                    if not any(d.get('race_id', 'blue') == results_json[driver]['race_id'] for d in
                               ratings_json['Racers'][iteration]['events']):
                        event_to_add = {}
                        event_to_add["race_id"] = results_json[driver]["race_id"]
                        event_to_add["model"] = results_json[driver]["model"]
                        event_to_add["average_ten"] = results_json[driver]["average_ten"]
                        event_to_add["laps_std"] = results_json[driver]["laps_std"]
                        event_to_add["gt3"] = results_json[driver]["gt3"]
                        event_to_add["race_type"] = results_json[driver]["race_type"]
                        ratings_json['Racers'][iteration]['events'].append(event_to_add)
                    else:
                        # if the event exists update the average_ten and laps_stdev
                        y = 0
                        while y < len(ratings_json['Racers'][iteration]['events']):
                            if ratings_json['Racers'][iteration]['events'][y]['race_id'] == results_json[driver]['race_id']:
                                if results_json[driver]["average_ten"] < ratings_json['Racers'][iteration]['events'][y][
                                        'average_ten']:
                                    ratings_json['Racers'][iteration]['events'][y]['average_ten'] = results_json[driver][
                                        "average_ten"]
                                    ratings_json['Racers'][iteration]['events'][y]['laps_std'] = results_json[driver][
                                        "laps_std"]
                            y += 1
                iteration += 1

    # Then calculate and add the driver ratings
    for driver in results_json:
        if results_json[driver]["gt3"] == "GT3":
            best_time = gt3_best
        else:
            best_time = gt4_best
        time = results_json[driver]["average_ten"]
        rating = (1 - (time - best_time) / ((best_time * lap_time_zero) - best_time)) * 100
        if time > best_time * lap_time_zero:
            rating = 0
        if rating < 0:
            rating = 0
        iteration = 0
        # search for the correct ratings_json record and update the ranking
        while iteration < len(ratings_json['Racers']):
            if ratings_json['Racers'][iteration]['steam_id'] == results_json[driver]['steam_id']:
                y = 0
                while y < len(ratings_json['Racers'][iteration]['events']):
                    if ratings_json['Racers'][iteration]['events'][y]['race_id'] == results_json[driver]['race_id']:
                        ratings_json['Racers'][iteration]['events'][y]['rating'] = rating
                    y += 1
            iteration += 1
    events_json["events"][event_key_index]['GT3Best'] = gt3_best
    events_json["events"][event_key_index]['GT4Best'] = gt4_best

    # cycle through all events to recalculate overall ratings
    racer = 0
    while racer < len(ratings_json['Racers']):
        event_num = 0
        ratings_list = [sub['rating'] for sub in ratings_json['Racers'][racer]['events']]
        # while event_num < len(ratings_json['Racers'][racer]['events']):
        #     for event in events_json['events']:
        #         if event['race_id'] == ratings_json['Racers'][racer]['events'][event_num]['race_id']:
        #             if ratings_json['Racers'][racer]['events'][event_num]['gt3'] == 'GT3':
        #                 best_time = event['GT3Best']
        #             else:
        #                 best_time = event['GT4Best']
        #         if event['rating']:
        #             time = ratings_json['Racers'][racer]['events'][event_num]['average_ten']
        #             rating = (1 + (best_time - time) / ((best_time * lap_time_zero) - time)) * 100
        #             if time > best_time * lap_time_zero:
        #                 rating = 0
        #             if rating < 0:
        #                 rating = 0
        #             ratings_list.append(rating)
        #     event_num += 1
        ratings_json['Racers'][racer]['rating'] = sum(ratings_list) / len(ratings_list)
        # print(ratings_list, ratings_json['Racers'][racer]['rating'])
        racer += 1

    with open('RatingData.json', 'w') as f:
        json.dump(ratings_json, f, indent=2)

    with open('events.json', 'w') as g:
        json.dump(events_json, g, indent=2)

    with open('RatingData.csv', 'w', newline='') as f: # todo ordering needs to be the same in events and rating_data
        writer = csv.writer(f, quoting=csv.QUOTE_NONE)
        # create a csv file for ratings, first columns to be populated by events_json
        csv_row0 = [' ', "Race ID"]
        csv_row1 = [' ', 'Track']
        csv_row2 = [' ', 'Race Type']
        csv_row3 = ['Name', 'Overall Rating']
        event_num = 0
        while event_num < len(events_json['events']):
            csv_row0_add = [events_json['events'][event_num]['race_id'], ' ', ' ', ' ']
            csv_row0 = csv_row0 + csv_row0_add
            csv_row1_add = [events_json['events'][event_num]['track'], ' ', ' ', ' ']
            csv_row1 = csv_row1 + csv_row1_add
            csv_row2_add = [events_json['events'][event_num]['race_type'], ' ', ' ', ' ']
            csv_row2 = csv_row2 + csv_row2_add
            csv_row3_add = ['Rating', 'Class', 'Average Lap', 'Standard Deviation']
            csv_row3 = csv_row3 + csv_row3_add
            event_num += 1
        writer.writerow(csv_row0)
        writer.writerow(csv_row1)
        writer.writerow(csv_row2)
        writer.writerow(csv_row3)
        ratings_json['Racers'] = sorted(ratings_json['Racers'], key=lambda i: i['rating'], reverse=True)
        racer = 0
        while racer < len(ratings_json['Racers']):
            event_num = 0
            csv_rows = []
            csv_rows.append(ratings_json['Racers'][racer]['name'])
            csv_rows.append(ratings_json['Racers'][racer]['rating'])
            for event in events_json['events']:
                if not any(
                        d.get('race_id', 'blue') == event['race_id'] for d in ratings_json['Racers'][racer]['events']):
                    csv_rows.append(' ')
                    csv_rows.append(' ')
                    csv_rows.append(' ')
                    csv_rows.append(' ')
                else:
                    racer_event = next(item for item in ratings_json['Racers'][racer]['events'] if item["race_id"]
                                       == event['race_id'])
                    csv_rows.append(racer_event['rating'])
                    csv_rows.append(racer_event['gt3'])
                    csv_rows.append(racer_event['average_ten'])
                    csv_rows.append(racer_event['laps_std'])
                event_num += 1
            writer.writerow(csv_rows)
            racer += 1
    # write output to google sheets
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

    credentials = ServiceAccountCredentials.from_json_keyfile_name('cms-ratings-fdc4bc99d823.json', scope)
    client = gspread.authorize(credentials)

    spreadsheet = client.open('CMSRatings')

    with open('RatingData.csv', 'r') as file_obj:
        content = file_obj.read()
        client.import_csv(spreadsheet.id, data=content)


if __name__ == '__main__':
    main('event_results_ID002.json')
