from marshmallow import Schema, fields, validate


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=32))
    email = fields.Email(required=True, validate=validate.Length(max=50))
    password = fields.Str(load_only=True)

    class Meta:
        ordered = True