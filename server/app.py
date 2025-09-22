from flask import Flask, request, jsonify, make_response
from flask_migrate import Migrate
from server.models import db, Restaurant, Pizza, RestaurantPizza

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///app.db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate = Migrate(app, db)

    @app.route("/restaurants", methods=["GET"])
    def get_restaurants():
        restaurants = Restaurant.query.all()
        return jsonify([r.to_dict() for r in restaurants]), 200

    @app.route("/restaurants/<int:id>", methods=["GET"])
    def get_restaurant(id):
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return jsonify({"error": "Restaurant not found"}), 404
        return jsonify(restaurant.to_dict(include_rp=True)), 200

    @app.route("/restaurants/<int:id>", methods=["DELETE"])
    def delete_restaurant(id):
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return jsonify({"error": "Restaurant not found"}), 404
        db.session.delete(restaurant)
        db.session.commit()
        return make_response("", 204)

    @app.route("/pizzas", methods=["GET"])
    def get_pizzas():
        pizzas = Pizza.query.all()
        return jsonify([p.to_dict() for p in pizzas]), 200

    @app.route("/restaurant_pizzas", methods=["POST"])
    def create_restaurant_pizza():
        data = request.get_json()
        price = data.get("price")
        pizza_id = data.get("pizza_id")
        restaurant_id = data.get("restaurant_id")

        errors = []
        if price is None:
            errors.append("price is required")
        if pizza_id is None:
            errors.append("pizza_id is required")
        if restaurant_id is None:
            errors.append("restaurant_id is required")

        if errors:
            return jsonify({"errors": errors}), 400

        pizza = Pizza.query.get(pizza_id)
        restaurant = Restaurant.query.get(restaurant_id)
        if not pizza:
            return jsonify({"errors": [f"Pizza id {pizza_id} not found"]}), 404
        if not restaurant:
            return jsonify({"errors": [f"Restaurant id {restaurant_id} not found"]}), 404

        # ✅ enforce test expectation for validation
        if not (1 <= price <= 30):
            return jsonify({"errors": ["validation errors"]}), 400

        try:
            rp = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
            db.session.add(rp)
            db.session.commit()
        except Exception:
            db.session.rollback()
            return jsonify({"errors": ["An unexpected error occurred"]}), 500

        return jsonify(rp.to_dict(include_nested_pizza=True, include_nested_restaurant=True)), 201

    return app


# 👇 instantiate app
app = create_app()

if __name__ == "__main__":
    app.run(port=5555, debug=True)
