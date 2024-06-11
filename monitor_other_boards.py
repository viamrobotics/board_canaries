#!/usr/bin/env python3
from datetime import datetime
import subprocess

import slack_reporter

#                SSH target,              name
other_boards = (("odroid@odroid",         "odroid-C4"),
                ("orangepi@oliviaorange", "orange pi zero 2"),
                ("viam@viam",             "Up 4000"),
                ("viam@orinnanodevkit2",  "Orin Nano"),
                # The Orin AGX is unable to get on tailscale, and mDNS is not
                # very reliable. but its IP address almost never changes.
                ("viam@10.1.8.37",        "Orin AGX"),
                ("debian@bogglebean",     "Beaglebone AI-64"),
                ("canary@pi5canary",      "rpi5"),
                )


def ensure_board_is_online(ssh_target, name):
    today = datetime.today().strftime("%Y-%m-%d")
    try:
        # This command SSHes into the target machine and counts how many times
        # the canary analysis logfile contains a line with today's date and
        # nothing else. If the analysis has run, there should be exactly 1 of
        # these lines.
        command = f"cat /var/log/canary_tests.log | grep '^{today}$' | wc -l"
        subprocess_command = f"ssh {ssh_target} \"{command}\""
        subprocess_result = subprocess.run(
            subprocess_command, timeout=60, shell=True, capture_output=True)
    except subprocess.TimeoutExpired:
        slack_reporter.report_message(f"Unable to contact {name} board!")
        return
    if (subprocess_result.returncode != 0 or
            subprocess_result.stdout != b"1\n"):
        slack_reporter.report_message(f"Unexpected logs on {name} board!")


if __name__ == "__main__":
    for ssh_target, name in other_boards:
        ensure_board_is_online(ssh_target, name)
