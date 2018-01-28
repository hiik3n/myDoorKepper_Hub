class IOMessage(object):
    messageCode = "IO_MSG"
    SHT_MESSAGE = 'SHT'

    def __init__(self, *args, **kwargs):
        self.type = kwargs['type'] if 'type' in kwargs.keys() else None
        self.payload = kwargs['payload'] if 'payload' in kwargs.keys() else None
        self.ts = kwargs['ts'] if 'ts' in kwargs.keys() else None
        self.sender = kwargs['sender'] if 'sender' in kwargs.keys() else None
        self.recipient = kwargs['recipient'] if 'recipient' in kwargs.keys() else None

    def __repr__(self):
        return "%s,%s,%s,%s,%s" % (self.sender, self.recipient, self.type, self.payload, self.ts)
