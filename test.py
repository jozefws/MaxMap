import requests
import constants
import json

#Arbroath
ref = "36b58db3-1db6-4b6e-85b5-ab4c7aa90c58"


url = 'https://api.mapbox.com/datasets/v1/jozef-7/' + constants.MAPBOX_DATASETID + '/features/'+ ref + '?access_token=' + constants.MAPBOX_TOKEN
header = {"Content-Type" : "application/json"}

fetch = requests.get(url, headers=header)
if(fetch.status_code != 200):
    print(fetch.content)
    code = fetch.status_code
    fetch.close()
    raise Exception("Could not fetch feature, code: " + str(code)) 
jresp = fetch.json()
coords = jresp['geometry']['coordinates']
props = jresp['properties']


data = {
      "id": ref,
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": coords
        },
        "properties": {
            "Name": str(props['Name']),
            "Added": str(props['Added']),
            "Count" : str(props['Count'] + 1)
        }
}

print(data)

resp = requests.put(url, headers=header, data=json.dumps(data))
if(resp.status_code != 200):
    print(resp.content)
    code = resp.status_code
    resp.close()
    raise Exception("Could not add counter to feature, code: " + str(code))
print(resp.json())