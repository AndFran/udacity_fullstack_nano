import requests
import json

# configuration
google_api_key = "sorry_sign_up_for_your_own"
foursquare_client_id = "sorry_sign_up_for_your_own"
foursquare_client_secret = "sorry_sign_up_for_your_own"
result_limit = 1
photo_resolution = "300x300"
places = [
    ("Pizza", "Tokyo, Japan"),
    ("Tacos", "Jakarta, Indonesia"),
    ("Tapas", "Maputo, Mozambique"),
    ("Falafel", "Cairo, Egypt"),
    ("Spaghetti", "New Delhi, India"),
    ("Cappuccino", "Geneva, Switzerland"),
    ("Sushi", "Los Angeles, California"),
    ("Steak", "La Paz, Bolivia"),
    ("Gyros", "Sydney Australia")
]


def get_lat_lng(location):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = dict(
        key=google_api_key,
        address=location
    )
    try:
        response_json = json.loads(requests.get(url=url, params=params).content)
    except AttributeError:
        return {"error": "could not find address"}

    try:
        location = response_json['results'][0]['geometry']['location']
    except KeyError:
        return {"error": "could not parse google response"}

    return {"location": {"lat": location['lat'], "lng": location['lng']}}


def get_photo_url(venue_id):
    url = "https://api.foursquare.com/v2/venues/{}/photos".format(venue_id)

    params = dict(
        client_id=foursquare_client_id,
        client_secret=foursquare_client_secret,
        v="20180323",
    )
    result = json.loads(requests.get(url=url, params=params).content)

    try:
        prefix = result['response']['photos']['items'][0]['prefix']
        suffix = result['response']['photos']['items'][0]['suffix']
    except (KeyError, IndexError):
        return "https://picsum.photos/300/300"

    return prefix + photo_resolution + suffix


def find_a_restaurant(meal_type, location):
    response_location = get_lat_lng(location)
    if response_location.get('location') is None:
        print("Cannot find location")
        return

    lat = response_location['location']['lat']
    lng = response_location['location']['lng']

    url = "https://api.foursquare.com/v2/venues/search"

    params = dict(
        client_id=foursquare_client_id,
        client_secret=foursquare_client_secret,
        v="20180323",
        ll=str(lat) + "," + str(lng),
        query=meal_type,
        limit=result_limit
    )

    result = json.loads(requests.get(url=url, params=params).content)

    for venue in result['response']['venues']:
        yield {"id": venue['id'],
               "name": venue['name'],
               "address": venue['location']['formattedAddress'],
               "photo": get_photo_url(venue['id'])}


if __name__ == '__main__':
    for place in places:
        print("Results for {} in {}".format(place[0], place[1]))
        for dx, rest in enumerate(find_a_restaurant(*place), start=0):
            print("\t", dx + 1, rest)
            print("-" * 100)
