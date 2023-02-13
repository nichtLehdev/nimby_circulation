import http.client
from config import getClientID, getClientSecret
import json
import xml.etree.ElementTree as ET

conn = http.client.HTTPSConnection("iris.noncd.db.de")

headers = {
    'DB-Client-Id': getClientID(),
    'DB-Api-Key': getClientSecret(),
    'accept': "application/xml"
}

conn.request(
    "GET", "/iris-tts/timetable/plan/8000001/230116/00", headers=headers)

res = conn.getresponse()
print(res.status)
data = res.read()
stops = ET.fromstring(data)

for stop in stops:
    # main train data
    type = stop.find('tl').attrib["c"]
    no = stop.find('tl').attrib["n"]
    flag = stop.find('tl').attrib["f"]

    train = type + " " + no

    resultstr = ""
    resultstr += train + ":\n"

    # arriving data
    if not (stop.find('ar') == None):
        ar_time = stop.find('ar').attrib["pt"]
        ar_hrs = ar_time[-4:-2]
        ar_min = ar_time[-2:]
        origin = stop.find('ar').attrib["ppth"].split('|')[0]
        platform = stop.find('ar').attrib["pp"]

        resultstr += "Arriving at " + ar_hrs + ":" + ar_min + \
            " on Platform " + platform + " from " + origin + "\n"

    else:
        resultstr += "Starting at " + stops.attrib["station"] + "\n"

    # departing data
    if not (stop.find('dp') == None):
        dp_time = stop.find('dp').attrib["pt"]
        dp_hrs = dp_time[-4:-2]
        dp_min = dp_time[-2:]
        destination = stop.find('dp').attrib["ppth"].split('|')[-1]
        platform = stop.find('dp').attrib["pp"]

        resultstr += "Departing at " + dp_hrs + ":" + dp_min + \
            " on Platform " + platform + " to " + destination + "\n"

    else:
        resultstr += "Ending at " + stops.attrib["station"] + "\n"

    print(resultstr)


# for stop in stops:
#   flag = stop["tl"]["@f"]
#  if (flag == "F"):  # is long distance
#     print(stop["tl"]["@c"] + " " + stop["tl"]["@n"])
