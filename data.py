import http.client
import time
from datetime import date
from main import Run, Stop, Station, loadStations
from config import getClientID, getClientSecret
import xmltodict
import pandas as pd

conn = http.client.HTTPSConnection("apis.deutschebahn.com")

headers = {
    'DB-Client-Id': getClientID(),
    'DB-Api-Key': getClientSecret(),
    'accept': "application/xml"
}

stations = loadStations()
for station in stations:
    if(station.traffic == "FV"):
        print(station)


