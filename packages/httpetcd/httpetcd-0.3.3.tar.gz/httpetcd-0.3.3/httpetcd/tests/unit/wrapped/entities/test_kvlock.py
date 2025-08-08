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
from httpetcd.wrapped.entities import kvlock as kvlock_e


class InitTestCase(unittest.TestCase):

    def test_invalid(self):
        self.assertRaises(ValueError, kvlock_e.KVLock,
                          lease=mock.Mock(), key="")

    def test_valid(self):
        kvlock_e.KVLock(lease=mock.Mock(), key="key")


class ReleaseTestCase(unittest.TestCase):

    def test_released(self):
        lock = kvlock_e.KVLock(lease=mock.Mock(), key="key")

        lock.release()

    def test_unexpected_exception(self):
        fake_lease = mock.Mock(name="fake_lease")
        fake_lease.revoke.side_effect = ZeroDivisionError
        lock = kvlock_e.KVLock(lease=fake_lease, key="key")

        self.assertRaises(ZeroDivisionError, lock.release)

    def test_expired(self):
        fake_lease = mock.Mock(name="fake_lease")
        fake_lease.revoke.side_effect = exc.LeaseExpired
        lock = kvlock_e.KVLock(lease=fake_lease, key="key")

        self.assertRaises(exc.KVLockExpired, lock.release)
