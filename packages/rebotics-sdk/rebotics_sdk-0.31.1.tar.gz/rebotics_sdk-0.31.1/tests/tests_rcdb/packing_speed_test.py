import csv
import datetime as dt
import gc
import os
import subprocess as sp
import time
import typing
from dataclasses import dataclass
from pathlib import Path
from unittest import TestCase, skip

from rebotics_sdk.advanced.packers import ClassificationEntry, FileInputZipDatabasePacker
from rebotics_sdk.rcdb import Packer, Unpacker
from rebotics_sdk.rcdb.entries import BaseEntry
from rebotics_sdk.rcdb.fields import BinaryFeatureVectorField, FeatureVectorField, StringField

if typing.TYPE_CHECKING:
    from pathlib import PurePath, WindowsPath


RUNS = 5


def get_ram_in_bytes() -> int:
    time.sleep(5)
    return int(sp.check_output("cat /sys/fs/cgroup/memory/memory.usage_in_bytes".split(" ")).decode("utf-8"))


def get_size(path: Path):
    total = 0
    if path.is_file():
        return path.stat().st_size

    for root, directories, files in os.walk(path):
        for file in files:
            try:
                total += os.path.getsize(Path(root) / file)
            except (PermissionError, FileNotFoundError):
                continue

    return total

@dataclass
class TestCaseParameterSet:
    name: str
    input_path: typing.Union["PurePath", "WindowsPath", Path]
    archive_name: str
    model_type: typing.Type["BaseEntry"]


class LegacyEntry(BaseEntry):
    label = StringField()
    feature_vector = FeatureVectorField()


class BinaryFeatureVectorEntry(BaseEntry):
    label = StringField()
    feature_vector = BinaryFeatureVectorField()


class SpeedFrameworkTest(TestCase):
    test_folder = Path("/app/temp/")
    stat_file_path = Path("/resources/stats.csv")
    stat_file_headers = [
        "test_case", "run_index", "archive_size",
        "packing_start", "packing_end", "packing_seconds",
        "unpacking_start", "unpacking_end", "unpacking_seconds",
        "fv_count",
    ]
    ram_stat_file_path = Path("/resources/stats_ram.csv")
    ram_stat_file_headers = [
        "test_case", "run_index", "initial",
        "packing_start", "packing_before_cleanup", "packing_end",
        "unpacking_before_cleanup", "unpacking_end",
    ]
    test_cases = [
        TestCaseParameterSet(
            "Text number test",
            test_folder,
            "archive.rcdb",
            model_type=LegacyEntry,
        ),
        TestCaseParameterSet(
            "Binary number test",
            test_folder,
            "archive.rcdb",
            model_type=BinaryFeatureVectorEntry,
        ),
    ]
    fvs: typing.List[ClassificationEntry] = []

    def setUp(self):
        default_archive = Path("/app/data_ea20c7d283ab417e9e8536807ae2f208.rcdb")
        default_unpacker = FileInputZipDatabasePacker(source=default_archive)
        self.fvs: typing.List[ClassificationEntry] = list(default_unpacker.unpack())
        if not self.test_folder.exists():
            self.test_folder.mkdir(exist_ok=True)

    @skip(reason="The test should only be invoked manually.")
    def test_execution_time(self):
        if not self.stat_file_path.exists():
            with open(self.stat_file_path, "w") as file:
                writer = csv.DictWriter(file, fieldnames=self.stat_file_headers)
                writer.writeheader()
            del writer
        if not self.ram_stat_file_path.exists():
            with open(self.ram_stat_file_path, "w") as file:
                writer = csv.DictWriter(file, fieldnames=self.ram_stat_file_headers)
                writer.writeheader()
            del writer
        gc.collect()

        initial_ram = get_ram_in_bytes()

        for packer_test_case in self.test_cases:
            for run_index in range(RUNS):
                archive_path = packer_test_case.input_path / packer_test_case.archive_name
                if archive_path.exists():
                    archive_path.unlink(missing_ok=True)

                packing_start_ram = get_ram_in_bytes()
                packing_start = dt.datetime.now()
                with Packer(archive_path, packer_test_case.model_type, batch_size=50_000) as packer:
                    for entry in self.fvs:
                        packer.add_entry(packer_test_case.model_type(
                            label=entry.label,
                            feature_vector=entry.feature,
                        ))
                packing_end = dt.datetime.now()
                packing_cleanup_ram = get_ram_in_bytes()
                del packer
                gc.collect()
                packing_end_ram = get_ram_in_bytes()

                archive_size = get_size(archive_path)

                unpacking_start = dt.datetime.now()
                with Unpacker(archive_path, packer_test_case.model_type) as unpacker:
                    values = list(unpacker.entries())
                unpacking_end = dt.datetime.now()
                unpacking_cleanup_ram = get_ram_in_bytes()
                del unpacker
                gc.collect()
                unpacking_end_ram = get_ram_in_bytes()

                values_count = len(values)

                with open(self.stat_file_path, "a") as file:
                    writer = csv.DictWriter(file, fieldnames=self.stat_file_headers)
                    writer.writerow({
                        "test_case": packer_test_case.name,
                        "run_index": run_index,
                        "archive_size": int(archive_size),
                        "packing_start": packing_start.timestamp(),
                        "packing_end": packing_end.timestamp(),
                        "packing_seconds": (packing_end - packing_start).total_seconds(),
                        "unpacking_start": unpacking_start.timestamp(),
                        "unpacking_end": unpacking_end.timestamp(),
                        "unpacking_seconds": (unpacking_end - unpacking_start).total_seconds(),
                        "fv_count": values_count,
                    })
                with open(self.ram_stat_file_path, "a") as file:
                    writer = csv.DictWriter(file, fieldnames=self.ram_stat_file_headers)
                    writer.writerow({
                        "test_case": packer_test_case.name,
                        "run_index": run_index,
                        "initial": initial_ram,
                        "packing_start": packing_start_ram,
                        "packing_before_cleanup": packing_cleanup_ram,
                        "packing_end": packing_end_ram,
                        "unpacking_before_cleanup": unpacking_cleanup_ram,
                        "unpacking_end": unpacking_end_ram,
                    })

                archive_path.unlink()
                del values
                gc.collect()
