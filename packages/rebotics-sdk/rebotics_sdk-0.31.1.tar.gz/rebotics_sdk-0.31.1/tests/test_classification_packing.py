import json
import os
import pathlib
import tempfile
from unittest import TestCase

import pytest
import requests_mock

from rebotics_sdk.advanced.packers import (
    ClassificationDatabasePacker,
    DuplicateFeatureVectorsException,
    Py7zrClassificationDatabasePacker,
    FileInputZipDatabasePacker,
    VirtualClassificationDatabasePacker,
    ZipDatabasePacker,
    ZstdClassificationDatabasePacker,
    get_packer_class,
    PACKERS
)
from rebotics_sdk.constants import RCDBBaseFileNames
from rebotics_sdk.providers import FVMProvider


def test_classification_packing(script_cwd):
    db_folder = script_cwd / "db"
    with tempfile.TemporaryDirectory() as dirname:
        destination_filename = pathlib.Path(dirname, 'test')
        packer = ClassificationDatabasePacker(destination=destination_filename)
        features = db_folder / 'features.txt'
        labels = db_folder / 'labels.txt'
        images_folder = db_folder / 'custom_folder/'

        res = packer.pack(labels, features, images_folder)

        assert 'test.rcdb' in res

        with packer.zipfile(res, mode='r') as zip_io:
            meta = json.loads(packer.read_lines(zip_io.read('meta.json').decode('utf-8'))[0])

        expected_keys = [
            'packed',
            'model_type',
            'model_codename',
            'sdk_version',
            'packer_version',
            'core_version',
            'fvm_version'
        ]
        for key in expected_keys:
            assert key in meta.keys()

        assert len(packer.images) == 2

        packer = ClassificationDatabasePacker(source=res)
        entries = list(packer.unpack())
        assert len(entries) == 2
        entry = entries[0]
        assert entry.label.strip() == '123123123'
        assert entry.feature.strip() == '123123123123123'
        internal_filename = entry.filename
        assert internal_filename == 'image_1.png'

        for key in expected_keys:
            assert key in packer.meta_data.keys()

        # testing if it can be dumped to the FS
        og_file = images_folder / internal_filename
        tmp_file = db_folder / internal_filename

        with open(tmp_file, 'wb') as fout:
            fout.write(entry.image)

        assert og_file.stat().st_size == tmp_file.stat().st_size
        tmp_file.unlink()


def test_classification_packing_check_duplicates(script_cwd):
    db_folder = script_cwd / "db"
    packer = ClassificationDatabasePacker(destination='test', check_duplicates=True)
    features = db_folder / 'features.txt'
    labels = db_folder / 'labels.txt'
    images_folder = db_folder / 'custom_folder/'

    with pytest.raises(DuplicateFeatureVectorsException) as excinfo:
        packer.pack(labels, features, images_folder)
    assert "duplicate" in str(excinfo.value)


def test_zip_packing():
    packer = ZipDatabasePacker()
    packed = packer.pack(
        labels=[
            '123123123'
        ],
        features=[
            '123123123123123'
        ]
    )
    assert packer.meta_data['count'] == 1

    unpacker = ZipDatabasePacker(source=packed)
    for entry in unpacker.unpack():
        assert entry.label.strip() == '123123123'
        assert entry.feature.strip() == '123123123123123'

    assert unpacker.meta_data['count'] == 1


def test_virtual_packing_and_unpacking(script_cwd):
    db_folder = script_cwd / "db"

    with tempfile.TemporaryDirectory() as dirname, requests_mock.Mocker() as m:
        m.get('https://via.placeholder.com/150', text='some file')
        destination_filename = pathlib.Path(dirname, 'test')
        # destination_filename = db_folder / "test.rcdb"
        provider = FVMProvider(host='https://r3dev-fvm.rebotics.net/')
        packer = VirtualClassificationDatabasePacker(
            destination=destination_filename,
            provider=provider,
        )

        features = db_folder / RCDBBaseFileNames.FEATURES
        labels = db_folder / RCDBBaseFileNames.LABELS
        images = db_folder / 'image_urls.txt'
        uuids = db_folder / 'uuid.txt'

        res = packer.pack(
            labels, features, uuids, images
        )
        assert 'test.rcdb' in res, "Same destination is returned properly and extension is set normally"

        unpacker = VirtualClassificationDatabasePacker(
            source=pathlib.Path(dirname, 'test.rcdb'),
            with_images=True,
            provider=provider,
        )
        data = list(unpacker.unpack())
        assert len(data) == 2, "There are only two entries along the way"


def test_file_input_string_packing_and_unpacking(script_cwd):
    filename = 'test'
    labels = [
        '123123123',
        '123123123'
    ]
    features = [
        '123123123123123',
        '123123123123123'
    ]

    with tempfile.TemporaryDirectory() as dirname:
        destination_file_path = pathlib.Path(dirname, filename)
        filename_full = f"{filename}.{FileInputZipDatabasePacker.extension}"
        packer = FileInputZipDatabasePacker(
            destination=destination_file_path,
        )
        res = packer.pack(labels, features)
        assert filename_full in res, "Same destination is returned properly and extension is set normally"

        unpacker = FileInputZipDatabasePacker(source=pathlib.Path(dirname, filename_full))
        data = list(unpacker.unpack())
        assert len(data) == 2, "There are only two entries along the way"


