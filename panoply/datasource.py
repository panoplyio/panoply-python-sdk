import events
import requests
from errors import PanoplyException
import traceback

# abstract DataSource object
class DataSource(events.Emitter):

    source = None
    options = None

    # data source constructor
    def __init__(self, source, options = {}, events = {}):
        super(DataSource, self).__init__(events)

        if 'destination' not in source:
            source['destination'] = source.get('type')

        self.source = source
        self.options = options

    # log a message
    def log(self, *msgs):
        if "logger" in self.options:
            self.options["logger"](msgs)
        else:
            print(msgs)

    def progress(self, loaded, total, msg=''):
        self.fire("progress", {
            "loaded": loaded,
            "total": total,
            "msg": msg
        })

# a decorator used to invalidate the access_token for oauth based data sources
# this should be used on every method in the data source that fetches data
# from the server (controlled by this oauth), and that needs to be invalidated
def invalidate_token(refresh_url, callback=None,
                     keys=['access_token', 'refresh_token']):
    def _invalidate_token(f):
        def wrapper(*args):
            self = args[0]
            try:
                return f(*args)
            except Exception, e:
                try:
                    self.log("Reinvalidating access_token...")
                    self.source[keys[0]] = None

                    # get a new token from refresh_url
                    token = self.source.get(keys[1])
                    r = requests.post(
                        refresh_url,
                        data = dict(self.options['refresh'], **{keys[1]:token}))
                    self.source[keys[0]] = r.json()[keys[0]]

                    # save the new token in the database
                    changes = {keys[0]: self.source[keys[0]]}
                    self.fire("source-change", changes)

                    # notify the callback that a new token was issued
                    if callback:
                        if callable(callback):
                            _callback = callback
                        else:
                            _callback = getattr(self, callback)
                        _callback(self.source.get(keys[0]))

                    return f(*args)
                except:
                    # make sure the real exception is logged
                    self.log(e, traceback.format_exc())
                    self.log("Error: Access token can't be invalidated." +
                          " The user would have to re-authenticate")
                    # raise a non-retryable exception
                    raise PanoplyException(
                        'access token could not be refreshed ({})'
                        .format(str(e)), retryable=False)
        return wrapper
    return _invalidate_token
