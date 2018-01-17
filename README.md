# panoply-python-sdk
SQS-based Python SDK for streaming data in real-time to the Panoply platform.

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
#### Generating an API Key and Secret

While logged into the Panoply.io platform, click to add a new data source.  Select the Panoply SDK as your data source. This will automatically generate and display in your browser an API key and API secret. Use this key and secret to instantiate SDK objects.

#### API

###### SDK( apikey, apisecret )

Create a new SDK instance, and the underlying Thread for sending the data over HTTP.

###### .write( tablename, data )

Writes a record with the arbitrary `data` dictionary into `tablename`. Not that the record isn't saved immediately but instead it's buffered and will be saved within up to 2 seconds.

###### .on( evname, handlerfn )

Sets the handler for the given event name. Available events are:

 * `send` - emitted immediately **before** sending a batch to the Panoply queue.
 * `flush` - emitted immediately **after** successfully sending a batch to the panoply queue.
 * `error` - emitted when an error occurred during the process.


# Building Data Sources
The SDK also contains the building blocks for creating your own data source. The data source can be used to read data from any external source, like a database, or an API, and write the data to the Panoply.io platform. After the code is written, it can either be open-sourced or sent to the Panoply team in order to include it in the platform's UI.

See an example of a working Data Source here:

* [Librato Data Source](https://github.com/panoplyio/source-librato)

#### Base Data Source

You first need to create a Python class that inherits from the SDK's `panoply.DataSource` base class:

```python
import panoply

class MyDataSource(panoply.DataSource):
  def __init__(self, source, options, *args, **kwargs):
    super(MyDataSource, self).__init__(source, options, *args, **kwargs)
    # and any initialization code you might need

  def read(self, n = None):
    # read up to n objects
    return [{hello:"world"}

  def close(self):
    # if relevant - close/cleanup any resources used by the datasource
    pass
```

The `DataSource` base class exposes the following methods:

###### \_\_init\_\_(self, source, options)

Constructor. Receives a dictionary with the data `source` parameters (see below) and a dictionary with any additional `options`. Generally, it's safe to disregard the options, however it may be used for performance optimizations, as it contains hints about incremental keys, excluded fields, etc. It may also contain additional parameters that can't be transferred with the source (e.g. secret keys).


`source` and `options` are available as attributes from within the class instance.

`source` should have a `destination` key (String) pertaining to the destination table name. Data retrieved using the data source will be saved in a table having that name.

```python
def __init__(self, source, options):
    ...
    if 'destination' not in source:
        source['destination'] = source['type']
```


**Make sure** to call `super()` with all the arguments if you need to override it.

###### read(self, n = None)

Required abstract function. Reads up to `N` objects from the source. `N` is just a hint for the number of objects to return, but it can be disregarded if it's not relevant for your specific data source. This method should return either:

* List of arbitrary objects (python dictionaries). For performance sake, it's advised to return a large batch of objects, as close as possible to N.
* `None`, to indicate an EOF when all of the available data has been read.

###### close(self)

Optional abstract function. Close and cleanup any resources used by the data source, like temporary files, opened db connections, etc.

###### log(self, *msgs)

Writes a message to the log. It's advised to add log lines extensively in order to debug issues in production. **NEVER** log user credentials or other sensitive information. This is also verified as part of our code review process when submitting a data source.

###### progress(self, loaded, total, msg)

Update the progress of the data source during calls to `read()`. It's used by the UI to show a progress bar, and for internal monitoring. You want to call `.progress()` at least once per `read()` call. `loaded` and `total` are integers, representing the number of resources loaded out of the total number of resources. It can be anything, like db rows, files, API calls, etc. `msg` is an optional human-readable text describing the progress status, for example: `3,000/6,000 files loaded`. For the best user experience, it is advised to provide a clear and coherent message.

###### state(self, state_id, state)

Report the current state of the data collection.

- Each state that is reported should have a **unique** `state_id` across the entire process.
- Each data object returned by the source should contain a `__state` key with the value of the current `state_id` of the batch that is being returned.
- Note that every state object that is reported is **merged into one** - this allows for incremental updates to the progress of each resource.

For supported data sources, in the event of a failure, data collection is retried and this state object is provided together with the source dict to allow for the data source to continue from where it left off. An example of a state object would be the name of the current resource (tablename/api endpoint) and the number of data objects already fetched:

    # Note that `tableName` is used as a key so that merging this state object
    # into previous ones will override the loaded value.
    {"state_id": "unique_id`, "state": { "tableName": "loaded": 500}}

With this state object, the data source would be able to use the `loaded` value as a `SKIP` or `OFFSET` parameter.

###### raw(self, tag, raw, metadata)

Constructs a `raw` message object.

This is useful when you wish to send raw messages (bytes) and need a way to attach additional information to each message.

* `tag` - A unique identifier that allows linking between the message and its metadata e.g. file name, batch ID etc.
* `raw` - The raw message.
* `metadata` - A dictionary of fields you wish to append to the message e.g. `{ '__state': 'my-state-id' }`

###### fire(self, type, data)

Fire an event of type `type` with the specified `data`.

Each data source comes with a predefined `source-change` event that can be fired to indicate that the source parameters have changed in order for the system to save the new parameters. The data in this case, is a dictionary of the changed parameters.


#### Exceptions

Exceptions that arise from data sources are not handled by the system. However, if the exceptions were originated from the `read` method, the system will retry the action 3 times before giving up on the task. While this may usually be the required process, there are times when a retry will not yield a different result (e.g HTTP 404 from a service the data source uses). For this reason, the SDK exposes the exception `panoply.errors.PanoplyException` that includes a `retryable` boolean attribute specifying whether the system should retry or not.


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
  "params": [] # see below
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

#### Decorators

The SDK exposes some utilities to help with tasks that recur in many data sources:

###### panoply.validate_token(refresh_url, exceptions, callback=None, access_key='access_token', refresh_key='refresh_token')

The `validate_token` decorator may be used in data sources having OAuth2 authentication, that need to validate (refresh) the token. It should be placed before each method that might fail due to token validation problems. This decorator receives a `refresh_url` string indicating the URL to call in order to refresh the token, an `exceptions` tuple (or single exception) that indicate the exceptions that should be caught in order to refresh the token, `callback` which is an optional `string` (in case it is a method of the data source) or `callable` to call upon receiving the new token (that will be passed as a parameter to the specified callback), an optional `access_key` string indicating the access token key (default: 'access_token') and an optional 'refresh_key' string indicating the refresh token key (default: 'refresh_token').

```python
import panoply

class Stream(panoply.DataSource):
    @panoply.validate_token('https://oauth.provider/token/refresh', HttpError, 'my_callback')
    def read(self, n=None):
        # call an authenticated process relying on the validity of the access token
        ...

    def my_callback(new_token):
        # do something with the new_token
        # there is no need to save it in the source or call the failing method again
        # as those actions are already handled by the decorator
        ...
```


#### Tests and publishing

Every data source is code-reviewed by the Panoply.io team before being integrated to the system. In order to save time, make sure that:

* You follow the best-practices and standard code conventions for the programming language used.
* Keep it slim. Avoid too many dependencies if possible.
* Test it throughly with unit-tests.
* Add an annotated git tag with the version number (eg: v1.0.0) to the master branch locking the data source to a specific version.
* Notify the Panoply.io team of your data source, and we will integrate it promptly.
