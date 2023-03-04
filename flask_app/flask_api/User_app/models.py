from flask_jwt_extended import create_access_token, create_refresh_token

from werkzeug.security import generate_password_hash, check_password_hash

from flask_api.Car_app.models import CarModel
from flask_api import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    email = db.Column(db.String(50), unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('user_role.id'), default=2)

    cars = db.relationship(CarModel, backref='user_id')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_access_token(self):
        token = create_access_token(identity=self.id)
        return token

    def get_refresh_token(self):
        token = create_refresh_token(identity=self.id)
        return token

    def is_admin(self):
        if self.role_id == 1:
            return True
        return False


class UserRole(db.Model):
    __tablename__ = 'user_role'

    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(50), unique=True)

    users = db.relationship(User, backref='role')