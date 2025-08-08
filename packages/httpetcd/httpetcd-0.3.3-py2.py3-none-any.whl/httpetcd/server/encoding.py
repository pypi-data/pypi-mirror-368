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

import base64

import six


bytes_types = (bytes, bytearray)


def encode64(data):
    """Encode the given data using base-64

    :param data:
    :return: base-64 encoded string
    """
    if not isinstance(data, bytes_types):
        data = six.b(str(data))
    return base64.b64encode(data).decode("utf-8")


def decode64(data):
    """Decode the base-64 encoded string

    :param data:
    :return: decoded data
    """
    if not isinstance(data, bytes_types):
        data = six.b(str(data))
    return base64.b64decode(data.decode("utf-8")).decode("utf-8")
