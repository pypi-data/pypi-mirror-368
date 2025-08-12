import io
import pathlib
import typing
import uuid

import numpy as np

if typing.TYPE_CHECKING:
    from rebotics_sdk.rcdb.entries import BaseEntry
    from rebotics_sdk.rcdb.service import Unpacker, Packer


class DataGenerator:
    def __init__(self, descriptor):
        self.descriptor = descriptor
        # data = self.descriptor.readlines()
        # self.iterator = iter(data)
        self.counter = 0

    def readline(self):
        try:
            result = self.descriptor.readline()
            self.counter += 1
            return result
        except StopIteration:
            return None

    def close(self):
        # self.iterator = None
        self.descriptor.close()


class BinaryFeatureVectorDataGenerator(DataGenerator):
    def __init__(self, descriptor, record_length_bytes: int):
        super().__init__(descriptor)
        self.record_length_bytes = record_length_bytes

    def readline(self):
        try:
            result = self.descriptor.read(self.record_length_bytes)
            self.counter += 1
            return result
        except StopIteration:
            return None


class DeferredAttribute:
    def __init__(self, field):
        self.field = field

    def __get__(self, instance, cls=None):
        if instance is None:
            return self
        data = instance.__dict__
        field_name = self.field.name
        if field_name not in instance.options.fields:
            raise ValueError(f'Field {field_name} is not initialized.')

        if field_name not in data:
            # there is no value set
            return self.field.default
        return data[field_name]

    def __getattr__(self, item):
        if hasattr(self.field, item):
            return getattr(self.field, item)
        raise AttributeError(f'Field {self.field.name} has no attribute {item}')

    def __set__(self, instance, value):
        data = instance.__dict__
        field_name = self.field.name
        data[f'raw_{field_name}'] = value

        if value is None and self.field.null:  # if null is allowed
            if self.field.default is not None:
                data[field_name] = self.field.default
            return

        data[field_name] = self.field.to_python(value)


class BaseField:
    descriptor_class = DeferredAttribute
    column_name: str = None
    name: typing.Optional[str] = None
    extension: str = 'txt'
    text_wrap = True

    write_mode = 'w'
    read_mode = 'r'

    def __init__(self, *, column_name=None, extension=None, default=None, null=False):
        self.name = None
        self.base_entry = None

        if extension is not None:
            self.extension = extension

        if column_name is not None:
            self.column_name = column_name

        self.default = default
        self.null = null

    def contribute_to_class(self, cls: typing.Type['BaseEntry'], name):
        self.name = name
        self.base_entry = cls

        if self.column_name is None:
            # if the column name is still None, use the name attribute
            self.column_name = name

        # here is the magic shenanigans that we need to do
        cls.options.add_field(name, self)  # noqa
        setattr(cls, self.name, self.descriptor_class(self))

    def read_from_rcdb(self, *, index: int, descriptor: io.IOBase, unpacker: 'Unpacker'):
        if descriptor is None:
            return None
        return descriptor.readline()

    def write_to_rcdb(self, value, *, index, descriptor, packer: 'Packer'):
        descriptor.write(self.to_rcdb(value))

    def to_python(self, value):
        return value

    def to_rcdb(self, value):
        return f'{value}\n'

    def get_filename(self, batch_number=None):
        if batch_number is None:
            return f'{self.column_name}.{self.extension}'
        return f'{self.column_name}_{batch_number}.{self.extension}'

    def wrap_descriptor(self, descriptor):
        if self.text_wrap:
            return io.TextIOWrapper(descriptor)
        else:
            return descriptor

    def make_generator(self, descriptor):
        if descriptor is None:
            return descriptor

        # this will read the file into the memory completely
        return DataGenerator(descriptor)

    def get_raw_value(self, instance):
        if hasattr(instance, f'raw_{self.name}'):
            return getattr(instance, f'raw_{self.name}')
        return None

    def is_empty(self, instance):
        raw_value = self.get_raw_value(instance)
        return raw_value is None

    def decompose(self):
        properties = dict(vars(self))
        properties.pop('base_entry', None)

        cls_properties = dict(vars(self.__class__))
        properties['column_name'] = cls_properties.get('column_name')

        return {
            'module': self.__class__.__module__,
            'class_name': self.__class__.__name__,
            'properties': {
                "column_name": self.column_name,
                "name": self.name,
                "extension": self.extension,
                "text_wrap": self.text_wrap,
                **properties
            }
        }

    def __str__(self):
        return f'<{self.__class__.__name__} >'


class StringField(BaseField):
    # no changes
    def to_rcdb(self, value):
        return f"{value}\n"

    def to_python(self, value):
        if value is None:
            return None
        if isinstance(value, bytes):
            value = value.decode()
            value.strip()
        return str(value).strip()

    def is_empty(self, instance):
        raw_value = self.get_raw_value(instance)
        if raw_value is None:
            return True
        return str(raw_value).strip() == ''


