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
See also: :ref:`wutta-tell`
"""

import logging

import typer
from typing_extensions import Annotated

from wuttjamaican.cli import wutta_typer


log = logging.getLogger(__name__)


@wutta_typer.command()
def tell(
        ctx: typer.Context,
        profile: Annotated[
            str,
            typer.Option('--profile', '-p',
                         help="Profile (type) of telemetry data to collect.  "
                         "This also determines where/how data is submitted.  "
                         "If not specified, default profile is assumed.")] = None,
        dry_run: Annotated[
            bool,
            typer.Option('--dry-run',
                         help="Go through all the motions but do not submit "
                         "the data to server.")] = False,
):
    """
    Collect and submit telemetry data
    """
    config = ctx.parent.wutta_config
    app = config.get_app()
    telemetry = app.get_telemetry_handler()

    data = telemetry.collect_all_data(profile=profile)
    log.info("data collected okay: %s", ', '.join(sorted(data)))
    log.debug("%s", data)

    if dry_run:
        log.info("dry run, so will not submit data to server")
    else:
        telemetry.submit_all_data(profile=profile, data=data)
        log.info("data submitted okay")
