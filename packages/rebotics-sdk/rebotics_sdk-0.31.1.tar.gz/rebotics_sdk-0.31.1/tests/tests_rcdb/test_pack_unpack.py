import hashlib
import pathlib
import uuid
import zipfile

import numpy as np
import pytest

from rebotics_sdk.advanced.packers import ClassificationDatabasePacker
from rebotics_sdk.rcdb.entries import BaseEntry
from rebotics_sdk.rcdb import EntryTypeBuilder, ZipArchiver
from rebotics_sdk.rcdb.fields import StringField, FeatureVectorField, UUIDField, RemoteImageField, ImageField, \
    BooleanField
from rebotics_sdk.rcdb.service import Packer, Unpacker


class RawEntry(BaseEntry):
    id = StringField()
    label = StringField(column_name='labels')
    feature_vector = FeatureVectorField()


class RawEntryWithSynthetic(RawEntry):
    # for the future, we have to be able to inherit from the entry
    # so to do that we have to walk through mro and add contributable fields to the entry.options
    id = StringField()
    label = StringField(column_name='labels')
    feature_vector = FeatureVectorField()
    synthetic = BooleanField(default=False)


class RawEntryWithNonsenseFields(BaseEntry):
    id = StringField()
    uuid = UUIDField(null=True, default=None)
    label = StringField(column_name='labels')
    feature_vector = FeatureVectorField()
    image_url = RemoteImageField()
    image = ImageField()


test_data = {
    'id': '1',
    'label': 'test',
    'feature_vector': [1, 2, 3],
    'synthetic': False,
    'unknown_field': 'vasya_pupkin',
}


def test_basic_packing(tmp_path):
    """Basic packing on the items that are provided"""
    with Packer(tmp_path / 'test_file.rcdb',
                entry_type=RawEntryWithSynthetic,
                model_codename='arcface_123123') as packer:
        packer.add_entry(RawEntryWithSynthetic(**test_data))
    assert packer.metadata.model_codename == 'arcface_123123'
    assert packer.metadata.model_type == 'arcface'

    assert len(packer.metadata.files) == 1, 'Only one batch should be present'
    files = packer.metadata.files[0]
    assert files['id'] == 'id.txt', 'name should be set as a name of the field'
    assert files['label'] == 'labels.txt', 'filename is set in the field'
    assert files['feature_vector'] == 'features.txt', 'filename is set ' \
                                                      'because FeatureVectorField has a default column name'

    with Unpacker(tmp_path / 'test_file.rcdb', entry_type=RawEntry) as unpacker:
        for i, entry in enumerate(unpacker.entries()):
            assert entry.id == test_data['id'], entry.dict()
            assert entry.label == test_data['label']
            assert entry.feature_vector.tolist() == test_data['feature_vector']

    assert i == 0, "there should be only one entry"

    # test to autodetect what entry it is and what fields it may have
    with Unpacker(tmp_path / 'test_file.rcdb') as unpacker:
        for i, entry in enumerate(unpacker.entries()):
            assert entry.id == test_data['id'], entry.dict()
            assert entry.label == test_data['label']
            assert entry.feature_vector.tolist() == test_data['feature_vector']
    assert i == 0, "there should be only one entry"

    # test unpacker with nonsense fields
    with Unpacker(tmp_path / 'test_file.rcdb', entry_type=RawEntryWithNonsenseFields) as unpacker:
        i = 0
        for entry in unpacker.entries():
            i += 1
            assert entry.uuid is None
            assert entry.image_url is None

            # everything else should be setup properly
            assert entry.id == test_data['id'], entry.dict()
            assert entry.label == test_data['label']
            assert entry.feature_vector.tolist() == test_data['feature_vector']

            with pytest.raises(AttributeError):
                entry.vasya_pupkin  # noqa

        assert i == 1, "there should be only one entry"


