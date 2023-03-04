from flask_api import db


class CarModel(db.Model):
    __tablename__ = 'cars'

    id = db.Column(db.Integer, primary_key=True)
    brand_id = db.Column(db.Integer, db.ForeignKey('car_brand.id'), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


class CarBrandModel(db.Model):
    __tablename__ = 'car_brand'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    cars = db.relationship(CarModel, backref='cars_brand')

