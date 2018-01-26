class BlePayload(object):
    def __init__(self, *args, **kwargs):
        self.itemDict = {}
        self._payload = kwargs['payload'] if 'payload' in kwargs.keys() else None
        if self._payload is not None:
            self._parse_raw_payload()

    def _add_item(self, key, value):
            self.itemDict[str(key)] = value

    def get_items(self):
        return self.itemDict

    def _parse_raw_payload(self):
        '''list of tuples [(tag, description, value)]'''
        if self._payload is not None:
            for _item in self._payload:
                self._add_item(_item[1], _item[2])

    def __repr__(self):
        return '%s' % str([(_item, self.itemDict[_item]) for _item in self.itemDict.keys()])


