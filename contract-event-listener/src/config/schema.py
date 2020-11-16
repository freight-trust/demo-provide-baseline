import os
import json
from collections import Counter, namedtuple
import yaml
from marshmallow import Schema, fields, validate, ValidationError, post_load, validates_schema
from marshmallow.fields import Nested


class ConfigSchema(Schema):

    class Meta:
        ordered = True

    @post_load
    def make_named_tuple(self, data, **kwargs):
        cls = self.__class__
        name = cls.__name__.strip('_')
        try:
            cls.__namedtuple
        except AttributeError:
            cls.__namedtuple = namedtuple(name, list(self.fields.keys()))
        values = [data.get(key) for key in self.fields.keys()]
        return self.__class__.__namedtuple(*values)


class PolyNested(Nested):
    def _deserialize(self, value, attr, data, **kwarg):
        for schema in self.nested:
            schema = schema()
            try:
                data = schema.load(value)
            except ValidationError:
                continue
            return data

        nested_schema_names = [s.__name__ for s in self.nested]
        nested_schema_names.sort()
        raise ValidationError(f"Can't deserialize the field using any known schema: {nested_schema_names}")


class Worker(ConfigSchema):
    class __Blockchain(ConfigSchema):
        URI = fields.Str()

    class __General(ConfigSchema):
        PollingInterval = fields.Integer(validate=validate.Range(min=1), missing=5)
        ListenerBlocksLogDir = fields.String(required=True, validate=validate.Length(min=1))
        LoggerName = fields.String(validate=validate.Length(min=1), missing="Inbound Event Listener")

    class __Contract(ConfigSchema):
        class __File(ConfigSchema):
            ABI = fields.String(required=True, validate=validate.Length(min=1))
            Address = fields.String(required=True, validate=validate.Length(min=1))

        class __S3(ConfigSchema):
            Bucket = fields.String(required=True, validate=validate.Length(min=1))
            Key = fields.String(required=True, validate=validate.Length(min=1))
            NetworkId = fields.String(required=True, validate=validate.Length(min=1))

        File = fields.Nested(__File, required=False)
        S3 = fields.Nested(__S3, required=False)

    Blockchain = fields.Nested(__Blockchain, required=True)
    General = fields.Nested(__General, required=True)
    Contract = fields.Nested(__Contract, required=True)


class Listener(ConfigSchema):
    class __Event(ConfigSchema):
        Name = fields.String()
        Filter = fields.Dict(missing=dict())
    Id = fields.String(required=True, validate=validate.Length(min=1))
    Event = fields.Nested(__Event)
    Receivers = fields.List(fields.String(), validate=validate.Length(min=1))


class Receiver(ConfigSchema):
    class Type:
        SQS = 'SQS'
        LOG = 'LOG'
    Id = fields.String(required=True, validate=validate.Length(min=1))
    JSON = fields.Raw(required=False)


class LogReceiver(Receiver):
    Type = fields.String(required=True, validate=validate.Equal(Receiver.Type.LOG))


class SQSReceiver(Receiver):
    class __Config(ConfigSchema):
        AWS = fields.Dict(missing={})
        Message = fields.Dict(missing={})

    Type = fields.String(required=True, validate=validate.Equal(Receiver.Type.SQS))

    QueueUrl = fields.String(required=True)
    Config = fields.Nested(__Config, missing=__Config().load({}))


class Config(ConfigSchema):

    @classmethod
    def from_file(self, filename):
        name, ext = os.path.splitext(filename)
        with open(filename, 'rt') as f:
            if ext in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            elif ext in ['.json']:
                data = json.load(f)
            else:
                raise ValueError(f'Unsupported config file extension "{ext}"')
        return self().load(data)

    Receivers = fields.List(PolyNested([LogReceiver, SQSReceiver]), validate=validate.Length(min=1), required=True)
    Listeners = fields.List(fields.Nested(Listener), validate=validate.Length(min=1), required=True)
    Worker = fields.Nested(Worker, required=True)

    @validates_schema
    def validate(self, config_dict, **kwargs):
        for r in config_dict['Receivers']:
            if r.JSON is not None and not isinstance(r.JSON, (dict, list, str)):
                raise ValidationError(f'Type of JSON field must be [list, dict, str] not {type(r.JSON)}')
        receiver_ids = [r.Id for r in config_dict['Receivers']]
        listener_ids = [l.Id for l in config_dict['Listeners']]
        contract_s3 = config_dict['Worker'].Contract.S3
        constract_file = config_dict['Worker'].Contract.File
        if not (contract_s3 or constract_file):
            raise ValidationError('Config.Worker.Contract.S3 and Config.Worker.Contract.File are undefined')
        elif contract_s3 and constract_file:
            raise ValidationError(
                'Config.Worker.Contract.S3 and Config.Worker.Contract.File can\'t be defined together'
            )
        if receiver_id_duplicates := [k for k, v in Counter(receiver_ids).items() if v > 1]:
            raise ValidationError(f'Receiver id duplicates found {receiver_id_duplicates}')
        if listener_id_duplicates := [k for k, v in Counter(listener_ids).items() if v > 1]:
            raise ValidationError(f'Listener id duplicates found {listener_id_duplicates}')
        for listener in config_dict['Listeners']:
            for id in listener.Receivers:
                if id not in receiver_ids:
                    raise ValidationError(f'Receiver "{id}" not found')
