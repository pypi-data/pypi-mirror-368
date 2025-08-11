# -*- coding: utf-8; -*-

from unittest.mock import Mock, patch

from wuttjamaican.testing import ConfigTestCase

from wuttatell.cli import tell as mod
from wuttatell.telemetry import TelemetryHandler


class TestTell(ConfigTestCase):

    def test_basic(self):
        ctx = Mock()
        ctx.parent = Mock()
        ctx.parent.wutta_config = self.config
        with patch.object(TelemetryHandler, 'submit_all_data') as submit_all_data:

            # dry run
            with patch.object(TelemetryHandler, 'collect_all_data') as collect_all_data:
                mod.tell(ctx, dry_run=True)
                collect_all_data.assert_called_once_with(profile=None)
                submit_all_data.assert_not_called()

            # live run
            mod.tell(ctx)
            submit_all_data.assert_called_once()
