import typing
from copy import copy

from rebotics_sdk.rcdb.entries import BaseEntry, ETV
from rebotics_sdk.rcdb.fields import BaseField, FeatureVectorField, ImageField, RemoteImageField, StringField, \
    UUIDField, detect_field_class_by_name
from rebotics_sdk.rcdb.meta import Metadata


class EntryTypeBuilder:
    def __init__(self, base_cls: typing.Type[BaseEntry] = None):
        if base_cls is None:
            base_cls = BaseEntry
        self.base_cls = base_cls
        self.fields = copy(self.base_cls.options.fields)

    def add_field(self, name, field: BaseField):
        if name in self.fields:
            raise ValueError(f'Field with name {name} already exists.')

        if not isinstance(field, BaseField):
            # when you don't set proper BaseField subclassed object, the field will not be registered
            # meaning that it will not function properly
            raise ValueError(f'Field {name} is not an instance of BaseField.')

        self.fields[name] = field

    def build(self) -> typing.Type[ETV]:
        return type('Entry', (self.base_cls,), self.fields)  # noqa

    @classmethod
    def construct_from_metadata(cls, metadata: 'Metadata') -> typing.Type[ETV]:
        # create a class with fields that are available in metadata
        # check if we have files in metadata
        # if yes, then we need to read them to get the format of the fields

        entry_type_builder = cls()
        if metadata.packer_version == 4:
            for field_name, filename in metadata.files[0].items():
                # read the first file and try to detect the format
                column_name, ext = filename.split('.')
                field_cls = detect_field_class_by_name(field_name)
                entry_type_builder.add_field(field_name, field_cls(extension=ext, column_name=column_name))

            return entry_type_builder.build()

        # need to list all files in archive and try to initialize entry_type
        # or try to read predefined files that we can actually find and read
        # default available fields across all versions
        entry_type_builder.add_field('label', StringField(extension='txt', column_name='labels'))
        entry_type_builder.add_field('feature_vector', FeatureVectorField(extension='txt', column_name='features'))

        if metadata.packer_version == 1:
            if metadata.images:
                # need to read arcnames for images and create ImageField
                entry_type_builder.add_field('image', ImageField())

        if metadata.packer_version == 2:
            # this means it is an archive with RemoteImageField
            entry_type_builder.add_field('image_url', RemoteImageField())
            entry_type_builder.add_field('uuid', UUIDField())

        if metadata.packer_version == 3:
            # read additional files from meta to find known usages
            for arcname, _ in metadata.additional_files:
                if 'features_uuid' in arcname:
                    # found in CORE at common.classification.actions
                    entry_type_builder.add_field('uuid', UUIDField(column_name='features_uuid'))

        # single batch with multiple files
        entry_type: typing.Type[ETV] = entry_type_builder.build()
        return entry_type
