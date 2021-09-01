import constants
import requests
import uuid
import json
import datetime;

def checkDataset(res, temp):
    lng = res['lng']
    lat = res['lat']
    rescoord = [lng, lat]
    for entry in temp:
       if entry['lng'] == lng and entry['lat'] == lat:
           countUpdate(entry['ref'], temp)
           raise Exception("AEE")

    url = 'https://api.mapbox.com/datasets/v1/jozef-7/' + constants.MAPBOX_DATASETID + '/features?access_token=' + constants.MAPBOX_TOKEN
    resp = requests.get(url)
    if(resp.status_code == 200):
        jresp = resp.json()
        for data in jresp['features']:
            coords = data['geometry']['coordinates']
            count = data['properties']['Count']
            if coords == rescoord:
                #temp.append({"lat": coords[0], "lng": coords[1], "ref": data['id'], "tempcount": str(count)})
                countUpdate(data['id'], temp)
                raise Exception("AEE")
        
        return True
    else:
        code = resp.status_code
        resp.close()
        raise Exception("Could not fetch databases, code: " + str(code))


def addToDataset(res, user):
    lng = res['lng']
    lat = res['lat']
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
            "Name": str(user),
            "Added": str(datetime.datetime.now()),
            "Count" : "1"
        }
    }

    resp = requests.put(url, headers=header, data=json.dumps(data))
    print(resp)

    if(resp.status_code != 200):
        print(resp.content)
        code = resp.status_code
        resp.close()
        raise Exception("Could not add to dataset, code: " + str(code))

    resp = resp.json()
    return {"lat": lat, "lng": lng, "ref": resp['id'], "tempcount": "1"}


def countUpdate(ref, temp):
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

    num = int(props['Count']) + 1

    for entry in temp:
        if entry['id'] == ref: 
            if(entry['tempcount'] != props['Count']):
                num = int(entry['tempcount']) + 1
            entry['tempcount'] = entry['tempcount'] + 1
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
                "Count" : str(num)
            }
    }

    resp = requests.put(url, headers=header, data=json.dumps(data))
    if(resp.status_code != 200):
        print(resp.content)
        code = resp.status_code
        resp.close()
        raise Exception("Could not add counter to feature, code: " + str(code))
    print((resp.json()))

    return True