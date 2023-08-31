#!/usr/bin/env python3

# TODO: remember to add slack_sdk to requirements.txt when that file exists

import slack_sdk

import slack_reporter_config as config

def report_errors(board_name, output):
    client = slack_sdk.WebClient(token=config.auth_token)
    text = "\n".join(["The canary tests on the {} board have failed. ".format(
                          board_name),
                      "Recent output is: ```"] +
                      output +
                      ["```"])
    result = client.chat_postMessage(
            channel=config.channel, text=text)
    # If we get a result, things worked. Failure raises exceptions instead.

vals = ["Here's the first line", "Here's the second line. It's longer"]
board_name = "fake"
report_errors(board_name, vals)
