import base64

import events
import requests
import traceback
from errors import PanoplyException


class DataSource(events.Emitter):
    """ A base DataSource object """

    def __init__(self, source, options={}):
        super(DataSource, self).__init__()

        self.source = source
        self.options = options

    def log(self, *msgs):
        """ Log a message """

        if 'logger' in self.options:
            self.options['logger'](msgs)
        else:
            print(msgs)

    def state(self, state_id, state):
        """ Notify on a change in state """

        self.fire('source-state', {
            "stateId": state_id,
            "state": state
        })

    def progress(self, loaded, total, msg=''):
        """ Notify on a progress change """

        self.fire('progress', {
            'loaded': loaded,
            'total': total,
            'msg': msg
        })

    def raw(self, tag, raw, metadata):
        """ Create a raw response object """
        raw = base64.b64encode(raw)
        return {
            'type': 'raw',
            'tag': tag,
            'raw': raw,
            'metadata': metadata
        }


def validate_token(refresh_url, exceptions=(), callback=None,
                   access_key='access_token', refresh_key='refresh_token'):
    ''' a decorator used to validate the access_token for oauth based
    data sources.
    This decorator should be used on every method in the data source that
    fetches data from the oauth controlled resource, and that relies on a
    valid access_token in order to operate properly.
    If the token is valid, the normal flow continues without any change.
    Otherwise, if any of `exceptions` tuple is raised, the normal flow
    will be preceded by the following steps:

    1. `refresh_url` will be called in order to refresh the token
    2. the newly refreshed token will be saved in the source
    3. the `callback` function will be called

    If the refresh fails for any reason, the user would have to re-grant
    permission for the application

    Parameters
    ----------
    refresh_url : str
        The URL to be called in order to refresh the access token.
    callback : str or callable
        A callback function to be called whenever the access_token is
        validated. The callback function would be called with the refreshed
        token as an argument.
        If the `callback` is not `callable`, but an `str` it will be called
        on `self` (i.e. call a method on your Data Source)
        Defaults to None
    exceptions : tuple
        A list of exceptions that should cause token revalidation
        Defaults to Exception, meaning that all errors will cause token
        refresh
    access_key : str
        The access token key as defined in the source and in the response from
        the refresh URL.
        Defaults to `access_token`
    refresh_key : str
        The refresh token key as defined in the source and in the request to
        the refresh URL.
        Defaults to `refresh_token`
    '''
    def _validate_token(f):
        def wrapper(*args):
            self = args[0]
            try:
                return f(*args)
            except exceptions:
                try:
                    self.log('Revalidating the access token...')
                    self.source[access_key] = None

                    # get a new token from refresh_url
                    token = self.source.get(refresh_key)
                    data = dict(self.options['refresh'],
                                **{refresh_key: token})
                    r = requests.post(refresh_url, data=data)
                    self.source[access_key] = r.json()[access_key]

                    # save the new token in the database
                    changes = {access_key: self.source[access_key]}
                    self.fire('source-change', changes)

                    # notify the callback that a new token was issued
                    if callback:
                        if callable(callback):
                            _callback = callback
                        else:
                            _callback = getattr(self, callback)
                        _callback(self.source.get(access_key))

                    return f(*args)
                except Exception, e:
                    self.log('Error: Access token can\'t be revalidated. '
                             'The user would have to re-authenticate',
                             traceback.format_exc())
                    # raise a non-retryable exception
                    raise PanoplyException(
                        'access token could not be refreshed ({})'
                        .format(str(e)), retryable=False)
        return wrapper
    return _validate_token
