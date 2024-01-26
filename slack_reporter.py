#!/usr/bin/env python3
import slack_sdk

import slack_reporter_config as config


# Re-export this value
board_name = config.board_name

def report_message(message):
    client = slack_sdk.WebClient(token=config.auth_token)
    result = client.chat_postMessage(channel=config.channel_id, text=message)
    # If we get a result, things worked. Failure raises exceptions instead.
    # Currently, we ignore any errors. The cron job that runs this script
    # will write all our output (including a stack trace from an uncaught
    # exception) to /tmp/canary_analysis.log, but there's no obvious way to
    # tell a human to go look at that. How do we report that we're unable to
    # report stuff!?
    return result  # Maybe whoever called us knows what to do with this.


def report_file(filename, contents, comment):
    client = slack_sdk.WebClient(token=config.auth_token)
    result = client.files_upload_v2(
        channel=config.channel_id, content=file_contents, snippet_type="text",
        filename="canary_tests.log", initial_comment=text)
    # Again, if things fail we'll raise an exception here, but there is no
    # obvious resolution for that.
    return result

