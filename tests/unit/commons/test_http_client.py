# -*- coding: utf-8 -*-

import unittest
import requests
import json
from pyowm.exceptions import api_call_error, unauthorized_error, not_found_error, \
    parse_response_error
from pyowm.commons.http_client import HttpClient


class MockResponse:
    def __init__(self, status, payload):
        self.status_code = status
        self.text = payload

    def json(self):
        return json.loads(self.text)


class TestHTTPClient(unittest.TestCase):

    requests_original_get = requests.get
    requests_original_post = requests.post
    requests_original_put= requests.put
    requests_original_delete = requests.delete

    def test_get_json(self):

        expected_data = '{"name": "james bond", "designation": "007"}'

        def monkey_patched_get(uri, params=None, headers=None):
            return MockResponse(200, expected_data)

        requests.get = monkey_patched_get
        status, data = HttpClient().get_json('http://anyurl.com')
        self.assertEquals(json.loads(expected_data), data)
        requests.get = self.requests_original_get

    def test_get_json_parse_error(self):

        def monkey_patched_get(uri, params=None, headers=None):
            return MockResponse(200, 123846237647236)

        requests.get = monkey_patched_get
        self.assertRaises(parse_response_error.ParseResponseError,
                          HttpClient().get_json,
                          'http://anyurl.com',
                          params=dict(a=1, b=2))
        requests.get = self.requests_original_get

    def test_post(self):
        expected_data = '{"key": "value"}'

        def monkey_patched_post(uri, params=None, headers=None, json=None):
            return MockResponse(201, expected_data)

        requests.post = monkey_patched_post
        status, data = HttpClient().post('http://anyurl.com', data=dict(key='value'))
        self.assertEquals(json.loads(expected_data), data)

        requests.post = self.requests_original_post

    def test_put(self):
        expected_data = '{"key": "value"}'

        def monkey_patched_put(uri, params=None, headers=None, json=None):
            return MockResponse(200, expected_data)

        requests.put = monkey_patched_put
        status, data = HttpClient().put('http://anyurl.com', data=dict(key=7))
        self.assertEquals(json.loads(expected_data), data)

        requests.put = self.requests_original_put

    def test_delete(self):
        # in case an empty payload is returned
        def monkey_patched_delete(uri, params=None, headers=None, json=None):
            return MockResponse(204, None)

        requests.delete = monkey_patched_delete
        status, data = HttpClient().delete('http://anyurl.com')
        self.assertIsNone(data)

        # in case a non-empty payload is returned
        expected_data = '{"message": "deleted"}'

        def monkey_patched_delete_returning_payload(uri, params=None, headers=None, json=None):
            return MockResponse(204, expected_data)

        requests.delete = monkey_patched_delete_returning_payload
        status, data = HttpClient().delete('http://anyurl.com')
        self.assertEquals(json.loads(expected_data), data)

        requests.delete = self.requests_original_delete

    def test_check_status_code(self):
        msg = 'Generic error'
        HttpClient.check_status_code(200, msg)
        with self.assertRaises(api_call_error.APICallError):
            HttpClient.check_status_code(400, msg)
        with self.assertRaises(unauthorized_error.UnauthorizedError):
            HttpClient.check_status_code(401, msg)
        with self.assertRaises(not_found_error.NotFoundError):
            HttpClient.check_status_code(404, msg)
        with self.assertRaises(api_call_error.BadGatewayError):
            HttpClient.check_status_code(502, msg)
        with self.assertRaises(api_call_error.APICallError):
            HttpClient.check_status_code(555, msg)

    def test_is_success(self):
        self.assertTrue(HttpClient.is_success(200))
        self.assertTrue(HttpClient.is_success(201))
        self.assertTrue(HttpClient.is_success(299))
        self.assertFalse(HttpClient.is_success(300))
        self.assertFalse(HttpClient.is_success(400))
        self.assertFalse(HttpClient.is_success(500))
