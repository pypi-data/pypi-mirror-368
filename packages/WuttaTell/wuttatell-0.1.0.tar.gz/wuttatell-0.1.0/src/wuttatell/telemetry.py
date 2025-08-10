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
Telemetry submission handler
"""

import os
import re
import subprocess

from wuttjamaican.app import GenericHandler
from wuttjamaican.conf import WuttaConfigProfile


class TelemetryHandler(GenericHandler):
    """
    Handler for submission of telemetry data

    The primary caller interface involves just two methods:

    * :meth:`collect_all_data()`
    * :meth:`submit_all_data()`
    """

    def get_profile(self, profile):
        """ """
        if isinstance(profile, TelemetryProfile):
            return profile

        return TelemetryProfile(self.config, profile or 'default')

    def collect_all_data(self, profile=None):
        """
        Collect and return all data pertaining to the given profile.

        The profile will determine which types of data to collect,
        e.g. ``('os', 'python')``.  Corresponding handler methods
        are then called to collect each type; for instance:

        * :meth:`collect_data_os()`
        * :meth:`collect_data_python()`

        Once all data has been collected, errors are grouped to the
        top level of the structure.

        :param profile: :class:`TelemetryProfile` instance, or key
           thereof.  If not specified, ``'default'`` is assumed.

        :returns: A dict of data, keyed by collection type.  If any
           errors were encountered during collection, the dict will
           also have an ``'errors'`` key.
        """
        data = {}
        profile = self.get_profile(profile)

        for key in profile.collect_keys:
            collector = getattr(self, f'collect_data_{key}')
            data[key] = collector(profile=profile)

        self.normalize_errors(data)
        return data

    def normalize_errors(self, data):
        """ """
        all_errors = []
        for key, value in data.items():
            if value:
                errors = value.pop('errors', None)
                if errors:
                    all_errors.extend(errors)
        if all_errors:
            data['errors'] = all_errors

    def collect_data_os(self, profile, **kwargs):
        """
        Collect basic data about the operating system.

        This parses ``/etc/os-release`` for basic OS info, and
        ``/etc/timezone`` for the timezone.

        If all goes well the result looks like::

           {
               "release_id": "debian",
               "release_version": "12",
               "release_full": "Debian GNU/Linux 12 (bookworm)",
               "timezone": "America/Chicago",
           }

        :param profile: :class:`TelemetryProfile` instance.  Note that
           the default logic here ignores the profile.

        :returns: Data dict similar to the above.  May have an
           ``'errors'`` key if anything goes wrong.
        """
        data = {}
        errors = []

        # release
        release_path = kwargs.get('release_path', '/etc/os-release')
        try:
            with open(release_path, 'rt') as f:
                output = f.read()
        except:
            errors.append(f"Failed to read {release_path}")
        else:
            release = {}
            pattern = re.compile(r'^([^=]+)=(.*)$')
            for line in output.strip().split('\n'):
                if match := pattern.match(line):
                    key, val = match.groups()
                    if val.startswith('"') and val.endswith('"'):
                        val = val.strip('"')
                    release[key] = val
            try:
                data['release_id'] = release['ID']
                data['release_version'] = release['VERSION_ID']
                data['release_full'] = release['PRETTY_NAME']
            except KeyError:
                errors.append(f"Failed to parse {release_path}")

        # timezone
        timezone_path = kwargs.get('timezone_path', '/etc/timezone')
        try:
            with open(timezone_path, 'rt') as f:
                output = f.read()
        except:
            errors.append(f"Failed to read {timezone_path}")
        else:
            data['timezone'] = output.strip()

        if errors:
            data['errors'] = errors
        return data

    def collect_data_python(self, profile):
        """
        Collect basic data about the Python environment.

        This primarily runs ``python --version`` for the desired
        environment.  Note that the profile will determine which
        environment to inspect, e.g. system-wide or a specific virtual
        environment.

        If all goes well the system-wide result looks like::

           {
               "executable": "/usr/bin/python3",
               "release_full": "Python 3.11.2",
               "release_version": "3.11.2",
           }
        
        If a virtual environment is involved the result will include
        its root path::

           {
               "envroot": "/srv/envs/poser",
               "executable": "/srv/envs/poser/bin/python",
               "release_full": "Python 3.11.2",
               "release_version": "3.11.2",
           }
        
        :param profile: :class:`TelemetryProfile` instance.

        :returns: Data dict similar to the above.  May have an
           ``'errors'`` key if anything goes wrong.
        """
        data = {}
        errors = []

        # envroot determines python executable
        envroot = profile.get_str('collect.python.envroot')
        if envroot:
            data['envroot'] = envroot
            python = os.path.join(envroot, 'bin/python')
        else:
            python = profile.get_str('collect.python.executable',
                                     default='/usr/bin/python3')

        # python version
        data['executable'] = python
        try:
            output = subprocess.check_output([python, '--version'])
        except (subprocess.CalledProcessError, FileNotFoundError) as err:
            errors.append("Failed to execute `python --version`")
            errors.append(str(err))
        else:
            output = output.decode('utf_8').strip()
            data['release_full'] = output
            if match := re.match(r'^Python (\d+\.\d+\.\d+)', output):
                data['release_version'] = match.group(1)
            else:
                errors.append("Failed to parse Python version")

        if errors:
            data['errors'] = errors
        return data

    def submit_all_data(self, profile=None, data=None):
        """
        Submit telemetry data to the configured collection service.

        Default logic is not implemented; subclass must override.

        :param profile: :class:`TelemetryProfile` instance.

        :param data: Data dict as obtained by
           :meth:`collect_all_data()`.
        """
        raise NotImplementedError


class TelemetryProfile(WuttaConfigProfile):
    """
    Represents a configured profile for telemetry submission.

    This is a subclass of
    :class:`~wuttjamaican:wuttjamaican.conf.WuttaConfigProfile`, and
    similarly works off the
    :attr:`~wuttjamaican:wuttjamaican.conf.WuttaConfigProfile.key` to
    identify each configured profile.

    Upon construction each profile instance will have the following
    attributes, determined by config:

    .. attribute:: collect_keys

       List of keys identifying the types of data to collect,
       e.g. ``['os', 'python']``.

    .. attribute:: submit_url

       URL to which collected telemetry data should be submitted.

    .. attribute:: submit_uuid

       UUID identifying the record to update when submitting telemetry
       data.  This value will only make sense in the context of the
       collection service responsible for receiving telemetry
       submissions.
    """

    @property
    def section(self):
        """ """
        return f"{self.config.appname}.telemetry"

    def load(self):
        """ """
        keys = self.get_str('collect.keys', default='os,python')
        self.collect_keys = self.config.parse_list(keys)
        self.submit_url = self.get_str('submit.url')
        self.submit_uuid = self.get_str('submit.uuid')
