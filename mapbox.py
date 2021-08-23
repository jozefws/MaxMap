import constants
import requests
import uuid
import json
import shutil

def checkDataset(res):
    lng = res['lng']
    lat = res['lat']

    lnglat = [lng, lat]

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
        raise Exception("Could not add to dataset, code: " + str(resp.status_code))

    return True

def fetchDataset():
    url = 'https://api.mapbox.com/datasets/v1/jozef-7/' + constants.MAPBOX_DATASETID + '/features?access_token=' + constants.MAPBOX_TOKEN
    resp = requests.get(url)

    if(resp.status_code == 200):
        return resp.content
    else: 
        print(resp.content)
        raise Exception("Could not fetch databases, code: " + str(resp.status_code))


def fetchStatic():
    geo = str(fetchDataset())
    geo = geo.strip("b'")
    overlay = "geojson(" + geo +")"
    url = 'https://api.mapbox.com/styles/v1/jozef-7/cksn8ehpr5gea18p84iqs4nii/static/'+ overlay +'/-0.1,50,0.0,0,60/960x480@2x?access_token=' + constants.MAPBOX_TOKEN
    resp = requests.get(url, stream=True)

    if(resp.status_code == 200):
        with open("map.png", 'wb') as f:
            resp.raw.decode_content = True
            shutil.copyfileobj(resp.raw, f)
        return True
    else:
        raise Exception("Could not fetch static, code: " + str(resp.status_code))


# def addToTileset(res):
#     lng = res['lng']
#     lat = res['lat']
#     vals = res['city_ascii'] + ", " + res['admin_name'] + ", " + res['country']
#     feature_id = str(uuid.uuid4())

#     url = 'https://api.mapbox.com/tilesets/v1/sources/jozef-7/'+ constants.MAPBOX_TILESETNM +'?access_token=' + constants.MAPBOX_TOKEN
#     header = {"Content-Type": "multipart/form-data"}

#     data = {"id" : feature_id, "type": "Feature", "geometry": {"type:": "Point", "coordinates": [lng, lat]}, "properties": {"name": vals}}
#     data = json.dumps(data)

#     with open('data.json', 'w') as f:
#         json.dump(data, f, ensure_ascii=False, indent=4)

#     file = {"file": open('data.json','r')}

#     print(url)

#     resp = requests.post(url, headers=header, files=file)
#     if(resp.status_code == 400):
#         print(400)
#         print(resp.content)
#         return False

#     print(resp.status_code)
#     print(resp.content)
#     return True


    