def test_write_to_opened_file(tmp_path):
    file = tmp_path / 'test_file.rcdb'
    with open(file, 'wb') as f:
        with Packer(f, entry_type=RawEntry) as packer:
            packer.add_entry(RawEntry(**test_data))
        assert packer.metadata.model_codename is None
        assert packer.metadata.model_type == 'facenet'

    with open(file, 'rb') as f:
        with Unpacker(f, entry_type=RawEntryWithSynthetic) as unpacker:
            for i, entry in enumerate(unpacker.entries()):
                assert entry.id == '1', entry.dict()
                assert entry.label == 'test'
                assert entry.feature_vector.tolist() == [1, 2, 3]
                assert entry.synthetic is False, "Synthetic default value should be set"
            assert i == 0


def test_write_to_internally_create_file_io():
    with Packer(destination=None, entry_type=RawEntry) as packer:
        packer.add_entry(RawEntry(**test_data))
    bytes_io = packer.output_file
    bytes_io.seek(0)

    with Unpacker(bytes_io, entry_type=RawEntry) as unpacker:
        for i, entry in enumerate(unpacker.entries()):
            assert entry.id == '1', entry.dict()
            assert entry.label == 'test'
            assert entry.feature_vector.tolist() == [1, 2, 3]
        assert i == 0


def test_attributes_set():
    entry = RawEntry(id=123, label=123123, feature_vector=[1, 2, 3])
    assert entry.id == '123', 'transformation to_python should be called'
    assert entry.label == '123123'
    assert entry.feature_vector.tolist() == np.array([1, 2, 3], dtype=np.float32).tolist()  # noqa

    assert RawEntry.id.to_python(123) == '123'
    assert RawEntry.label.to_python(123) == '123'

    data = entry.dict()
    assert data['id'] == '123'
    assert data['label'] == '123123'
    assert data['feature_vector'].tolist() == np.array([1, 2, 3], dtype=np.float32).tolist()


def test_empty_entry():
    entry = RawEntry(id=None, label=None, feature_vector=None)
    assert entry.is_empty(), "this entry should be empty"
    entry = RawEntry(id=123, label=None, feature_vector=None)
    assert not entry.is_empty(), "this entry should not be empty"

    entry = RawEntry(id='', label='', feature_vector='')
    assert entry.is_empty(), "this entry should be empty because it is string empty"

    entry = RawEntry(id=0, label=0, feature_vector=0)
    assert not entry.is_empty(), "this entry should not be empty because it is not string empty"


def test_do_not_populate_all_fields_in_unpack(tmp_path):
    """Test if we don't populate one of the fields, it should be None"""
    with Packer(tmp_path / 'test_file_not_all_fields.rcdb', entry_type=RawEntry) as packer:
        packer.add_entry(RawEntry(id=123, label=123123, feature_vector=None))

    with Unpacker(tmp_path / 'test_file_not_all_fields.rcdb', entry_type=RawEntry) as unpacker:
        for entry in unpacker.entries():
            assert entry.id == '123'
            assert entry.label == '123123'
            assert entry.feature_vector is None


def test_unknown_field_attributes():
    with pytest.raises(AttributeError):
        _ = RawEntry.id.vasya_pupkin  # noqa


def test_known_field_attributes():
    assert RawEntry.id.column_name == 'id'
    assert RawEntry.label.column_name == 'labels'
    assert RawEntry.feature_vector.column_name == 'features'
    assert RawEntry.id.extension == 'txt'
    assert RawEntry.label.extension == 'txt'
    assert RawEntry.feature_vector.extension == 'txt'
    assert RawEntry.id.text_wrap
    assert RawEntry.id.text_wrap
    assert RawEntry.id.text_wrap


