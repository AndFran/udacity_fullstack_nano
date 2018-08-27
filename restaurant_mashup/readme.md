Mash up application using requests, foursquare, google maps, sqlalchemy and flask.
The application lets you POST a URL such as:

http://127.0.0.1:5000/restaurants?location=Malaga,Spain&mealtype=tapas

Requests will then go to google maps and fetch the lng and lat, and then send these values on to foursquare along with the 
meal type. A restaurant is then returned (this can be changed by changing the limit in geocode.py 
(find_a_restaurant(meal_type, location, limit=result_limit))

The results are stored in the DB, you can then perform CRUD operations on it, see app.py for details.

