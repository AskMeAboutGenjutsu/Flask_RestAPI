from marshmallow import Schema, fields, validate


class CarBrandSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=50))

    class Meta:
        ordered = True


class CarSchema(Schema):
    id = fields.Int(dump_only=True)
    brand_id = fields.Int(load_only=True)
    brand = fields.Str(dump_only=True)
    model = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    price = fields.Int(required=True, validate=validate.Range(min=0))
    owner = fields.Str(dump_only=True)

    class Meta:
        ordered = True

