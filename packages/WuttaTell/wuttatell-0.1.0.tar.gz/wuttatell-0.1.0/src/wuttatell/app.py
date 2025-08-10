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
App Provider
"""

from wuttjamaican.app import AppProvider


class WuttaTellAppProvider(AppProvider):
    """
    The :term:`app provider` for WuttaTell.

    This adds the :meth:`get_telemetry_handler()` method for the
    :term:`app handler`.
    """

    def get_telemetry_handler(self, **kwargs):
        """
        Get the configured telemetry handler.

        :rtype: :class:`~wuttatell.telemetry.TelemetryHandler`
        """
        if not hasattr(self, 'telemetry_handler'):
            spec = self.config.get(f'{self.appname}.telemetry.handler',
                                   default='wuttatell.telemetry:TelemetryHandler')
            factory = self.app.load_object(spec)
            self.telemetry_handler = factory(self.config, **kwargs)
        return self.telemetry_handler
