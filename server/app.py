#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response ,jsonify 
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()

    restaurant_list = []
    for restaurant in restaurants:
        restaurant_dict = {
            "address": restaurant.address,
            "id": restaurant.id,
            "name": restaurant.name
        }
        restaurant_list.append(restaurant_dict)

    response = make_response(
        jsonify(restaurant_list),
        200
    )

    return response
@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    
    pizza_list = []
    for pizza in pizzas:
        pizza_dict = {
            "id": pizza.id,
            "ingredients": pizza.ingredients,
            "name": pizza.name
        }
        pizza_list.append(pizza_dict)

    response = make_response(
        jsonify(pizza_list),
        200
    )

    return response
@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = db.session.get(Restaurant, id)
    
    if restaurant is None:
        response = make_response(
            jsonify({"error": "Restaurant not found"}),
            404
        )
        return response

    db.session.delete(restaurant)
    db.session.commit()
    
    response = make_response(
        jsonify({}),
        204
    )
    
    return response

@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant(id):
    restaurant = db.session.get(Restaurant, id)
    
    if restaurant is None:
        response = make_response(
            jsonify({"error": "Restaurant not found"}),
            404
        )
        return response
    
    restaurant_dict = {
        "address": restaurant.address,
        "id": restaurant.id,
        "name": restaurant.name,
        "restaurant_pizzas": [
            {
                "id": restaurantpizza.id,
                "pizza": {
                    "id": restaurantpizza.pizza.id,
                    "ingredients": restaurantpizza.pizza.ingredients,
                    "name": restaurantpizza.pizza.name
                },
                "pizza_id": restaurantpizza.pizza_id,
                "price": restaurantpizza.price,
                "restaurant_id": restaurantpizza.restaurant_id
            }
            for restaurantpizza in restaurant.pizzas
        ]
    }

    response = make_response(
        jsonify(restaurant_dict),
        200
    )
    
    return response


@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()
    price = data.get("price")
    pizza_id = data.get("pizza_id")
    restaurant_id = data.get("restaurant_id")

    try:
        new_restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
        db.session.add(new_restaurant_pizza)
        db.session.commit()
        return jsonify(new_restaurant_pizza.to_dict()), 201
    except ValueError as e:
        return jsonify({"errors": ["validation errors"]}), 400
    except Exception as e:
        return jsonify({"error": "Internal Server Error"}), 500
if __name__ == "__main__":
    app.run(port=5555, debug=True)
