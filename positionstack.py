import http.client, urllib.parse
import constants as cs
import json
url = http.client.HTTPConnection('api.positionstack.com')

def ps_search(query):

    if(query == ""):
        raise Exception("Query cannot be empty")

    if(len(query) <= 3):
        raise Exception("Query needs to be longer than 3 characters")

    params = urllib.parse.urlencode({
    'access_key': cs.POS_STACK_KEY,
    'query': query,
    'limit': 1,
    'fields': 'latitude,longitude'
    })

    url.request('GET', '/v1/forward?{}'.format(params))

    res = url.getresponse()

    if res.status != 200:
        raise Exception("HTTP Request Error: " + str(res.status))

    data = res.read()
    jdata = json.loads(data.decode('utf-8'))
    lat = jdata['data'][0]['latitude']
    lon = jdata['data'][0]['longitude']
    url.close()
    return {"lat": lat, "lng": lon}

if __name__ == '__main__':
    query = input()
    try:
        print(ps_search(query))
    except Exception as e:
        print("Error: " + str(e))