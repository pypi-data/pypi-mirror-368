# FSEconomy Python Bindings

This package provides Python bindings for various [FSEconomy](https://www.fseconomy.net) APIs.

[![Documentation Status](https://readthedocs.org/projects/fseconomy-python/badge/?version=latest)](https://fseconomy-python.readthedocs.io/en/latest/?badge=latest)

**Important Links**

* Documentation: https://fseconomy-python.readthedocs.io/
* GitHub: https://github.com/fseconomy/fseconomy-python
* Bug Tracker: https://github.com/fseconomy/fseconomy-python/issues

## Usage

### Initialization

In order to use any of FSEconomy's APIs, you will need to initialize 
the corresponding API keys:

```python
import fseconomy

fseconomy.set_access_key('0123456789ABCDEF')
fseconomy.set_service_key('0123456789ABCDEF')
fseconomy.set_user_key('0123456789ABCDEF')
```

Please refer to the corresponding section of the
[FSEconomy Operations Guide](https://sites.google.com/site/fseoperationsguide/data-feeds)
for an explanation of the different keys and their purpose.

### FSEconomy Data Feeds

Retrieve data from FSEconomy's data feed API. For most feeds, you must set a valid key first.

```python
import fseconomy
import fseconomy.data

fseconomy.set_access_key('0123456789ABCDEF')
fseconomy.set_service_key('0123456789ABCDEF')
fseconomy.set_user_key('0123456789ABCDEF')

data_feed = fseconomy.data.aircraft_configs()
print(data_feed.status) # HTTP response status code
print(data_feed.data)   # parsed into native python data types
print(data_feed.binary) # true if raw data is binary data
print(data_feed.raw)    # raw data as received from the server
```

A comprehensive list of all data feeds can be found in the
[official documentation](https://fseconomy-python.readthedocs.io/en/latest/)

### FSEconomy REST API

### FSEconomy Auth API
