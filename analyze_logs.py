#!/usr/bin/env python3
import fileinput # For accessing stdin

import slack_reporter
import stack_printing  # Set up the ability to print stack traces on SIGUSR1


if __name__ == "__main__":
    # Most lines from stdin end in a newline, but maybe not the last one. To
    # give a more uniform interface, we strip out all trailing whitespace here,
    # and maybe add newlines back later.
    contents = [line.rstrip() for line in fileinput.input()]
    # In May 2024, we began logging extra information about interrupt ticks,
    # to better diagnose a PWM issue on the Orin and Orin Nano. Ignore that
    # output here.
    filtered_contents = [line for line in contents
                         if not line.startswith("(") and
                             line != "data from tick stream:"]

    expected_contents = [
        "OK",
        "+ echo 'done running tests!'",
        "done running tests!",
        "+ popd",
        "+ exit 0",
        ]
    if filtered_contents[-len(expected_contents):] != expected_contents:
        if contents == [] or contents == [""]:
            slack_reporter.report_message(
                "the canary tests had no recent output!")
        else:
            text = "the canary tests have failed. Recent output is:"
            file_contents = "\n".join(contents)
            slack_reporter.report_file("canary_tests.log", file_contents, text)
