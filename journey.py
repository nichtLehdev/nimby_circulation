import os
from config import getDataPath
from datetime import datetime, timedelta
from main import loadStations
import math
import pandas as pd

def getRil100FromName(name):
  stations = loadStations()
  for station in stations:
    if (station.name == name):
      return station.ds100

  print("Station not found: " + name)


def getNameFromRil100(ril100):
  stations = loadStations()
  for station in stations:
    if (station.ds100 == ril100):
      return station.name

def getNextStation(ril100, date, type, number, journey, index):
  dataPath = getDataPath()
  #find concat file of station
  concatPath = dataPath + "/concatFiles/" + ril100 + "/" + date + ".csv"
  #read csv as dataframe
  df = pd.read_csv(concatPath, sep=";" ,header=1, names=["train", "type", "number", "flag", "origin", "destination", "ar_hrs", "ar_min", "dp_hrs", "dp_min", "platform", "prev_station", "next_station"])
  #loop through all rows
  for row in df.itertuples():
    #find row with train type and number
    if (row.type == type and str(row.number) == str(number)):
      index += 1
      #add station to journey

      #check if next station is in row
      if (pd.isnull(row.next_station)):
        journey.append(pd.DataFrame({"station": getNameFromRil100(ril100), "ril100": ril100, "ar_time": str(math.trunc(float(row.ar_hrs))) + ":" +str(math.trunc(float(row.ar_min))), "platform": row.platform}, index=[index]))
        return journey
      else:
        journey.append(pd.DataFrame({"station": getNameFromRil100(ril100), "ril100": ril100, "ar_time": str(math.trunc(float(row.ar_hrs))) + ":" +str(math.trunc(float(row.ar_min))), "dp_time": str(math.trunc(float(row.dp_hrs))) + ":" + str(math.trunc(float(row.dp_min))), "platform": row.platform}, index=[index]))
        return getNextStation(getRil100FromName(row.next_station), date, type, number, journey, index)

def main():
  # get yesterdays date (later strftime("%d.%m.%Y"))"))
  date = (datetime.now() - timedelta(days=1)).strftime("%A")
  date = "Saturday"

  # loop through all subfolders in data/concatFiles
  dataPath = getDataPath()
  concatPath = dataPath + "/concatFiles"

  length = len(os.listdir(concatPath))
  stationCount = 0
  journeyCount = 0

  for station in os.listdir(concatPath):
    stationCount += 1
    if (stationCount % 100 == 0):
      if (length - stationCount < 100):
        next_step = length - stationCount
      else:
        next_step = 100
      print("Calculating journeys for " + str(next_step) + " stations: (" + str(stationCount) + "/" + str(length) + ")")
      print("Journeys found: " + str(journeyCount))

    pathToJourney = dataPath + "/journeys/"
    if (not os.path.exists(pathToJourney)):
      os.makedirs(pathToJourney)

    # find yesterdays file
    pathToCsv = concatPath + "/" + station + "/" + date + ".csv"
    if (not os.path.exists(pathToCsv)):
      print("No data for " + station + " on " + date)
      continue

    # read csv as dataframe
    df = pd.read_csv(pathToCsv, dtype=str, header=1, names=["train", "type", "number", "flag", "origin", "destination", "ar_hrs", "ar_min", "dp_hrs", "dp_min", "platform", "prev_station", "next_station"], sep=";")
    # loop through all rows
    for row in df.itertuples():
      # check if field prev_station in row is empty
      if (pd.isnull(row.prev_station)):
        # if yes create a new dataframe
        index = 0
        journey = []
        journey.append(pd.DataFrame(columns=["station", "ril100", "ar_time", "dp_time", "platform"]))
        # add station to journey
        journey.append(pd.DataFrame({"station": getNameFromRil100(station), "ril100": station, "dp_time": str(math.trunc(float(row.dp_hrs))) + ":" + str(math.trunc(float(row.dp_min))), "platform": row.platform }, index=[index]))

        #check if next station is in row
        if ( not pd.isnull(row.next_station)):
          print("Started concatenating journey of " + row.type + " " + str(row.number) + " from " + row.origin + " to " + row.destination)
          # there are not journeys with only one station
          getNextStation(getRil100FromName(row.next_station), date, row.type, row.number, journey, index)
          # check if savepath exists
          if (not os.path.exists(pathToJourney + row.type + "/" + str(row.number))):
            os.makedirs(pathToJourney + row.type + "/" + str(row.number))
          # save journey as csv
          df = pd.concat(journey)
          df.to_csv(pathToJourney + row.type + "/" +str(row.number) + "/" + date + ".csv", sep=";", index=False)
          journeyCount += 1
main()