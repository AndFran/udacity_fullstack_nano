import requests
import json

# configuration
google_api_key = "SIGN_UP_FOR_YOUR_OWN"
foursquare_client_id = "SIGN_UP_FOR_YOUR_OWN"
foursquare_client_secret = "SIGN_UP_FOR_YOUR_OWN"
result_limit = 1
photo_resolution = "300x300"


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


def find_a_restaurant(meal_type, location, limit=result_limit):
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
        limit=limit
    )

    result = json.loads(requests.get(url=url, params=params).content)

    for venue in result['response']['venues']:
        yield {"id": venue['id'],
               "restaurant_name": venue['name'],
               "restaurant_address": ", ".join(venue['location']['formattedAddress']),
               "restaurant_image": get_photo_url(venue['id'])}
