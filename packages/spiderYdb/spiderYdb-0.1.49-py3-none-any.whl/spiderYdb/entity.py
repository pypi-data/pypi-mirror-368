from .entityMeta import EntityMeta
from .fields import Field
from .query import Query


class Entity(object, metaclass=EntityMeta):
    def __init__(self, *args, new=True, **kwargs):
        if args:
            raise TypeError('%s constructor accept only keyword arguments. Got: %d positional argument%s'
                                 % (self.__name__, len(args), len(args) > 1 and 's' or ''))
        self.params = dict()
        # print(kwargs)
        for atr in self.attrs_dict:
            attr = self.attrs_dict[atr].copy()
            if atr in kwargs or f"{self.table_name}.{atr}" in kwargs:
                attr.changed = new
                attr.set_value(kwargs.get(atr) if atr in kwargs else kwargs.get(f"{self.table_name}.{atr}"))
            self.params[atr] = attr
        for atr in self.relationship_dict:
            t1 = self._database_.get_table(getattr(self, atr).class_name)
            if not t1: continue
            if any((i.startswith(f'{t1.table_name}.') for i in kwargs)):
                # params1 = {i: kwargs[i] for i in kwargs if i.startswith(f'{t1.table_name}.')}
                self.__setattr__(atr, t1(new=False, **kwargs))
            else:
                if atr in kwargs and isinstance(kwargs[atr], list):
                    # print(kwargs[atr])
                    self.__setattr__(atr, [t1(new=False, **item) for item in kwargs[atr]])
        self._database_.add_item(self)

    @property
    def fields(self):
        return self.__dict__.items()

    @property
    def need_update(self):
        for field in self.params:
            if self.params[field].changed:
                return True

    def save(self, copy=False):
        return Query.save_item(self, copy)



    @classmethod
    def from_dict(cls, obj):
        return cls(new=False, **obj)

    def __getattribute__(self, item):
        field = object.__getattribute__(self, item)
        if isinstance(field, Field):
            return self.params[field.name].value
        return field

    def __setattr__(self, key, value):
        if key in self.attrs_dict:
            field = self.params[key]
            field.value = value
            field.changed = True
        else:
            super(Entity, self).__setattr__(key, value)

    def __str__(self):
        result = [f'{self.__class__.__name__} table {self.table_name}']
        for field in self.params:
            field = self.params[field].value
            if str(field):
                result.append(str(field))
        return str('\n'.join(result))


    def object(self):
        result = {}
        for field in self.params:
            result[field] = self.params[field].value
        for field in self.relationship_dict:
            # print(type(self.__getattribute__(field)))
            if isinstance(self.__getattribute__(field), Entity):
                result[field] = self.__getattribute__(field).object()
            elif isinstance(self.__getattribute__(field), list):
                result[field] = [i.object() for i in self.__getattribute__(field)]
        return result