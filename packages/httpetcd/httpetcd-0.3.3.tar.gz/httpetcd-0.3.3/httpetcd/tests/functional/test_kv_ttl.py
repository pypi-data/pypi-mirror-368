# -*- coding: latin-1 -*-

# Copyright 2023 VK Cloud.
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

import os
import random
import string
import time
import unittest
import uuid

from httpetcd.clients import get_wrapped_client
from httpetcd.exceptions import KVCreateError
from httpetcd.raw.managers import kv as kv_m
from httpetcd.raw.managers import lease as lease_m

_ENDPOINT_DEFAULT = "http://127.0.0.1:2379"
ENDPOINTS = [os.getenv('ETCD_ENDPOINT', _ENDPOINT_DEFAULT)]


class KvTtlTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        client = get_wrapped_client(ENDPOINTS, 'path', 5)
        cls.client = client
        cls.kv_mgr = kv_m.RawKVManager(client=client)
        cls.lease_mgr = lease_m.RawLeaseManager(client=client)

    def test_kv_ttl(self):
        random_str = ''.join(
            random.choice(string.ascii_uppercase) for _ in range(3))
        key = "key_" + random_str
        value = "value_" + random_str

        self.kv_mgr.put(key, value)
        values = self.kv_mgr.get(key)

        self.assertEqual(len(values), 1)
        self.assertEqual(values[0], value)

        items = list(self.kv_mgr.items())

        assert any(item[0] == key for item in items)

        delete_res = self.kv_mgr.delete(key)

        self.assertTrue(delete_res)

        items = list(self.kv_mgr.items())

        assert not any(item[0] == key for item in items)

        lease = self.lease_mgr.grant(1)
        self.kv_mgr.new(key, value, lease)
        values = self.kv_mgr.get(key)

        self.assertEqual(len(values), 1)
        self.assertEqual(values[0], value)

        time.sleep(3)
        values = self.kv_mgr.get(key)

        self.assertEqual(len(values), 0)

    def test_kv_manager_with_keys_and_values(self):
        umlaut_byte = u'ö'.encode('utf-8')

        self.assertTrue(self.kv_mgr.put('foo0', 'bar0'))
        self.assertTrue(self.kv_mgr.put('foo1', 2001))
        self.assertTrue(self.kv_mgr.put('foo2', b'bar2'))
        self.assertTrue(self.kv_mgr.put('foo3', umlaut_byte))

        self.assertEqual([u'bar0'], self.kv_mgr.get('foo0'))
        self.assertEqual([u'2001'], self.kv_mgr.get('foo1'))
        self.assertEqual([u'bar2'], self.kv_mgr.get('foo2'))

        umlaut_unicode = self.kv_mgr.get('foo3')
        self.assertEqual([u'ö'], umlaut_unicode)
        self.assertNotEqual([umlaut_byte], umlaut_unicode)

        self.assertEqual(True, self.kv_mgr.delete('foo0'))
        self.assertEqual([], self.kv_mgr.get('foo0'))

        self.assertEqual(False, self.kv_mgr.delete('foo0'))
        self.assertTrue(len(self.kv_mgr.get_all()) > 0)

    def test_get_and_delete_prefix(self):
        for i in range(20):
            self.kv_mgr.put('/doot1/range{}'.format(i), 'i am a range')

        values = list(self.kv_mgr.get_prefix('/doot1/range'))
        assert len(values) == 20
        for value, metadata in values:
            self.assertEqual(u'i am a range', value)
            self.assertTrue(metadata['key'].startswith(u'/doot1/range'))

        self.assertEqual(True, self.kv_mgr.delete_prefix('/doot1/range'))
        values = list(self.kv_mgr.get_prefix('/doot1/range'))
        assert len(values) == 0

    def test_get_prefix_sort_order(self):
        def remove_prefix(string, prefix):
            return string[len(prefix):]

        initial_keys = u'abcde'
        initial_values = u'qwert'

        for k, v in zip(initial_keys, initial_values):
            self.kv_mgr.put('/doot2/{}'.format(k), v)

        keys = u''
        for value, meta in self.kv_mgr.get_prefix(
                '/doot2', sort_order='ascend'):
            keys += remove_prefix(meta['key'], '/doot2/')

        assert keys == initial_keys

        reverse_keys = u''
        for value, meta in self.kv_mgr.get_prefix(
                '/doot2', sort_order='descend'):
            reverse_keys += remove_prefix(meta['key'], '/doot2/')

        assert reverse_keys == u''.join(reversed(initial_keys))

    def test_get_prefix_sort_order_explicit_sort_target_key(self):
        def remove_prefix(string, prefix):
            return string[len(prefix):]

        initial_keys_ordered = u'abcde'
        initial_keys = u'aebdc'
        initial_values = u'qwert'

        for k, v in zip(initial_keys, initial_values):
            self.kv_mgr.put('/doot2/{}'.format(k), v)

        keys = u''
        for value, meta in self.kv_mgr.get_prefix(
                '/doot2', sort_order='ascend', sort_target='key'):
            keys += remove_prefix(meta['key'], '/doot2/')

        assert keys == initial_keys_ordered

        reverse_keys = u''
        for value, meta in self.kv_mgr.get_prefix(
                '/doot2', sort_order='descend', sort_target='key'):
            reverse_keys += remove_prefix(meta['key'], '/doot2/')

        assert reverse_keys == u''.join(reversed(initial_keys_ordered))

    def test_get_prefix_sort_order_explicit_sort_target_rev(self):
        def remove_prefix(string, prefix):
            return string[len(prefix):]

        initial_keys = u'aebdc'
        initial_values = u'qwert'

        for k, v in zip(initial_keys, initial_values):
            self.kv_mgr.put('/expsortmod/{}'.format(k), v)

        keys = u''
        for value, meta in self.kv_mgr.get_prefix(
                '/expsortmod', sort_order='ascend', sort_target='mod'):
            keys += remove_prefix(meta['key'], '/expsortmod/')

        assert keys == initial_keys

        reverse_keys = u''
        for value, meta in self.kv_mgr.get_prefix(
                '/expsortmod', sort_order='descend', sort_target='mod'):
            reverse_keys += remove_prefix(meta['key'], '/expsortmod/')

        assert reverse_keys == u''.join(reversed(initial_keys))

    def test_replace_success(self):
        key = '/doot/thing' + str(uuid.uuid4())
        self.kv_mgr.put(key, 'toot')
        status = self.kv_mgr.replace(key, 'toot', 'doot')
        v = self.kv_mgr.get(key)
        self.assertEqual([u'doot'], v)
        self.assertTrue(status)

    def test_replace_fail(self):
        key = '/doot/thing' + str(uuid.uuid4())
        self.kv_mgr.put(key, 'boot')
        status = self.kv_mgr.replace(key, 'toot', 'doot')
        v = self.kv_mgr.get(key)
        self.assertEqual([u'boot'], v)
        self.assertFalse(status)

    def test_lease(self):
        lease = self.lease_mgr.grant(ttl=60)
        self.assertIsNotNone(lease)

        ttl = lease.ttl()
        self.assertTrue(0 <= ttl <= 60)

        keys = lease.keys()
        self.assertEqual([], keys)

        ttl = lease.refresh()
        self.assertTrue(0 <= ttl <= 60)

        self.assertTrue(lease.revoke())

    def test_lease_with_keys(self):
        lease = self.lease_mgr.lease(ttl=60)
        self.assertIsNotNone(lease)

        self.assertTrue(self.kv_mgr.put('foo12', 'bar12', lease))
        self.assertTrue(self.kv_mgr.put('foo13', 'bar13', lease))

        keys = lease.keys()
        self.assertEqual(2, len(keys))
        self.assertIn(u'foo12', keys)
        self.assertIn(u'foo13', keys)

        self.assertEqual([u'bar12'], self.kv_mgr.get('foo12'))
        self.assertEqual([u'bar13'], self.kv_mgr.get('foo13'))

        self.assertTrue(lease.revoke())

    def test_create_success(self):
        key = '/foo/unique' + str(uuid.uuid4())
        # Verify that key is empty
        self.assertEqual([], self.kv_mgr.get(key))

        status = self.kv_mgr.new(key, 'bar')
        # Verify that key is 'bar'
        self.assertEqual([u'bar'], self.kv_mgr.get(key))
        self.assertTrue(status)

    def test_create_fail(self):
        key = '/foo/' + str(uuid.uuid4())
        # Assign value to the key
        self.kv_mgr.put(key, 'bar')
        self.assertEqual([u'bar'], self.kv_mgr.get(key))

        with self.assertRaises(KVCreateError):
            self.kv_mgr.new(key, 'goo')
        # Verify that key is still 'bar'
        self.assertEqual([u'bar'], self.kv_mgr.get(key))

    def test_create_with_lease_success(self):
        key = '/foo/unique' + str(uuid.uuid4())
        # Verify that key is empty
        self.assertEqual([], self.kv_mgr.get(key))
        lease = self.lease_mgr.lease()

        status = self.kv_mgr.new(key, 'bar', lease=lease)
        # Verify that key is 'bar'
        self.assertEqual([u'bar'], self.kv_mgr.get(key))
        self.assertTrue(status)
        keys = lease.keys(convert=False)
        self.assertEqual(1, len(keys))
        self.assertIn(key, keys)

    def _post_key(self, key_name, provide_value=True):
        payload = {"key": kv_m._encode(key_name)}
        if provide_value:
            payload["value"] = kv_m._encode(key_name)
        self.kv_mgr._session.request(path="kv/put", data=payload)

    def test_client_keys_with_metadata_and_value(self):
        test_key_value = u"some_key"
        self._post_key(test_key_value)
        result = self.kv_mgr.get(test_key_value, metadata=True)
        self.assertTrue(
            len(result) > 0,
            str(test_key_value) + " key is not found in etcd"
        )
        value, metadata = result[0]
        self.assertEqual(
            value,
            test_key_value,
            "unable to get value for " + str(test_key_value)
        )

    def test_client_keys_with_metadata_and_no_value(self):
        value_is_not_set_default = u""
        test_key = u"some_key"
        self._post_key(test_key, provide_value=False)
        result = self.kv_mgr.get(test_key, metadata=True)
        self.assertTrue(
            len(result) > 0,
            str(test_key) + " key is not found in etcd"
        )
        value, metadata = result[0]
        self.assertEqual(
            value,
            value_is_not_set_default,
            "unable to get value for " + str(test_key)
        )
