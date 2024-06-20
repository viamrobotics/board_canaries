#!/usr/bin/env python3
from datetime import datetime
import subprocess

import slack_reporter

#               SSH target               name
all_boards = (("odroid@odroid",         "odroid-C4"),
              ("orangepi@oliviaorange", "orange pi 02"),
              ("viam@viam",             "Up 4000"),
              ("viam@orinnanodevkit2",  "Orin Nano"),
              # The Orin AGX is unable to get on tailscale, and mDNS is not
              # very reliable. but its IP address (almost?) never changes.
              ("viam@10.1.8.37",        "Orin AGX"),
              ("debian@bogglebean",     "Beaglebone AI-64"),
              ("canary@pi5canary",      "rpi5"),
              )


def ensure_board_is_online(ssh_target, name):
    print(f"now checking the {name} board...")
    today = datetime.today().strftime("%Y-%m-%d")
    # This command SSHes into the target machine and counts how many times the
    # canary analysis logfile contains a line with today's date and nothing
    # else. If the analysis has run, there should be exactly 1 of these lines.
    command = f"cat /var/log/canary_tests.log | grep '^{today}$' | wc -l"
    ssh_command = f"ssh -i board_canary.priv '{ssh_target}' \"{command}\""
    try:
        subprocess_result = subprocess.run(
            ssh_command, timeout=60, shell=True, capture_output=True)
    except subprocess.TimeoutExpired:
        slack_reporter.report_message(f"Cannot contact the {name} board!")
        return
    if subprocess_result.returncode != 0:
        slack_reporter.report_message(f"Cannot read from the {name} board!")
        return
    if subprocess_result.stdout == b"0\n":
        slack_reporter.report_message(
            f"The {name} board did not analyze its tests!")
        return
    # Otherwise, we're able to connect to the board and it has run its tests at
    # least once. Call that a win.


if __name__ == "__main__":
    # Monkey-patch the board name to indicate on Slack that it's acting as the
    # canary monitor right now, not just a canary.
    slack_reporter.config.board_name += " (canary monitor)"

    for ssh_target, name in all_boards:
        ensure_board_is_online(ssh_target, name)
