import dataclasses
import io
import json
import logging
import os
import pathlib
import re
import sys
import uuid
import zipfile
from collections import namedtuple, defaultdict
from datetime import datetime, timezone
from hashlib import md5
from io import BytesIO, StringIO
from typing import AnyStr, Callable, Iterator, List, Optional, Type, Union

import py7zr
import tqdm

import rebotics_sdk
from rebotics_sdk.constants import RCDBBaseFileNames
from rebotics_sdk.utils import validate_files, read_lines

logger = logging.getLogger(__name__)

ClassificationEntry = namedtuple('ClassificationEntry', ['label', 'feature', 'image', 'filename', 'index'])
ImageEntry = namedtuple('ImageEntry', ['filename', 'filepath', 'order'])


class VirtualClassificationEntry(object):
    def __init__(self, label, feature, image_url, index=None):
        self.label = label
        self.feature = feature
        self.image_url = image_url
        self.index = index

    def to_dict(self):
        return {
            'label': self.label,
            'feature': self.feature,
            'image_url': self.image_url,
            'index': self.index
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            label=d['label'],
            feature=d['feature'],
            image_url=d['image_url'],
            index=d['index']
        )


NUMERIC_VALUE = re.compile(r'\d+')


class ClassificationDatabaseException(Exception):
    pass


class DuplicateFeatureVectorsException(ClassificationDatabaseException):
    def __init__(self, msg, duplicates):
        super(DuplicateFeatureVectorsException, self).__init__(msg)
        self.duplicates = duplicates


class UnpackException(ClassificationDatabaseException):
    def __init__(self, archive_name: AnyStr, data_keys: List):
        msg = f'Archive {archive_name} has incorrect structure. Expected to have \'{RCDBBaseFileNames.LABELS}\', ' \
              f'\'{RCDBBaseFileNames.FEATURES}\' and \'{RCDBBaseFileNames.META}\' files among keys. ' \
              f'Provided keys are: {str(data_keys)}.'
        super(UnpackException, self).__init__(msg)
        self.archive_name = archive_name
        self.data_keys = data_keys


def extract_numeric(filename):
    found = NUMERIC_VALUE.findall(filename)
    if len(found) == 0:
        raise ClassificationDatabaseException('Images name should contain numeric value that represents the order. '
                                              'Instead of {} name was used'.format(filename))
    return int(found[0])


class BaseClassificationDatabasePacker:
    """
    Base class for classification database packing process.
    """
    extension = 'rcdb'

    def __init__(self, destination, **kwargs):
        self.meta_data = {
            'packed': datetime.now().strftime('%c'),
            'model_type': kwargs.get('model_type', 'facenet'),
            'model_codename': kwargs.get('model_codename'),
            'sdk_version': rebotics_sdk.__version__,
            'core_version': kwargs.get('core_version'),
            'fvm_version': kwargs.get('fvm_version')
        }

        if hasattr(destination, 'write') or hasattr(destination, 'read'):
            self.destination = destination  # file like object
        elif destination is None:
            self.destination = BytesIO()
        elif isinstance(destination, str) or isinstance(destination, pathlib.PurePath):
            # in python 2 it doesn't accept pathlib PurePath, but only os.path or str
            self.destination = str(destination)
            if not self.destination.endswith(self.extension):
                self.destination = "{}.{}".format(self.destination, self.extension)

    def pack(self, *args, **kwargs):
        """
        Function to pack data from arguments into an archive. Should accept set of parameters that describe input data,
        and write it all into archive that was set up in __init__.

        :returns: path to archive
        """
        raise NotImplementedError()

    def unpack(self):
        """
        Function to unpack existing archive. Unpacks the archive, then merges together entries from label and

        :returns: Returns a single classification entry iteratively (yield return)
        """
        raise NotImplementedError()

    def archive_file(self, **kwargs):
        """
        Function to return fully-initialized file-like object that provides interface to archive file.

        :returns: file-like object that represents the archive
        """
        raise NotImplementedError()

    def read_meta(self):
        """
        Function to read metadata from sourcing archive, if it exists.
        """
        raise NotImplementedError()


