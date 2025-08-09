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


import asyncio
import selectors
from typing import Optional


class _LoopValidator:
    """
    **INTERNAL**
    """

    REQUIRED_METHODS = {'add_reader', 'remove_reader', 'add_writer', 'remove_writer'}

    @staticmethod
    def _get_working_loop() -> asyncio.AbstractEventLoop:
        """
        **INTERNAL**
        """
        evloop = asyncio.get_event_loop()
        gen_new_loop = not _LoopValidator._is_valid_loop(evloop)
        if gen_new_loop:
            evloop.close()
            selector = selectors.SelectSelector()
            new_loop = asyncio.SelectorEventLoop(selector)
            asyncio.set_event_loop(new_loop)
            return new_loop

        return evloop

    @staticmethod
    def _is_valid_loop(evloop: Optional[asyncio.AbstractEventLoop] = None) -> bool:
        """
        **INTERNAL**
        """
        if not evloop:
            return False
        for meth in _LoopValidator.REQUIRED_METHODS:
            abs_meth, actual_meth = (getattr(asyncio.AbstractEventLoop, meth), getattr(evloop.__class__, meth))
            if abs_meth == actual_meth:
                return False
        return True

    @staticmethod
    def get_event_loop(evloop: Optional[asyncio.AbstractEventLoop] = None) -> asyncio.AbstractEventLoop:
        """
        **INTERNAL**
        """
        if evloop and _LoopValidator._is_valid_loop(evloop):
            return evloop
        return _LoopValidator._get_working_loop()

    @staticmethod
    def close_loop() -> None:
        """
        **INTERNAL**
        """
        evloop = asyncio.get_event_loop()
        evloop.close()


def get_event_loop(evloop: Optional[asyncio.AbstractEventLoop] = None) -> asyncio.AbstractEventLoop:
    """
    Get an event loop compatible with acouchbase_analytics.
    Some Event loops, such as ProactorEventLoop (the default asyncio event
    loop for Python 3.8 on Windows) are not compatible with acouchbase_analytics as
    they don't implement all members in the abstract base class.

    :param evloop: preferred event loop
    :return: The preferred event loop, if compatible, otherwise, a compatible
    alternative event loop.
    """
    return _LoopValidator.get_event_loop(evloop)
