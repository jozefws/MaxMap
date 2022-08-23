import requests
import constants as cn
def city_country_to_coords(city, country):
    try: 
        url = 'http://api.positionstack.com/v1/forward?access_key='+cn.POS_STACK_KEY+'&query=' + city + ' ' + country +'&limit=1'
        r = requests.get(url)
        data = r.json()
        if data['data'] == []:
            return False, data
        else:
            return data['data'][0]['latitude'], data['data'][0]['longitude']
    except Exception as e:
        print("Postition stack error " + str(e))
        return True, str(e)