class BaseZipClassificationDatabasePacker(BaseClassificationDatabasePacker):
    version = 0
    extension = 'zip'

    def __init__(
        self,
        source=None,
        destination=None,
        progress_bar=False,
        check_duplicates=False,
        compresslevel=1,
        *args,
        **kwargs
    ):
        if source is not None and destination is not None:
            raise ValueError("You can't sent source and destination at a same time.")

        super().__init__(destination, **kwargs)
        self.__compresslevel = compresslevel
        self.meta_data['packer_version'] = self.version

        self.source = source

        self.zip_io = None

        if self.source is not None:
            self.read_meta()

        self.check_duplicates = check_duplicates
        self.images = []
        self.progress_bar = progress_bar

    @property
    def compresslevel(self):
        return self.__compresslevel

    def read_lines(self, lines):
        return [x for x in lines.split('\n') if x]

    def zipfile(self, file, **kwargs):
        # if python version is
        params = dict(
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=self.__compresslevel,
            allowZip64=True,
        )
        #
        # if (sys.version_info.major, sys.version_info.minor) >= (3, 7):
        #     # using the most aggressive compression
        #     params['compresslevel'] = 9  # default is 6

        # Compatibility with py36
        if sys.version_info < (3, 7):
            params.pop('compresslevel', None)

        params.update(kwargs)

        for compression_option in [zipfile.ZIP_DEFLATED, zipfile.ZIP_STORED, ]:
            try:
                params['compression'] = compression_option
                return zipfile.ZipFile(file, **params)
            except RuntimeError:
                pass

    archive_file = zipfile

    def __enter__(self):
        if self.zip_io is not None:
            return self

        # check for file to be not closed

        if self.source is not None:
            self.zip_io = self.zipfile(self.source, mode='r')
        elif self.destination is not None:
            self.zip_io = self.zipfile(self.destination, mode='w')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.zip_io.close()
        self.zip_io = None

    def read_meta(self):
        with self as packer:
            self.meta_data = json.load(packer.zip_io.open(RCDBBaseFileNames.META))


class ZipDatabasePacker(BaseZipClassificationDatabasePacker):
    """
    Unified file format for packing classification database into single folder
    File format is the zip based archive with following :

    labels.txt
    features.txt
    meta.json
    """
    version = 0
    extension = 'zip'

    def pack(self, labels, features, *args, **kwargs):
        labels_io = StringIO("\n".join(labels))
        features_io = StringIO("\n".join(features))
        self.meta_data['count'] = len(labels)

        with self.zipfile(self.destination, mode='w') as zip_io:
            zip_io.writestr(RCDBBaseFileNames.LABELS, labels_io.getvalue())
            zip_io.writestr(RCDBBaseFileNames.FEATURES, features_io.getvalue())
            zip_io.writestr(RCDBBaseFileNames.META, json.dumps(self.meta_data))
        return self.destination

    def unpack(self):
        if self.source is None:
            raise ClassificationDatabaseException("Can not unpack with empty source file")

        with self.zipfile(self.source, mode='r') as zip_io:
            try:
                self.meta_data = json.load(zip_io.open(RCDBBaseFileNames.META))
            except KeyError:
                # meta is not presented, working in the compatibility mode
                pass

            labels = self.read_lines(zip_io.read(RCDBBaseFileNames.LABELS).decode('utf-8'))
            features = self.read_lines(zip_io.read(RCDBBaseFileNames.FEATURES).decode('utf-8'))

            for index, (label, feature) in enumerate(zip(labels, features)):
                yield ClassificationEntry(
                    label, feature, None, None, index
                )


