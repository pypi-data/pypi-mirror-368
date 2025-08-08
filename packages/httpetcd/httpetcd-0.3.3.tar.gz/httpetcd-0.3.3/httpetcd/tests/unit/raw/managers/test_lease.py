# Copyright 2020-2021 Mail.ru Group
#
# All Rights Reserved.
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

from httpetcd import exceptions as exc
from httpetcd.raw.managers import lease as lease_m


class GrantTestCase(unittest.TestCase):

    def test_bad_response_value(self):
        fake_client = mock.Mock()
        fake_client._session.request.return_value = {"ID": "asd"}
        mgr = lease_m.RawLeaseManager(client=fake_client)

        self.assertRaises(exc.EtcdException, mgr.grant, 5)

    def test_bad_response_missing(self):
        fake_client = mock.Mock()
        fake_client._session.request.return_value = {}
        mgr = lease_m.RawLeaseManager(client=fake_client)

        self.assertRaises(exc.EtcdException, mgr.grant)
