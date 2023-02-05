import uuid
import pandas
import requests
from datetime import date


class Run:
    def __init__(self, number, type, start, destination,  identifier=None):
        self.number = number
        self.type = type
        self.id = uuid.uuid4().hex
        self.start = start
        self.destination = destination
        self.identifier = identifier
        self.stops = []

    def __str__(self):
        if "identifier" not in self.__dict__:  # if identifier is None
            tmp = self.type + " " + self.number + ": " + "\n"
        else:
            tmp = self.type + " " + self.number
            tmp += "(" + str(self.identifier) + ")" + ": " + "\n"
        tmp += "Start: " + str(self.start) + "\n"
        for stop in self.stops:
            tmp += "Stop: " + str(stop) + "\n"
        tmp += "Destination: " + str(self.destination) + "\n"

        return tmp

    def addStop(self, stop):
        self.stops.append(stop)


class Stop:
    def __init__(self, station, arrival=None, departure=None):
        self.station = station
        if (arrival != None):
            self.arrival = arrival
        if (departure != None):
            self.departure = departure
        self.id = uuid.uuid4().hex

    def __str__(self):
        if "arrival" not in self.__dict__:  # if arrival is None
            return str(self.station) + " (- " + self.departure + ")"
        elif "departure" not in self.__dict__:
            return str(self.station) + " (" + self.arrival + " - )"
        return str(self.station) + " (" + self.arrival + " - " + self.departure + ")"


class Station:
    def __init__(self, name, ds100):
        self.name = name
        self.ds100 = ds100
        self.id = uuid.uuid4().hex
        self.arrivals = []
        self.departures = []

    def __str__(self):
        return self.name + " (" + self.ds100 + ")"


def loadStations():
    # Load stations from file
    # Return a list of stations
    csv = pandas.read_csv('./data/stations.csv', keep_default_na=False, sep=';', names=[
                          "Bundesland", "RB", "BM", "Nr", "Station", "DS100", "Kat", "Str", "PLZ", "Ort", "Verbund"], index_col=False)
    stations = []
    for row in csv.itertuples():
        if (row.Station != "" and row.DS100 != ""):
            stations.append(Station(row.Station, row.DS100))
    return stations


def loadRuns(dateTime, type):
    stations = loadStations()

    json = requests.get(
        "https://bahn.expert/api/reihung/v4/runsPerDate/"+dateTime).json()
    runs = []
    for run in json:
        if (run["product"]["type"] == type):
            if "br" not in run:
                tmpRun = Run(run["product"]["number"], run["product"]["type"], Stop(next((station for station in stations if station.name == run["origin"]["name"]), run["origin"]["name"]), None, run["origin"]["departureTime"]), Stop(
                    next((station for station in stations if station.name == run["destination"]["name"]), run["destination"]["name"]), run["destination"]["arrivalTime"], None))
            else:
                tmpRun = Run(run["product"]["number"], run["product"]["type"], Stop(next((station for station in stations if station.name == run["origin"]["name"]), run["origin"]["name"]), None, run["origin"]["departureTime"]), Stop(
                    next((station for station in stations if station.name == run["destination"]["name"]), run["destination"]["name"]), run["destination"]["arrivalTime"], None), run["br"]["identifier"])
            for stop in run["via"]:
                if "arrivalTime" and "departureTime" in stop:
                    tmpRun.addStop(
                        Stop(next((station for station in stations if station.name == stop["name"]), stop["name"]), stop["arrivalTime"],
                             stop["departureTime"])
                    )
            runs.append(tmpRun)

    return runs


# date = "2023-02-04"
type = "ICE"
dateTime = str(date.fromisocalendar(2023, 5, 7))
print("All runs on " + dateTime + " of type " + type + ":\n")
for run in loadRuns(dateTime, type):
    print(run)
