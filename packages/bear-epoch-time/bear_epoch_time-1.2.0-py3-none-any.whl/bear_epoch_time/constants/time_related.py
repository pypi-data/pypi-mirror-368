"""Constants for time-related calculations in the Bear Epoch Time package."""

from typing import Literal

MILLISECONDS_IN_SECOND: Literal[1000] = 1000
"""1000 milliseconds in a second"""

SECONDS_IN_MINUTE: Literal[60] = 60
"""60 seconds in a minute"""

MINUTES_IN_HOUR: Literal[60] = 60
"""60 minutes in an hour"""

HOURS_IN_DAY: Literal[24] = 24
"""24 hours in a day"""

DAYS_IN_MONTH: Literal[30] = 30
"""30 days in a month, approximation for a month"""


SECONDS_IN_HOUR: Literal[3600] = SECONDS_IN_MINUTE * MINUTES_IN_HOUR
"""60 * 60 = 3600 seconds in an hour"""

SECONDS_IN_DAY: Literal[86400] = SECONDS_IN_HOUR * HOURS_IN_DAY
"""24 * 60 * 60 = 86400 seconds in a day"""

SECONDS_IN_MONTH: Literal[2592000] = SECONDS_IN_DAY * DAYS_IN_MONTH
"""30 * 24 * 60 * 60 = 2592000 seconds in a month"""
