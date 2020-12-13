import json
import csv
import numpy as np
import pandas as pd
from json import JSONEncoder

CAR_MODEL_TYPES = {
    0: 'Porsche 911 (991) GT3 R',
    1: 'Mercedes-AMG GT3',
    2: 'Ferrari 488 GT3',
    3: 'Audi R8 LMS',
    4: 'Lamborghini Huracán GT3',
    5: 'McLaren 650S GT3',
    6: 'Nissan GT-R Nismo GT3 (2018)',
    7: 'BMW M6 GT3',
    8: 'Bentley Continental GT3 (2018)',
    9: 'Porsche 911.2 GT3 Cup',
    10: 'Nissan GT-R Nismo GT3 (2017)',
    11: 'Bentley Continental GT3 (2016)',
    12: 'Aston Martin Racing V12 Vantage GT3',
    13: 'Lamborghini Gallardo R-EX',
    14: 'Jaguar G3',
    15: 'Lexus RC F GT3',
    16: 'Lamborghini Huracan Evo (2019)',
    17: 'Honda/Acura NSX GT3',
    18: 'Lamborghini Huracán Super Trofeo (2015)',
    19: 'Audi R8 LMS Evo (2019)',
    20: 'AMR V8 Vantage (2019)',
    21: 'Honda NSX Evo (2019)',
    22: 'McLaren 720S GT3 (Special)',
    23: 'Porsche 911 II GT3 R (2019)',
    50: 'Alpine A110 GT4',
    51: 'Aston Martin Vantage GT4',
    52: 'Audi R8 LMS GT4',
    53: 'BMW M4 GT4',
    55: 'Chevrolet Camaro GT4',
    56: 'Ginetta G55 GT4',
    57: 'KTM X-Bow GT4',
    58: 'Maserati MC GT4',
    59: 'McLaren 570S GT4',
    60: 'Mercedes AMG GT4',
    61: 'Porsche 718 Cayman GT4'
}


class Driver:
    def __init__(self, driver_index, car_data):
        self.index = driver_index
        self.model = CAR_MODEL_TYPES.get(car_data['car']["carModel"])
        self.name = car_data['car']['drivers'][driver_index]['firstName'] + ' ' + \
            car_data['car']['drivers'][driver_index]['lastName']
        self.steam_id = car_data['car']['drivers'][driver_index]['playerId']
        self.car_lap_total = car_data['timing']['lapCount']
        self.car_id = car_data['car']['carId']
        self.laps = []
        self.lap_times = {}
        self.average_ten = None
        self.laps_std = None
        self.track_name = None
        self.gt3 = "GT4"


class DriverEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


class Event:
    def __init__(self, event_data):
        self.session_type = event_data["sessionType"]
        self.track_name = event_data["trackName"]
        self.race_index = event_data["raceWeekendIndex"]
        self.event_id = None
        self.race_type = None


def add_laps(drivers, laps):
    for lap in laps:
        if lap['isValidForBest']:
            driver = drivers[str(lap['carId']) + ':' + str(lap['driverIndex'])]
            driver.laps.append(lap['laptime'])


def create_driver_dict(leader_board_lines, results_json, event_id, race_type) -> dict:
    drivers = {}
    for leader_board_line in leader_board_lines:
        for i in range(0, len(leader_board_line['car']['drivers'])):
            driver = Driver(i, leader_board_line)
            if "GT4" not in driver.model:
                driver.gt3 = "GT3"
            driver.race_id = event_id
            driver.race_type = race_type
            driver.track_name = results_json["trackName"]
            drivers[str(driver.car_id) + ':' + str(driver.index)] = driver
    return drivers


def main(argv):
    race_id = argv[3]
    race_type = argv[2]
    # main version
    # file_name = argv[0] + '//' + argv[1]
    # debug version
    file_name = argv[1]
    # first load in the files
    results_file = open(file_name, 'rb')
    # parse it
    results_file_stringify = results_file.read()
    results_file.close()
    results_json = json.loads(results_file_stringify, strict=False)
    if results_json['sessionType'] == 'R2':
        race_id = race_id + 'R2'
    leader_board_lines = results_json["sessionResult"]["leaderBoardLines"]
    laps = results_json["laps"]
    drivers = create_driver_dict(leader_board_lines, results_json, race_id, race_type)
    add_laps(drivers, laps)
    # bad_laps = [d for d in laps if d['isValidForBest'] == False]
    # print(len(bad_laps))

    # now for each driver (who has proper lap times) we need to sort ascending and filter any with fewer than 10 laps
    drivers_to_pop = []
    for driver_key in drivers:
        driver = drivers.get(driver_key)
        if len(driver.laps) < 10:
            drivers_to_pop.append(str(driver.car_id) + ':' + str(driver.index))
        else:
            driver.laps.sort()
            del driver.laps[10:]
            driver.laps = list(map(float, driver.laps))
            driver.average_ten = sum(driver.laps)/10000
            driver.laps_std = np.std(driver.laps)/1000
            if driver.laps_std > 10:
                drivers_to_pop.append(str(driver.car_id) + ':' + str(driver.index))
            print(driver.laps_std)


# pop, lock drop (this is the actual removal)
    for popper in drivers_to_pop:
        drivers.pop(popper)

    # and then we write to a csv, I can do this later
    results_file_csv = ''.join([argv[1], "event_results_ID", str(race_id),".csv"])
    results_file_json = ''.join([argv[1], "event_results_ID", str(race_id),".json"])
    with open(results_file_csv, 'a', newline='') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_NONE)
        for driver_key in drivers:
            driver = drivers.get(driver_key)
            csv_row = [str(driver.name), driver.steam_id, driver.track_name, driver.gt3, driver.car_lap_total,
                       driver.average_ten]
            csv_row = csv_row + driver.laps
            writer.writerow(csv_row)

    with open(results_file_json, 'a') as f:
        json.dump(drivers, f, indent=2, cls=DriverEncoder)

    # df = pd.DataFrame(results_json)


if __name__ == '__main__':
   main(["", "201026_213001_R1.json", "sprint", "002"])