def test_unpack_mjhd_960(script_cwd: pathlib.Path):
    """Try to read an existing rcdb file generated by CORE on mjhd_960 example from r3us-admin"""
    rcdb_file = script_cwd / 'mjhd_960.rcdb'
    assert rcdb_file.exists()
    with Unpacker(rcdb_file) as unpacker:
        metadata = unpacker.get_metadata()
        assert metadata.packer_version == 1
        assert metadata.count == 254, 'There are 254 feature vectors with images'

        assert unpacker.entry_type is not None, "After reading metadata, entry type should be populated"
        assert unpacker.entry_type.options.fields

        assert 'image' in unpacker.entry_type.options.fields, 'There should be an image field in the entry type'

        for i, entry in enumerate(unpacker.entries()):
            if i == 0:
                # do assert statements only for the first entry
                assert len(entry.feature_vector.tolist()) == 512, \
                    "Check that there is at least a feature vector with correct number of features"
                assert entry.image is not None, "The image can be read automatically " \
                                                "without specifying in the entry type"

        assert i == 254 - 1, "After reading all entries, the total count should be 254, starting from 0"


class ImageEntry(BaseEntry):
    label = StringField(column_name='labels')
    feature_vector = FeatureVectorField(column_name='features')
    image = ImageField(column_name='images')


def test_unpack_mjhd_960_with_image(script_cwd: pathlib.Path):
    rcdb_file = script_cwd / 'mjhd_960.rcdb'
    assert rcdb_file.exists()

    with Unpacker(rcdb_file, entry_type=ImageEntry) as unpacker:
        metadata = unpacker.get_metadata()
        assert metadata.packer_version == 1
        for entry in unpacker.entries():
            assert entry.label is not None
            assert entry.feature_vector is not None
            assert entry.image is not None
            break


def test_pack_with_images_image(tmp_path, script_cwd):
    image_path = script_cwd / '..' / 'db' / 'custom_folder' / 'image_1.png'
    with Packer(tmp_path / 'test_file.rcdb', entry_type=ImageEntry) as packer:
        packer.add_entry(ImageEntry(label="123123", feature_vector=[1, 2, 3], image=image_path))

    with open(image_path, 'rb') as fio:
        image_hash = hashlib.md5(fio.read()).hexdigest()

    with Unpacker(tmp_path / 'test_file.rcdb', entry_type=ImageEntry) as unpacker:
        for entry in unpacker.entries():
            assert entry.label == "123123"
            assert entry.feature_vector.tolist() == [1, 2, 3]
            assert entry.image is not None
            image_hash_2 = hashlib.md5(entry.image.read()).hexdigest()
            assert image_hash == image_hash_2, "Two images in archive and out archive should have the same hash"


def test_batching(tmp_path):
    batch_size = 10
    with Packer(tmp_path / 'test_file.rcdb', entry_type=RawEntry, batch_size=batch_size) as packer:
        for i in range(100):
            packer.add_entry(RawEntry(id=i, label=i, feature_vector=[i, i, i]))

    assert packer.entries_count == 100, 'There should be 100 entries'
    assert packer.batch_counter == 11, 'There should be 10 batches'
    assert len(packer.metadata.files) == 10, 'There should be 10 batches'

    with Unpacker(tmp_path / 'test_file.rcdb', entry_type=RawEntry) as unpacker:
        i = 0
        for i, entry in enumerate(unpacker.entries()):
            assert entry.feature_vector is not None

        assert i == 100 - 1, "there should be only 100 entries"


