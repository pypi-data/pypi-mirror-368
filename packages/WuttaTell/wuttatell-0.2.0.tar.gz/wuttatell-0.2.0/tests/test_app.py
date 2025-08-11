# -*- coding: utf-8; -*-

from wuttjamaican.testing import ConfigTestCase

from wuttatell import app as mod
from wuttatell.telemetry import TelemetryHandler


class TestWuttaTellAppProvider(ConfigTestCase):

    def make_provider(self):
        return mod.WuttaTellAppProvider(self.config)

    def test_get_telemetry_handler(self):
        handler = self.app.get_telemetry_handler()
        self.assertIsInstance(handler, TelemetryHandler)
