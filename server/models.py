# server/models.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates

db = SQLAlchemy()

class Restaurant(db.Model):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)

    # relationship -> RestaurantPizza
    restaurant_pizzas = db.relationship(
        "RestaurantPizza",
        back_populates="restaurant",
        cascade="all, delete-orphan",
        lazy=True
    )

    def to_dict(self, include_rp=False):
        data = {
            "id": self.id,
            "name": self.name,
            "address": self.address
        }
        if include_rp:
            data["restaurant_pizzas"] = [rp.to_dict(include_nested_pizza=True) for rp in self.restaurant_pizzas]
        return data


class Pizza(db.Model):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    ingredients = db.Column(db.String, nullable=False)

    # relationship -> RestaurantPizza
    restaurant_pizzas = db.relationship(
        "RestaurantPizza",
        back_populates="pizza",
        cascade="all, delete-orphan",
        lazy=True
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "ingredients": self.ingredients
        }


class RestaurantPizza(db.Model):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    pizza_id = db.Column(db.Integer, db.ForeignKey("pizzas.id"), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"), nullable=False)

    # relationships back to parent
    pizza = db.relationship("Pizza", back_populates="restaurant_pizzas", lazy=True)
    restaurant = db.relationship("Restaurant", back_populates="restaurant_pizzas", lazy=True)

    @validates("price")
    def validate_price(self, key, value):
        if value is None:
            raise ValueError("Price is required")
        if not (1 <= value <= 30):
            raise ValueError("Price must be between 1 and 30")
        return value

    def to_dict(self, include_nested_pizza=False, include_nested_restaurant=False):
        data = {
            "id": self.id,
            "pizza_id": self.pizza_id,
            "restaurant_id": self.restaurant_id,
            "price": self.price
        }
        if include_nested_pizza and self.pizza:
            data["pizza"] = self.pizza.to_dict()
        if include_nested_restaurant and self.restaurant:
            data["restaurant"] = self.restaurant.to_dict()
        return data
