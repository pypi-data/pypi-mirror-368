from ydb import PrimitiveType, OptionalType
# import uuid
import shortuuid
import json
import copy

shortuuid.set_alphabet("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")


class Relationship:
    def __init__(self, class_name):
        self.class_name = class_name


class Field:
    title = 'String'
    ydb_type = None
    value = None

    def __init__(self, pk=False, optional=True, fk=None):
        self.pk = pk
        self.optional = optional
        self.foreign_key = fk if fk else []
        # if not pk:
        #     print('type', type(self.ydb_type))
        #     self.ydb_type = OptionalType(self.ydb_type)
        self.changed = False

    def __eq__(self, other):
        # ==
        return '=', self, other

    def __ne__(self, other):
        # !=
        return '!=', self, other

    def __lt__(self, other):
        # <
        return '<', self, other

    def __le__(self, other):
        # <=
        return '<=', self, other

    def __gt__(self, other):
        # >
        return '>', self, other

    def __ge__(self, other):
        # >=
        return '>=', self, other

    def in_(self, other):
        return 'in', self, other

    def is_null(self):
        return 'is NULL', self, None


    def ilike(self, other):
        return 'ILIKE', self, other

    def __str__(self):
        if hasattr(self, 'value'):
            return str(self.value)
        return 'None'

    def _init_(self, table, name):
        self.table = table
        self.name = name

    @property
    def need_update(self):
        if self.pk or (hasattr(self, 'value') and self.changed):
            return True

    @property
    def to_save(self):
        return self.value

    def copy(self):
        obj = copy.copy(self)
        return obj

    def set_value(self, value):
        self.value = value


class Utf8(Field):
    title = 'Utf8'
    ydb_type = PrimitiveType.Utf8
    value = ''

    def concat(self, other):
        q = type(self.title+other.title, (Utf8,), dict())
        q.name = self.name + ' || ' + other.name
        return q()

class Uuid(Utf8):
    @staticmethod
    def new():
        return shortuuid.uuid()

    def __getattr__(self, item):
        if item == 'value' and self.pk:
            value = self.new()
            self.value = value
            self.changed = True
            return value
        else:
            raise AttributeError(f"{self.__class__.__name__} object has no attribute {item}")

    def __getattribute__(self, item):
        field = object.__getattribute__(self, item)
        if item == 'value':
            if not field:
                field = self.new()
                self.value = field
        return field


class Int64(Field):
    title = 'Int64'
    ydb_type = PrimitiveType.Int64
    value = 0


class Uint64(Field):
    title = 'Uint64'
    ydb_type = PrimitiveType.Uint64
    value = 0


class Bool(Field):
    title = 'Bool'
    ydb_type = PrimitiveType.Bool
    value = False


class Datetime(Field):
    title = 'Datetime'
    ydb_type = PrimitiveType.Datetime
    value = 0

class Date(Datetime):
    title = 'Date'
    ydb_type = PrimitiveType.Date

class Json(Field):
    title = 'Json'
    ydb_type = PrimitiveType.Json

    def set_item(self, d):
        class CheckDict(dict):
            def __setitem__(self_, key, value):
                if value != self_.get(key):
                    self.changed = True
                dict.__setitem__(self_, key, value)

        dc = CheckDict()
        dc.update(d)
        return dc

    def __getattribute__(self, item):
        field = object.__getattribute__(self, item)
        if item == 'value':
            if isinstance(field, dict) or isinstance(field, list):
                return field
            if field:
                try:
                    value = json.loads(field, object_hook=self.set_item)
                except Exception as e:
                    value = json.loads('{}', object_hook=self.set_item)
            else:
                value = json.loads('{}', object_hook=self.set_item)
            self.value = value
            return value
        return field

    def __str__(self):
        if hasattr(self, 'value'):
            try:
                value = json.loads(self.value)
            except:
                value = self.value
        else:
            value = ''
        return str(value)

    @property
    def to_save(self):
        value = object.__getattribute__(self, 'value')
        if isinstance(self.value, dict) or isinstance(self.value, list):
            return json.dumps(value)
        return value


class JsonUtf8(Json):
    title = 'Utf8'
    ydb_type = PrimitiveType.Utf8



class Float(Field):
    title = "Float"
    ydb_type = PrimitiveType.Float
