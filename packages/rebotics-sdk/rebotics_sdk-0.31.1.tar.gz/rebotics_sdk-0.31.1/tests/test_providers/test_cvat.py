from unittest import TestCase

import requests_mock

from rebotics_sdk.providers.cvat import CvatProvider


class CvatTestCase(TestCase):
    def setUp(self) -> None:
        self.provider = CvatProvider('http://test.com')
        self.provider.set_retailer_identifier('retailer', 'secret-key')

    def test_import_training_data(self):
        with requests_mock.Mocker() as m:
            m.post('http://test.com/api/retailer_import/', json={'result': 'ok'})
            response = self.provider.start_retailer_import(data={'image': 'url'})
            assert response['result'] == 'ok'
            headers = m.last_request.headers
            assert headers['X-Retailer-Codename'] == 'retailer'
            assert headers['X-Retailer-Secret-Key'] == 'secret-key'

    def test_check_import_progress(self):
        with requests_mock.Mocker() as m:
            m.get('http://test.com/api/retailer_import/1/', json={'result': 'ok'})
            response = self.provider.check_import_progress(task_id=1)
            assert response['result'] == 'ok'
            headers = m.last_request.headers
            assert headers['X-Retailer-Codename'] == 'retailer'
            assert headers['X-Retailer-Secret-Key'] == 'secret-key'
