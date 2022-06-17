import base64
import traceback
from abc import abstractmethod, ABCMeta
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from threading import Event
from typing import List, Dict, Union

import backoff
import requests

from . import events
from .errors.exceptions import (TokenValidationException, MetadataNotSupportedException)
from .records import RecordGroup
from .resources import Resource


class DataSource(events.Emitter, metaclass=ABCMeta):
    """ A base DataSource object """

    def __init__(self, source, options={}):
        super(DataSource, self).__init__()

        self.source = source
        self.options = options

    @abstractmethod
    def read(self, batch_size=None) -> List[Union[RecordGroup, Dict]]:
        """
        Reads data from the sources and returns it as record group
        """

    @classmethod
    def get_resource(cls, resource_id: str, source, options={}) -> Resource:
        """
        Returns a resource object with the list of fields
        """
        raise MetadataNotSupportedException("`get_resource` method is not supported.")

    @classmethod
    def list_resources(cls, source, options={}) -> List[Resource]:
        """
        Returns a list of resources the source can extract from.
        The list depends on the user permissions.
        """
        raise MetadataNotSupportedException("`list_resources` method is not supported.")

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


@backoff.on_exception(backoff.expo,
                      requests.exceptions.RequestException,
                      max_tries=3)
def __send_request(url, data):
    response = requests.post(url, data=data)
    response.raise_for_status()
    return response


def validate_token(refresh_url, exceptions=(), callback=None,
                   access_key='access_token', refresh_key='refresh_token'):
    """
    a decorator used to validate the access_token for oauth based
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
    """

    def _validate_token(f):
        def wrapper(*args, **kwargs):
            self = args[0]
            try:
                return f(*args, **kwargs)
            except exceptions:
                try:
                    self.log('Revalidating the access token...')
                    self.source[access_key] = None

                    # get a new token from refresh_url
                    token = self.source.get(refresh_key)
                    data = dict(self.options['refresh'],
                                **{refresh_key: token})
                    r = __send_request(refresh_url, data=data)
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
                except Exception as e:
                    self.log('Error: Access token can\'t be revalidated. '
                             'The user would have to re-authenticate',
                             traceback.format_exc())
                    # raise a non-retryable exception
                    raise TokenValidationException(e,
                                                   'access token could not be'
                                                   ' refreshed ({})'.format(str(e)),
                                                   retryable=False)

                return f(*args, **kwargs)

        return wrapper

    return _validate_token


def background_progress(message, waiting_interval=10 * 60):
    """ A decorator is used to emit progress while long operation is executed.
        For example, for database's data sources such operations might be
        declaration of the cursor or counting number of rows.
        This decorator should only be used on methods that are waiting for
        input/output operations to be completed.

       Parameters
       ----------
       message : str
           Message that will be emitted while waiting for operation to complete.
       waiting_interval : float
           Time in seconds to wait between progress emitting.
           Defaults to 10 minutes
    """

    def _background_progress(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self = args[0]
            self.log('Creating background progress emitter')
            finished = Event()
            with ThreadPoolExecutor(max_workers=1) as executor:
                func_future = executor.submit(func, *args, **kwargs)
                func_future.add_done_callback(lambda future: finished.set())

                while not func_future.done():
                    self.log(message)
                    self.progress(None, None, message)
                    finished.wait(timeout=waiting_interval)

                return func_future.result()

        return wrapper

    return _background_progress
