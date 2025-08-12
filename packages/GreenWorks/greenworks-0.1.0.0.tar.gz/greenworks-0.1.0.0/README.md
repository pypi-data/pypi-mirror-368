# GreenWorks-Core

GreenWorks-Core is a Python package that provides an API wrapper for the Greenworks robotic lawn mower, enabling you to authenticate, list devices, and retrieve mower status and properties.

## Install

Install from PyPI (name subject to change if unpublished):

```
pip install GreenWorks
```

## Quick start

```python
from src.GreenWorksAPI.GreenWorksAPI import GreenWorksAPI

api = GreenWorksAPI("you@example.com", "your-password", "Europe/Copenhagen")
devices = api.get_devices()
for d in devices:
		print(d.name, d.is_online, d.operating_status.mower_main_state)
```

## Logging

This library uses the standard Python `logging` module with a module-level logger. No handlers are configured by default (a NullHandler is attached), so logs are propagated to the host application.

### Home Assistant

Home Assistant captures Python logs. To enable debug logs for this library, add to your `configuration.yaml`:

```
logger:
	default: warning
	logs:
		src.GreenWorksAPI: debug
```

You can also target a single module:

```
logger:
	logs:
		src.GreenWorksAPI.GreenWorksAPI: debug
```

### Standalone scripts

```python
import logging
logging.basicConfig(level=logging.INFO)
```
