import http.client
from config import getClientID, getClientSecret

conn = http.client.HTTPSConnection("apis.deutschebahn.com")

headers = {
    'DB-Client-Id': getClientID(),
    'DB-Api-Key': getClientSecret(),
    'accept': "application/xml"
}

conn.request(
    "GET", "/db-api-marketplace/apis/timetables/v1/station/SHO", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
