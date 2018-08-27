from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from geocode import find_a_restaurant
from flask import Flask, request, jsonify
from models import Restaurant, Base

engine = create_engine("sqlite:///restaruants.db")
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = scoped_session(sessionmaker(bind=engine))  # does not work because of threading

app = Flask(__name__)


@app.route("/")
@app.route('/restaurants', methods=['GET', 'POST'])
def all_restaurants_handler():
    if request.method == 'GET':
        restaurants = session.query(Restaurant).all()
        return jsonify({"restaurants": [r.serialize for r in restaurants]})

    elif request.method == 'POST':
        location = request.args.get('location')
        mealtype = request.args.get('mealtype')

        results = find_a_restaurant(mealtype, location, limit=1)
        added = []
        for result in results:
            restaurant = Restaurant(restaurant_name=result['restaurant_name'],
                                    restaurant_address=result['restaurant_address'],
                                    restaurant_image=result['restaurant_image'])
            session.add(restaurant)
            added.append(restaurant)
        session.commit()
    return jsonify({"restaurants": [r.serialize for r in added]})


@app.route('/restaurants/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def restaurant_handler(id):
    restaurant = session.query(Restaurant).filter_by(id=id).one()

    if request.method == 'GET':
        return jsonify(restaurant=restaurant.serialize)
    elif request.method == 'PUT':
        restaurant_name = request.args.get('restaurant_name')
        restaurant_address = request.args.get('restaurant_address')
        restaurant_image = request.args.get('restaurant_image')
        restaurant.restaurant_name = restaurant_name
        restaurant.restaurant_address = restaurant_address
        restaurant.restaurant_image = restaurant_image
        session.add(restaurant)
        session.commit()
        return jsonify(restaurant=restaurant.serialize)

    elif request.method == 'DELETE':
        session.delete(restaurant)
        session.commit()
        return jsonify(message="restaurant with id: {} removed".format(id))


if __name__ == '__main__':
    app.run(debug=True)
