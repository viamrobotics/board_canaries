#!/usr/bin/env python3
import slack_sdk

import slack_reporter_config as config


if __name__ == "__main__":
    client = slack_sdk.WebClient(token=config.auth_token)
    text = ("Canary tests on the {} board should be able to report to Slack!"
            .format(config.board_name))
    result = client.chat_postMessage(channel=config.channel_id, text=text)
