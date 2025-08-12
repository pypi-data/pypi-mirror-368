# Backup-chan client library

![PyPI - License](https://img.shields.io/pypi/l/backupchan-client-lib)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/backupchan-client-lib)
![PyPI - Version](https://img.shields.io/pypi/v/backupchan-client-lib)

This is the Python library for interfacing with a Backup-chan server.

## Installing

```bash
# The easy way
pip install backupchan-client-lib

# Install from source
git clone https://github.com/Backupchan/client-lib.git backupchan-client-lib
cd backupchan-client-lib
pip install .
```

For instructions on setting up the server, refer to Backup-chan server's README.

## Testing

```
pytest
```

## Example 

```python
from backupchan import *

# Connect to a server
api = API("http://192.168.1.43", 5000, "your api key")

# Print every target
targets = api.list_targets()
for target in targets:
    print(target)

# Create a new target
target_id = api.new_target(
    "the waifu collection", # name
    BackupType.MULTI,
    BackupRecycleCriteria.AGE,
    10, # recycle value
    BackupRecycleAction.RECYCLE,
    "/var/backups/waifu", # location
    "wf-$I_$D", # name template
    False, # deduplicate
    None # alias
)
target = api.get_target(target_id)
print(f"Created new target: {target}")
```
