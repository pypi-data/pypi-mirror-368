import pathlib
from unittest.mock import Mock

import pytest
from click.testing import CliRunner

from rebotics_sdk.providers.hawkeye import HawkeyeProvider, HawkeyeCameraProvider


@pytest.fixture(scope="module")
def script_cwd(request):
    return pathlib.Path(request.fspath.join(".."))


@pytest.fixture(scope="function")
def runner():
    return CliRunner()


@pytest.fixture(scope="function")
def mocker_patch_hawkeye_provider(mocker):
    provider_mock = Mock(spec=HawkeyeProvider)
    mocker.patch('rebotics_sdk.cli.utils.ReboticsCLIContext.provider', new=provider_mock)
    mocker.patch('rebotics_sdk.cli.hawkeye.process_role', return_value=None)

    return provider_mock


@pytest.fixture(scope="function")
def mocker_patch_hawkeye_camera_provider(mocker):
    provider_mock = Mock(spec=HawkeyeCameraProvider)
    mocker.patch('rebotics_sdk.cli.utils.ReboticsCLINoConfigContext.provider', new=provider_mock)
    mocker.patch('rebotics_sdk.advanced.flows.PresignedURLFileUploader.upload', return_value=None)

    return provider_mock
