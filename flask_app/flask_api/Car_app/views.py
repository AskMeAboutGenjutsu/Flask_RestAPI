from flask import request, jsonify, Blueprint
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from flask_api.User_app.models import User
from flask_api import db
from flask_api.Car_app.models import CarModel, CarBrandModel
from flask_api.Car_app.schemes import CarSchema, CarBrandSchema

car_app_bp = Blueprint('cars', __name__)


class CarAPIView(MethodView):
    init_every_request = False
    decorators = [jwt_required()]

    model = CarModel
    schema = CarSchema()
    brand_model = CarBrandModel
    user = User

    def _get_item(self, id):
        return self.model.query.filter(self.model.id == id)

    def get(self, id):
        item = self._get_item(id).join(self.brand_model).join(self.user)\
            .with_entities(
            self.model.id,self.brand_model.name.label('brand'),
            self.model.model, self.model.price, self.user.name.label('owner')
            ).one()

        if item is None:
            return jsonify({'message': {'id': 'Invalid id'}}), 400

        return self.schema.dump(item), 200

    def patch(self, id):
        item = self._get_item(id).one()
        if item is None:
            return jsonify({'message': {'id': 'Invalid id'}}), 400

        if item.owner_id != get_jwt_identity():
            return jsonify({'message': 'You are not the owner'}), 403

        try:
            params = self.schema.load(request.json)
        except ValidationError as e:
            return jsonify({'message': e.messages}), 400
        for key, value in params.items():
            setattr(item, key, value)
        db.session.commit()
        return self.schema.dump(item)

    def delete(self, id):
        item = self._get_item(id).one()
        if item is None:
            return jsonify({'message': {'id': 'Invalid id'}}), 400

        if item.owner_id != get_jwt_identity():
            return jsonify({'message': 'You are not the owner'}), 403

        db.session.delete(item)
        db.session.commit()
        return '', 204


class CarsAPIView(MethodView):
    init_every_request = False
    decorators = [jwt_required()]

    model = CarModel
    schema = CarSchema()
    brand_model = CarBrandModel
    user = User

    def get(self):
        items = self.model.query.join(self.brand_model).join(self.user)\
            .with_entities(
            self.model.id,self.brand_model.name.label('brand'),
            self.model.model, self.model.price, self.user.name.label('owner'))\
            .all()

        items_schema = self.schema
        items_schema.many = True
        return items_schema.dump(items), 200

    def post(self):
        try:
            data = self.schema.load(request.json)
        except ValidationError as e:
            return jsonify({'message': e.messages}), 400

        data['owner_id'] = get_jwt_identity()
        item = self.model(**data)
        db.session.add(item)
        db.session.commit()
        return self.schema.dump(item), 201


class CarBrandAPIView(MethodView):
    init_every_request = False
    decorators = [jwt_required()]
    model = CarBrandModel
    schema = CarBrandSchema()
    user = User

    def _is_admin(self, id):
        return self.user.query.filter(self.user.id == id).one().is_admin()

    def _get(self, id):
        return self.model.query.filter(self.model.id == id).one()

    def get(self, id):
        item_schema = self.schema
        if id is None:
            item = self.model.query.all()
            item_schema.many = True
        else:
            item = self._get(id)
            if item is None:
                return jsonify({'message': {'id': 'Invalid id'}}), 400

        return item_schema.dump(item), 200

    def post(self):
        if not self._is_admin(get_jwt_identity()):
            return jsonify({'message': "You don't have enough authority"}), 403
        try:
            data = self.schema.load(request.json)
        except ValidationError as e:
            return jsonify({'message': e.messages}), 400

        item = self.model(**data)

        db.session.add(item)
        db.session.commit()
        return self.schema.dump(item), 201

    def patch(self, id):
        if not self._is_admin(get_jwt_identity()):
            return jsonify({'message': "You don't have enough authority"}), 403

        item = self._get(id)

        if item is None:
            return jsonify({'message': {'id': 'Invalid id'}}), 400

        try:
            params = self.schema.load(request.json)
        except ValidationError as e:
            return jsonify({'message': e.messages}), 400

        for key, value in params.items():
            setattr(item, key, value)

        db.session.commit()
        return self.schema.dump(item)

    def delete(self, id):
        if not self._is_admin(get_jwt_identity()):
            return jsonify({'message': "You don't have enough authority"}), 403

        item = self._get(id)

        if item is None:
            return jsonify({'message': {'id': 'Invalid id'}}), 400

        db.session.delete(item)
        db.session.commit()
        return '', 204


car_brand_view = CarBrandAPIView.as_view('car-brand')
car_app_bp.add_url_rule('/cars/<int:id>', view_func=CarAPIView.as_view('car-item'))
car_app_bp.add_url_rule('/cars/', view_func=CarsAPIView.as_view('car-group'))
car_app_bp.add_url_rule('/cars_brand/', defaults={'id': None},
                        view_func=car_brand_view, methods=['GET'])
car_app_bp.add_url_rule('/cars_brand/', view_func=car_brand_view, methods=['POST'])
car_app_bp.add_url_rule('/cars_brand/<int:id>', view_func=car_brand_view, methods=['GET', 'PATCH', 'DELETE'])


@car_app_bp.errorhandler(500)
def handle_error(err):
    return jsonify({'Invalid request': request.json}), 400
