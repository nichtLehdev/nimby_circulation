from config import getDataPath, getWebhook
from discord import SyncWebhook, Embed
import pandas as pd
import os
from datetime import datetime, timedelta
from datetime import date


def main():
    webhookData = getWebhook()
    webhook = SyncWebhook.partial(webhookData["id"], webhookData["code"])
    webhook.edit(name="DB-Data-Collector")
    embed = Embed(title="Concat --- Status",
                  description="Starting...", color=0xe47200)

    # Get yesterdays weekday
    weekday = (datetime.now() - timedelta(days=1)).strftime("%A")

    message = webhook.send("Concatenating data for: " + weekday, embeds=[
                           embed], wait=True, avatar_url="https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Deutsche_Bahn_AG-Logo.svg/1280px-Deutsche_Bahn_AG-Logo.svg.png")
    # Loop through all subfolders in data/stations/
    dataPath = getDataPath()
    stationsPath = dataPath + "/stations"

    length = len(os.listdir(stationsPath))
    count = 0

    for station in os.listdir(stationsPath):
        count += 1
        if (count % 100 == 0):
            if (length - count < 100):
                next_step = length - count
            else:
                next_step = 100
            embed.description = "Concatenating data for " + str(next_step) + " stations: (" + str(
                count) + "/" + str(length) + ")"
            embed.color = 0xe47200
            message.edit(embeds=[embed])

        pathToConcat = stationsPath + "/" + station + "/" + weekday
        concatData(pathToConcat, station, weekday)

    embed.description = "Finished concatenating data for " + \
        str(length) + " stations"
    embed.color = 0x00ff00
    message.edit(embeds=[embed])


def concatData(path, station, weekday):
    # Loop through all files in path
    # Read every file as dataframe from csv
    # Concat all dataframes
    # Save dataframe as csv to new location

    dataframes = []
    dataframes.append(pd.DataFrame(columns=["train", "type", "number", "flag", "origin", "destination",  "ar_hrs",
                                            "ar_min", "dp_hrs", "dp_min", "platform", "prev_station", "next_station"]))

    for file in os.listdir(path):
        df = pd.read_csv(path + "/" + file, sep=";")
        dataframes.append(df)

    df = pd.concat(dataframes)
    if (not os.path.exists(getDataPath() + "/concatFiles")):
        os.makedirs(getDataPath() + "/concatFiles")
    if (not os.path.exists(getDataPath() + "/concatFiles/" + station)):
        os.makedirs(getDataPath() + "/concatFiles/" + station)
    df.to_csv(getDataPath() + "/concatFiles/" + station +
              "/"+weekday+".csv", sep=";", index=False)


main()
