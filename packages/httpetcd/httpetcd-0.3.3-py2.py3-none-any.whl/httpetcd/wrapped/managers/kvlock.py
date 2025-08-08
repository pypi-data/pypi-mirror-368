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
import sys

from httpetcd.common import exc as exc_utils
import six

from httpetcd.base import managers
from httpetcd import exceptions
from httpetcd.wrapped.entities import kvlock
from httpetcd.wrapped.entities import lease as lease_e

LOG = logging.getLogger(__name__)


class WrappedKVLockManager(managers.BaseManager):

    _ENTITY = "kvlock"
    _SEP = ":"

    @staticmethod
    def from_lease(lease):
        if not isinstance(lease, lease_e.Lease):
            raise TypeError("Expected %r descendent but got %r"
                            % (lease_e.Lease, type(lease)))
        keys = lease.keys()
        if not lease.alive():
            raise exceptions.LeaseExpired()
        if len(keys) != 1:
            raise ValueError("Lease %r does not provide single key: %s"
                             % (lease, keys))
        return kvlock.KVLock(lease=lease, key=keys[0])

    def acquire(self, key_name, ttl, label=None):
        self._l(LOG).debug("Acquiring lock <%r> with ttl=%r and label=<%r>",
                           key_name, ttl, label)
        try:
            lease = self._client.lease.grant(ttl=ttl)
        except exceptions.EtcdException:
            exc_info = sys.exc_info()
            six.reraise(exceptions.KVLockCreateError,
                        exceptions.KVLockCreateError(),
                        exc_info[2])

        try:
            if label:
                value = self._SEP.join(("lease", hex(lease.id), str(ttl),
                                        label))
            else:
                value = self._SEP.join(("lease", hex(lease.id), str(ttl)))
            self._client.kv._new(entity=self._ENTITY,
                                 key_name=key_name,
                                 value=value,
                                 lease=lease)
            lock = kvlock.KVLock(lease=lease, key=key_name)
            self._l(LOG).info("Lock acquired: %r, ttl=%r, label='%r'",
                              lock, ttl, label)
            return lock
        except exceptions.KVCreateError:
            exc_info = sys.exc_info()

        with exc_utils.suppress_any():
            lease.revoke()

        six.reraise(exceptions.KVLockAlreadyOccupied,
                    exceptions.KVLockAlreadyOccupied(key_name),
                    exc_info[2])

    def list(self, prefix=""):
        locks = []
        for k, v in self._client.kv._items(entity=self._ENTITY, prefix=prefix):
            _, id_str, granted_ttl = v.split(self._SEP, 2)
            lease = lease_e.Lease(session=self._session,
                                  lease_id=int(id_str, 0))
            locks.append(kvlock.KVLock(lease=lease, key=k))
        return locks
