Mash up application using requests, foursquare, google maps, sqlalchemy and flask.
The application lets you POST a URL such as:

http://127.0.0.1:5000/restaurants?location=Malaga,Spain&mealtype=tapas

Requests will then go to google maps and fetch the lng and lat, and then send these values on to foursquare along with the 
meal type. A restaurant is then returned (this can be changed by changing the limit in geocode.py 
(find_a_restaurant(meal_type, location, limit=result_limit))

The results are stored in the DB, you can then perform CRUD operations on it, see app.py for details.

Example result set:

{
    "restaurants": [
        {
            "id": 1,
            "restaurant_address": "Calle de Tomás de Cozar, 7, 29008 Málaga Andalucía, España",
            "restaurant_image": "https://igx.4sqi.net/img/general/300x300/02SS5HRIRX4NVH5LWOXBDVSXTEKVV0ZDXXI52KCCOLY2ID4R.jpg",
            "restaurant_name": "Tapas bar - Échate Pa Llá (Mejicano)"
        },
        {
            "id": 2,
            "restaurant_address": "Plaza de la solidaridad (Avenida de las Americas), 29002 Málaga Andalucía, España",
            "restaurant_image": "https://igx.4sqi.net/img/general/300x300/47070665_TxRIwTwZS3yJDJvTMUyK1ErfHz_g4HIAp4o4crRrHR4.jpg",
            "restaurant_name": "Chopp Bocadillos Y Tapas"
        }      
    ]
}

