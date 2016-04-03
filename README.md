# Slack Saver

Saving Slack logs into LevelDB

# Install

In ubuntu/debian

```
$ sudo apt install libleveldb-dev python-dev
$ pip install -r requirements.txt
```

# Usage

### Copy setting file.

```
$ cp setting_example.yaml setting.yaml
```

### Get slack-token which begins with `xoxp-`.
https://api.slack.com/docs/oauth-test-tokens

### Modify `setting.yaml` with your own slack-token.

```
$ vim setting.yaml
```

### Run script

```
$ python main.py
```

### You got it!

# License

MIT License
