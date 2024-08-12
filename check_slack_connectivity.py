#!/usr/bin/env python3
try:
    import slack_reporter
except:
    print("\n\n Unable to import Slack stuff! Did you remember to run "
          "`source venv/bin/activate`?\n\n")
    raise


# This is simultaneously:
# 1) a way to demonstrate that you put the correct secrets into
#     slack_reporter_config.py, and
# 2) an announcement to the Slack channel that there's a new board running
#     canary tests.
if __name__ == "__main__":
    text = "the canary tests should be able to report to Slack!"
    result = slack_reporter.report_message(text)
