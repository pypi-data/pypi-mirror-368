# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Provides utilities for implementing retry mechanisms in the Ansys HPS data transfer client.

This module includes functionality for handling transient errors and ensuring
robust and reliable operations during data transfer.
"""

import logging
import os

import backoff
import httpx

from ..exceptions import HPSError, NotReadyError, TimeoutError

log = logging.getLogger(__name__)

max_tries_env_name = "ANSYS_DT_CLIENT_RETRY_MAX_TIME"
max_time_env_name = "ANSYS_DT_CLIENT_RETRY_MAX_TRIES"


def _on_backoff(details):
    try:
        msg = "Backing off {wait:0.1f} seconds after {tries} tries: {exception}".format(**details)
        log.info(msg)
    except Exception as ex:
        log.warning(f"Failed to log in backoff handler: {ex}")


def _giveup(e):
    if isinstance(e, httpx.ConnectError):
        return False
    elif isinstance(e, TimeoutError):
        return True
    elif isinstance(e, NotReadyError):
        return False
    elif isinstance(e, HPSError) and e.give_up:
        return True
    elif isinstance(e, TypeError):
        return True

    return False


def _lookup_max_time():
    v = os.getenv(max_time_env_name)
    if v is not None:
        return v
    return 300


def _lookup_max_tries():
    v = os.getenv(max_tries_env_name)
    if v is not None:
        return v
    return 40


def retry(
    max_tries=_lookup_max_tries,
    max_time=_lookup_max_time,
    raise_on_giveup=True,
    jitter=backoff.full_jitter,
):
    """Provides a decorator for retrying a function call with exponential backoff."""
    return backoff.on_exception(
        backoff.expo,
        Exception,
        max_tries=max_tries,
        max_time=max_time,
        jitter=jitter,
        raise_on_giveup=raise_on_giveup,
        on_backoff=_on_backoff,
        logger=None,
        giveup=_giveup,
    )
