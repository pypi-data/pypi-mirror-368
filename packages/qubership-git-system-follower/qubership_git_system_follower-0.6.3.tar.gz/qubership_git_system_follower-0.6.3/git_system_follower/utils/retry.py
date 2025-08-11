# Copyright 2024-2025 NetCracker Technology Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Callable
import functools


class NeedRetry(Exception):
    def __init__(self, msg='', *args):
        super().__init__(msg, *args)


class MaxRetries(Exception):
    def __init__(self, msg, *args):
        super().__init__(msg, *args)


def retry(max_retries: int = 5, *, output_func: Callable = print, error_output_func: Callable = print):
    """ Decorator to re-execute the function if an exception occurs

    :param max_retries: Maximum number of attempts to execute the function
    :param output_func: normal message output function
    :param error_output_func: error output function
    """
    def decorator_retry(func):
        @functools.wraps(func)
        def wrapper_retry(*args, **kwargs):
            count = 0
            while count < max_retries:
                try:
                    result = func(*args, **kwargs)
                    return result
                except NeedRetry as error:
                    count += 1
                    error_output_func(f'{error.__class__.__name__}: {error}')

                if count >= max_retries:
                    raise MaxRetries('Max retries reached. Operation failed')
                output_func(f'There is been an error. Retry №{count}')
        return wrapper_retry
    return decorator_retry
