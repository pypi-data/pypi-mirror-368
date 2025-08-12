from unittest import TestCase
from unittest.mock import patch, MagicMock

from click.testing import CliRunner

from rebotics_sdk.cli.retailer import api
from rebotics_sdk.cli.utils import ReboticsScriptsConfiguration
from rebotics_sdk.providers.retailer import RetailerProvider
from rebotics_sdk.constants import CvatTaskPriority


class RetailerProviderTestCase(TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()

    @patch('rebotics_sdk.cli.retailer.process_role')
    @patch.object(ReboticsScriptsConfiguration, 'get_provider')
    @patch.object(RetailerProvider, 'export_to_cvat')
    def test_export_to_cvat(self, export_mock: MagicMock, provider_mock: MagicMock, *args):
        scan_ids = [1, 2, 3]
        image_quality = 70
        segment_size = 30
        workspace = 'Workspace'
        priority = list(CvatTaskPriority.OPTIONS)[0]
        command = 'export-to-cvat'
        provider_mock.return_value = RetailerProvider('https://example.com')

        self.runner.invoke(api, [
            command,
            '-q', image_quality,
            '-s', segment_size,
            '-w', workspace,
            '-p', priority,
            *[str(i) for i in scan_ids]
        ])
        export_mock.assert_called_once_with(
            tuple(scan_ids),
            image_quality,
            segment_size,
            workspace,
            CvatTaskPriority.OPTIONS.get(priority),
        )
