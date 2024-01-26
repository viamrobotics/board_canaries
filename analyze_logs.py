#!/usr/bin/env python3
import fileinput # For accessing stdin

import slack_reporter


if __name__ == "__main__":
    # Most lines from stdin end in a newline, but maybe not the last one. To
    # give a more uniform interface, we strip out all trailing whitespace here,
    # and maybe add newlines back later.
    contents = [line.rstrip() for line in fileinput.input()]
    expected_contents = [
        "OK",
        "+ echo 'done running tests!'",
        "done running tests!",
        "+ popd",
        "+ exit 0",
        ]
    if contents[-len(expected_contents):] != expected_contents:
        if contents == [] or contents == [""]:
            slack_reporter.report_message(
                "the canary tests had no recent output!")
        else:
            text = "the canary tests have failed. Recent output is:"
            file_contents = "\n".join(contents)
            slack_reporter.report_file("canary_tests.log", file_contents, text)
