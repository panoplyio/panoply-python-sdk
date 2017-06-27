import events
import requests
from errors import PanoplyException
import traceback


# abstract DataSource object
class DataSource(events.Emitter):

    source = None
    options = None

    # data source constructor
    def __init__(self, source, options={}, events={}):
        super(DataSource, self).__init__(events)

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


def invalidate_token(refresh_url, callback=None,
                     access_key='access_token', refresh_key='refresh_token'):
    ''' a decorator used to invalidate the access_token for oauth based
    data sources.
    This decorator should be used on every method in the data source that
    fetches data from the oauth controlled resource, and that relies on a
    valid access_token in order to operate properly

    Parameters
    ----------
    refresh_url : str
        The URL to be called in order to refresh the access token.
    callback : callable
        A callback function to be called whenever the access_token is
        invalidated. The callback function would be called with the refreshed
        token as an argument
    access_key : str
        The access token key as defined in the source and in the response from
        the refresh URL.
        Defaults to `access_token`
    refresh_key : str
        The refresh token key as defined in the source and in the request to
        the refresh URL.
        Defaults to `refresh_token`
    '''
    def _invalidate_token(f):
        def wrapper(*args):
            self = args[0]
            try:
                return f(*args)
            except Exception, e:
                try:
                    self.log("Reinvalidating access_token...")
                    self.source[access_key] = None

                    # get a new token from refresh_url
                    token = self.source.get(refresh_key)
                    r = requests.post(
                        refresh_url,
                        data=dict(self.options['refresh'],
                                  **{refresh_key: token}))
                    self.source[access_key] = r.json()[access_key]

                    # save the new token in the database
                    changes = {access_key: self.source[access_key]}
                    self.fire("source-change", changes)

                    # notify the callback that a new token was issued
                    if callback:
                        if callable(callback):
                            _callback = callback
                        else:
                            _callback = getattr(self, callback)
                        _callback(self.source.get(access_key))

                    return f(*args)
                except:
                    # make sure the real exception is logged
                    self.log(e, traceback.format_exc())
                    self.log("Error: Access token can't be invalidated."
                             " The user would have to re-authenticate")
                    # raise a non-retryable exception
                    raise PanoplyException(
                        'access token could not be refreshed ({})'
                        .format(str(e)), retryable=False)
        return wrapper
    return _invalidate_token
