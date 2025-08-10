# Timezones Library

A Python library and CLI tool for getting current time in different timezones: PST, BST, WAT, CET, and EST.

## Installation

```bash
pip install timezones-lib
```

## Usage

### Python Library
```python
from timezones_lib import get_time_in_timezone, get_all_times

# Get time for specific timezone
pst_time = get_time_in_timezone('PST')
print(f"PST: {pst_time}")

# Get all supported timezones
all_times = get_all_times()
for tz, time in all_times.items():
    print(f"{tz}: {time}")
```

### CLI Tool
```bash
# Show all timezones
tzlib --all

# Get specific timezone
tzlib --timezone PST

# Show available options
tzlib
```

## Supported Timezones
- **PST**: Pacific Standard Time (US/Pacific)
- **BST**: British Summer Time (Europe/London)
- **WAT**: West Africa Time (Africa/Lagos)
- **CET**: Central European Time (Europe/Berlin)
- **EST**: Eastern Standard Time (US/Eastern)

## Development

### Setup
```bash
git clone <repo-url>
cd timezones_lib
pip install -e .
```

### Testing
```bash
python -m pytest tests/
```

### Building
```bash
python -m build
```

## License
MIT