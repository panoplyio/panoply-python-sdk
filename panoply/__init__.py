import base64
import json
import time
import urllib2
import threading
import Queue
import logging
from copy import copy

VERSION = "1.1.0"
PKGNAME = "panoply-python-sdk"
MAXSIZE = 1024 * 250 # 250kib
FLUSH_TIMEOUT = 2.0 # 2 seconds

def noop( self, *args, **kwargs ):
    pass

class SDK ( object ):

    account = None
    apikey = None
    apisecret = None

    # duck-typed logger object that exposes a `.log(lvl, msg)` method
    logger = None

    # internal buffer queue
    _buffer = None
    _onerror = noop
    _onsend = noop
    _onflush = noop


    def __init__( self, apikey, apisecret ):
        self.apikey = apikey
        self.apisecret = apisecret

        # decompose the api key and secret
        # api-key: ACCOUNT/RAND1
        # api-secret: BASE64( RAND2/UUID/AWSACCOUNT/REGION )
        decoded = base64.b64decode( apisecret ).split( "/" )
        rand = decoded[ 0 ]
        awsaccount = decoded[ 2 ]
        region = decoded[ 3 ]
        account = apikey.split( "/" )[ 0 ]

        # construct the queue url
        # queue: sdk-ACCOUNT-RAND2
        self.qurl = "https://sqs.%s.amazonaws.com/%s/sdk-%s-%s" % ( 
            region, 
            awsaccount, 
            account, 
            rand 
        )

        self._buffer = Queue.Queue()
        thread = threading.Thread( target = self._sendloop )
        thread.daemon = True
        thread.start()

    def write( self, table, data ):
        # add the new data entry to the internal buffer
        data = copy( data )
        data[ "__table" ] = table
        data = json.dumps( data ).encode( "utf-8" )
        data = urllib2.quote( data )
        self._buffer.put( data + "\n" )

    def on( self, type_, fn ):
        if type_ == "error":
            self._onerror = fn
        elif type_ == "send":
            self._onsend = fn
        elif type_ == "flush":
            self._onflush = fn
        return self

    # flush the buffer to SQS
    def _send( self, body ):
        body = [
            "Action=SendMessage",
            "MessageBody=" + body,
            "MessageAttribute.1.Name=key",
            "MessageAttribute.1.Value.DataType=String",
            "MessageAttribute.1.Value.StringValue=" + self.apikey,
            "MessageAttribute.2.Name=secret",
            "MessageAttribute.2.Value.DataType=String",
            "MessageAttribute.2.Value.StringValue=" + self.apisecret,
            "MessageAttribute.3.Name=sdk",
            "MessageAttribute.3.Value.DataType=String",
            "MessageAttribute.3.Value.StringValue=" + PKGNAME + "-" + VERSION,
        ]

        body = "&".join( body )
        
        headers = {
            "Content-Length": len( body ),
            "Content-Type": "application/x-www-form-urlencoded"
        }
        print "SENDING NOW"

        req = urllib2.Request( self.qurl, body, headers )
        self._onsend( req )
        try:
            res = urllib2.urlopen( req )
        except Exception as err:
            self._onerror( err )
            return
        self._onflush( req, res )

    def _sendloop ( self ):
        buf = self._buffer
        body = ""
        lastsend = time.time()
        while True:
            data = None
            try:
                data = buf.get( True, FLUSH_TIMEOUT ) # blocking
                body += data + "\n"
            except Queue.Empty:
                pass

            length = len( body )
            elapsed = time.time() - lastsend

            if length is 0:
                # reset the time when there's nothing to send
                lastsend = time.time()
            elif length > MAXSIZE or elapsed > FLUSH_TIMEOUT:
                lastsend = time.time()
                self._send( body )
                body = ""

            if data:
                buf.task_done()

