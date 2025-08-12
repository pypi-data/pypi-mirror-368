import datetime
import json
import shutil
import tempfile
from pathlib import Path

from rebotics_sdk.cli.hawkeye import hawkeye_camera

from . import RESOURCES_FOLDER


def test_api_heartbeat_invoke(runner, mocker_patch_hawkeye_camera_provider):
    data = {"status": 200, "actions": []}
    mocker_patch_hawkeye_camera_provider.save_camera_heartbeat.side_effect = lambda *args: data

    result = runner.invoke(
        hawkeye_camera,
        [
            '--host', 'http://xd.com',
            '--format', 'json',
            'heartbeat',
            '-c', 'test_camera',
            '-b', '0.55',
            '-w', '4.00',
            '-t', '2021-09-16T10:33:45.582912'
        ],
    )
    mocker_patch_hawkeye_camera_provider.save_camera_heartbeat.assert_called_once_with(
        'test_camera',
        0.55,
        4.00,
        datetime.datetime(2021, 9, 16, 10, 33, 45, 582912).isoformat(),
    )
    assert result.exit_code == 0
    assert not result.exception
    assert data == json.loads(result.output)


def test_api_heartbeat_invoke_without_camera(runner, mocker_patch_hawkeye_provider):
    result = runner.invoke(
        hawkeye_camera,
        [
            '--host', 'http://xd.com',
            'heartbeat',
            '-b', '0.55',
            '-w', '4.00',
            '-t', '2021-09-16T10:33:45.582912'
        ],
    )
    assert result.exit_code == 2
    assert result.exception
    assert "Missing option '-c' / '--camera'" in result.output.strip()


def test_api_capture_invoke(runner, mocker_patch_hawkeye_camera_provider):
    data = {
        'destination': {
            'provider': 'aws-s3-skip',
            'url': 'https://chum-bucket.s3.amazing.com'
        },
        'file_key': 'some/body/once/told/me.jpg',
    }
    mocker_patch_hawkeye_camera_provider.create_capture_url.return_value = data
    mocker_patch_hawkeye_camera_provider.create_capture.return_value = {}

    with tempfile.TemporaryDirectory() as base_dir:
        base_dir_path = Path(base_dir)
        filename = 'qwerty.csv'
        filepath = base_dir_path.absolute() / filename
        shutil.copy(RESOURCES_FOLDER / filename, filepath)
        result = runner.invoke(
            hawkeye_camera,
            [
                '--host', 'http://xd.com',
                'create-capture',
                str(filepath),
                '-c', 'test_camera',
            ],
        )
    mocker_patch_hawkeye_camera_provider.create_capture_url.assert_called_once_with(
        'test_camera', filename
    )
    mocker_patch_hawkeye_camera_provider.create_capture.assert_called_once_with(
        'test_camera', data['file_key']
    )
    assert result.exit_code == 0
    assert not result.exception
    assert 'Capture created successfully' in result.output.strip()
