# -*- coding: utf-8; -*-

import json
import threading
import time
from http import HTTPStatus
from http.server import HTTPServer, BaseHTTPRequestHandler

import requests
from urllib3.util.retry import Retry

from wuttjamaican.testing import ConfigTestCase
from wuttatell import client as mod


class TestSimpleAPIClient(ConfigTestCase):

    def make_client(self, **kw):
        return mod.SimpleAPIClient(self.config, **kw)

    def test_constructor(self):

        # caller specifies params
        client = self.make_client(base_url='https://example.com/api/',
                                  token='XYZPDQ12345',
                                  ssl_verify=False,
                                  max_retries=5)
        self.assertEqual(client.base_url, 'https://example.com/api') # no trailing slash
        self.assertEqual(client.token, 'XYZPDQ12345')
        self.assertFalse(client.ssl_verify)
        self.assertEqual(client.max_retries, 5)
        self.assertIsNone(client.session)

        # now with some defaults
        client = self.make_client(base_url='https://example.com/api/',
                                  token='XYZPDQ12345')
        self.assertEqual(client.base_url, 'https://example.com/api') # no trailing slash
        self.assertEqual(client.token, 'XYZPDQ12345')
        self.assertTrue(client.ssl_verify)
        self.assertIsNone(client.max_retries)
        self.assertIsNone(client.session)

        # now from config
        self.config.setdefault('wutta.api.base_url', 'https://another.com/api/')
        self.config.setdefault('wutta.api.token', '9843243q4')
        self.config.setdefault('wutta.api.ssl_verify', 'false')
        self.config.setdefault('wutta.api.max_retries', '4')
        client = self.make_client()
        self.assertEqual(client.base_url, 'https://another.com/api') # no trailing slash
        self.assertEqual(client.token, '9843243q4')
        self.assertFalse(client.ssl_verify)
        self.assertEqual(client.max_retries, 4)
        self.assertIsNone(client.session)

    def test_init_session(self):

        # client begins with no session
        client = self.make_client(base_url='https://example.com/api', token='1234')
        self.assertIsNone(client.session)

        # session is created here
        client.init_session()
        self.assertIsInstance(client.session, requests.Session)
        self.assertTrue(client.session.verify)
        self.assertTrue(all([a.max_retries.total == 0 for a in client.session.adapters.values()]))
        self.assertIn('Authorization', client.session.headers)
        self.assertEqual(client.session.headers['Authorization'], 'Bearer 1234')

        # session is never re-created
        orig_session = client.session
        client.init_session()
        self.assertIs(client.session, orig_session)

        # new client/session with no ssl_verify
        client = self.make_client(base_url='https://example.com/api', token='1234', ssl_verify=False)
        client.init_session()
        self.assertFalse(client.session.verify)

        # new client/session with max_retries
        client = self.make_client(base_url='https://example.com/api', token='1234', max_retries=5)
        client.init_session()
        self.assertEqual(client.session.adapters['https://example.com/api'].max_retries.total, 5)

    def test_make_request_get(self):

        # start server
        threading.Thread(target=start_server).start()
        while not SERVER['running']:
            time.sleep(0.02)

        # server returns our headers
        client = self.make_client(base_url=f'http://127.0.0.1:{SERVER["port"]}', token='1234', ssl_verify=False)
        response = client.make_request('GET', '/telemetry')
        result = response.json()
        self.assertIn('headers', result)
        self.assertIn('Authorization', result['headers'])
        self.assertEqual(result['headers']['Authorization'], 'Bearer 1234')
        self.assertNotIn('payload', result)

    def test_make_request_post(self):

        # start server
        threading.Thread(target=start_server).start()
        while not SERVER['running']:
            time.sleep(0.02)

        # server returns our headers + payload
        client = self.make_client(base_url=f'http://127.0.0.1:{SERVER["port"]}', token='1234', ssl_verify=False)
        response = client.make_request('POST', '/telemetry', data={'os': {'name': 'debian'}})
        result = response.json()
        self.assertIn('headers', result)
        self.assertIn('Authorization', result['headers'])
        self.assertEqual(result['headers']['Authorization'], 'Bearer 1234')
        self.assertIn('payload', result)
        self.assertEqual(json.loads(result['payload']), {'os': {'name': 'debian'}})

    def test_make_request_unsupported(self):

        # start server
        threading.Thread(target=start_server).start()
        while not SERVER['running']:
            time.sleep(0.02)

        # e.g. DELETE is not implemented
        client = self.make_client(base_url=f'http://127.0.0.1:{SERVER["port"]}', token='1234', ssl_verify=False)
        self.assertRaises(NotImplementedError, client.make_request, 'DELETE', '/telemetry')

        # nb. issue valid request to stop the server
        client.make_request('GET', '/telemetry')

    def test_get(self):

        # start server
        threading.Thread(target=start_server).start()
        while not SERVER['running']:
            time.sleep(0.02)

        # server returns our headers
        client = self.make_client(base_url=f'http://127.0.0.1:{SERVER["port"]}', token='1234', ssl_verify=False)
        response = client.get('/telemetry')
        result = response.json()
        self.assertIn('headers', result)
        self.assertIn('Authorization', result['headers'])
        self.assertEqual(result['headers']['Authorization'], 'Bearer 1234')
        self.assertNotIn('payload', result)

    def test_post(self):

        # start server
        threading.Thread(target=start_server).start()
        while not SERVER['running']:
            time.sleep(0.02)

        # server returns our headers + payload
        client = self.make_client(base_url=f'http://127.0.0.1:{SERVER["port"]}', token='1234', ssl_verify=False)
        response = client.post('/telemetry', data={'os': {'name': 'debian'}})
        result = response.json()
        self.assertIn('headers', result)
        self.assertIn('Authorization', result['headers'])
        self.assertEqual(result['headers']['Authorization'], 'Bearer 1234')
        self.assertIn('payload', result)
        self.assertEqual(json.loads(result['payload']), {'os': {'name': 'debian'}})


class FakeRequestHandler(BaseHTTPRequestHandler):
    """ """

    def do_GET(self):
        headers = dict([(k, v) for k, v in self.headers.items()])
        result = {'headers': headers}
        result = json.dumps(result).encode('utf_8')

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", 'text/json')
        self.send_header("Content-Length", str(len(result)))
        self.end_headers()
        self.wfile.write(result)

    def do_POST(self):
        headers = dict([(k, v) for k, v in self.headers.items()])
        length = int(self.headers.get('Content-Length'))
        payload = self.rfile.read(length).decode('utf_8')
        result = {'headers': headers, 'payload': payload}
        result = json.dumps(result).encode('utf_8')

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", 'text/json')
        self.send_header("Content-Length", str(len(result)))
        self.end_headers()
        self.wfile.write(result)


SERVER = {'running': False, 'port': 7314}

def start_server():
    if SERVER['running']:
        raise RuntimeError("http server is already running")

    with HTTPServer(('127.0.0.1', SERVER['port']), FakeRequestHandler) as httpd:
        SERVER['running'] = True
        httpd.handle_request()

    SERVER['running'] = False
