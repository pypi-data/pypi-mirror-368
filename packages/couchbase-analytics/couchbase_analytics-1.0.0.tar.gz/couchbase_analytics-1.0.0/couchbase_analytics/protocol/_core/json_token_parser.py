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

from typing import Callable, List, Optional

from couchbase_analytics.common._core.json_token_parser_base import (
    POP_EVENTS,
    START_EVENTS,
    VALUE_TOKENS,
    JsonTokenParserBase,
    JsonTokenParsingError,
    ParsingState,
    TokenType,
)


class JsonTokenParser(JsonTokenParserBase):
    def __init__(self, result_handler: Optional[Callable[[bytes], None]] = None) -> None:
        self._result_handler = result_handler
        super().__init__(emit_results_enabled=result_handler is not None)

    def _handle_obj_emit(self, obj: str) -> bool:
        if (
            self._emit_results_enabled
            and self._result_handler is not None
            and ParsingState.okay_to_emit(self._state, self._previous_state)
        ):
            self._result_handler(bytes(obj, 'utf-8'))
            return True
        return False

    def _handle_pop_event(self, token_type: TokenType) -> None:
        matching_token = self._get_matching_token(token_type)
        obj_pairs: List[str] = []
        while self._stack:
            next_token = self._pop()
            if next_token.type == matching_token.type:
                should_emit = self._handle_pop_transition(next_token.state)
                # NOTE: obj_pairs.reverse() vs. reversed(obj_pairs) are essentially the same _because_ we convert
                #       the obj_pairs to a string (e.g. ",".join(...)); using reversed() in this case is slightly
                #       more convenient as it returns an iterator
                if matching_token.type == TokenType.START_ARRAY:
                    obj = f'[{",".join(reversed(obj_pairs))}]'
                else:
                    obj = f'{{{",".join(reversed(obj_pairs))}}}'
                if should_emit and self._handle_obj_emit(obj):
                    break  # this means we emiited the result/error, so stop processing the stack

                if len(self._stack) > 0 and self._stack[-1].type == TokenType.MAP_KEY:
                    map_key = self._pop()
                    # If we are emitting rows and/or errors,
                    # we don't keep them in the stack and therefore don't need to return the results
                    if self._should_push_pair(next_token):
                        self._push(TokenType.PAIR, f'{map_key.value}:{obj}')
                else:
                    self._push(TokenType.OBJECT, obj)

                break
            obj_pairs.append(next_token.value)

    def get_result(self) -> Optional[bytes]:
        return bytes(self._stack.pop().value, 'utf-8') if self._stack else None

    def parse_token(self, token: str, value: str) -> None:
        token_type = TokenType.from_str(token)
        if token_type in VALUE_TOKENS:
            val = self._handle_value_token(token_type, value)
            if val is not None:
                self._handle_obj_emit(val)
        elif token_type == TokenType.MAP_KEY:
            self._handle_map_key_token(value)
        elif token_type in START_EVENTS:
            self._handle_start_event(token_type)
        elif token_type in POP_EVENTS:
            self._handle_pop_event(token_type)
        else:
            raise JsonTokenParsingError(f'Invalid token type: {token_type}; {value=}')
