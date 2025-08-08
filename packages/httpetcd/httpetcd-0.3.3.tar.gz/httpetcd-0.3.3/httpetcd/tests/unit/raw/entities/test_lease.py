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
from httpetcd.raw.entities import lease as lease_e
from httpetcd.server import codes as lr_codes


class LeaseIDTestCase(unittest.TestCase):

    def test_invalid(self):
        self.assertRaises(ValueError, lease_e.Lease,
                          session=mock.Mock(), lease_id="id")

    def test_str(self):
        lease_e.Lease(session=mock.Mock(), lease_id="42")

    def test_int(self):
        lease_e.Lease(session=mock.Mock(), lease_id=42)


class RefreshTestCase(unittest.TestCase):

    def test_no_result(self):
        fake_session = mock.Mock(name="fake_session")
        fake_session.request.return_value = {}
        lease = lease_e.Lease(session=fake_session, lease_id=42)

        self.assertRaises(exc.EtcdException, lease.refresh)

    def test_invalid_result(self):
        fake_session = mock.Mock(name="fake_session")
        fake_session.request.return_value = 1
        lease = lease_e.Lease(session=fake_session, lease_id=42)

        self.assertRaises(exc.EtcdException, lease.refresh)

    def test_expired(self):
        fake_session = mock.Mock(name="fake_session")
        fake_session.request.return_value = {"result": {}}
        lease = lease_e.Lease(session=fake_session, lease_id=42)

        self.assertRaises(exc.LeaseExpired, lease.refresh)

    def test_success(self):
        fake_session = mock.Mock(name="fake_session")
        fake_session.request.return_value = {"result": {"TTL": 100}}
        lease = lease_e.Lease(session=fake_session, lease_id=42)

        lease.refresh()


class TTLTestCase(unittest.TestCase):

    @mock.patch("httpetcd.raw.entities.lease.Lease._ttl")
    def test_alive(self, fake_ttl):
        fake_ttl.return_value = {"TTL": "10"}
        lease = lease_e.Lease(session=mock.Mock(), lease_id=42)

        self.assertEqual(10, lease.ttl())

    @mock.patch("httpetcd.raw.entities.lease.Lease._ttl")
    def test_zero_ttl(self, fake_ttl):
        fake_ttl.return_value = {}
        lease = lease_e.Lease(session=mock.Mock(), lease_id=42)

        self.assertEqual(0, lease.ttl())

    @mock.patch("httpetcd.raw.entities.lease.Lease._ttl")
    def test_expired(self, fake_ttl):
        fake_ttl.return_value = {"TTL": -1}
        lease = lease_e.Lease(session=mock.Mock(), lease_id=42)

        self.assertEqual(-1, lease.ttl())

    @mock.patch("httpetcd.raw.entities.lease.Lease._ttl")
    def test_invalid(self, fake_ttl):
        fake_ttl.return_value = {"TTL": -5}
        lease = lease_e.Lease(session=mock.Mock(), lease_id=42)

        self.assertRaises(exc.EtcdException, lease.ttl)


class AliveTestCase(unittest.TestCase):

    @mock.patch("httpetcd.raw.entities.lease.Lease.ttl")
    def test_alive(self, fake_ttl):
        fake_ttl.return_value = 10
        lease = lease_e.Lease(session=mock.Mock(), lease_id=42)

        self.assertTrue(lease.alive())

    @mock.patch("httpetcd.raw.entities.lease.Lease.ttl")
    def test_zero_ttl(self, fake_ttl):
        fake_ttl.return_value = 0
        lease = lease_e.Lease(session=mock.Mock(), lease_id=42)

        self.assertTrue(lease.alive())

    @mock.patch("httpetcd.raw.entities.lease.Lease.ttl")
    def test_not_alive(self, fake_ttl):
        fake_ttl.return_value = -1
        lease = lease_e.Lease(session=mock.Mock(), lease_id=42)

        self.assertFalse(lease.alive())


class KeysTestCase(unittest.TestCase):

    @mock.patch("httpetcd.raw.entities.lease.Lease._ttl")
    def test_no_keys(self, fake_ttl):
        fake_ttl.return_value = {}
        lease = lease_e.Lease(session=mock.Mock(), lease_id=42)

        self.assertFalse(lease.keys())

    @mock.patch("httpetcd.raw.entities.lease.Lease._ttl")
    def test_with_keys(self, fake_ttl):
        fake_ttl.return_value = {"keys": ["YXNkLnh5eg==", "YmxhaA=="]}
        lease = lease_e.Lease(session=mock.Mock(), lease_id=42)

        self.assertEqual(["asd.xyz", "blah"], lease.keys())


class RevokeTestCase(unittest.TestCase):

    def test_revoked(self):
        lease = lease_e.Lease(session=mock.Mock(), lease_id=42)

        lease.revoke()

    def test_unexpected_exception(self):
        fake_session = mock.Mock(name="fake_session")
        fake_session.request.side_effect = ZeroDivisionError
        lease = lease_e.Lease(session=fake_session, lease_id=42)

        self.assertRaises(ZeroDivisionError, lease.revoke)

    def test_unexpected_response(self):
        fake_session = mock.Mock(name="fake_session")
        fake_session.request.side_effect = exc.UnsuccessfulResponse("code",
                                                                    "resp")
        lease = lease_e.Lease(session=fake_session, lease_id=42)

        self.assertRaises(exc.UnsuccessfulResponse, lease.revoke)

    def test_expired(self):
        fake_session = mock.Mock(name="fake_session")
        fake_session.request.side_effect = exc.UnsuccessfulResponse(
            lr_codes.LeaseRevokeCodes.NOT_FOUND, "resp")
        lease = lease_e.Lease(session=fake_session, lease_id=42)

        self.assertRaises(exc.LeaseExpired, lease.revoke)