class ClassificationDatabasePacker(BaseZipClassificationDatabasePacker):
    """
    Unified file format for packing classification database into single folder
    File format is the zip based archive with following :

    labels.txt
    features.txt
    meta.json
    images/  - folder with images, this folder can be empty
    """

    version = 1
    extension = 'rcdb'
    images_extensions = {'jpeg', 'png', 'jpg'}

    def extract_meta_data(self, labels_path, features_path, images_folder):
        known_order = set()
        for f in pathlib.Path(images_folder).iterdir():
            if f.is_file():
                extension = f.suffix
                if extension in self.images_extensions:
                    raise ClassificationDatabaseException("Extension is not supported by packer: {}".format(f.name))
                numeric_order = extract_numeric(f.name)
                if numeric_order in known_order:
                    raise ClassificationDatabaseException("Numeric order collision. {}".format(f.name))

                known_order.add(numeric_order)
                self.images.append(ImageEntry(f.name, str(f), numeric_order))

        # repack based on the filename and it's numeric value
        self.images.sort(key=lambda i: i.order)  # sort by numeric value of the filename

        with open(labels_path, 'r') as labels_io, open(features_path, 'r') as features_io:
            labels = self.read_lines(labels_io.read())
            features = self.read_lines(features_io.read())

        labels_count = len(labels)
        features_count = len(features)
        files_count = len(self.images)

        if labels_count != features_count:
            raise ClassificationDatabaseException('Inconsistent count of labels and features. {}/{}'.format(
                labels_count, features_count
            ))

        if labels_count != files_count:
            raise ClassificationDatabaseException(
                'Inconsistent count of labels and features and files. {}/{}/{}'.format(
                    labels_count, features_count, files_count
                ))

        self.meta_data.update({
            'count': features_count,
            'images': [str(img.filename) for img in self.images]
        })

        if not self.check_duplicates:
            return

        # checking for the uniqueness of the FV
        features_map = defaultdict(list)
        for i, fv in tqdm.tqdm(enumerate(features), total=features_count, disable=not self.progress_bar, leave=False):
            md_ = md5(fv.encode('utf-8'))
            features_map[md_.hexdigest()].append(i)
        duplicates = []
        for same_fv_ids in features_map.values():
            if len(same_fv_ids) > 1:
                duplicates.append([
                    ClassificationEntry(
                        labels[id_],
                        features[id_],
                        None,
                        self.images[id_].filename,
                        id_
                    ) for id_ in same_fv_ids
                ])

        if duplicates:
            raise DuplicateFeatureVectorsException(
                "Detected {} duplicate groups.".format(len(duplicates)),
                duplicates=duplicates
            )

    def pack(self, labels, features, images, *args, **kwargs):
        self.extract_meta_data(labels, features, images)

        with self.zipfile(self.destination, mode='w') as zip_io:
            zip_io.write(labels, RCDBBaseFileNames.LABELS)
            zip_io.write(features, RCDBBaseFileNames.FEATURES)
            zip_io.writestr(RCDBBaseFileNames.META, json.dumps(self.meta_data))

            for img in tqdm.tqdm(
                self.images,
                leave=False,
                disable=not self.progress_bar
            ):
                zip_io.write(img.filepath, str(pathlib.Path('images') / img.filename))

        return self.destination

    def unpack(self):
        """

        :return: generator of label, feature, image_io
        :rtype:self.meta_data
        """
        if self.source is None:
            raise ClassificationDatabaseException("Can not unpack with empty source file")

        with self.zipfile(self.source, mode='r') as zip_io:
            labels = self.read_lines(zip_io.read(RCDBBaseFileNames.LABELS).decode('utf-8'))
            features = self.read_lines(zip_io.read(RCDBBaseFileNames.FEATURES).decode('utf-8'))

            for index, (label, feature, image_name) in enumerate(zip(
                labels,
                features,
                self.meta_data['images']
            )):
                image = zip_io.read('images/{}'.format(image_name))
                yield ClassificationEntry(
                    label, feature, image, image_name, index
                )


@dataclasses.dataclass(frozen=True)
class DataEntry:
    label: str
    feature: List[float]
    uuid: Optional[uuid.UUID]
    image_url: Optional[str]


