#!/usr/bin/env python3
import asyncio
import traceback

from viam.robot.client import RobotClient

import monitor_config
import slack_reporter
import stack_printing  # Set up the ability to print stack traces on SIGUSR1


async def main():
    # Monkey-patch the board name to indicate on Slack that it's acting as the
    # canary monitor right now, not just a canary.
    slack_reporter.config.board_name += " (canary monitor)"

    for name, address, creds in monitor_config.all_boards:
        print(f"now checking the {name} board...")
        try:
            robot = await RobotClient.at_address(address, creds)
            await robot.close()
        except:
            # If there's a problem connecting to the board, it's possible
            # we'll want to see details later. Print them here, so they'll be
            # in the logs later.
            print(f"Cannot connect to the {name} board!")
            traceback.print_exc()
            try:
                slack_reporter.report_message(
                    f"Cannot connect to the {name} board!")
            except:
                # If we're unable to connect to Slack, it's possible our
                # network connection is down. Write to our logs again.
                print("Unable to report to Slack!?")
                traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
