#!/usr/bin/env python3
import fileinput # For accessing stdin

# TODO: remember to add slack_sdk to requirements.txt when that file exists
import slack_sdk

import slack_reporter_config as config


def report_errors(output):
    client = slack_sdk.WebClient(token=config.auth_token)
    text = "\n".join(["The canary tests on the {} board have failed. ".format(
                          config.board_name),
                      "Recent output is: ```"] +
                      output +
                      ["```"])
    result = client.chat_postMessage(
            channel=config.channel, text=text)
    # If we get a result, things worked. Failure raises exceptions instead.
    # Currently, we ignore any errors. How do we report that we're unable to
    # report stuff!?


def tests_succeeded(contents):
    return contents[-2:] == ["Success!", "done running tests!"]



if __name__ == "__main__":
    contents = [line for line in fileinput.input()]
    if not tests_succeeded(contents):
        report_errors(contents)
