import datetime

from rebotics_sdk.cli.hawkeye import api


def test_api_fixture_invoke(runner, mocker_patch_hawkeye_provider):
    data = {
        "id": 1,
        "created": datetime.datetime(2021, 9, 16, 10, 33, 45, 582912),
        "modified": datetime.datetime(2021, 9, 16, 10, 33, 45, 582912),
        "store_id": "1",
        "aisle": "aisletest",
        "section": "sectiontest",
    }
    mocker_patch_hawkeye_provider.save_fixture.side_effect = lambda *args, **kwargs: data
    result = runner.invoke(
        api,
        [
            'fixture',
            '-i', "1",
            '-a', 'aisletest',
            '-s', 'sectiontest'
        ]
    )
    mocker_patch_hawkeye_provider.save_fixture.assert_called_once_with(
        store_id="1",
        aisle='aisletest',
        section='sectiontest',
        planogram=None,
        category=None,
        shelf_camera_id=None
    )
    assert result.exit_code == 0, f"Failed because of {result.exception}"
    assert not result.exception
    assert str(data) in result.output


def test_api_fixture_invoke_without_option(runner, mocker_patch_hawkeye_provider):
    result = runner.invoke(
        api,
        [
            'fixture',
            '-i', 'storetest'
        ]
    )
    assert result.exit_code == 0


def test_get_fixtures_invoke(runner, mocker_patch_hawkeye_provider):
    data = []
    mocker_patch_hawkeye_provider.get_fixtures.side_effect = lambda *args, **kwargs: data
    result = runner.invoke(
        api,
        ['fixtures']
    )
    mocker_patch_hawkeye_provider.get_fixtures.assert_called()
    assert result.exit_code == 0
    assert not result.exception
    assert str(data) in result.output.strip()


def test_api_camera_invoke(runner, mocker_patch_hawkeye_provider):
    data = {
        "id": 1,
        "created": datetime.datetime(2021, 9, 16, 10, 33, 45, 582912),
        "modified": datetime.datetime(2021, 9, 16, 10, 33, 45, 582912),
        "camera_id": "testcameraid",
        "added_by": 1,
        "aisle": 1,
        "section": 1
    }
    mocker_patch_hawkeye_provider.create_shelf_camera.side_effect = lambda *args: data
    result = runner.invoke(
        api,
        [
            'camera',
            '-c', 'testcameraid',
            '-a', '1',
            '-f', '1'
        ]
    )
    mocker_patch_hawkeye_provider.create_shelf_camera.assert_called_once_with(
        'testcameraid',
        1,
        1
    )
    assert result.exit_code == 0
    assert not result.exception
    assert str(data) in result.output.strip()


def test_api_camera_invoke_without_option(runner, mocker_patch_hawkeye_provider):
    result = runner.invoke(
        api,
        [
            'camera',
            '-c', 'testcameraid'
        ]
    )
    assert result.exit_code == 2
    assert result.exception
    assert "Missing option" in result.output.strip()


def test_get_list_shelf_cameras(runner, mocker_patch_hawkeye_provider):
    mocker_patch_hawkeye_provider.get_shelf_cameras.side_effect = lambda *args: []
    result = runner.invoke(
        api,
        ['cameras']
    )
    mocker_patch_hawkeye_provider.get_shelf_cameras.assert_called()
    assert result.exit_code == 0
    assert not result.exception
    assert str([]) in result.output.strip()
