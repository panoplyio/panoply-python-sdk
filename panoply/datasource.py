import events

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
        pass
    