from flask import request, jsonify, Blueprint
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from flask_api.User_app.models import User
from flask_api.User_app.schemes import UserSchema
from flask_api import db


user_app_bp = Blueprint('users', __name__)


class UserAPIView(MethodView):
    init_every_request = False
    decorators = [jwt_required()]
    model = User
    schema = UserSchema()

    def _get_user(self, id):
        return self.model.query.filter(self.model.id == id).one()

    def get(self, id):
        item = self._get_user(id)
        if item is None:
            return jsonify({'message': {'id': 'Invalid id'}}), 400

        if id != get_jwt_identity():
            return jsonify({'message': 'You are not the owner'}), 403

        return self.schema.dump(item), 200

    def patch(self, id):
        item = self._get_user(id)
        if item is None:
            return jsonify({'message': {'id': 'Invalid id'}}), 400

        if id != get_jwt_identity():
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
        item = self._get_user(id)
        if item is None:
            return jsonify({'message': {'id': 'Invalid id'}}), 400

        if id != get_jwt_identity():
            return jsonify({'message': 'You are not the owner'}), 403

        db.session.delete(item)
        db.session.commit()
        return '', 204


@user_app_bp.route('/register', methods=['POST'])
def register():
    schema = UserSchema()
    try:
        data = schema.load(request.json)
        user = User(**data)
        db.session.add(user)
        db.session.commit()
    except ValidationError as e:
        return jsonify({'message': e.messages}), 400
    except IntegrityError:
        return jsonify({'message': 'User with this email already exists'}), 400

    return jsonify({'access_token': user.get_access_token(), 'refresh_token': user.get_refresh_token()}), 201


@user_app_bp.route('/login', methods=['POST'])
def login():
    try:
        user = User.query.filter(User.email == request.json.get('email')).one()
        if user.verify_password(request.json.get('password')):
            return jsonify({'access_token': user.get_access_token(), 'refresh_token': user.get_refresh_token()}), 200

    except Exception:
        return jsonify({'error': 'Invalid email or password'}), 400


@user_app_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    user = User.query.filter(User.id == identity).one()
    return jsonify({'access_token': user.get_access_token()})


@user_app_bp.errorhandler(500)
def handle_error(err):
    return jsonify({'Invalid request': request.json}), 400


user_app_bp.add_url_rule('/profile/<int:id>', view_func=UserAPIView.as_view('user'))
