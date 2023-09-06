#!/usr/bin/env python3
import fileinput # For accessing stdin

import slack_sdk

import slack_reporter_config as config


def report_no_output():
    client = slack_sdk.WebClient(token=config.auth_token)
    text = (f"The canary tests on the {config.board_name} board had no " +
            "recent output!")
    result = client.chat_postMessage(channel=config.channel_id, text=text)
    # If we get a result, things worked. Failure raises exceptions instead.
    # Currently, we ignore any errors. The cron job that runs this script
    # will write all our output (including a stack trace from an uncaught
    # exception) to /tmp/canary_analysis.log, but there's no obvious way to
    # tell a human to go look at that. How do we report that we're unable to
    # report stuff!?


def report_errors(output):
    client = slack_sdk.WebClient(token=config.auth_token)
    text = (f"The canary tests on the {config.board_name} board have failed. " +
            "Recent output is:")
    file_contents = "\n".join(output)

    result = client.files_upload_v2(
        channel=config.channel_id, content=file_contents, snippet_type="text",
        filename="canary_tests.log", initial_comment=text)
    # Again, if things fail we'll raise an exception here, but there is no
    # obvious resolution for that.


def tests_succeeded(contents):
    ideal_end = [
        "OK",
        "+ echo 'done running tests!'",
        "done running tests!",
        "+ popd",
        "+ exit 0",
        ]
    return contents[-len(ideal_end):] == ideal_end


if __name__ == "__main__":
    # Most lines from stdin end in a newline, but maybe not the last one. To give a more uniform
    # interface, we strip out all trailing whitespace here, and maybe add newlines back later.
    contents = [line.rstrip() for line in fileinput.input()]
    if not tests_succeeded(contents):
        if contents == []:
            report_no_output()
        else:
            report_errors(contents)
