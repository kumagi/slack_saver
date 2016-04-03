# Slack Saver

Saving Slack logs into LevelDB

# Usage

1. Copy setting file.

```
$ cp setting_example.yaml setting.yaml
```

2. Get slack-token which begins with `xoxp-`.
https://api.slack.com/docs/oauth-test-tokens

3. Modify `setting.yaml` with your own slack-token.

```
$ vim setting.yaml
```

4. Run script

```
$ python main.py
```

5. You got it!
