# -*- coding: utf-8 -*-
from __future__ import print_function
import plyvel
import urllib
import urllib2
import logging
import yaml
import json
import percache
import msgpack

# logger
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

data = yaml.load(open('setting.yaml').read().decode('utf8'))
token = data["api_token"]

cache = percache.Cache("slack-cache")
@cache
def request(path, params = {}):
    url = "https://slack.com/api/" + path + "?";
    params["token"] = token
    return json.loads(
        urllib2.urlopen(url + "&" + urllib.urlencode(params)).read()
    )
def users_list():
    return request('users.list')
def team_info():
    return request('team.info')
def channels_list():
    return request('channels.list')['channels']
def get_log(channel_id, since):
    options = {
        "oldest": since,
        "count": 1000,
        "channel": channel_id,
        "inclusive": 0
    }
    return request('channels.history', options)


def main():
    team = team_info()
    if not team["ok"]:
        print("cannot get Team information")
        return
    team_name = team["team"]["name"]
    logdb = plyvel.DB(team_name, create_if_missing=True)

    cl = channels_list()
    channels = {}
    for c in cl:
        if not c['is_channel']:
            continue
        channels[c['name']] = c

    write_count = 0
    for name in channels.keys():
        channeldb = logdb.prefixed_db(name + b"-")

        # get latest timestamp
        try:
            c_iter = channeldb.iterator()
            key = None
            for k, v in c_iter:
                key = k
            if key == None:
                raise StopIteration
            # logger.info("{n} latest {k}".format(n=name, k=key))
            since = key
        except StopIteration as e:
            # if latest message doesn't exist, get from first
            since = "1"

        # get all log from timestamp
        logs = []
        while True:
            log = get_log(channels[name]['id'], since)
            #print("{s}:{l}".format(s=since, l=log))
            msgs = filter(lambda x: str(x["ts"]) != str(since), log["messages"])
            logs.extend(msgs)
            if len(msgs) == 0:
                break
            logger.info("{n} since {s} got {t}".format(n=name, s=since, t=len(msgs)))
            logs.sort(key=lambda x: float(x["ts"]), reverse=True)
            # print("{n} latest is {s}".format(n=name, s=logs[0]["ts"]))
            if log["has_more"]:
                since = logs[0]["ts"]
            else:
                break

        # save message logs
        wb = channeldb.write_batch(sync=True)
        for mes in logs:
            #logger.info("{k}: {v}".format(k=str(mes["ts"]),v=json.dumps(mes)))
            wb.put(str(mes["ts"]),
                   msgpack.dumps(mes))
        write_count += len(logs)
        #logger.info('wrote {c} messages for {n}'.format(c=len(logs), n=name))
        wb.write()

    logdb.close()
    logger.info('{c} messages saved in total {n} channels'.format(c=write_count, n=len(channels)))

if __name__ == "__main__":
    main()
