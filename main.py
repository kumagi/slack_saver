# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import absolute_import

import urllib
import urllib2
import logging
import yaml
import json

import msgpack
from slack_client import SlackClient
from slack_storage import SlackStorage


def main():
    # logger
    logging.basicConfig()
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # read settings
    setting = yaml.load(open('setting.yaml').read().decode('utf8'))
    token = setting["api_token"]

    sc = SlackClient(token)

    team = sc.team_info()
    db = SlackStorage(team["name"])

    cl = sc.channels_list()
    channels = [c['name'] for c in cl]

    wrote_count = 0
    for name in channels:
        # get the latest timestamp
        since = db.get_latest_timestamp(name)

        # get all messages from timestamp
        messages = sc.get_messages(name, since)
        if 0 < len(messages):
            logger.info("#{n} since {s} got {t} messages".format(n=name,
                                                                s=since,
                                                                t=len(messages)))
        else:
            continue

        # save message logs
        db.save(name, messages)
        logger.info('wrote {c} messages for #{n}'.format(c=len(messages),
                                                        n=name))

    db.close()
    logger.info('{c} messages saved in total {n} channels'.format(c=wrote_count,
                                                                  n=len(channels)))

if __name__ == "__main__":
    main()
