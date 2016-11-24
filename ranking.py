from __future__ import print_function
import plyvel
import msgpack
import pandas as pd
import numpy as np
import sys, yaml

from slack_client import SlackClient
from pprint import pprint
import os.path

def get_members_dict(token):
    if os.path.exists("members.yaml"):
        with open("members.yaml") as f:
            return yaml.load(f)
    sc = SlackClient(token)
    members = sc.users_list()['members']
    member_dict = {}
    for member in members:
        member_dict[member['id']] = member
    with open("members.yaml", "w") as f:
        yaml.dump(member_dict, f)
    return member_dict

def get_dataframe():
    filename = "frame.pickle"

    if os.path.exists(filename):
        return pd.read_pickle(filename)

    setting = yaml.load(open('setting.yaml').read().decode('utf8'))
    token = setting["api_token"][0]

    members_dict = get_members_dict(token)

    db = plyvel.DB("ntt-developers", create_if_missing=False)
    user_text = []
    for k, v in db:#.iterator(prefix=sys.argv[1]):
        obj = msgpack.loads(v)
        if not "text" in obj or not 'user' in obj:
            continue
        user_text.append([members_dict[obj['user']]['name'], obj['text']])
    db.close()
    user_text_table = pd.DataFrame({"user": [d[0] for d in user_text],
                                    "text": [d[1] for d in user_text]})
    user_text_table.to_pickle(filename)
    return user_text_table

user_text_table = get_dataframe()
texts = user_text_table['text']
text = ""
for t in texts:
    text += t + " "
import re

# mention = re.compile('<@[0-9A-Z]{9}?\|[^>]{,20}>')
reaction = re.compile(':[a-z]+?:')
res = reaction.findall(text)
reactions = []
for r in res:
    reactions.append(r)

rea = pd.DataFrame({"reaction": reactions})
print(rea['reaction'].value_counts()[0: 50])