def test_pack_and_unpack_vrcdb_file(tmp_path):
    class VRCDBEntry(BaseEntry):
        label = StringField(column_name='labels')
        feature_vector = FeatureVectorField()
        uuid = UUIDField()
        image_url = RemoteImageField()

    packer = Packer(
        tmp_path / 'test_file.rcdb', entry_type=VRCDBEntry,
    )
    packer.metadata.packer_version = 2  # force overwrite of the version

    with packer:
        packer.add_entry(VRCDBEntry(
            label='123',
            feature_vector=[1, 2, 3],
            uuid='123e4567-e89b-12d3-a456-426655440000',
            image_url='https://example.com/image.jpg',
        ))

    unpacker = Unpacker(tmp_path / 'test_file.rcdb')  # open without entry type
    with unpacker:
        i = 0
        for entry in unpacker.entries():
            i += 1
            assert entry.label == '123'
            assert entry.feature_vector.tolist() == [1, 2, 3]
            assert entry.uuid == uuid.UUID('123e4567-e89b-12d3-a456-426655440000'), "Should automatically detect UUID"
            assert entry.image_url == 'https://example.com/image.jpg'

            with pytest.raises(AttributeError):
                # id is never populated
                _ = entry.id  # noqa

        assert i == 1, "there should be only one entry"
        assert unpacker.metadata.packer_version == 2, "version should be 2 as it is set in packer"
        assert sorted(unpacker.fields.keys()) == sorted(['label', 'feature_vector', 'uuid', 'image_url'])

    unpacker = Unpacker(tmp_path / 'test_file.rcdb', entry_type=VRCDBEntry)  # open with entry type
    with unpacker:
        i = 0
        for entry in unpacker.entries():
            i += 1
            assert entry.label == '123'
            assert entry.feature_vector.tolist() == [1, 2, 3]
            assert entry.uuid == uuid.UUID('123e4567-e89b-12d3-a456-426655440000'), \
                "Because there is a formatting to UUID field"
            assert entry.image_url == 'https://example.com/image.jpg'

            with pytest.raises(AttributeError):
                _ = entry.roga_kopyta  # noqa

        assert i == 1, "there should be only one entry"
        assert sorted(unpacker.fields.keys()) == sorted(['label', 'feature_vector', 'uuid', 'image_url'])


def test_entry_type_builder():
    builder = EntryTypeBuilder()
    builder.add_field('label', StringField())

    with pytest.raises(ValueError):
        builder.add_field('feature_vector', FeatureVectorField)  # noqa

    class Field:
        pass

    with pytest.raises(ValueError):
        builder.add_field('feature_vector', Field)  # noqa

    with pytest.raises(ValueError):
        builder.add_field('feature_vector', Field())  # noqa

    builder = EntryTypeBuilder()
    entry_type = builder.build()

    with pytest.raises(ValueError) as exc:
        entry_type(label="123")
    assert "has no fields registered" in str(exc)


def test_entry_builder_adds_a_field():
    builder = EntryTypeBuilder(RawEntry)
    builder.add_field('synthetic', BooleanField(default=True, null=True))
    entry_type = builder.build()

    entry = entry_type(label="123", feature_vector=[1, 2, 3])
    assert entry.synthetic is True, "Test default value initialization and new field"
    assert entry.label == '123', "Other field should still be there"

    assert not entry.is_empty()

    empty_entry = entry_type()
    assert empty_entry.is_empty(), "Should be empty with default value"
    assert empty_entry.synthetic is True, "Test default value initialization and new field"


def test_repack_v1_to_v2(script_cwd, tmp_path):
    db_folder = (script_cwd / '..' / 'db').resolve()
    destination_filename = pathlib.Path(tmp_path, 'test_with_images.rcdb')
    repacked_filename = pathlib.Path(tmp_path, 'repacked.rcdb')
    packer_v1 = ClassificationDatabasePacker(destination=destination_filename)
    features = db_folder / 'features.txt'
    labels = db_folder / 'labels.txt'
    images_folder = db_folder / 'custom_folder/'
    packer_v1.pack(labels, features, images_folder)

    unpacker = Unpacker(destination_filename)
    with unpacker:
        unpacker.get_metadata()
        assert unpacker.metadata.packer_version == 1, "version should be 1 as it is set in packer"
        assert sorted(unpacker.fields.keys()) == sorted(['label', 'feature_vector', 'image'])
        assert unpacker.metadata.count == 2, "there should be only 2 entries with images"

        packer_v2 = Packer(
            repacked_filename, entry_type=unpacker.entry_type,
            archiver=ZipArchiver(compression=zipfile.ZIP_DEFLATED, compresslevel=3),
        )
        with packer_v2:
            for item in unpacker.entries():
                assert item.label == '123123123'
                packer_v2.add_entry(item)
            assert packer_v2.entries_count == 2
        assert packer_v2.metadata.count == 2
