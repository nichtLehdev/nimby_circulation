import http.client
from config import getClientID, getClientSecret, getDataPath, getWebhook
from datetime import date
from datetime import datetime
import time
import pandas as pd
import os
import xml.etree.ElementTree as ET
from main import loadStations
import numpy as np
from discord import SyncWebhook, Embed
import requests

headers = {
    'DB-Client-Id': getClientID(),
    'DB-Api-Key': getClientSecret(),
    'accept': "application/xml"
}


def __main__():
    webhookData = getWebhook()
    webhook = SyncWebhook.partial(webhookData["id"], webhookData["code"])
    webhook.edit(name="DB-Data-Collector")
    embed = Embed(title="Fetch --- Status",
                  description="Starting...", color=0x00ff00)
    error_embed = Embed(title="API Errors", description="", color=0xff0000)
    message = webhook.send("Start collecting data for: " + datetime.now().strftime("%A") +
                           " " + datetime.now().strftime("%H")+":xx", embeds=[embed], wait=True, avatar_url="https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Deutsche_Bahn_AG-Logo.svg/1280px-Deutsche_Bahn_AG-Logo.svg.png")

    stations = loadStations()
    crt_hrs = datetime.now().strftime("%H")
    crt_date = datetime.now().strftime("%y%m%d")
    weekday = datetime.now().strftime("%A")

    count = 0
    avg_sleeptime = 0
    start_time = time.time()
    next_time = start_time
    stop_count = 0
    for station in stations:
        count += 1
        stations_left = len(stations) + 1 - count

        time_left_in_hr = (50 - datetime.now().minute) * 60
        if (time_left_in_hr <= 0):
            time_left_in_hr = 1
        sleeptime = time_left_in_hr / stations_left
        if (sleeptime > 0.15):
            sleeptime = 0.15
        avg_sleeptime = (avg_sleeptime + sleeptime) / 2

        if (count % 100 == 0):

            embed.description = "Collecting data for 100 stations: (" + str(count) + "/" + str(len(stations)-1) + ")\nTime per Request: " + "{:.3f}".format(round(
                ((time.time() - next_time)/100), 3)) + "s \n Average Sleeptime: " + "{:.3f}".format(round((avg_sleeptime)/60, 3)) + "\nTotal Stops added: "+str(stop_count)
            embed.color = 0xe47200
            next_time = time.time()
            if (error_embed.description == ""):
                message.edit(embeds=[embed])
            else:
                message.edit(embeds=[embed, error_embed])

        re = getStationData(station, crt_date, crt_hrs, sleeptime, weekday)
        if re["type"] == "error":
            error_embed.description += re["msg"] + "\n"
        elif re["type"] == "success":
            stop_count += re["count"]

    embed.description = "Done! \n Finished to collect data from "+str(
        len(stations)-1) + " stations in "+"{:.1f}".format(round((time.time()-start_time)/60, 3)) + "min\n Stops added: "+str(stop_count)
    embed.color = 0x00ff00

    if (error_embed.description == ""):
        message.edit(embeds=[embed])
    else:
        message.edit(embeds=[embed, error_embed])


def getStationData(station, date, hrs, sleep, weekday):
    conn = http.client.HTTPSConnection("iris.noncd.db.de")
    url = "/iris-tts/timetable/plan/" + \
        str(station.eva) + "/" + str(date) + "/" + str(hrs)

    conn.request("GET", url, headers=headers)
    res = conn.getresponse()
    if (res.status == 200):
        data = res.read()
        stops = ET.fromstring(data)
        dataframes = []
        dataframes.append(pd.DataFrame(columns=["train", "type", "number", "flag", "origin", "destination",  "ar_hrs",
                                                "ar_min", "dp_hrs", "dp_min", "platform", "prev_station", "next_station"]))
        count = 0
        for stop in stops:
            count += 1
            # main train data
            type = stop.find('tl').attrib["c"]
            no = stop.find('tl').attrib["n"]
            if not (stop.find('tl').find('f') == None):
                flag = stop.find('tl').attrib["f"]
            else:
                flag = ""
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
                next_station = stop.find(
                    'dp').attrib["ppth"].split('|')[0]
                if (platform == ""):
                    platform = stop.find('dp').attrib["pp"]

            else:
                destination = stops.attrib["station"]
                next_station = ""
                dp_hrs = ""
                dp_min = ""
                if (platform == ""):
                    platform = ""

            # add data to dataframe
            frame = pd.DataFrame({"train": train, "type": type, "number": no, "flag": flag, "origin": origin, "destination": destination,  "ar_hrs": ar_hrs,
                                  "ar_min": ar_min, "dp_hrs": dp_hrs, "dp_min": dp_min, "platform": platform, "prev_station": prev_station, "next_station": next_station}, index=[count])
            dataframes.append(frame)

        df = pd.concat(dataframes)
        dataPath = getDataPath()

        if not os.path.exists(dataPath + "/stations/" + station.ds100):
            os.makedirs(dataPath + "/stations/" + station.ds100)
        if not os.path.exists(dataPath + "/stations/" + station.ds100 + "/" + weekday):
            os.makedirs(dataPath + "/stations/" +
                        station.ds100 + "/" + weekday)

        np.savetxt(dataPath + "/stations/" + station.ds100 + "/" +
                   weekday + "/"+hrs+".csv", df, delimiter=";", fmt="%s", header="train;type;number;flag;origin;destination;ar_hrs;ar_min;dp_hrs;dp_min;platform;prev_station;next_station", comments="")

        time.sleep(sleep)
        return {"type": "success", "count": len(stops)}
    else:
        time.sleep(sleep)
        return {"type": "error", "msg": station.ds100 + " --- " + str(res.status)}


__main__()
