
# abstract DataSource object
class DataSource(object):

    source = None
    options = None

    # data source constructor
    def __init__(self, source, options = {}):
        self.source = source
        self.options = options

    # log a message
    def log(self, *msgs):
        if "logger" in self.options:
            self.options["logger"](msgs)
        else:
            print msgs

    def progress(self, loaded, total, msg):
        pass