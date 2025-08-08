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

from httpetcd.wrapped.entities import lease as lease_e


class KeysTestCase(unittest.TestCase):

    @mock.patch("httpetcd.raw.entities.lease.Lease.keys")
    def test_with_keys(self, fake_keys):
        fake_keys.return_value = iter(["ns/kvlock/asd.xyz",
                                       "ns/kvlock/blah"])
        lease = lease_e.Lease(session=mock.Mock(), lease_id=42)

        self.assertEqual(["asd.xyz", "blah"], lease.keys())
