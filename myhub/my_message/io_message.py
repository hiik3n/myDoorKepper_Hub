class IOMessage(object):
    messageCode = "IO_MSG"

    def __init__(self, *args, **kwargs):
        self.payload = kwargs['payload'] if 'payload' in kwargs.keys() else None

    def __repr__(self):
        return "%s" % (self.payload)