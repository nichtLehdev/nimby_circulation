import http.client
from config import getClientID, getClientSecret
from datetime import date
from datetime import datetime
import time


headers = {
    'DB-Client-Id': getClientID(),
    'DB-Api-Key': getClientSecret(),
    'accept': "application/xml"
}

# conn.request(
#     "GET", "/iris-tts/timetable/plan/8000001/230116/00", headers=headers)

# res = conn.getresponse()
# print(res.status)

start_min = datetime.now().minute
count = 0

while datetime.now().minute == start_min:
    conn = http.client.HTTPSConnection("iris.noncd.db.de")
    count += 1
    conn.request(
        "GET", "/iris-tts/timetable/plan/8000001/230215/22", headers=headers)
    res = conn.getresponse()

    print("Run :" + str(count) + "---" + str(res.status))
    time.sleep(0.25)
