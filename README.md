# panoply-python-sdk
SQS-based Python SDK for streaming data in realtime to the Panoply platform

#### Install

```
$ python setup.py install
```

#### Usage

```python
import panoply
conn = panoply.SDK( "APIKEY", "APISECRET" )
conn.write( "tablename", { "foo": "bar" } )
```

#### API

###### SDK( apikey, apisecret )

Create a new SDK instance, and the underlying Thread for sending the data over HTTP.

###### .write( tablename, data )

Writes a record with the arbitrary `data` dictionary into `tablename`. Not that the record isn't saved immediately but instead it's buffered and will be saved within up to 2 seconds.

###### .on( evname, handlerfn )

Sets the handler for the given event name. Available events are:

 * `error`
 * `send`, emitted immediately before sending a batch to the Panoply queue.
 * `flush`, emitted immediately after successfully sending a batch to the panoply queue.


# Building Data Sources
The SDK also contains the building blocks for creating your own data source. The data source can be used to read data from any external source, like a database, or an API, and write the data to the Panoply.io platform. After the code is written, it can either be open-sourced or sent to the Panoply team in order to include it in the platform's UI.

See an example of a working Data Source here:

* [Librato Data Source](https://github.com/panoplyio/source-librato)

#### Base Data Source

You first need to create a Python class that inherits from the SDK's `panoply.DataSource` base class:

```python
import panoply

class MyDataSource(panoply.DataSource):
  def __init__(self, source, options):
    super(MyDataSource, self).__init__(source, options)
    # and any initialization code you might need

  def read(self, n = None):
    # read up to n objects
    return [{hello:"world"}
    
  def close(self):
    # if relevant - close/cleanup any resources used by the datasource
    pass
```

The `DataSource` base class exposes the following methods:

###### __init__(self, source, options)

Constructor. Receives a dictionary with the data `source` parameters (see below) and a dictionary with any additional `options`. Generally, it's safe to disregard the options, however it may be used for performance optimizations, as it contains hints about incremental keys, excluded fields, etc.

**Make sure** to call `super()` if you need to override it.

###### read(self, n = None)

Required abstract function. Reads up to `N` objects from the source. `N` is just a hint for the number of objects to return, but it can be disregarded if it's not relevant for your specific data source. This method should return either:

* List of arbitrary objects (python dictionaries), preferrably in a large batch. For performance, it's advised to return a large amount of objects, as close as possible to N.
* `None`, to indicate an EOF when all of the available data has been read.

###### close(self)

Optional abstract function. Close and cleanup any resources used by the data source, like temporary files, opened db connections, etc.

###### log(self, *msgs)

Writes a message to the log. It's advised to add log lines extensively in order to debug issues in production. **NEVER** log user credentials or other sensitive information. This is also verified as part of our code review process when submitting a data source.

###### progress(self, loaded, total, msg)

Update the progress of the data source during calls to `read()`. It's used by the UI to show a progress bar, and for internal monitoring. You want to call `.progress()` at least once per `read()` call. `loaded` and `total` are integers, representing the number of resources loaded out of the total number of resources. It can be anything, like db rows, files, API calls, etc. `msg` is a human-readable text describing the progress status, for example: `3,000/6,000 files loaded`.


#### Configuration

Your python module should expose the following fixed attributes:

###### Stream

Reference to your inherited Data Source class.

```python
Stream = MyDataSource
```

###### CONFIG

A dictionary with configuration details for the data source.

```python
CONFIG = {
  "title": "My Data Source", # human-readable title
  "icon": "data:image/png;base64,iVBORw...", # a data-url icon to show in the UI
  "params": {} # see below
}
```

the `CONFIG["params"]` directive contains the list of input variables required by your data source, for example, the hostname of a database, user credentials, etc. These variables are used to generate the UI and CLI for running your data source. The actual values are delivered to the data source constructor in the `source` argument:

```python
CONFIG["params"] = [
  {
    "name": "user",
    "title": "User name",
    "placeholder": "Example: myuser1234",
  },
  {
    "name": "database",
    "placeholder": "Example: 127.0.0.1",
    "help": "Host name or IP address"
  }
]
```


#### Tests and publishing

Every data source is code-reviewed by the Panoply.io team before being integrated to the system. In order to save time, make sure that:

* You follow the best-practices and standard code conventions for the programming language used.
* Keep it slim. Avoid too many dependencies if possible.
* Test it throughly with unit-tests.
* Notify the Panoply.io team of your data source, and we will integrate it promptly.