class BooleanField(StringField):
    def to_rcdb(self, value):
        return super().to_rcdb(int(value))

    def to_python(self, value):
        val = super().to_python(value)
        if not val:
            return self.default

        val = val.lower()
        if val in ('true', '1', 'yes'):
            return True
        elif val in ('false', '0', 'no'):
            return False
        else:
            raise ValueError(f'Cannot convert {value} to boolean')


class FeatureVectorField(StringField):
    text_wrap = True

    column_name = 'features'

    def __init__(self, dtype=np.float32, length=512, **kwargs):
        super().__init__(**kwargs)
        self.dtype = dtype
        self.length = length

    def to_python(self, value):
        # convert from str or binary to List[float]
        # assume that internal representation of the field is a List[float]
        if value is None:
            return None

        if isinstance(value, bytes):
            value = value.decode()

        if isinstance(value, str):
            value = value.strip().strip('[]')
            if value == '':
                return None
            return np.fromstring(value, dtype=self.dtype, sep=',')
        return np.array(value, dtype=self.dtype)

    def to_rcdb(self, value):
        if value is None:
            return ''

        # convert from List[float] to str or binary
        rendered_string = ','.join(map(str, value))
        # maybe code it to ascii??
        # or better to binary later on
        return f"{rendered_string}\n"


class BinaryFeatureVectorField(FeatureVectorField):
    """
    A field that serializes feature vectors as binary data to pack RCDB archives more efficient.
    Inner representation of data is a result of numpy.ndarray.tobytes() call.
    """
    column_name = "features_binary"
    extension = "eba"
    write_mode = "wb"
    read_mode = "rb"

    def wrap_descriptor(self, descriptor):
        return io.BufferedReader(descriptor)

    def make_generator(self, descriptor):
        if descriptor is None:
            return descriptor

        # this will read the file into the memory completely
        return BinaryFeatureVectorDataGenerator(descriptor, self.length * np.dtype(self.dtype).itemsize)

    def read_from_rcdb(self, *, index: int, descriptor: DataGenerator, unpacker: 'Unpacker'):
        if descriptor is None:
            return None

        return descriptor.readline()

    def to_python(self, value: bytes):
        return np.frombuffer(value, dtype=self.dtype)

    def to_rcdb(self, value: bytes) -> bytes:
        return value

    def is_empty(self, instance):
        raw_value = self.get_raw_value(instance)
        return np.count_nonzero(np.frombuffer(raw_value, dtype=self.dtype)) >= 0


class RemoteImageField(StringField):
    """A file with image urls in the same order as the entries."""
    column_name = 'images'


class ImageField(StringField):
    column_name = 'images'
    text_wrap = True

    def read_from_rcdb(self, index: int, descriptor: io.IOBase, unpacker: 'Unpacker'):
        if descriptor is None:
            if not unpacker.metadata.images:
                return None
            # assume it is a proper index and string
            # surely support images that we have in the metadata
            # in other words support packer version 1
            try:
                image_name = unpacker.metadata.images[index]
                image_name = f'images/{image_name}'
            except IndexError:
                return None  # we reached the end of the file
        else:
            image_name = self.to_python(descriptor.readline())  # load string properly

        if not image_name:
            return None
        return unpacker.archive.read(image_name)

    def write_to_rcdb(self, value: typing.Union[str, pathlib.Path],
                      *, index, descriptor, packer: 'Packer'):
        if hasattr(value, 'read'):
            arcname = f"images/{pathlib.Path(value.name).name}"
            return packer.archive.writestr(value.read(), arcname)

        arcname = f"images/{pathlib.Path(value).name}"
        if descriptor is None:
            if not packer.metadata.images:
                return
            packer.metadata.images[index] = arcname
        else:
            super().write_to_rcdb(arcname, index=index, descriptor=descriptor, packer=packer)
        packer.archive.write(value, arcname)

    def to_python(self, value):
        if hasattr(value, 'read'):
            return value
        return super().to_python(value)

    def wrap_descriptor(self, descriptor):
        if descriptor is None:
            return None
        return super().wrap_descriptor(descriptor)


class UUIDField(StringField):
    column_name = 'uuid'

    def to_python(self, value):
        value = super().to_python(value)
        if not value:
            return None
        return uuid.UUID(value)

    def to_rcdb(self, value):
        value = super().to_rcdb(value)
        if value is None:
            return ''
        if isinstance(value, uuid.UUID):
            value = value.hex
        return value


def detect_field_class_by_name(name: str) -> typing.Type[BaseField]:
    if name in ('feature_vector_binary', 'features_binary', 'fvb'):
        return BinaryFeatureVectorField
    if name in ('feature_vector', 'features', 'fv'):
        return FeatureVectorField
    if name in ('image', 'images'):
        return RemoteImageField
    if name in ('uuid', 'uuids'):
        return UUIDField
    if name in ('synthetic', 'is_active', 'active', 'mark_for_deactivate'):
        return BooleanField
    return StringField
