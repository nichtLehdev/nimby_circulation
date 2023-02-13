import http.client
import time
from datetime import date
from main import Run, Stop, Station, loadStations
from config import getClientID, getClientSecret
import xmltodict
import pandas as pd
from datetime import date as datetime
import os
import xml.etree.ElementTree as ET

conn = http.client.HTTPSConnection("apis.deutschebahn.com")

headers = {
    'DB-Client-Id': getClientID(),
    'DB-Api-Key': getClientSecret(),
    'accept': "application/xml"
}


def getStationData(eva, cw, year, ds100):
    print("Getting data for station " + ds100 + "...")
    for day in range(1, 7+1):
        date = datetime.fromisocalendar(year, cw, day)
        year = date.year
        month = date.month
        day = date.day
        datestr = "{:02d}".format(
            year)[-2:]+"{:02d}".format(month)+"{:02d}".format(day)

        frames = []
        frames.append(pd.DataFrame(columns=["train", "type", "number", "flag", "origin", "destination",  "ar_hrs",
                                   "ar_min", "dp_hrs", "dp_min", "platform", "next_station", "prev_station"]))

        for hrs in range(0, 23+1):
            url = "/db-api-marketplace/apis/timetables/v1/plan/" + \
                str(eva)+"/"+str(datestr)+"/"+str("{:02d}".format(hrs))
            conn.request(
                "GET", url, headers=headers)
            res = conn.getresponse()
            data = res.read()
            print(url)
            exit()
            if (len(data) == 0):

                continue

            stops = ET.fromstring(data)
            for stop in stops:
                # main train data
                type = stop.find('tl').attrib["c"]
                no = stop.find('tl').attrib["n"]
                flag = stop.find('tl').attrib["f"]

                train = type + " " + no

                # arriving data
                if not (stop.find('ar') == None):
                    ar_time = stop.find('ar').attrib["pt"]
                    ar_hrs = ar_time[-4:-2]
                    ar_min = ar_time[-2:]
                    origin = stop.find('ar').attrib["ppth"].split('|')[0]
                    platform = stop.find('ar').attrib["pp"]
                    prev_station = stop.find(
                        'ar').attrib["ppth"].split('|')[-1]

                else:
                    origin = stops.attrib["station"]
                    platform = ""
                    prev_station = ""
                    ar_hrs = ""
                    ar_min = ""

                # departing data
                if not (stop.find('dp') == None):
                    dp_time = stop.find('dp').attrib["pt"]
                    dp_hrs = dp_time[-4:-2]
                    dp_min = dp_time[-2:]
                    destination = stop.find('dp').attrib["ppth"].split('|')[-1]
                    platform = stop.find('dp').attrib["pp"]
                    next_station = stop.find(
                        'dp').attrib["ppth"].split('|')[0]

                else:
                    destination = stops.attrib["station"]
                    platform = ""
                    next_station = ""
                    dp_hrs = ""
                    dp_min = ""

                frames.append(pd.DataFrame({"train": train, "type": type, "number": no, "flag": flag, "origin": origin, "destination": destination, "ar_hrs": ar_hrs,
                                            "ar_min": ar_min, "dp_hrs": dp_hrs, "dp_min": dp_min, "platform": platform, "next_station": next_station, "prev_station": prev_station}))
                print(frames)
            time.sleep(1)
        result = pd.concat(frames)
        result.to_csv("data/stations/"+str(ds100)+"/" +
                      str(date.strftime('%A'))+".csv", index=False)
        print("done with "+date.strftime('%A'))
    print("done with "+ds100)


stations = loadStations()
for station in stations:
    if (station.traffic == "FV"):
        path = "data/stations/" + station.ds100.split(",")[0]
        # skip preexisting stations
        if not os.path.exists(path):
            os.mkdir("data/stations/" + station.ds100.split(",")[0])
            getStationData(station.eva, 3, 2023, station.ds100.split(",")[0])
