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
            source['destination'] = source['type']

        self.source = source
        self.options = options

    # log a message
    def log(self, *msgs):
        if "logger" in self.options:
            self.options["logger"](msgs)
        else:
            print msgs

    def progress(self, loaded, total, msg):
        self.fire("progress", {
            "loaded": loaded,
            "total": total,
            "msg": msg
        })

# a decorator used to invalidate the access_token for oauth based data sources
# this should be used on every method in the data source that fetches data
# from the server (controlled by this oauth), and that needs to be invalidated
def invalidate_token(refresh_url, callback=None):
    def _invalidate_token(f):
        def wrapper(*args):
            self = args[0]
            try:
                return f(*args)
            except:
                try:
                    print("Reinvalidating access_token...")
                    self.source['access_token'] = None

                    token = self.source.get('refresh_token')
                    r = requests.post(
                        refresh_url,
                        data = dict(self.options['refresh'],
                                    refresh_token=token))
                    self.source['access_token'] = r.json()['access_token']

                    changes = {'access_token': self.source['access_token']}
                    self.fire("source-change", changes)

                    if callback:
                        _callback = getattr(self, callback)
                        _callback(self.source.get('access_token'))

                    return f(*args)
                except:
                    traceback.print_exc()
                    print("Error: Access token can't be invalidated." +
                          " The user would have to re-authenticate")
                    raise PanoplyException(
                        'access token could not be refreshed',
                        retryable=False)
        return wrapper
    return _invalidate_token
