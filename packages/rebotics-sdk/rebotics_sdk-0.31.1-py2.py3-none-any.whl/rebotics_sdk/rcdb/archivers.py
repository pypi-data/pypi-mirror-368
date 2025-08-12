import os
import pathlib
import typing
import zipfile
from typing import AnyStr, Type, Union

import py7zr


class ArchiveFacade:
    def __init__(self, archive):
        self.archive = archive

    def read(self, arcname) -> typing.IO:
        raise NotImplementedError()

    def write(self, filename, arcname):
        """Write a file from filesystem into an archive"""
        raise NotImplementedError()

    def writestr(self, file, arcname):
        raise NotImplementedError()

    def close(self):
        self.archive.close()

    def read_batch(self, arcnames: typing.List[str]) -> typing.Dict[str, typing.IO]:
        """Read multiple files from archive"""
        raise NotImplementedError()


class Py7zrArchiveFacade(ArchiveFacade):
    archive: py7zr.SevenZipFile

    def read(self, arcname) -> typing.IO:
        self.archive.reset()  # stupid py7z requires this

        result_dict = self.archive.read(arcname)
        if result_dict is None:
            raise ValueError(f"Could not find {arcname} in archive")
        # py7zr returns a dict with a single key of arcname and returns and IO object
        return result_dict[arcname]

    def write(self, filename, arcname):
        self.archive.write(filename, arcname)

    def read_batch(self, arcnames: typing.List[str]) -> typing.Dict[str, typing.IO]:
        self.archive.reset()
        result = self.archive.read(targets=arcnames)

        # we might have a memory leak here
        return {
            arcname: result[arcname]
            for arcname in result
        }


class ZipArchiveFacade(ArchiveFacade):
    archive: zipfile.ZipFile

    def read_batch(self, arcnames: typing.List[str]) -> typing.Dict[str, typing.Optional[typing.IO]]:
        data = {}
        for arcname in arcnames:
            try:
                data[arcname] = self.read(arcname)
            except KeyError:
                data[arcname] = None
        return data

    def read(self, arcname) -> typing.IO:
        return self.archive.open(arcname)

    def write(self, filename, arcname):
        self.archive.write(filename, arcname)

    def writestr(self, file, arcname):
        self.archive.writestr(arcname, file)


class BaseArchiver:
    supports_batching = True

    def __init__(self, **kwargs):
        # some archivers may require some additional parameters
        self.kwargs = kwargs

    @classmethod
    def can_open(cls, filepath):
        raise NotImplementedError()

    def open_for_read(self, filepath) -> ArchiveFacade:
        raise NotImplementedError()

    def open_for_write(self, filepath) -> ArchiveFacade:
        raise NotImplementedError()

    def __str__(self):
        arguments = ', '.join(
            f'{k}="{v}"' if not str(v).isdigit() else f'{k}={v}'
            for k, v in self.kwargs.items()
        )
        return f'{self.__class__.__name__}({arguments})'


class Py7zrArchiver(BaseArchiver):
    supports_batching = False

    @classmethod
    def can_open(cls, filepath):
        return py7zr.is_7zfile(filepath)

    def open_for_read(self, filepath):
        return Py7zrArchiveFacade(
            py7zr.SevenZipFile(filepath, mode='r', **self.kwargs)
        )

    def open_for_write(self, filepath):
        return Py7zrArchiveFacade(
            py7zr.SevenZipFile(filepath, mode='w', **self.kwargs)
        )


class ZipArchiver(BaseArchiver):
    supports_batching = True

    @classmethod
    def can_open(cls, filepath):
        return zipfile.is_zipfile(filepath)

    def open_for_read(self, filepath):
        return ZipArchiveFacade(
            zipfile.ZipFile(filepath, mode='r', **self.kwargs)
        )

    def open_for_write(self, filepath):
        return ZipArchiveFacade(
            zipfile.ZipFile(filepath, mode='w', **self.kwargs)
        )


def detect_archiver(filepath: Union[AnyStr, pathlib.PurePath]) -> Union[None, Type[BaseArchiver]]:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File {filepath} does not exist")

    for archiver_class in [Py7zrArchiver, ZipArchiver]:
        if archiver_class.can_open(filepath):
            return archiver_class
    else:
        return None