class VirtualClassificationDatabasePacker(BaseZipClassificationDatabasePacker):
    class FieldNames(RCDBBaseFileNames):
        UUIDS = 'uuid.txt'
        IMAGES = 'images.txt'

    version = 2
    extension = 'rcdb'

    def __init__(self, *args, **kwargs):
        self.concurrency = kwargs.get('concurrency', None)
        if self.concurrency is None or self.concurrency < 1:
            self.concurrency = os.cpu_count()
        super(VirtualClassificationDatabasePacker, self).__init__(*args, **kwargs)

    def pack(self, labels, features, uuids, images, *args, **kwargs):
        with open(labels, 'r') as labels_io:
            self.meta_data['count'] = sum(1 for _ in labels_io)

        with self.zipfile(self.destination, mode='w') as zip_io:
            # writing those as a file
            zip_io.write(labels, self.FieldNames.LABELS)
            zip_io.write(features, self.FieldNames.FEATURES)
            zip_io.write(uuids, self.FieldNames.UUIDS)
            zip_io.write(images, self.FieldNames.IMAGES)

            zip_io.writestr(RCDBBaseFileNames.META, json.dumps(self.meta_data))
        return self.destination

    def unpack(self) -> Iterator[DataEntry]:
        for batch in self._data_entry_generator():
            yield from batch

    def get_features_count(self) -> Optional[int]:
        return self.meta_data.get('count')

    def get_images_links_expiration(self) -> Optional[datetime]:
        images_links_expiration_iso: Optional[str] = self.meta_data.get('images_links_expiration')
        if images_links_expiration_iso is None:
            return

        images_links_expiration = datetime.fromisoformat(images_links_expiration_iso)
        if images_links_expiration.utcoffset() is None:
            images_links_expiration = images_links_expiration.replace(tzinfo=timezone.utc)
        return images_links_expiration

    def _data_entry_generator(self):
        batch = []  # initial batch
        with self.zipfile(self.source, mode='r') as zip_io:
            labels_io = io.TextIOWrapper(zip_io.open(self.FieldNames.LABELS), encoding='utf-8')
            features_io = io.TextIOWrapper(zip_io.open(self.FieldNames.FEATURES), encoding='utf-8')
            uuids_io = io.TextIOWrapper(zip_io.open(self.FieldNames.UUIDS), encoding='utf-8')
            images_io = io.TextIOWrapper(zip_io.open(self.FieldNames.IMAGES), encoding='utf-8')

            while True:
                label = labels_io.readline().strip()
                feature = features_io.readline().strip()
                uuid_ = uuids_io.readline().strip()
                image_url = images_io.readline().strip()

                if label == '' or feature == '':
                    # stop the cycle if there are empty lines
                    break

                if not feature.startswith('[') and not feature.endswith(']'):
                    feature = f'[{feature}]'
                feature_vector = json.loads(feature)

                batch.append(DataEntry(
                    label,
                    feature_vector,
                    uuid.UUID(uuid_) if uuid_ else None,
                    image_url if image_url else None,
                ))
                # if len(batch) >= self.concurrency:
                if len(batch) >= self.concurrency:
                    yield batch
                    batch = []

            if batch:
                yield batch


def is_iterable(obj):
    try:
        iter(obj)
    except Exception:
        return False
    else:
        return True


class FileInputZipDatabasePacker(ZipDatabasePacker):
    """
    Class copied from rebotics_core and one to be used as main zipfile module database packer.
    """

    def pack(self, labels, features, *args, **kwargs):
        """
        Overload of the packer to utilize files instead of IO or numpy arrays
        """
        self.meta_data["count"] = kwargs.get("count")

        self.meta_data["additional_files"] = kwargs.get("additional_files", [])

        if (
            isinstance(labels, pathlib.PurePath)
            and isinstance(features, pathlib.PurePath)
            or isinstance(labels, str)
            and isinstance(features, str)
        ):  # check if it is a str path
            with self.zipfile(self.destination, mode="w") as zip_io:
                zip_io.write(str(labels), RCDBBaseFileNames.LABELS)
                zip_io.write(str(features), RCDBBaseFileNames.FEATURES)

                for filename, path in kwargs.get("additional_files", []):
                    zip_io.write(str(path), filename)

                zip_io.writestr(RCDBBaseFileNames.META, json.dumps(self.meta_data))

        if is_iterable(labels) and is_iterable(features):
            return super().pack(
                labels, features, *args, **kwargs
            )


