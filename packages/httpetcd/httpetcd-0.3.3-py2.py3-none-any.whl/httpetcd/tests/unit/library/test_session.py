# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
#    Copyright 2022 VK Cloud Solutions
#
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import unittest

import mock
from requests import exceptions as req_exc

from httpetcd import exceptions as exc
from httpetcd.library import session


class EndpointShuffleTestCase(unittest.TestCase):

    def test_shuffle(self):
        fake_error = ValueError(42)
        eps = ["http://host1:1", "https://host2/2", "http://host3:3"]
        ep_count = len(eps)
        s = session.Session(endpoints=eps, api_path="/fake_path", timeout=10)

        ep_loop_1 = []
        ep_loop_2 = []

        for i in range(ep_count):
            ep_loop_1.append(s._endpoint)
            s._shift_endpoint(fake_error)

        for i in range(ep_count):
            ep_loop_2.append(s._endpoint)
            s._shift_endpoint(fake_error)

        self.assertEqual(ep_loop_1, ep_loop_2)
        self.assertNotEqual(ep_loop_1[0], ep_loop_1[1])
        self.assertNotEqual(ep_loop_1[1], ep_loop_1[2])
        self.assertNotEqual(ep_loop_1[2], ep_loop_1[0])
        self.assertEqual(set(ep_loop_1), set(s._endpoints))


class ShiftOnErrorTestCase(unittest.TestCase):

    def test_error_type(self):
        eps = ["http://host1:1", "https://host2/2", "http://host3:3"]
        s = session.Session(endpoints=eps, api_path="/fake_path", timeout=10)

        self.assertRaises(exc.ConnectionError, s.request, "asd", {})

    def test_shift(self):
        eps = ["http://host1:1", "https://host2/2", "http://host3:3"]
        s = session.Session(endpoints=eps, api_path="/fake_path", timeout=10)

        ep_before = s._endpoint
        try:
            s.request("asd", {})
        except Exception:
            pass
        ep_after = s._endpoint

        self.assertNotEqual(ep_before, ep_after)

    @mock.patch("requests.session")
    def test_no_shift(self, mock_session):
        eps = ["http://host1:1", "https://host2/2", "http://host3:3"]
        s = session.Session(endpoints=eps, api_path="/fake_path", timeout=10)

        ep_before = s._endpoint
        s.request("asd", {})
        ep_after = s._endpoint

        self.assertEqual(ep_before, ep_after)


class ReadTimeoutTestCase(unittest.TestCase):

    @mock.patch("requests.session")
    def test_session_close(self, mock_session):
        mock_session_cls = mock.MagicMock(
            post=mock.MagicMock(side_effect=req_exc.ReadTimeout()))
        mock_session.return_value = mock_session_cls

        eps = ["http://host1:1"]
        s = session.Session(endpoints=eps, api_path="/fake_path", timeout=10)

        try:
            s.request("qwe", {})
        except exc.EtcdException:
            assert mock_session_cls.close.call_count == 1
        else:
            self.fail("The request is expected to fail")
