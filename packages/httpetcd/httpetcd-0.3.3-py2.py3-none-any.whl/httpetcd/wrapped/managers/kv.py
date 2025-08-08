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

from httpetcd.base import managers


LOG = logging.getLogger(__name__)


class WrappedKVManager(managers.BaseManager):

    KV_SEPARATOR = "/"
    _ENTITY = "kv"

    @property
    def _raw(self):
        return self._client._raw

    def _to_raw_key(self, entity, key_name):
        return self.KV_SEPARATOR.join([self._conf.namespace, entity, key_name])

    @classmethod
    def _from_raw_key(cls, raw_key):
        return raw_key.split(cls.KV_SEPARATOR, 2)[-1]

    def _new(self, entity, key_name, value, lease=None):
        raw_key = self._to_raw_key(entity=entity, key_name=key_name)
        return self._raw.kv.new(raw_key=raw_key, value=value, lease=lease)

    def new(self, key_name, value, lease=None):
        return self._new(entity=self._ENTITY,
                         key_name=key_name,
                         value=value,
                         lease=lease)

    def _items(self, entity, prefix=""):
        raw_prefix = self._to_raw_key(entity=entity, key_name=prefix)
        for k, v in self._raw.kv.items(prefix=raw_prefix):
            yield self._from_raw_key(k), v

    def items(self, prefix=""):
        for k, v in self._items(entity=self._ENTITY, prefix=prefix):
            yield k, v
