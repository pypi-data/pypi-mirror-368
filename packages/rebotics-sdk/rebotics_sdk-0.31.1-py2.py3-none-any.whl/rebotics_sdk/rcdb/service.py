import io
import json
import logging
import pathlib
import tempfile
import typing
import zipfile

from rebotics_sdk.constants import RCDBBaseFileNames
from rebotics_sdk.rcdb.archivers import BaseArchiver, detect_archiver, ArchiveFacade, ZipArchiver
from rebotics_sdk.rcdb.entries import BaseEntry, ETV
from rebotics_sdk.rcdb.fields import (
    StringField,
    FeatureVectorField,
    BaseField
)
from rebotics_sdk.rcdb.meta import Metadata
from rebotics_sdk.rcdb.utils import EntryTypeBuilder


class BasePackerInterface:
    metadata: typing.Optional[Metadata]
    version: int
    archive: typing.Optional[ArchiveFacade]
    entry_type: typing.Type[BaseEntry]

    @property
    def fields(self):
        return self.entry_type.options.fields

    def open(self):
        raise NotImplementedError()

    def close(self):
        raise NotImplementedError()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return


class Packer(BasePackerInterface):
    """
    new packer method to add files to a RCDB archive via generator.

    usage example:

    >>> class RawEntry(BaseEntry):
    >>>     id = StringField()
    >>>     label = StringField(column_name='labels')
    >>>     feature_vector = FeatureVectorField()
    >>>
    >>> test_data = dict(label='123', feature_vector=fv)  # some data here
    >>> archiver = ZipArchiver(compression=zipfile.ZIP_STORED)  # no compression
    >>> with Packer('test_file.rcdb', entry_type=RawEntry, archiver=archiver) as packer:
    >>>     packer.add_entry(RawEntry(**test_data))
    """
    version = 4
    extension = 'rcdb'

    tmp_folder_path: typing.Optional[pathlib.Path]

    def __init__(self,
                 destination: typing.Union[pathlib.PurePath, typing.IO, None, str],
                 entry_type: typing.Type[BaseEntry],
                 archiver: BaseArchiver = None,
                 batch_size: int = None,
                 **metadata):

        if hasattr(destination, 'write'):
            self.output_file = destination

            assert self.output_file.mode == 'wb', "Output file must be opened in binary mode"
            assert not self.output_file.closed, "Output file must be opened in binary mode"

            # set caret to the start
            self.output_file.seek(0)
        elif isinstance(destination, (str, pathlib.PurePath)):
            self.output_file = pathlib.Path(destination)
            if self.output_file.suffix[1:] != self.extension:
                # or change the output_file extension to .rcdb
                raise ValueError(f"Output file must have {self.extension} extension")
        else:
            self.output_file = io.BytesIO()

        self.entry_type = entry_type

        self.metadata = Metadata(**metadata)
        self.metadata.packer_version = self.version
        self.metadata.batch_size = batch_size

        self.batch_size = batch_size  # default behavior is to write all entries at once
        self.batch_counter = 0

        if not archiver:
            # use default archiver to be zipfile
            archiver = ZipArchiver()

        if self.batch_size is not None and not archiver.supports_batching:
            raise ValueError(f"Archiver {archiver.__class__.__name__} does not support batching")

        self.archiver = archiver
        self.archive = None
        self.temporary_folder = None
        self.tmp_folder_path = None

        self.column_descriptors = {}
        self.entries_count = 0
        self.per_batch_counter = 0

    def add_entry(self, entry: BaseEntry):
        # Check that entry is of the type that user requested
        # Convert entry to the format that is required by
        fields = self.entry_type.options.fields

        for field_name, field in fields.items():
            value = getattr(entry, field_name)
            field.write_to_rcdb(value,
                                index=self.entries_count,
                                descriptor=self.column_descriptors[field_name],
                                packer=self)
            self.per_batch_counter += 1

        self.entries_count += 1

        if self.batch_size is not None:
            if self.entries_count % self.batch_size == 0:
                self._flush_into_archive()
                self.per_batch_counter = 0

    def __enter__(self):
        self.open()
        return self

    def open(self):
        self.archive = self.archiver.open_for_write(self.output_file)
        # open a temporary descriptors to store column entities for each field from the entry_type
        self.temporary_folder = tempfile.TemporaryDirectory()
        self.tmp_folder_path = pathlib.Path(self.temporary_folder.name)
        self._create_file_descriptors()

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Fill meta.json with
        #  - User-provided data
        #  - entries count
        #  - fields that are available in entries and their types
        # Close files, pack archive
        self.close()

    def close(self):
        self.metadata.count = self.entries_count

        if self.batch_size is None:
            self.metadata.batch_size = self.entries_count
        else:
            self.metadata.batch_size = self.batch_size

        self._flush_into_archive(recreate_descriptors=False)
        # we can read additionally size of the archive and populate the metadata as well

        # flush metadata file
        with open(self.tmp_folder_path / RCDBBaseFileNames.META, 'w') as fio:
            fio.write(self.metadata.model_dump_json())
        self.archive.write(self.tmp_folder_path / RCDBBaseFileNames.META, RCDBBaseFileNames.META)

        self.archive.close()
        self.temporary_folder.cleanup()

    def _create_file_descriptors(self):
        for field_name, field in self.fields.items():
            self.column_descriptors[field_name] = open(self.tmp_folder_path / field.column_name, field.write_mode)

    def _flush_into_archive(self, recreate_descriptors=True):
        """with given column descriptors, write down """
        for field_name, descriptor in self.column_descriptors.items():
            descriptor.close()

        if self.batch_size is not None:
            self.batch_counter += 1
        else:
            self.batch_counter = None

        batched_files = {}

        if self.per_batch_counter > 0:
            # Do not write empty files into an archive
            for field_name, field in self.fields.items():
                archive_name = field.get_filename(self.batch_counter)
                self.archive.write(
                    self.tmp_folder_path / field.column_name,
                    archive_name
                )
                batched_files[field_name] = archive_name
            self.metadata.files.append(batched_files)

        if recreate_descriptors:
            # recreate descriptors for the next batch
            self._create_file_descriptors()


