import constants
import requests
import uuid
import json
import datetime;

def checkDataset(res, temp):
    lng = res['lng']
    lat = res['lat']
    list = []
    lnglat = [lng, lat]
    if lnglat in temp:
        raise Exception("The city you tried to add is already on the map! \n**If this is a mistake message jozef#2508** :)")
        
    url = 'https://api.mapbox.com/datasets/v1/jozef-7/' + constants.MAPBOX_DATASETID + '/features?access_token=' + constants.MAPBOX_TOKEN
    resp = requests.get(url)
    if(resp.status_code == 200):
        jresp = resp.json()
        for data in jresp['features']:
            geo = (data['geometry'])
            coords = geo['coordinates']
            list.append(coords)
            print(coords)

        if lnglat in list:
            resp.close()
            raise Exception("The city you tried to add is already on the map! \n**If this is a mistake message jozef#2508** :)")
        else:
           return True
    else:
        code = resp.status_code
        resp.close()
        raise Exception("Could not fetch databases, code: " + str(code))


def addToDataset(res):
    lng = res['lng']
    lat = res['lat']
    vals = res['city_ascii'] + ", " + res['admin_name'] + ", " + res['country']
    feature_id = str(uuid.uuid4())
    url = 'https://api.mapbox.com/datasets/v1/jozef-7/' + constants.MAPBOX_DATASETID + '/features/'+ feature_id + '?access_token=' + constants.MAPBOX_TOKEN
    header = {"Content-Type" : "application/json"}
    
    data = {
        "id": feature_id,
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [lng, lat]
        },
        "properties": {
            "Name": vals,
            "Added": str(datetime.datetime.now())
        }
    }

    resp = requests.put(url, headers=header, data=json.dumps(data))
    if(resp.status_code != 200):
        print(resp.content)
        code = resp.status_code
        resp.close()
        raise Exception("Could not add to dataset, code: " + str(code))

    return [lng, lat]