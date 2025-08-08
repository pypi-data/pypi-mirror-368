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
from httpetcd import exceptions
from httpetcd.wrapped.entities import lease as lease_e


LOG = logging.getLogger(__name__)


class RawLeaseManager(managers.BaseManager):

    _LEASE_TYPE = lease_e.Lease

    def get(self, lease_id):
        return self._LEASE_TYPE(session=self._session, lease_id=lease_id)

    def grant(self, ttl=_LEASE_TYPE.DEFAULT_TIMEOUT):
        self._l(LOG).debug("Granting lease with TTL=%d", ttl)
        # TTL: the advisory time-to-live, in seconds.
        # ID:  the requested ID for the lease
        #      (if ID is set to 0, etcd will choose an ID)
        resp = self._session.request(path="lease/grant",
                                     data={"TTL": ttl, "ID": 0})
        try:
            lease_id = int(resp['ID'])
        except Exception as e:
            raise exceptions.EtcdException(e)
        lease = self._LEASE_TYPE(session=self._session, lease_id=lease_id)
        # response example:
        #   {'header': {...},
        #    'ID': u'7587851347026109712',
        #    'TTL': u'30'}
        self._l(LOG).info("Lease granted: %r", lease)
        return lease

    lease = grant
