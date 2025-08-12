import inspect
import typing
import warnings

from rebotics_sdk.rcdb.fields import (
    FeatureVectorField,
    ImageField,
    StringField,
)

if typing.TYPE_CHECKING:
    from rebotics_sdk.rcdb.fields import BaseField


class Options:
    fields: typing.Dict[str, 'BaseField']

    def __init__(self, cls):
        self.cls = cls
        self.fields = {}  # name: field

    def add_field(self, name, field):
        if name in self.fields:
            raise ValueError(f'Field with name {name} already exists.')
        self.fields[name] = field


def _has_contribute_to_class(obj):
    return hasattr(obj, 'contribute_to_class') and not inspect.isclass(obj)


class BaseEntryMeta(type):
    """Base entry metaclass."""

    def __new__(cls, name, bases, attrs, **kwargs):
        super_new = super().__new__

        new_attrs = {}

        contributable_attrs = {}
        for obj_name, obj in attrs.items():
            if _has_contribute_to_class(obj):
                contributable_attrs[obj_name] = obj
            else:
                new_attrs[obj_name] = obj

        new_class = super_new(cls, name, bases, new_attrs, **kwargs)
        new_class.add_to_class('options', Options(new_class))
        # might need to add mro here

        for obj_name, obj in contributable_attrs.items():
            new_class.add_to_class(obj_name, obj)

        return new_class

    def add_to_class(cls, name, value):
        if hasattr(value, 'contribute_to_class'):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)


class BaseEntry(metaclass=BaseEntryMeta):
    """
        Shameless copy of the django.db.models.Model class with minimal required functionality.
        Because MRO is not implemented, all custom entries has to inherit from this class.
    """
    options: Options

    def __init__(self, **kwargs):
        # instead of _meta making options public, so packer and unpacker can extend and work with it
        opts = self.options
        if not opts.fields:
            raise ValueError(f"{self.__class__.__name__} has no fields registered.")

        # intentionally do not support args, only kwargs
        for field in opts.fields.values():
            value = kwargs.pop(field.name, None)
            setattr(self, field.name, value)

        if kwargs:
            # some fields that are not registered into the Entry
            warnings.warn(f"Unknown values supplied for Entry: {kwargs}")

    def __str__(self):
        return f'{self.__class__.__name__}'

    def dict(self):
        fields = self.options.fields

        return {
            field_name: getattr(self, field_name)
            for field_name in fields
        }

    def is_empty(self):
        per_field_emptyness = {
            field.name: field.is_empty(self)
            for field in self.options.fields.values()
        }
        return all(per_field_emptyness.values())

    @classmethod
    def get_field_to_filename_map(cls):
        field_to_filename_map = {}
        for field_name, field in cls.options.fields.items():
            field_to_filename_map[field_name] = field.get_filename(None)
        return field_to_filename_map

    @classmethod
    def decompose(cls):
        return {
            'name': cls.__name__,
            'module': cls.__module__,
            'fields': {
                field_name: field.decompose()
                for field_name, field in cls.options.fields.items()
            }
        }


class ImportEntry(BaseEntry):
    label = StringField()
    feature_vector = FeatureVectorField()
    image = ImageField()


ETV = typing.TypeVar('ETV', bound=BaseEntry)
