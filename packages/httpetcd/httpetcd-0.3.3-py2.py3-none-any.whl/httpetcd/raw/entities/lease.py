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

from httpetcd.common import exc
from httpetcd.common import obj

from httpetcd import exceptions
from httpetcd.server import codes
from httpetcd.server import encoding

LOG = logging.getLogger(__name__)


class Lease(obj.BaseObject):

    DEFAULT_TIMEOUT = 30

    def __init__(self, session, lease_id):
        super(Lease, self).__init__(obj_id=lease_id)
        self._session = session
        if isinstance(lease_id, int):
            self._id = lease_id
        else:
            self._id = int(str(lease_id), 10)

    @property
    def id(self):
        return self._id

    def refresh(self):
        self._l(LOG).debug("Refreshing...")
        resp = self._session.request(path="lease/keepalive",
                                     data={"ID": self._id})

        try:
            result = resp["result"]
        except Exception:
            raise exceptions.EtcdException("Lease refresh response: %s" % resp)

        try:
            ttl = int(result["TTL"])
            self._l(LOG).info("Refreshed.")
            return ttl
        except KeyError:
            raise exceptions.LeaseExpired()

    def _ttl(self, with_keys):
        return self._session.request(path="lease/timetolive",
                                     data={"ID": self._id,
                                           "keys": with_keys})

    def ttl(self):
        resp = self._ttl(with_keys=False)
        # response example (alive):
        #   {'header': {...},
        #   'grantedTTL': '12',
        #   'ID': '7587851347026109728',
        #   'TTL': '10'}
        # response example (zero - still alive):
        #   {'header': {...},
        #    'ID': '7587851347026109718',
        #    'grantedTTL': '2'}
        # response example (expired):
        #   {'header': {...},
        #    'ID': '7587851347026109712',
        #    'TTL': u'-1'}
        ttl = int(resp.get("TTL", 0))
        if ttl < -1:
            raise exceptions.EtcdException("Unexpected lease ttl: %s" % ttl)
        return ttl

    def alive(self):
        return self.ttl() != -1

    def keys(self):
        resp = self._ttl(with_keys=True)
        return [encoding.decode64(key) for key in resp.get("keys", [])]

    def revoke(self):
        self._l(LOG).debug("Revoking...")
        lr_codes = codes.LeaseRevokeCodes
        try:
            self._session.request(path="lease/revoke",
                                  data={"ID": self._id},
                                  codes=lr_codes)
            self._l(LOG).info("Revoked.")
            return True
        except exceptions.UnsuccessfulResponse as e:
            with exc.raise_default():
                if e.code is lr_codes.NOT_FOUND:
                    raise exceptions.LeaseExpired()
