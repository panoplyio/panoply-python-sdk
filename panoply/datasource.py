import events
import inspect
import sched
import time
from errors import PanoplyException
from oauth2client.client import AccessTokenCredentialsError

# abstract DataSource object
class DataSource(events.Emitter):

    source = None
    options = None

    # data source constructor
    def __init__(self, source, options = {}):
        super(DataSource, self).__init__()

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

    def call(self, action, params=None):
        runner = get_parent_scope('call')
        runner(action, params)

# get the parent scope in which the key resides
# in `DataSource.call` for example, this is used to get the runner where the
# `call` function is
def get_parent_scope(key):
    frame = inspect.stack()[1][0]
    while key not in frame.f_locals:
        frame = frame.f_back
        if frame is None:
            return None
    return frame.f_locals[key]

# a decorator used to invalidate the access_token for oauth based data sources
# this should be used on every method in the data source that fetches data
# from the server (controlled by this oauth), and that needs to be authorized
def validate_token(callback=None):
    def _validate_token(f):
        def wrapper(*args):
            self = args[0]
            try:
                print("Reinvalidating access_token...")

                # refresh token and try again
                data = {
                    'refresh_token': self.source.get('refresh_token')
                }
                self.call('refresh_token', data)
                while self.source.get('access_token') is None:
                    time.sleep(.5)
                try:
                    _callback = getattr(self, callback)
                    _callback(self.source.get('access_token'))
                except:
                    pass

                return f(*args)
            except:
                print("Error: Access token can't be invalidated." +
                      " The user would have to re-authenticate")
                raise PanoplyException(
                    'access token could not be refreshed',
                    retryable=False)
        return wrapper
    return _validate_token
