from viam.robot.client import RobotClient


INPUT_PIN = "16"
OUTPUT_PIN = "15"

# Uncomment these if you can't reuse the INPUT_PIN and OUTPUT_PIN for both hw pwm and gpio functionality.
# HW_PWM_PIN = "17"
# HW_INTERRUPT_PIN = "18"

SW_PWM_PIN = "20"
SW_INTERRUPT_PIN = "21"

creds = RobotClient.Options.with_api_key(
    api_key="secret-api-key",
    api_key_id="put-the-secret-id-here")
address = "address-for-robot.viam.cloud"

# Most canaries should leave this as None, but we need at least one to set it to whichever board is
# making sure all the others are online. When set, it should be a pair of (address, creds) to
# connect to that robot.
board_monitor = None
