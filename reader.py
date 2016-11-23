from __future__ import print_function
import plyvel
import msgpack
from time import time
import sys

db = plyvel.DB("ntt-developers", create_if_missing=False)
for k, v in db.iterator(prefix=sys.argv[1]):
    obj = msgpack.loads(v)
    if not "text" in obj:
        continue
    print("{t}".format(t=obj["text"]))
db.close()
