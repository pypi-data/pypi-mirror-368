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
"""Provides utilities for implementing exponential backoff with optional jitter.

This module is commonly used in retry mechanisms to handle transient errors in distributed systems.
"""

from random import uniform


def get_expo_backoff(
    base: float, attempts: int = 1, cap: float = 100_000_000, attempts_cap: int = 100_000_000, jitter: bool = True
):
    """Get the backoff value.

    For more information, see `Exponential Backoff And Jitter
    <https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/>`_
    in the AWS documentation.

    Parameters
    ==========
    base : float
        Time to sleep in the first attempt.
    attempts : int, default: 1
        Number of attempts that have already been made.
    cap : float, default: 100000000
        Maximum value that can be returned.
    jitter : bool, default: True
        Whether to apply jitter to the returned value.
    """
    # Full jitter formula
    # https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
    attempts = min(attempts, attempts_cap)
    if jitter:
        try:
            return uniform(base, min(cap, base * 2 ** (attempts - 1)))
        except OverflowError:
            return cap
    else:
        return min(cap, base * 2 ** (attempts - 1))
