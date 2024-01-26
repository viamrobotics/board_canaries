#!/usr/bin/env python3
import fileinput # For accessing stdin

import slack_reporter


def report_no_output():
    slack_reporter.report_message("the canary tests had no recent output!")


def report_errors(output):
    text = "the canary tests have failed. Recent output is:"
    file_contents = "\n".join(output)
    slack_reporter.report_file("canary_tests.log", file_contents, text)


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
