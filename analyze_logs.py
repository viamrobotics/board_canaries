#!/usr/bin/env python3
import fileinput # For accessing stdin

# TODO: remember to add slack_sdk to requirements.txt when that file exists
import slack_sdk

import slack_reporter_config as config


def report_no_output():
    client = slack_sdk.WebClient(token=config.auth_token)
    text = ("The canary tests on the {} board had no recent output!"
            .format(config.board_name))
    result = client.chat_postMessage(channel=config.channel, text=text)
    # If we get a result, things worked. Failure raises exceptions instead.
    # Currently, we ignore any errors. How do we report that we're unable to
    # report stuff!?


def report_errors(output):
    client = slack_sdk.WebClient(token=config.auth_token)
    text = ("The canary tests on the {} board have failed. Recent output is:"
        .format(config.board_name))
    file_contents = "".join(output).strip() # Remove the final trailing newline

    result = client.files_upload_v2(
        channel=config.channel, content=file_contents, initial_comment=text)
    # Again, if things fail we'll raise an exception here, but there is no
    # obvious resolution for that.


def tests_succeeded(contents):
    return contents[-2:] == ["Success!\n", "done running tests!\n"]


if __name__ == "__main__":
    contents = [line for line in fileinput.input()]
    if not tests_succeeded(contents):
        if contents == []:
            report_no_output()
        else:
            report_errors(contents)