class Unpacker(BasePackerInterface):
    """
    New type of unpackers that can support older versions of RCDB
    When entry_type is not defined, it is automatically detected from the metadata.json.
    The only exception being is for the ImageField, which is ambiguous and cannot be detected

    Example of usage:
    >>> with Unpacker('test_file.rcdb') as unpacker:
    >>>     for entry in unpacker.entries():
    >>>         print(entry)
    """
    version = 4
    archive: typing.Optional[ArchiveFacade]

    def __init__(self,
                 input_file: typing.Union[str, pathlib.PurePath, typing.IO],
                 entry_type: typing.Optional[typing.Type[BaseEntry]] = None,
                 archiver: BaseArchiver = None):
        """
        :param entry_type: defines the field set that user requests for extraction.
          If it's None, only RCDB meta could read.
        """
        if isinstance(input_file, (str, pathlib.PurePath)):
            self.input_file = pathlib.Path(input_file)
            if archiver is None:
                archiver_class = detect_archiver(input_file)
                archiver = archiver_class()
        elif isinstance(input_file, io.BytesIO):
            self.input_file = input_file
            if archiver is None:
                archiver = ZipArchiver()
        elif hasattr(input_file, 'mode'):
            self.input_file = input_file
            assert self.input_file.mode == 'rb', "File should be opened in binary mode"
            assert not self.input_file.closed, "File should not be closed"
            if archiver is None:
                archiver_class = detect_archiver(input_file.name)
                archiver = archiver_class()
        else:
            raise ValueError(f"Unsupported input file type {type(input_file)}")

        # when entry_type is None, we might just unpack all fields that are available in RCDB
        # in terms of string format first
        self.entry_type = entry_type

        self.archiver = archiver
        self.archive = None
        self.metadata = None

        self.batch_counter = 0

    def get_metadata(self) -> Metadata:
        """
        Get meta without opening the archive to check it or get fields format.
        """
        if self.archive is None:
            raise ValueError("Archive is not opened. Use 'with' statement to open it first")
        meta_json_content = json.load(self.archive.read(RCDBBaseFileNames.META))
        self.metadata = Metadata(**meta_json_content)

        if self.entry_type is None:
            self.entry_type = EntryTypeBuilder.construct_from_metadata(self.metadata)
            if not self.metadata.files:
                self.metadata.files = [self.entry_type.get_field_to_filename_map()]

        return self.metadata

    def entries(self) -> typing.Iterable[ETV]:
        """
        Iterate over entries in RCDB. Required archive to be opened
        """
        if self.archive is None:
            raise ValueError("Archive is not opened. Use 'with' statement to open it first")

        if self.metadata is None:
            self.get_metadata()

        if len(self.metadata.files) == 0:
            # read with available fields
            return

        if not self.archiver.supports_batching and len(self.metadata.files) > 1:
            raise ValueError(f"Archive {self.archiver} does not support batching.")

        # max_workers = min(os.cpu_count(), len(self.metadata.files))
        # logging.debug(f"Max number of workers: {max_workers}")
        #
        # with ThreadPoolExecutor(max_workers=max_workers) as executor:
        #     future_to_batch = {
        #         executor.submit(self.process_batch, batch): batch
        #         for batch in self.metadata.files
        #     }
        #     logging.debug(f"There are {len(future_to_batch)} futures...")
        #
        #     for future in as_completed(future_to_batch):
        #         batch = future_to_batch[future]
        #         self.batch_counter += 1
        #         try:
        #             # yield from self._get_entries_from_batch(future.result())
        #             yield from future.result()
        #         except Exception as exc:
        #             logging.error(f"Exception while reading batch {batch}: {exc}")
        #             raise exc

        for batch in self.metadata.files:
            self.batch_counter += 1
            yield from self.process_batch(batch)
        return

    def process_batch(self, batch):
        column_descriptors = self._get_column_descriptors(batch)

        yield from self._get_entries_from_batch(column_descriptors)

        if column_descriptors:
            for descriptor in column_descriptors.values():
                if descriptor is not None:
                    descriptor.close()

    def _get_column_descriptors(self, batch):
        files = list(batch.values())
        column_descriptors = {}
        file_descriptors = self.archive.read_batch(files)  # filename: IO

        logging.debug(f"Reading files from archive...")
        for field_name in self.fields:
            archive_name = batch.get(field_name, None)

            if archive_name is None:
                # there is nop such file
                continue

            # open descriptors for each file
            field: 'BaseField' = self.fields[field_name]

            logging.debug('Reading file %s', archive_name)
            # read the file from archive completely
            column_descriptors[field_name] = field.make_generator(
                field.wrap_descriptor(
                    file_descriptors[archive_name]
                )
            )
        return column_descriptors

    def _get_entries_from_batch(self, column_descriptors):
        entry_index = 0

        logging.debug("Reading the entries from the descriptors")
        while True:
            entry_kwargs = {}
            # so the biggest slowdown is this generator...
            for field_name, field in self.fields.items():
                entry_kwargs[field_name] = field.read_from_rcdb(
                    index=entry_index,
                    descriptor=column_descriptors.get(field_name),
                    unpacker=self
                )

            entry = self.entry_type(**entry_kwargs)
            if entry.is_empty():
                # we reached full empty row
                break

            yield entry
            entry_index += 1

    def __enter__(self):
        """
        Open an archive. Get meta first to get a field set with the typings.
        If packed RCDB contains more fields that are not defined in entry_type -
        they would be ignored and not extracted.
        If packed RCDB misses some fields, or they have a different type than requested, raise an error.
        """
        self.open()
        return self

    def open(self):
        if self.archive is None:
            self.archive = self.archiver.open_for_read(self.input_file)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self.archive.close()
        # un-assign archive will allow to open unpacker again
        self.archive = None
