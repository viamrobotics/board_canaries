#!/usr/bin/env python3
import slack_reporter


# This is simultaneously:
# 1) a way to demonstrate that you put the correct secrets into
#     slack_reporter_config.py, and
# 2) an announcement to the Slack channel that there's a new board running
#     canary tests.
if __name__ == "__main__":
    client = slack_sdk.WebClient(token=config.auth_token)
    text = (f"Canary tests on the {slack_reporter.board_name} board should " +
             "be able to report to Slack!")
    result = client.chat_postMessage(channel=config.channel_id, text=text)
