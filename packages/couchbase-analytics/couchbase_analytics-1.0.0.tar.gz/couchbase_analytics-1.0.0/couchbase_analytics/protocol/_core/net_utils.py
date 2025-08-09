#  Copyright 2016-2025. Couchbase, Inc.
#  All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.


from __future__ import annotations

import socket
from ipaddress import IPv4Address, IPv6Address, ip_address
from random import choice
from typing import Callable, Optional, Union

from couchbase_analytics.common.logging import LogLevel
from couchbase_analytics.protocol.errors import ErrorMapper


@ErrorMapper.handle_socket_error
def get_request_ip(host: str, port: int, logger_handler: Optional[Callable[..., None]] = None) -> str:
    # Lets not call getaddrinfo, if the host is already an IP address
    try:
        ip: Optional[Union[IPv4Address, IPv6Address, str]] = ip_address(host)
    except ValueError:
        ip = None

    if not ip:
        result = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM, family=socket.AF_UNSPEC)
        res_ip = choice([addr[4][0] for addr in result])  # nosec B311
        ip = str(res_ip)
        if logger_handler:
            message_data = {'results': [f'{addr[4][0]}' for addr in result], 'selected_ip': ip}
            logger_handler(f'getaddrinfo() returned {len(result)} results', LogLevel.DEBUG, message_data=message_data)
    else:
        ip = str(ip)

    return ip
