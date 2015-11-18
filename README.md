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


