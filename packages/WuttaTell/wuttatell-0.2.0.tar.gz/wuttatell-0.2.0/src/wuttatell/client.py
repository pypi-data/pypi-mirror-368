# -*- coding: utf-8; -*-
################################################################################
#
#  WuttaTell -- Telemetry submission for Wutta Framework
#  Copyright © 2025 Lance Edgar
#
#  This file is part of Wutta Framework.
#
#  Wutta Framework is free software: you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option) any
#  later version.
#
#  Wutta Framework is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#  more details.
#
#  You should have received a copy of the GNU General Public License along with
#  Wutta Framework.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Simple API Client
"""

import json
from urllib.parse import urlparse

import requests


class SimpleAPIClient:
    """
    Simple client for "typical" API service.

    This basically assumes telemetry can be submitted to a single API
    endpoint, and the request should contain an auth token.

    :param config: App :term:`config object`.

    :param base_url: Base URL of the API.

    :param token: Auth token for the API.

    :param ssl_verify: Whether the SSL cert presented by the server
       should be verified.  This is effectively true by default, but
       may be disabled for testing with self-signed certs etc.

    :param max_retries: Maximum number of retries each connection
       should attempt.  This value is ultimately given to the
       :class:`~requests:requests.adapters.HTTPAdapter` instance.

    Most params may be omitted, if config specifies instead:

    .. code-block:: ini

       [wutta.api]
       base_url = https://my.example.com/api
       token = XYZPDQ12345
       ssl_verify = false
       max_retries = 5

    Upon instantiation, :attr:`session` will be ``None`` until the
    first request is made.  (Technically when :meth:`init_session()`
    first happens.)

    .. attribute:: session

       :class:`requests:requests.Session` instance being used to make
       API requests.
    """

    def __init__(self, config, base_url=None, token=None, ssl_verify=None, max_retries=None):
        self.config = config

        self.base_url = base_url or self.config.require(f'{self.config.appname}.api.base_url')
        self.base_url = self.base_url.rstrip('/')
        self.token = token or self.config.require(f'{self.config.appname}.api.token')

        if max_retries is not None:
            self.max_retries = max_retries
        else:
            self.max_retries = self.config.get_int(f'{self.config.appname}.api.max_retries')

        if ssl_verify is not None:
            self.ssl_verify = ssl_verify
        else:
            self.ssl_verify = self.config.get_bool(f'{self.config.appname}.api.ssl_verify',
                                                   default=True)

        self.session = None

    def init_session(self):
        """
        Initialize the HTTP session with the API.

        This method is invoked as part of :meth:`make_request()`.

        It first checks :attr:`session` and will skip if already initialized.

        For initialization, it establishes a new
        :class:`requests:requests.Session` instance, and modifies it
        as needed per config.
        """
        if self.session:
            return

        self.session = requests.Session()

        # maybe *disable* SSL cert verification
        # (should only be used for testing e.g. w/ self-signed certs)
        if not self.ssl_verify:
            self.session.verify = False

        # maybe set max retries, e.g. for flaky connections
        if self.max_retries is not None:
            adapter = requests.adapters.HTTPAdapter(max_retries=self.max_retries)
            self.session.mount(self.base_url, adapter)

        # TODO: is this a good idea, or hacky security risk..?
        # without it, can get error response:
        # 400 Client Error: Bad CSRF Origin for url
        parts = urlparse(self.base_url)
        self.session.headers.update({
            'Origin': f'{parts.scheme}://{parts.netloc}',
        })

        # authenticate via token only (for now?)
        self.session.headers.update({
            'Authorization': f'Bearer {self.token}',
        })

    def make_request(self, request_method, api_method, params=None, data=None):
        """
        Make a request to the API, and return the response.

        This first calls :meth:`init_session()` to establish the
        session if needed.

        :param request_method: HTTP request method; for now only
           ``'GET'`` and ``'POST'`` are supported.

        :param api_method: API method endpoint to use,
           e.g. ``'/my/telemetry'``

        :param params: Dict of query string params for the request, if
           applicable.

        :param data: Payload data for the request, if applicable.
           Should be JSON-serializable, e.g. a list or dict.

        :rtype: :class:`requests:requests.Response` instance.
        """
        self.init_session()
        api_method = api_method.lstrip('/')
        url = f'{self.base_url}/{api_method}'
        if request_method == 'GET':
            response = self.session.get(url, params=params)
        elif request_method == 'POST':
            response = self.session.post(url, params=params,
                                         data=json.dumps(data))
        else:
            raise NotImplementedError(f"unsupported request method: {request_method}")
        response.raise_for_status()
        return response

    def get(self, api_method, params=None):
        """
        Perform a GET request for the given API method, and return the
        response.

        This calls :meth:`make_request()` for the heavy lifting.

        :param api_method: API method endpoint to use,
           e.g. ``'/my/telemetry'``

        :param params: Dict of query string params for the request, if
           applicable.

        :rtype: :class:`requests:requests.Response` instance.
        """
        return self.make_request('GET', api_method, params=params)

    def post(self, api_method, **kwargs):
        """
        Perform a POST request for the given API method, and return
        the response.

        This calls :meth:`make_request()` for the heavy lifting.

        :param api_method: API method endpoint to use,
           e.g. ``'/my/telemetry'``

        :rtype: :class:`requests:requests.Response` instance.
        """
        return self.make_request('POST', api_method, **kwargs)
