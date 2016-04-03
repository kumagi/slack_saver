# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import absolute_import

import plyvel
import msgpack

class SlackStorage(object):
    def __init__(self, filename):
        self.db = plyvel.DB(filename, create_if_missing=True)

    def get_latest_timestamp(self, name):
        channeldb = self.db.prefixed_db(str(name + u"-"))
        try:
            c_iter = channeldb.iterator()
            key = None
            for k, _ in c_iter:
                key = k
            if key == None:
                raise StopIteration
            return key
        except StopIteration as e:
            # if latest message doesn't exist, get from first
            return "1"

    def save(self, name, msgs):
        channeldb = self.db.prefixed_db(str(name + "-"))
        wb = channeldb.write_batch(sync=True)
        for msg in msgs:
            wb.put(str(msg["ts"]), msgpack.dumps(msg))
        wb.write()
        return len(msgs)

    def close(self):
        self.db.close()
