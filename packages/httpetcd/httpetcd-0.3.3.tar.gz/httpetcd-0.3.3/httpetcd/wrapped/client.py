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

from httpetcd.base import client
from httpetcd.raw import client as raw_client_m
from httpetcd.wrapped.managers import kv as kv_m
from httpetcd.wrapped.managers import kvlock as kvlock_m
from httpetcd.wrapped.managers import lease as lease_m


LOG = logging.getLogger(__name__)


class WrappedHTTPEtcdClient(client.HTTPEtcdClient):

    def __init__(self, conf):
        super(WrappedHTTPEtcdClient, self).__init__(conf=conf)
        self._raw = raw_client_m.RawHTTPEtcdClient(conf=conf)
        self.kv = kv_m.WrappedKVManager(client=self)
        self.kvlock = kvlock_m.WrappedKVLockManager(client=self)
        self.lease = lease_m.WrappedLeaseManager(client=self)
