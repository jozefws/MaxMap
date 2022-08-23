import uuid
import constants as cn
import datetime
import json
import requests

def add_entry(lat, lng, name):
    try:
        feature_id = str(uuid.uuid4())
        url = 'https://api.mapbox.com/datasets/v1/jozef-7/' + cn.MAPBOX_DATASETID + '/features/'+ feature_id + '?access_token=' + cn.MAPBOX_TOKEN
        header = {"Content-Type" : "application/json"}
        
        data = {
            "id": feature_id,
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lng, lat]
            },
            "properties": {
                "Name": str(name),
                "Added": str(datetime.datetime.now()),
                "Count" : "1"
            }
        }
        resp = requests.put(url, headers=header, data=json.dumps(data))

        if(resp.status_code != 200):
            print(resp.content)
            resp.close()
            return False, "Could not add to dataset, code: " + str(resp.status_code)
        else:
            return True, feature_id
    except Exception as e:
        return False, str(e)

def update_entry(featureid, lat, lng, names, count):
    print("Updating entry\n")
    print(featureid, lat, lng, names, count)
    print("\n")
    url = 'https://api.mapbox.com/datasets/v1/jozef-7/' + cn.MAPBOX_DATASETID + '/features/'+ featureid + '?access_token=' + cn.MAPBOX_TOKEN
    print(url)
    header = {"Content-Type" : "application/json"}
    fetch = requests.get(url, headers=header)
    if(fetch.status_code != 200):
        print(fetch.content)
        code = fetch.status_code
        fetch.close()
        return False, "Could not fetch feature, code: " + str(code)
    data = {
        "id": featureid,
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lng, lat]
            },
            "properties": {
                "Updated": str(datetime.datetime.now()),
                "Name": str(names),
                "Count" : str(count)
            }
    }
    resp = requests.put(url, headers=header, data=json.dumps(data))
    if(resp.status_code != 200):
        code = resp.status_code
        resp.close()
        print(resp.content)
        return False, "Could not update feature, code: " + str(code)
    return True, ""

def delete_feature(featureid):
    url = 'https://api.mapbox.com/datasets/v1/jozef-7/' + cn.MAPBOX_DATASETID + '/features/'+ featureid + '?access_token=' + cn.MAPBOX_TOKEN
    header = {"Content-Type" : "application/json"}
    resp = requests.delete(url, headers=header)
    if(resp.status_code != 204):
        code = resp.status_code
        resp.close()
        return False, "Could not delete feature, code: " + str(code)
    return True, ""