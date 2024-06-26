from viam.robot.client import RobotClient

# This is a list of (name, address, credentials) tuples.
all_boards = (
    ("first_board", "first-board.12345.viam.cloud",
         RobotClient.Options.with_api_key(
             api_key="67890",
             api_key_id="abcdef")
    ),
    ("second_board", "second-board.54321.viam.cloud",
         RobotClient.Options.with_api_key(
             api_key="09876",
             api_key_id="fedcba")
    ),
)
