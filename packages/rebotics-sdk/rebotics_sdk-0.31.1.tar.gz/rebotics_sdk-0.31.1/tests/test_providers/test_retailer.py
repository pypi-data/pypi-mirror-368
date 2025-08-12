from unittest import TestCase
from unittest.mock import patch, MagicMock

from rebotics_sdk.providers.base import ProviderRequestProxy
from rebotics_sdk.providers.retailer import RetailerProvider
from rebotics_sdk.constants import CvatTaskPriority


class RetailerProviderTestCase(TestCase):
    def setUp(self) -> None:
        self.provider = RetailerProvider('https://example.com')

    @patch.object(ProviderRequestProxy, 'post')
    def test_export_to_cvat(self, mock_func: MagicMock):
        scan_ids = [4, 3, 4, 2, 1, 2, 1, 3]
        image_quality = 70
        segment_size = 30
        workspace = 'Workspace'
        priority = CvatTaskPriority.LOW
        self.provider.export_to_cvat(scan_ids, image_quality, segment_size, workspace, priority)
        mock_func.assert_called_once_with(json={
            'scans': [1, 2, 3, 4],
            'image_quality': image_quality,
            'segment_size': segment_size,
            'workspace': workspace,
            'priority': priority,
        })
