# -*- coding: utf-8; -*-

from unittest.mock import patch

from wuttjamaican.testing import ConfigTestCase

from wuttatell import telemetry as mod


class TestTelemetryHandler(ConfigTestCase):

    def setUp(self):
        super().setUp()
        self.handler = self.make_handler()

    def make_handler(self):
        return mod.TelemetryHandler(self.config)

    def test_get_profile(self):

        # default
        default = self.handler.get_profile('default')
        self.assertIsInstance(default, mod.TelemetryProfile)
        self.assertEqual(default.key, 'default')

        # same profile is returned
        profile = self.handler.get_profile(default)
        self.assertIs(profile, default)

    def test_collect_data_os(self):
        profile = self.handler.get_profile('default')

        # typical / working scenario
        data = self.handler.collect_data_os(profile)
        self.assertIsInstance(data, dict)
        self.assertIn('release_id', data)
        self.assertIn('release_version', data)
        self.assertIn('release_full', data)
        self.assertIn('timezone', data)
        self.assertNotIn('errors', data)

        # unreadable release path
        data = self.handler.collect_data_os(profile, release_path='/a/path/which/does/not/exist')
        self.assertIsInstance(data, dict)
        self.assertNotIn('release_id', data)
        self.assertNotIn('release_version', data)
        self.assertNotIn('release_full', data)
        self.assertIn('timezone', data)
        self.assertIn('errors', data)
        self.assertEqual(data['errors'], [
            "Failed to read /a/path/which/does/not/exist"
        ])

        # unparsable release path
        path = self.write_file('release', "bad-content")
        data = self.handler.collect_data_os(profile, release_path=path)
        self.assertIsInstance(data, dict)
        self.assertNotIn('release_id', data)
        self.assertNotIn('release_version', data)
        self.assertNotIn('release_full', data)
        self.assertIn('timezone', data)
        self.assertIn('errors', data)
        self.assertEqual(data['errors'], [
            f"Failed to parse {path}"
        ])

        # unreadable timezone path
        data = self.handler.collect_data_os(profile, timezone_path='/a/path/which/does/not/exist')
        self.assertIsInstance(data, dict)
        self.assertIn('release_id', data)
        self.assertIn('release_version', data)
        self.assertIn('release_full', data)
        self.assertNotIn('timezone', data)
        self.assertIn('errors', data)
        self.assertEqual(data['errors'], [
            "Failed to read /a/path/which/does/not/exist"
        ])

    def test_collect_data_python(self):
        profile = self.handler.get_profile('default')

        # typical / working (system-wide) scenario
        data = self.handler.collect_data_python(profile)
        self.assertIsInstance(data, dict)
        self.assertNotIn('envroot', data)
        self.assertIn('executable', data)
        self.assertIn('release_full', data)
        self.assertIn('release_version', data)
        self.assertNotIn('errors', data)

        # missing executable
        with patch.dict(self.config.defaults, {'wutta.telemetry.default.collect.python.executable': '/bad/path'}):
            data = self.handler.collect_data_python(profile)
            self.assertIsInstance(data, dict)
            self.assertNotIn('envroot', data)
            self.assertIn('executable', data)
            self.assertNotIn('release_full', data)
            self.assertNotIn('release_version', data)
            self.assertIn('errors', data)
            self.assertEqual(data['errors'][0], "Failed to execute `python --version`")

        # unparsable executable output
        with patch.object(mod, 'subprocess') as subprocess:
            subprocess.check_output.return_value = 'bad output'.encode('utf_8')

            data = self.handler.collect_data_python(profile)
            self.assertIsInstance(data, dict)
            self.assertNotIn('envroot', data)
            self.assertIn('executable', data)
            self.assertIn('release_full', data)
            self.assertNotIn('release_version', data)
            self.assertIn('errors', data)
            self.assertEqual(data['errors'], [
                "Failed to parse Python version",
            ])

        # typical / working (virtual environment) scenario
        self.config.setdefault('wutta.telemetry.default.collect.python.envroot', '/srv/envs/poser')
        data = self.handler.collect_data_python(profile)
        self.assertIsInstance(data, dict)
        self.assertIn('executable', data)
        self.assertEqual(data['executable'], '/srv/envs/poser/bin/python')
        self.assertNotIn('release_full', data)
        self.assertNotIn('release_version', data)
        self.assertIn('errors', data)
        self.assertEqual(data['errors'][0], "Failed to execute `python --version`")

    def test_normalize_errors(self):
        data = {
            'os': {
                'timezone': 'America/Chicago',
                'errors': [
                    "Failed to read /etc/os-release",
                ],
            },
            'python': {
                'executable': '/usr/bin/python3',
                'errors': [
                    "Failed to run `python --version`",
                ],
            },
        }

        self.handler.normalize_errors(data)
        self.assertIn('os', data)
        self.assertIn('python', data)
        self.assertIn('errors', data)
        self.assertEqual(data['errors'], [
            "Failed to read /etc/os-release",
            "Failed to run `python --version`",
        ])

    def test_collect_all_data(self):

        # typical / working scenario
        data = self.handler.collect_all_data()
        self.assertIsInstance(data, dict)
        self.assertIn('os', data)
        self.assertIn('python', data)
        self.assertNotIn('errors', data)

    def test_submit_all_data(self):

        # not (yet?) implemented
        self.assertRaises(NotImplementedError, self.handler.submit_all_data)


class TestTelemetryProfile(ConfigTestCase):

    def make_profile(self, key='default'):
        return mod.TelemetryProfile(self.config, key)

    def test_section(self):

        # default
        profile = self.make_profile()
        self.assertEqual(profile.section, 'wutta.telemetry')

        # custom appname
        with patch.object(self.config, 'appname', new='wuttatest'):
            profile = self.make_profile()
            self.assertEqual(profile.section, 'wuttatest.telemetry')

    def test_load(self):

        # defaults
        profile = self.make_profile()
        self.assertEqual(profile.collect_keys, ['os', 'python'])
        self.assertIsNone(profile.submit_url)
        self.assertIsNone(profile.submit_uuid)

        # configured
        self.config.setdefault('wutta.telemetry.default.collect.keys', 'os,network,python')
        self.config.setdefault('wutta.telemetry.default.submit.url', '/nodes/telemetry')
        self.config.setdefault('wutta.telemetry.default.submit.uuid', '06897669-272b-7c74-8000-4d311924d24f')
        profile = self.make_profile()
        self.assertEqual(profile.collect_keys, ['os', 'network', 'python'])
        self.assertEqual(profile.submit_url, '/nodes/telemetry')
        self.assertEqual(profile.submit_uuid, '06897669-272b-7c74-8000-4d311924d24f')
