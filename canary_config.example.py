from viam.rpc.dial import Credentials


INPUT_PIN = "16"
OUTPUT_PIN = "15"

# Uncomment these if you can't reuse the same two pins for all functionality.
# PWM_PIN = "17"
# INTERRUPT_PIN = "18"

creds = Credentials(
    type="robot-location-secret",
    payload="put-the-secret-here")
address = "address-for-robot.viam.cloud"
