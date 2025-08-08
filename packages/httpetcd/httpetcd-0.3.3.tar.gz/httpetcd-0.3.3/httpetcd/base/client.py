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

from httpetcd.common import obj

from httpetcd.library import session

LOG = logging.getLogger(__name__)


class HTTPEtcdClient(obj.BaseObject):

    def __init__(self, conf):
        super(HTTPEtcdClient, self).__init__()
        self._conf = conf
        self._s = session.get_session(endpoints=conf.endpoints,
                                      timeout=conf.timeout)

    @property
    def conf(self):
        return self._conf

    @property
    def _session(self):
        return self._s