class Py7zrClassificationDatabasePacker(BaseClassificationDatabasePacker):
    """
    Database packer with the py7zr implementation of pyzstd library.
    """
    allowed_path_types = (str, pathlib.PurePath)
    version = 3

    def __init__(
        self,
        archive_file: Union[pathlib.PurePath, AnyStr] = None,
        # check_duplicates=False,
        **kwargs
    ) -> None:
        """
        :param archive_file: string or path object of the archive file
        """
        if 'destination' in kwargs:
            destination = kwargs['destination']
            source = None
            del kwargs['destination']
        elif 'source' in kwargs:
            destination = None
            source = kwargs['source']
            del kwargs['source']
        else:
            destination = archive_file
            source = None

        super().__init__(source=source, destination=destination, **kwargs)
        self.meta_data['packer_version'] = self.version
        self.read_meta()

    @property
    def filters(self):
        return [{'id': py7zr.FILTER_DEFLATE, }]

    def archive_file(self, **kwargs) -> py7zr.SevenZipFile:
        # TODO: from created SevenZipFile object it is possible to create ArchiveInfo object, that contains all info
        #  about used filters, meaning it is possible to create filter-attribute-independent unpacker process
        return py7zr.SevenZipFile(self.destination, filters=self.filters, **kwargs)

    def pack(
        self,
        labels: Union[AnyStr, pathlib.PurePath],
        features: Union[AnyStr, pathlib.PurePath],
        *args, **kwargs
    ):
        """
        Packs provided label and feature files (by path) into the archive file. Additional arguments provided should
        correspond **kwargs of py7zr zip file interface.

        :param labels: label input file, path of some sort
        :param features: features input file, path of some sort
        """
        # TODO: additional file array, possibly
        file_state, error = validate_files([labels, features])
        if not file_state:
            raise FileNotFoundError(error)

        if isinstance(labels, str):
            labels = pathlib.Path(labels)
        if isinstance(features, str):
            features = pathlib.Path(features)

        archive_file = self.archive_file(mode='w', **kwargs)

        archive_file.write(labels, RCDBBaseFileNames.LABELS)
        archive_file.write(features, RCDBBaseFileNames.FEATURES)
        archive_file.writestr(json.dumps(self.meta_data), RCDBBaseFileNames.META)

        archive_file.close()

    def unpack(self):
        """
        Reads contents of RCDB archive into memory and provides generator of feature values.
        """
        file_state, error = validate_files([self.destination, ])
        if not file_state:
            raise FileNotFoundError(error)

        with self.archive_file(mode='r') as archive_file:
            data = archive_file.readall()

            if RCDBBaseFileNames.LABELS not in data or RCDBBaseFileNames.FEATURES not in data:
                raise UnpackException(archive_file.filename, list(data.keys()))

            labels = read_lines(data[RCDBBaseFileNames.LABELS].getvalue().decode('utf-8'), skip_empty_lines=True)
            features = read_lines(data[RCDBBaseFileNames.FEATURES].getvalue().decode('utf-8'), skip_empty_lines=True)

        for index, (label, feature) in enumerate(zip(labels, features)):
            yield ClassificationEntry(label, feature, None, None, index)

    def read_meta(self):
        if not os.path.exists(self.destination):
            return

        with self.archive_file(mode='r') as archive_file:
            data = archive_file.read(RCDBBaseFileNames.META)
            if RCDBBaseFileNames.META not in data:
                raise UnpackException(self.destination, list(data.keys()))

            self.meta_data = json.loads(data[RCDBBaseFileNames.META].getvalue().decode('utf-8'))


class ZstdClassificationDatabasePacker(Py7zrClassificationDatabasePacker):
    def __init__(
        self,
        archive_file: Union[pathlib.PurePath, AnyStr] = None,
        compression_level=7,
        **kwargs
    ):
        """
        :param archive_file: string or path object of the archive file
        :param compression_level: compression level in shared paradigm of py7zr and zstd, 1 to 22, from fastest to
        most compressed
        """
        self.__compression_level = compression_level
        super().__init__(archive_file, **kwargs)

    @property
    def compression_level(self):
        return self.__compression_level

    @property
    def filters(self):
        return [{'id': py7zr.FILTER_ZSTD, 'level': self.compression_level}]


@dataclasses.dataclass
class Packer:
    checker: Callable
    # Basically, we're fine with any subclass of base class
    base_class: Type[BaseClassificationDatabasePacker]


# THIS LIST IS ORDER-DEPENDENT
# Basically, zipfile.is_zipfile accepts 7z archives made by py7zr module. This is stupid, but
#
# it is how it is.
#
PACKERS: List[Packer] = [
    Packer(checker=py7zr.is_7zfile, base_class=Py7zrClassificationDatabasePacker),
    Packer(checker=zipfile.is_zipfile, base_class=FileInputZipDatabasePacker),
]


def get_packer_class(file_path: Union[AnyStr, pathlib.PurePath]) -> Union[Type[BaseClassificationDatabasePacker], None]:
    if not os.path.exists(file_path):
        raise FileNotFoundError("Unable to identify database packer class for file that does not exist.")

    for packer in PACKERS:
        if packer.checker(file_path):
            return packer.base_class
    else:
        return None
