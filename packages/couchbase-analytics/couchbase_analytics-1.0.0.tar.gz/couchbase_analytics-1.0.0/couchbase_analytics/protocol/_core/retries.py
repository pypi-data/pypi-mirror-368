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

from concurrent.futures import CancelledError
from functools import wraps
from time import sleep
from typing import TYPE_CHECKING, Callable, Optional, Union

from httpx import ConnectError, ConnectTimeout, CookieConflict, HTTPError, InvalidURL, ReadTimeout, StreamError

from couchbase_analytics.common.errors import AnalyticsError, InternalSDKError, TimeoutError
from couchbase_analytics.common.logging import LogLevel
from couchbase_analytics.common.request import RequestState
from couchbase_analytics.protocol.errors import WrappedError

if TYPE_CHECKING:
    from couchbase_analytics.protocol._core.request_context import RequestContext
    from couchbase_analytics.protocol.streaming import HttpStreamingResponse


class RetryHandler:
    """
    **INTERNAL**
    """

    @staticmethod
    def handle_httpx_retry(ex: Union[ConnectError, ConnectTimeout], ctx: RequestContext) -> Optional[Exception]:
        err_str = str(ex)
        if 'SSL:' in err_str:
            message = 'TLS connection error occurred.'
            return AnalyticsError(cause=ex, message=message, context=str(ctx.error_context))
        delay = ctx.calculate_backoff()
        err: Optional[Exception] = None
        if not ctx.okay_to_delay_and_retry(delay):
            if ctx.retry_limit_exceeded:
                err = AnalyticsError(cause=ex, message='Retry limit exceeded.', context=str(ctx.error_context))
            else:
                err = TimeoutError(message='Request timed out during retry delay.', context=str(ctx.error_context))
        if err:
            return err
        sleep(delay)
        ctx.log_message(
            'Retrying request',
            LogLevel.DEBUG,
            {'num_attempts': f'{ctx.error_context.num_attempts}', 'delay': f'{delay}s'},
        )
        return None

    @staticmethod
    def handle_retry(ex: WrappedError, ctx: RequestContext) -> Optional[Union[BaseException, Exception]]:
        if ex.retriable is True:
            delay = ctx.calculate_backoff()
            err: Optional[Union[BaseException, Exception]] = None
            if not ctx.okay_to_delay_and_retry(delay):
                if ctx.retry_limit_exceeded:
                    if ex.is_cause_query_err:
                        ex.maybe_set_cause_context(ctx.error_context)
                        err = ex.unwrap()
                    else:
                        err = AnalyticsError(
                            cause=ex.unwrap(), message='Retry limit exceeded.', context=str(ctx.error_context)
                        )
                else:
                    err = TimeoutError(message='Request timed out during retry delay.', context=str(ctx.error_context))

            if err:
                return err
            sleep(delay)
            ctx.log_message(
                'Retrying request',
                LogLevel.DEBUG,
                {'num_attempts': f'{ctx.error_context.num_attempts}', 'delay': f'{delay}s'},
            )
            return None
        ex.maybe_set_cause_context(ctx.error_context)
        return ex.unwrap()

    @staticmethod
    def with_retries(fn: Callable[[HttpStreamingResponse], None]) -> Callable[[HttpStreamingResponse], None]:  # noqa: C901
        @wraps(fn)
        def wrapped_fn(self: HttpStreamingResponse) -> None:  # noqa: C901
            while True:
                try:
                    fn(self)
                    break
                except WrappedError as ex:
                    err = RetryHandler.handle_retry(ex, self._request_context)
                    if err is None:
                        continue
                    self._request_context.shutdown(ex)
                    raise err from None
                except (ConnectError, ConnectTimeout) as ex:
                    err = RetryHandler.handle_httpx_retry(ex, self._request_context)
                    if err is None:
                        continue
                    self._request_context.shutdown(ex)
                    raise err from None
                except ReadTimeout as ex:
                    # we set the read timeout to the query timeout, so if we get a ReadTimeout,
                    # it means the request timed out from the httpx client
                    self._request_context.shutdown(ex)
                    raise TimeoutError(
                        message='Request timed out.', context=str(self._request_context.error_context)
                    ) from None
                except (CookieConflict, HTTPError, StreamError, InvalidURL) as ex:
                    # these are not retriable errors, so we just shutdown the request context and raise the error
                    self._request_context.shutdown(ex)
                    raise AnalyticsError(
                        cause=ex, message=str(ex), context=str(self._request_context.error_context)
                    ) from None
                except AnalyticsError:
                    # if an AnalyticsError is raised, we have already shut down the request context
                    raise
                except RuntimeError as ex:
                    self._request_context.shutdown(ex)
                    if self._request_context.timed_out:
                        raise TimeoutError(
                            message='Request timeout.', context=str(self._request_context.error_context)
                        ) from None
                    if self._request_context.cancelled:
                        raise CancelledError('Request was cancelled.') from None
                    raise ex
                except BaseException as ex:
                    self._request_context.shutdown(ex)
                    if self._request_context.timed_out:
                        raise TimeoutError(
                            message='Request timeout.', context=str(self._request_context.error_context)
                        ) from None
                    if self._request_context.cancelled:
                        raise CancelledError('Request was cancelled.') from None
                    if isinstance(ex, Exception):
                        # If the exception is an Exception, we raise it as an InternalSDKError as this is
                        # an unexpected error in the SDK
                        raise InternalSDKError(
                            cause=ex, message=str(ex), context=str(self._request_context.error_context)
                        ) from None
                    # we should have handled CancelledError and TimeoutError above, so if we get here,
                    # raise the BaseException as is (most likely a KeyboardInterrupt)
                    raise ex
                finally:
                    if not RequestState.is_okay(self._request_context.request_state):
                        self.close()

        return wrapped_fn
