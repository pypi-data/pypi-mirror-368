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


class EtcdException(Exception):
    pass


class ConnectionError(EtcdException):

    endpoints = None

    def __init__(self, endpoints, *args):
        super(ConnectionError, self).__init__(*args)
        self.endpoints = tuple(endpoints)


class LeaseExpired(EtcdException):
    pass


class KVCreateError(EtcdException):
    pass


class KVLockCreateError(EtcdException):
    pass


class KVLockAlreadyOccupied(EtcdException):
    pass


class KVLockExpired(EtcdException):
    pass


class UnknownResponseCode(EtcdException):
    pass


class UnsuccessfulResponse(EtcdException):

    def __init__(self, code, resp):
        self.code = code
        self.resp = resp
        super(UnsuccessfulResponse, self).__init__("Server returned code: %s"
                                                   % self.code)
