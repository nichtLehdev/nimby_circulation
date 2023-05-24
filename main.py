import uuid
import pandas
import requests
from datetime import date
from datetime import datetime
from config import getDataPath
from time import sleep


class Station:
    def __init__(self, name, ds100, eva, traffic):
        self.name = name
        self.ds100 = ds100
        self.id = uuid.uuid4().hex
        self.arrivals = []
        self.departures = []
        self.eva = eva
        self.traffic = traffic

    def __str__(self):
        return self.name + " (" + self.ds100 + ")|[" + str(self.eva) + "]"


def loadStations():
    # Load stations from file
    # Return a list of stations
    dataPath = getDataPath()
    csv = pandas.read_csv(dataPath+'/stations.csv', sep=';', header=1, names=[
                          "EVA_NR", "DS100", "IFOPT", "NAME", "Verkehr", "Laenge", "Breite", "Betreiber_Name", "Betreiber_Nr", "Status"], index_col=False)
    stations = []
    for row in csv.itertuples():
        if (row.NAME != "" and row.DS100 != "" and row.EVA_NR and row.Verkehr != ""):
            ds100 = row.DS100.split(",")[0]
            stations.append(Station(row.NAME, ds100, row.EVA_NR, row.Verkehr))
    return stations


def dataLoop():
    while (datetime.now().minute != 0):
        sleep(60)

    main()
