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
from httpetcd.raw.managers import kv as kv_m
from httpetcd.server import encoding


class NewTestCase(unittest.TestCase):

    @mock.patch('httpetcd.raw.managers.kv.RawKVManager._txn')
    def test_unsuccessfull_response(self, fake_txn):
        fake_txn.return_value = {}
        mgr = kv_m.RawKVManager(client=mock.Mock())

        self.assertRaises(exc.KVCreateError, mgr.new, "k", "v")

    @mock.patch('httpetcd.raw.managers.kv.RawKVManager._txn')
    def test_unsuccessfull_response_missing(self, fake_txn):
        fake_txn.return_value = {"succeeded": False}
        mgr = kv_m.RawKVManager(client=mock.Mock())

        self.assertRaises(exc.KVCreateError, mgr.new, "k", "v")


class ItemsTestCase(unittest.TestCase):

    def test_empty_prefix(self):
        fake_client = mock.Mock()
        fake_request = mock.Mock(return_value={})
        fake_client._session.request = fake_request
        mgr = kv_m.RawKVManager(client=fake_client)

        list(mgr.items())

        fake_request.assert_called_once_with(path=mock.ANY,
                                             data={"key": "AA==",
                                                   "range_end": "AA=="})

    def test_with_prefix(self):
        fake_client = mock.Mock()
        fake_request = mock.Mock(return_value={})
        fake_client._session.request = fake_request
        mgr = kv_m.RawKVManager(client=fake_client)
        prefix = "asd"
        end = "ase"

        list(mgr.items(prefix=prefix))

        fake_request.assert_called_once_with(
            path=mock.ANY,
            data={"key": encoding.encode64(prefix),
                  "range_end": encoding.encode64(end)},
        )
