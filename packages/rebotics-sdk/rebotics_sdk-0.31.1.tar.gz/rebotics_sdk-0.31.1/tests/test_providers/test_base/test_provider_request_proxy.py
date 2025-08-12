import json
from unittest import TestCase
from urllib.parse import urljoin

import requests_mock

from rebotics_sdk.providers import ReboticsBaseProvider, ProviderRequestProxy, remote_service
from tests.utils import get_random_string

test_method_uri = '/dummy/'


class Stub:
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class TestProvider(ReboticsBaseProvider):

    proxy_class = ProviderRequestProxy
    proxy_config = {}

    @remote_service(test_method_uri)
    def dummy_call(self, method: str, kwargs):
        return getattr(self.session, method)(**kwargs)


class ProviderLoggingTestCase(TestCase):
    def setUp(self):
        self.host_url = 'https://' + get_random_string(6).lower() + '/'
        self.api_url = urljoin(self.host_url, test_method_uri)

    @requests_mock.Mocker()
    def test_logging_cases(self, mock_requests):
        """
        If api_verbosity = 0, no logging
        If api_verbosity = 1, logging HTTP method name with requested URL
        If api_verbosity = 2 and method GET - logging HTTP method name with requested URL
        If api_verbosity = 2 and method in 'put', 'patch', 'post' - logging HTTP method name, requested URL, body.
        If api_verbosity = 3 display all curl requests via requests-to-curl
        """
        body = {'test': 'same_data'}
        cases = (
            (
                'get', {}, 0, '', ''
            ),
            (
                'get', {}, 1, f'\nGET {self.api_url}', ''
            ),
            (
                'patch', {'json': body}, 1, f'\nPATCH {self.api_url}', ''
            ),
            (
                'get', {}, 2, f'\nGET {self.api_url}', ''
            ),
            (
                'put', {'params': body}, 2, f'\nPUT {self.api_url}', f'\n{json.dumps(body, indent=4)}\n'
            ),
            (
                'post',
                {'data': body},
                3,
                f"curl -X POST -H 'Content-Type: application/x-www-form-urlencoded' -d test=same_data {self.api_url}",
                ''
            ),
        )
        for method, body, verbosity, expected_http, expected_body in cases:
            mock_requests.register_uri(method, self.api_url, json={"test": "test"})

            provider = TestProvider(self.host_url, api_verbosity=verbosity)

            # assertLogs fail unless a log message of level *level* or higher is emitted
            # use assertRaises(AssertionError)
            with (self.assertRaises(AssertionError) if verbosity == 0 else Stub()), self.subTest(msg=method), \
                self.assertLogs() as logger:

                provider.dummy_call(method, body)

            if verbosity == 0:
                self.assertEqual(0, len(logger.records))

            elif verbosity == 1:
                self.assertEqual(1, len(logger.records))
                self.assertEqual(expected_http, logger.records[0].message)

            elif verbosity == 2:
                if method == 'get':
                    self.assertEqual(1, len(logger.records))
                    self.assertEqual(expected_http, logger.records[0].message)
                if method in ('put', 'patch', 'post'):
                    self.assertEqual(2, len(logger.records))
                    self.assertEqual(expected_http, logger.records[0].message)
                    self.assertEqual(expected_body, logger.records[1].message)

            elif verbosity == 3:
                self.assertEqual(1, len(logger.records))
                self.assertEqual(expected_http, logger.records[0].message)


