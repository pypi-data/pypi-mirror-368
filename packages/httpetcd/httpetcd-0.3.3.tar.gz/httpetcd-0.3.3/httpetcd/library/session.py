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

import itertools
import logging
import random
import sys

import enum
from httpetcd.common import obj
import requests
from requests import compat
from requests import exceptions as req_exc
import six

from httpetcd import constants
from httpetcd import exceptions

LOG = logging.getLogger(__name__)


class Session(obj.BaseObject):

    def __init__(self, endpoints, api_path, timeout):
        super(Session, self).__init__()

        # shuffle & cycle endpoints
        self._endpoints = [compat.urljoin(ep, api_path) for ep in endpoints]
        random.shuffle(self._endpoints)
        self._l(LOG).debug("Initialized endpoints: %s", self._endpoints)
        self._ep_cycled = itertools.cycle(self._endpoints)
        # prepare active endpoint
        self._endpoint = None
        self._shift_endpoint("init")

        self._api_path = api_path
        self._session = requests.session()
        self._timeout = timeout

    def _shift_endpoint(self, reason):
        old_ep = self._endpoint
        self._endpoint = next(self._ep_cycled)
        self._l(LOG).info("Shifted endpoint from %s to %s for reason: %r",
                          old_ep, self._endpoint, reason)

    def request(self, path, data, codes=enum.IntEnum):
        url = compat.urljoin(self._endpoint, path)
        try:
            self._l(LOG).debug("Requesting url %s with timeout %d",
                               url, self._timeout)
            resp = self._session.post(url=url,
                                      json=data,
                                      timeout=self._timeout)
        except req_exc.ConnectionError as e:
            self._shift_endpoint(e)
            exc_info = sys.exc_info()
            six.reraise(exceptions.ConnectionError,
                        exceptions.ConnectionError((self._endpoint,),
                                                   repr(exc_info[1])),
                        exc_info[2])
        except req_exc.ReadTimeout:
            # May happen when master etcd node location is controlled by
            # switching IP address in DNS record pointing to the master node.
            # We have to reestablish connection to fetch correct IP address.
            self._session.close()
            exc_info = sys.exc_info()
            six.reraise(exceptions.ConnectionError,
                        exceptions.ConnectionError((self._endpoint,),
                                                   repr(exc_info[1])),
                        exc_info[2])
        except Exception:
            exc_info = sys.exc_info()
            six.reraise(exceptions.EtcdException,
                        exceptions.EtcdException(repr(exc_info[1])),
                        exc_info[2])
        resp.raise_for_status()
        result = resp.json()
        self._l(LOG).debug("Response: %s", result)

        if "code" not in result:
            return result

        try:
            code = codes(result["code"])
        except ValueError:
            raise exceptions.UnknownResponseCode("path=%s, data=%r, result=%r"
                                                 % (path, data, result))

        raise exceptions.UnsuccessfulResponse(code=code, resp=result)


def get_session(endpoints, timeout):
    return Session(endpoints=endpoints,
                   api_path=constants.APIVersions.V3BETA.value + "/",
                   timeout=timeout)
