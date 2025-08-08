# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
#    Copyright 2011 OpenStack Foundation
#    Copyright 2019-2021 Mail.ru Group.
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

import logging

from six import moves

from httpetcd.base import managers
from httpetcd import exceptions
from httpetcd.server import encoding

LOG = logging.getLogger(__name__)

_SORT_ORDER = ['none', 'ascend', 'descend']
_SORT_TARGET = ['key', 'version', 'create', 'mod', 'value']
bytes_types = (bytes, bytearray)


def _encode(data):
    """Encode the given data using base-64"""
    return encoding.encode64(data)


def _decode(data):
    """Decode the base-64 encoded string"""
    return encoding.decode64(data)


def _increment_last_byte(data):
    """Get the last byte in the array and increment it

    :param bytes_string:
    :return:
    """
    if not isinstance(data, bytes_types):
        if isinstance(data, str):
            data = data.encode('utf-8')
        else:
            data = str(data).encode("latin-1")
    s = bytearray(data)
    s[-1] = s[-1] + 1
    return bytes(s)


class RawKVManager(managers.BaseManager):

    def _txn(self, txn):
        self._l(LOG).debug("Attempting transaction: %r", txn)
        return self._session.request(path="kv/txn", data=txn)

    def new(self, raw_key, value, lease=None):
        lease_id = 0 if lease is None else lease.id
        self._l(LOG).debug("Creating new key <%s> (lease_id=%d)",
                           raw_key, lease_id)
        key64 = _encode(raw_key)
        value64 = _encode(value)

        compare_data = {"key": key64,
                        "result": "EQUAL",
                        "target": "CREATE",
                        "create_revision": 0}
        put_data = {"key": key64, "value": value64, "lease": lease_id}
        txn = {"compare": [compare_data],
               "success": [{"request_put": put_data}],
               "failure": []}

        result = self._txn(txn)
        # response example:
        #   {'header': {...},
        #    'responses': [{'response_put': {'header': {'revision': '2'}}}],
        #    'succeeded': True}
        if not result.get("succeeded", False):
            raise exceptions.KVCreateError(raw_key)
        self._l(LOG).info("Created new key <%s> (lease_id=%d)",
                          raw_key, lease_id)
        return True

    @staticmethod
    def _range_end_from_key(key):
        end = bytearray(key.encode("utf-8"))
        for i in moves.range((len(end) - 1), -1, -1):
            if end[i] < 0xff:
                end[i] += 1
                return bytes(end[:i+1])
        return b"\0"

    def items(self, prefix=""):
        if prefix:
            end = self._range_end_from_key(key=prefix)
        else:
            prefix = b"\0"
            end = prefix
        prefix = _encode(prefix)
        end = _encode(end)

        result = self._session.request(path="kv/range",
                                       data={"key": prefix,
                                             "range_end": end})

        for item in result.get("kvs", []):
            yield (_decode(item["key"]),
                   _decode(item["value"]))

    def replace(self, key, initial_value, new_value):
        """Atomically replace the value of a key with a new value.

        This compares the current value of a key, then replaces it with a new
        value if it is equal to a specified value. This operation takes place
        in a transaction.

        :param key: key in etcd to replace
        :param initial_value: old value to replace
        :type initial_value: bytes or string
        :param new_value: new value of the key
        :type new_value: bytes or string
        :returns: status of transaction, ``True`` if the replace was
                  successful, ``False`` otherwise
        :rtype: bool
        """
        base64_key = _encode(key)
        base64_initial_value = _encode(initial_value)
        base64_new_value = _encode(new_value)
        txn = {
            'compare': [{
                'key': base64_key,
                'result': 'EQUAL',
                'target': 'VALUE',
                'value': base64_initial_value
            }],
            'success': [{
                'request_put': {
                    'key': base64_key,
                    'value': base64_new_value,
                }
            }],
            'failure': []
        }
        result = self._txn(txn)
        if 'succeeded' in result:
            return result['succeeded']
        return False

    def put(self, key, value, lease=None):
        """Put puts the given key into the key-value store.

        A put request increments the revision of the key-value store
        and generates one event in the event history.
        :param key:
        :param value:
        :param lease:
        :return: boolean
        """

        payload = {
            "key": _encode(key),
            "value": _encode(value)
        }
        if lease:
            payload['lease'] = lease.id
        self._session.request(path="kv/put",
                              data=payload)
        return True

    def get(self, key, metadata=False, sort_order=None,
            sort_target=None, **kwargs):
        """Range gets the keys in the range from the key-value store.

        :param key:
        :param metadata:
        :param sort_order: 'ascend' or 'descend' or None
        :param sort_target: 'key' or 'version' or 'create' or 'mod' or 'value'
        :param kwargs:
        :return:
        """

        try:
            order = 0
            if sort_order:
                order = _SORT_ORDER.index(sort_order)
        except ValueError:
            raise ValueError('sort_order must be one of "ascend" or "descend"')

        try:
            target = 0
            if sort_target:
                target = _SORT_TARGET.index(sort_target)
        except ValueError:
            raise ValueError('sort_target must be one of "key", '
                             '"version", "create", "mod" or "value"')

        payload = {
            "key": _encode(key),
            "sort_order": order,
            "sort_target": target,
        }
        payload.update(kwargs)
        result = self._session.request("kv/range",
                                       data=payload)
        if 'kvs' not in result:
            return []

        if metadata:
            def value_with_metadata(item):
                item['key'] = _decode(item['key'])
                value = _decode(item.pop('value', b""))
                return value, item

            return [value_with_metadata(item) for item in result['kvs']]
        else:
            return [_decode(item['value']) for item in result['kvs']]

    def get_all(self, sort_order=None, sort_target='key'):
        """Get all keys currently stored in etcd.

        :returns: sequence of (value, metadata) tuples
        """

        return self.get(
            key=_encode(b'\0'),
            metadata=True,
            sort_order=sort_order,
            sort_target=sort_target,
            range_end=_encode(b'\0'),
        )

    def get_prefix(self, key_prefix, sort_order=None, sort_target=None):
        """Get a range of keys with a prefix.

        :param sort_order: 'ascend' or 'descend' or None
        :param key_prefix: first key in range

        :returns: sequence of (value, metadata) tuples
        """
        return self.get(key_prefix,
                        metadata=True,
                        range_end=_encode(_increment_last_byte(key_prefix)),
                        sort_order=sort_order,
                        sort_target=sort_target)

    def delete(self, key, **kwargs):
        """DeleteRange deletes the given range from the key-value store.

        A delete request increments the revision of the key-value store and
        generates a delete event in the event history for every deleted key.

        :param key:
        :param kwargs:
        :return:
        """

        payload = {
            "key": _encode(key),
        }
        payload.update(kwargs)

        result = self._session.request("kv/deleterange",
                                       data=payload)
        if 'deleted' in result:
            return True
        return False

    def delete_prefix(self, key_prefix):
        """Delete a range of keys with a prefix in etcd."""
        return self.delete(
            key_prefix, range_end=_encode(_increment_last_byte(key_prefix)))
