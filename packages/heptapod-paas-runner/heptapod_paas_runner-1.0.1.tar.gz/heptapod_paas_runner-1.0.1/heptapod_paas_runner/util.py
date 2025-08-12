# Copyright 2024 Georges Racinet <georges.racinet@cloudcrane.io>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-3.0-or-later
from functools import wraps
import logging
import time

logger = logging.getLogger(__name__)


def retry(attempts=2, delay_seconds=0, break_exceptions=()):
    """Decorator adding a simple retry logic to any function.

    :param int attemps: total number of attempts
    :param delay_seconds: Time to sleep between attempts. The main drawback is
      that this is not interruptable sleeping, hence it should be kept at
      only a few seconds max.
    :param break_exceptions: iterable of exception classes. If the catched
      exception is an instance of these classes, no retry is attempted.
    """
    def decorate(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            attempt = 1
            while attempt <= attempts:
                try:
                    return f(*args, **kwargs)
                except Exception as exc:
                    if attempt == attempts:
                        raise
                    if any(isinstance(exc, cls) for cls in break_exceptions):
                        raise
                    logger.warning("Caught exception %r in attempt %d/%d of "
                                   "%r", exc, attempt, attempts, f)
                    attempt += 1
                    time.sleep(delay_seconds)

        return wrapper
    return decorate
