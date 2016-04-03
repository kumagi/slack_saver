# -*- coding: utf-8 -*-
from __future__ import print_function
import json
import urllib
import urllib2

# for debug use
# import percache
# cache = percache.Cache("slack-cache")

class SlackError(Exception):
    pass

class SlackClient(object):
    """
    Slack API wrapper
    """
    def __init__(self, token):
        """
        @parameter: token:str slack token which looks like xoxp-
        """
        self.token = token
        self.channels = None

    #@cache
    def _request(self, path, params = {}):
        url = "https://slack.com/api/" + path + "?";
        params["token"] = self.token
        return json.loads(
            urllib2.urlopen(url + "&" + urllib.urlencode(params)).read()
        )

    def users_list(self):
        return self._request('users.list')

    def team_info(self):
        info = self._request('team.info')
        if not info.has_key("ok") or (info["ok"] == False):
            raise SlackError()
        return info["team"]

    def channels_list(self):
        if self.channels == None:
            ret = self._request('channels.list')
            if not ret.has_key("ok") or ret["ok"] == False:
                raise SlackError()
            self.channels = ret["channels"]
            self.channel_map = {}
            for c in ret["channels"]:
                self.channel_map[c["name"]] = c
        return self.channels

    def _get_log(self, channel_id, since):
        messages = []
        options = {
            "oldest": since,
            "count": 1000,
            "channel": channel_id,
            "inclusive": 0
        }
        ret = self._request('channels.history', options)
        if not ret.has_key("ok") or ret["ok"] == False:
            raise SlackError()
        return ret

    def get_messages(self, name, since):
        messages = []
        while True:
            log = self._get_log(self.channel_map[name]['id'], since)
            msgs = filter(lambda x: str(x["ts"]) != str(since), log["messages"])
            messages.extend(msgs)
            if len(messages) == 0:
                return messages
            messages.sort(key=lambda x: float(x["ts"]), reverse=True)
            if log["has_more"]:
                since = messages[0]["ts"]
            else:
                return messages
