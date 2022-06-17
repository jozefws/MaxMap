import constants
import requests
import uuid
import json
import datetime;
import traceback

def checkDataset(res, temp):
    lng = res['lng']
    lat = res['lat']
    rescoord = [lng, lat]
 
    # Check if theres already a feature at this location in temp.
    for entry in temp:
        if int(entry['lng']) == int(lng) and int(entry['lat']) == int(lat):
            return{"ref": entry['ref']}

    url = 'https://api.mapbox.com/datasets/v1/jozef-7/' + constants.MAPBOX_DATASETID + '/features?access_token=' + constants.MAPBOX_TOKEN
    resp = requests.get(url)

    if(resp.status_code == 200):
        jresp = resp.json()
        for data in jresp['features']:
            coords = data['geometry']['coordinates']
            count = str(data['properties']['Count'])
            if coords == rescoord:
                return{"lat": coords[1], "lng": coords[0], "ref": data['id'], "tempcount": str(int(count) + 1)}
        return True
    else:
        code = resp.status_code
        resp.close()
        raise Exception("Could not fetch databases, code: " + str(code))


def addToDataset(res, user, title):
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
            "Title": str(title),
            "Name": str(user) + ",",
            "Added": str(datetime.datetime.now()),
            "Count" : "1"
        }
    }

    resp = requests.put(url, headers=header, data=json.dumps(data))

    if(resp.status_code != 200):
        code = resp.status_code
        resp.close()
        raise Exception("Could not add to dataset, code: " + str(code))

    resp = resp.json()
    return{"lat": lat, "lng": lng, "ref": resp['id'], "tempcount": "1"}


def countUpdate(ref, temp, user):
    url = 'https://api.mapbox.com/datasets/v1/jozef-7/' + constants.MAPBOX_DATASETID + '/features/'+ ref + '?access_token=' + constants.MAPBOX_TOKEN
    header = {"Content-Type" : "application/json"}
    fetch = requests.get(url, headers=header)
    if(fetch.status_code != 200):
        code = fetch.status_code
        fetch.close()
        raise Exception("Could not fetch feature, code: " + str(code))
    jresp = fetch.json()
    coords = jresp['geometry']['coordinates']
    props = jresp['properties']

    users = props['Name']

    usrsplit = users.split(",")

    if user not in usrsplit:
        users = users +  str(user) + ","

    num = int(props['Count']) + 1
    for entry in temp:
        if entry['ref'] == ref: 
            if(entry['tempcount'] != props['Count']):
                num = int(entry['tempcount']) + 1
    data = {
        "id": ref,
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": coords
            },
            "properties": {
                "Title": props['Title'],
                "Name": str(users),
                "Added": str(props['Added']),
                "Count" : str(num)
            }
    }
    resp = requests.put(url, headers=header, data=json.dumps(data))
    if(resp.status_code != 200):
        code = resp.status_code
        resp.close()
        raise Exception("Could not add counter to feature, code: " + str(code))
    return True

def userList(author):
    url = 'https://api.mapbox.com/datasets/v1/jozef-7/' + constants.MAPBOX_DATASETID + '/features?access_token=' + constants.MAPBOX_TOKEN
    resp = requests.get(url)
    features = []
    if(resp.status_code == 200):
        jresp = resp.json()
        for data in jresp['features']:
            #if name matches author add to features list
            if data['properties']['Name'].find(author) != -1:
                features.append(data)

        return features
    else:
        code = resp.status_code
        resp.close()
        raise Exception("Could not fetch databases, code: " + str(code))

def updateFeatureNames(author, feature_id):
    url = 'https://api.mapbox.com/datasets/v1/jozef-7/' + constants.MAPBOX_DATASETID + '/features?access_token=' + constants.MAPBOX_TOKEN
    resp = requests.get(url)

    if(resp.status_code == 200):
        jresp = resp.json()
        for data in jresp['features']:
            if data['id'] == feature_id:
                if data['properties']['Name'].find(author) != -1 and int(data['properties']['Count']) == 1:
                    print("Delete feature, code:" + str(feature_id) + " SINGLE")
                    try:
                        delete_feature(feature_id)
                    except:
                        raise Exception("Could not delete feature, code: " + str(feature_id))
                if data['properties']['Name'].find(author) != -1 and int(data['properties']['Count']) > 1:
                    print("Delete user in feature, code:" + str(feature_id) + " " + str(author))
                    names = data['properties']['Name'].replace(author+",", "")

                    if names == "":
                        try:
                            delete_feature(feature_id)
                        except:
                            raise Exception("Could not delete feature, code: " + str(feature_id))
                    new_data = {
                        "id": feature_id,
                            "type": "Feature",
                            "geometry": {
                                "type": "Point",
                                "coordinates": data['geometry']['coordinates']
                            },
                            "properties": {
                                "Title": str(data['Title']),
                                "Name": names,
                                "Added": str(data['Added']),
                                "Count" : data['Count']
                            }
                        }

                    header = {"Content-Type" : "application/json"}
                    resp = requests.put(url, headers=header, data=json.dumps(new_data))
                    if(resp.status_code != 200):
                        code = resp.status_code
                        resp.close()
                        raise Exception("Could not add delete name from feature, code: " + str(code))
                    return True
        raise Exception("Could not find feature")
    else:
        code = resp.status_code
        resp.close()
        raise Exception("Could not fetch databases, code: " + str(code))
        
def delete_feature(feature_id):
    url = 'https://api.mapbox.com/datasets/v1/jozef-7/' + constants.MAPBOX_DATASETID + '/features/'+ feature_id + '?access_token=' + constants.MAPBOX_TOKEN
    header = {"Content-Type" : "application/json"}
    resp = requests.delete(url, headers=header)
    if(resp.status_code != 204):
        code = resp.status_code
        resp.close()
        raise Exception("Could not delete feature, code: " + str(code))
    return True
    
if __name__ == '__main__':
    print("Enter discord username with discriminator:")