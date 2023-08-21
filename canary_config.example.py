from viam.rpc.dial import Credentials


INPUT_PIN = "16"
OUTPUT_PIN = "15"

creds = Credentials(
    type='robot-location-secret',
    payload='put-the-secret-here')
address = 'address-for-robot.viam.cloud'
