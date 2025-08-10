# Bear Epoch Time v1.1.4

Bear Epoch Time is a lightweight helper library for working with epoch timestamps. It provides timezone-aware
conversion utilities and an optional fluent API for manipulating times without having to remember all of the
`datetime` quirks. Supports Python 3.10+, trying to update things so it supports Python 3.9.

## WIP

README will need to be expanded and elaborated upon.

## Installation

Install from PyPI using `uv`:

```bash
uv pip install bear-epoch-time
```

## Quick Start

### EpochTimestamp

```python
from bear_epoch_time import EpochTimestamp

# current UTC timestamp in milliseconds
now = EpochTimestamp.now()
print(now) # Will print the epoch timestamp as an int
print(now.to_seconds)  # convert to seconds
print(now.date_str())  # "06-12-2025"
```

### TimeTools

```python
from bear_epoch_time import TimeTools

# helper for day ranges and conversions
utils = TimeTools()
start, end = utils.get_day_range()
print(start.to_string())
print(end.to_string())
```

### Limitations

The EpochTimestamp class is designed to work with UTC timestamps in the recent past and future. It is not really meant to work with historical dates or times before the Unix epoch (1970-01-01). It is also not meant to be used for very high precision timing. This is more of a utility library for working with epoch timestamps in a more human-friendly way.