def test_file_input_file_packing_and_unpacking(script_cwd):
    db_folder = script_cwd / "db"

    filename = "test"
    labels = db_folder / RCDBBaseFileNames.LABELS
    features = db_folder / RCDBBaseFileNames.FEATURES

    with tempfile.TemporaryDirectory() as dirname:
        destination_file_path = pathlib.Path(dirname, filename)
        filename_full = f"{filename}.{FileInputZipDatabasePacker.extension}"
        packer = FileInputZipDatabasePacker(
            destination=destination_file_path,
        )
        packer.pack(labels, features)

        unpacker = FileInputZipDatabasePacker(source=pathlib.Path(dirname, filename_full))
        data = list(unpacker.unpack())
        assert len(data) == 2, "There are only two entries along the way"


def test_different_comrpessionlevel_compatibility(script_cwd):
    db_folder = script_cwd / "db"

    with open(db_folder.joinpath(RCDBBaseFileNames.LABELS)) as labels_file:
        labels = labels_file.read().splitlines()

    with open(db_folder.joinpath(RCDBBaseFileNames.FEATURES)) as features_file:
        features = features_file.read().splitlines()

    with tempfile.TemporaryDirectory() as dirname:
        archive_file_path = pathlib.Path(dirname).joinpath('fv.zip')

        database_packer = ZipDatabasePacker(destination=archive_file_path, compresslevel=3)
        database_packer.pack(labels, features)

        database_unpacker = ZipDatabasePacker(source=archive_file_path)
        data = list(database_unpacker.unpack())

        assert len(data) == 2


@pytest.mark.skip
def test_full_data():
    """
    This is a custom test that requires preparation and must be skipped by default.
    """
    import datetime as dt
    db_source = pathlib.Path('G:\\retech\\rebotics_sdk\\archive_test_suite\\fv')
    archive_name = 'fv.zip'
    labels_path = pathlib.Path(db_source).joinpath(RCDBBaseFileNames.LABELS)
    features_path = pathlib.Path(db_source).joinpath(RCDBBaseFileNames.FEATURES)
    log = []

    def run_compression_program(temporary_directory, compression_level):
        archive_path = temporary_directory.joinpath(archive_name)
        packer = FileInputZipDatabasePacker(destination=archive_path, compresslevel=compression_level)
        pack_start = dt.datetime.now()
        packer.pack(labels_path, features_path)
        pack_end = dt.datetime.now()
        del packer

        unpacker = FileInputZipDatabasePacker(source=archive_path)
        unpack_start = dt.datetime.now()
        data = list(unpacker.unpack())
        unpack_end = dt.datetime.now()
        del unpacker

        return {
            'compression_level': compression_level,
            # 'pack_start': pack_start,
            # 'pack_end': pack_end,
            'pack_duration': str(pack_end - pack_start),
            # 'unpack_start': unpack_start,
            # 'unpack_end': unpack_end,
            'unpack_duration': str(unpack_end - unpack_start),
        }

    with tempfile.TemporaryDirectory() as dir_c1, tempfile.TemporaryDirectory() as dir_c6:
        for folder, compresslevel in ((pathlib.Path(dir_c1), 1), (pathlib.Path(dir_c6), 6)):
            result = run_compression_program(folder, compresslevel)
            log.append(result)

    print(json.dumps(log, indent=4))


class Py7zrClassificationDatabasePackerTestCase(TestCase):
    archiver = Py7zrClassificationDatabasePacker
    archive_packed_flag = False
    magic_text = 'Lorem ipsum dolor sit amet.'

    def test_archiver(self):
        local_path = pathlib.Path(os.path.realpath(__file__)).parent
        self.database_source = local_path.joinpath('db')

        with tempfile.TemporaryDirectory() as working_directory:
            self.archive_file = pathlib.Path(working_directory).joinpath('fv') \
                .with_suffix('.' + self.archiver.extension)

            with self.subTest("Archive file packing test"):
                self.pack_database()

            with self.subTest("Archive file unpacking test"):
                self.unpack_database()

    def pack_database(self):
        self.archive_handler = self.archiver(self.archive_file)
        self.archive_handler.meta_data['test_easter_egg'] = self.magic_text
        self.archive_handler.pack(
            self.database_source.joinpath(RCDBBaseFileNames.LABELS),
            self.database_source.joinpath(RCDBBaseFileNames.FEATURES)
        )

        self.assertTrue(os.path.exists(self.archive_file))
        self.archive_packed_flag = True

    def unpack_database(self):
        if not self.archive_packed_flag:
            self.skipTest("Failed to create archive in previous test method "
                          "Py7zrClassificationDatabasePackerTestCase.pack_database")

        data = list(self.archive_handler.unpack())
        self.assertTrue(len(data) == 2)
        self.assertTrue(self.archive_handler.meta_data['packer_version'] == 3)
        self.assertTrue(self.archive_handler.meta_data['test_easter_egg'] == 'Lorem ipsum dolor sit amet.')


class ZstdClassificationDatabasePackerTestCase(Py7zrClassificationDatabasePackerTestCase):
    archiver = ZstdClassificationDatabasePacker


class GetPackerTestCase(TestCase):
    archive_name = 'fv'

    def setUp(self) -> None:
        self.test_data_path = pathlib.Path(os.path.realpath(__file__)).parent.joinpath('db')

    def test_packers(self):
        for packer in PACKERS:
            with tempfile.TemporaryDirectory() as folder:
                archive_path = pathlib.Path(folder).joinpath(self.archive_name) \
                    .with_suffix('.' + packer.base_class.extension)

                archive = packer.base_class(destination=archive_path)
                archive.pack(
                    self.test_data_path.joinpath(RCDBBaseFileNames.LABELS),
                    self.test_data_path.joinpath(RCDBBaseFileNames.FEATURES)
                )
                del archive

                type_derived = get_packer_class(archive_path)

                self.assertTrue(type_derived is packer.base_class)
