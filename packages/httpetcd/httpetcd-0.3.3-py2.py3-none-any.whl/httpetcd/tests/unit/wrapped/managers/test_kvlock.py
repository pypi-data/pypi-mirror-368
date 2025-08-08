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
from httpetcd.raw.entities import lease as raw_lease_e
from httpetcd.wrapped.entities import lease as lease_e
from httpetcd.wrapped.managers import kvlock as kvlock_m


class AcquireTestCase(unittest.TestCase):

    def test_lease_not_created(self):
        fake_client = mock.Mock()
        fake_client.lease.grant.side_effect = exc.EtcdException
        mgr = kvlock_m.WrappedKVLockManager(client=fake_client)

        self.assertRaises(exc.KVLockCreateError, mgr.acquire, "key", 5)

    def test_kv_not_created(self):
        fake_client = mock.Mock()
        fake_client.lease.grant.return_value = mock.Mock(id=42)
        fake_client.kv._new.side_effect = exc.KVCreateError
        mgr = kvlock_m.WrappedKVLockManager(client=fake_client)

        self.assertRaises(exc.KVLockAlreadyOccupied, mgr.acquire, "key", 5)

    def test_locked(self):
        fake_client = mock.Mock()
        fake_client.lease.grant.return_value = mock.Mock(id=42)
        mgr = kvlock_m.WrappedKVLockManager(client=fake_client)

        mgr.acquire("key", 5)

    def test_existing_label(self):
        fake_client = mock.Mock()
        fake_client.lease.grant.return_value = mock.Mock(id=42)
        mgr = kvlock_m.WrappedKVLockManager(client=fake_client)

        mgr.acquire("key", 5, "hostname")

        self.assertEqual("lease:0x2a:5:hostname",
                         fake_client.kv._new.call_args[1]["value"])

    def test_non_existing_label(self):
        fake_client = mock.Mock()
        fake_client.lease.grant.return_value = mock.Mock(id=42)
        mgr = kvlock_m.WrappedKVLockManager(client=fake_client)

        mgr.acquire("key", 5, None)

        self.assertEqual("lease:0x2a:5",
                         fake_client.kv._new.call_args[1]["value"])


class ListTestCase(unittest.TestCase):

    def test_empty(self):
        fake_client = mock.Mock()
        fake_client.kv._items.return_value = []
        mgr = kvlock_m.WrappedKVLockManager(client=fake_client)

        res = mgr.list()

        self.assertFalse(res)

    def test_with_items(self):
        fake_client = mock.Mock()
        sep = kvlock_m.WrappedKVLockManager._SEP
        fake_client.kv._items.return_value = iter([
            ("lock%s" % _, sep.join(["lease", hex(int(_)), "90"]))
            for _ in ["1", "5", "17"]
        ])
        mgr = kvlock_m.WrappedKVLockManager(client=fake_client)

        res = mgr.list()

        self.assertEqual(len(res), 3)
        self.assertEqual(res[0].key, "lock1")
        self.assertEqual(res[1].key, "lock5")
        self.assertEqual(res[2].key, "lock17")
        self.assertEqual(res[0]._lease.id, 1)
        self.assertEqual(res[1]._lease.id, 5)
        self.assertEqual(res[2]._lease.id, 17)


class FromLeaseTestCase(unittest.TestCase):

    def test_from_lease_invalid_lease(self):
        self.assertRaises(TypeError, kvlock_m.WrappedKVLockManager.from_lease,
                          lease=mock.Mock())
        self.assertRaises(TypeError, kvlock_m.WrappedKVLockManager.from_lease,
                          lease=raw_lease_e.Lease(session=mock.Mock(),
                                                  lease_id=42))

    def test_from_lease_no_keys(self):
        lease = lease_e.Lease(session=mock.Mock(), lease_id=42)
        mock_keys = mock.Mock(return_value=[])
        mock_alive = mock.Mock(return_value=True)

        with mock.patch.multiple(lease, keys=mock_keys, alive=mock_alive):
            self.assertRaises(ValueError,
                              kvlock_m.WrappedKVLockManager.from_lease,
                              lease=lease)

    def test_from_lease_many_keys(self):
        lease = lease_e.Lease(session=mock.Mock(), lease_id=42)
        mock_keys = mock.Mock(return_value=["a", "b"])
        mock_alive = mock.Mock(return_value=True)

        with mock.patch.multiple(lease, keys=mock_keys, alive=mock_alive):
            self.assertRaises(ValueError,
                              kvlock_m.WrappedKVLockManager.from_lease,
                              lease=lease)

    def test_from_lease_valid(self):
        lease = lease_e.Lease(session=mock.Mock(), lease_id=42)
        mock_keys = mock.Mock(return_value=["the_key"])
        mock_alive = mock.Mock(return_value=True)

        with mock.patch.multiple(lease, keys=mock_keys, alive=mock_alive):
            kvlock_m.WrappedKVLockManager.from_lease(lease=lease)

    def test_from_lease_expired(self):
        lease = lease_e.Lease(session=mock.Mock(), lease_id=42)
        mock_keys = mock.Mock(return_value=[])
        mock_alive = mock.Mock(return_value=False)

        with mock.patch.multiple(lease, keys=mock_keys, alive=mock_alive):
            self.assertRaises(exc.LeaseExpired,
                              kvlock_m.WrappedKVLockManager.from_lease,
                              lease=lease)
