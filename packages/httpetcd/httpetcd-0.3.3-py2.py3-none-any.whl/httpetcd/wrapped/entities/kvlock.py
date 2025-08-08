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

from httpetcd.common import obj
import six

from httpetcd import exceptions

LOG = logging.getLogger(__name__)


class KVLock(obj.BaseObject):

    def __init__(self, lease, key):
        if not key:
            raise ValueError("key must be non-empty string")
        super(KVLock, self).__init__(obj_id=key)
        self._lease = lease
        self._key = key

    @property
    def id(self):
        return self._lease.id

    @property
    def key(self):
        return self._key

    def refresh(self):
        self._l(LOG).debug("Refreshing...")
        try:
            self._lease.refresh()
        except exceptions.LeaseExpired:
            exc_info = sys.exc_info()
            six.reraise(exceptions.KVLockExpired,
                        exceptions.KVLockExpired(self._key),
                        exc_info[2])
        self._l(LOG).info("Refreshed.")

    def ttl(self):
        return self._lease.ttl()

    def alive(self):
        return self._lease.alive()

    def release(self):
        self._l(LOG).debug("Releasing...")
        try:
            self._lease.revoke()
        except exceptions.LeaseExpired:
            exc_info = sys.exc_info()
            six.reraise(exceptions.KVLockExpired,
                        exceptions.KVLockExpired(self._key),
                        exc_info[2])
        self._l(LOG).info("Released.")
