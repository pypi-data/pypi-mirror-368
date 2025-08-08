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

import re

from httpetcd.common import obj

from httpetcd.wrapped import client as wrapped_client


class Config(obj.BaseObject):

    _NS_REGEXP_STR = '^[a-z0-9._-]+$'
    _NS_REGEXP = re.compile(_NS_REGEXP_STR, re.IGNORECASE)

    def __init__(self, endpoints, namespace, timeout):
        super(Config, self).__init__()
        self._endpoints = endpoints
        if not self._NS_REGEXP.match(namespace):
            raise ValueError("Namespace %r does not match %r"
                             % (namespace, self._NS_REGEXP_STR))
        self._namespace = namespace
        self._timeout = timeout

    @property
    def endpoints(self):
        return self._endpoints

    @property
    def namespace(self):
        return self._namespace

    @property
    def timeout(self):
        return self._timeout


def _get_client(client_cls, endpoints, namespace, timeout):
    conf = Config(endpoints=endpoints,
                  namespace=namespace,
                  timeout=timeout)
    return client_cls(conf=conf)


def get_wrapped_client(endpoints, namespace, timeout):
    return _get_client(client_cls=wrapped_client.WrappedHTTPEtcdClient,
                       endpoints=endpoints,
                       namespace=namespace,
                       timeout=timeout)
