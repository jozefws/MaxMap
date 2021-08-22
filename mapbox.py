import constants
import requests
import pandas as pd
import uuid
import json
import geojson

def checkDataset(res):
    lng = res['lng']
    lat = res['lat']

    lnglat = [lng, lat]
    # url = 'https://api.mapbox.com/datasets/v1/jozef-7/' + constants.MAPBOX_DATASETID + '?access_token=' + constants.MAPBOX_TOKEN
    # resp = requests.get(url)
    # if(resp.status_code == 200):
    #     jresp = resp.json()
    #     print("No. of Features:")
    #     print(jresp['features'])

    url = 'https://api.mapbox.com/datasets/v1/jozef-7/' + constants.MAPBOX_DATASETID + '/features?access_token=' + constants.MAPBOX_TOKEN
    resp = requests.get(url)
    if(resp.status_code == 200):
        jresp = resp.json()
        list = []

        for data in jresp['features']:
            geo = (data['geometry'])
            coords = geo['coordinates']
            list.append(coords)

        if lnglat in list:
            raise Exception("The city you tried to add is already on the map! \n**If this is a mistake message jozef#2508** :)")
        else:
           return True
    else:
        raise Exception("Could not fetch databases, code: " + str(resp.status_code))

def addToDataset(res):
    return True
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
            "prop0": vals
        }
    }

    data = json.dumps(data)
    resp = requests.put(url, headers=header, data=data)
    if(resp.status_code == 400):
        print(resp.content)
        return False

    print(resp.content)
    return True

def addToTileset(res):
    lng = res['lng']
    lat = res['lat']
    vals = res['city_ascii'] + ", " + res['admin_name'] + ", " + res['country']
    feature_id = str(uuid.uuid4())

    url = 'https://api.mapbox.com/tilesets/v1/sources/jozef-7/'+ constants.MAPBOX_TILESETID +'?access_token=' + constants.MAPBOX_TOKEN
    header = {"Content-Type: multipart/form-data"}

    data = {
        "id": feature_id,
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [lng, lat]
        },
        "properties": {
            "prop0": vals
        }
    }

    data = geojson.dumps(data)
    resp = requests.put(url, headers=header, file=data)
    if(resp.status_code == 400):
        print(resp.content)
        return False

    print(resp.content)
    return True


    