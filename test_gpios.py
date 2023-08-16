#!/usr/bin/env python3

import asyncio
import time

from viam.components.board import Board
from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions

INPUT_PIN = "16"
OUTPUT_PIN = "15"


async def connect():
    creds = Credentials(
        type='robot-location-secret',
        payload='12wedufyzcbqtj3wv93f75tgdnpq6fugdrogmmcj8eh65sf3')
    opts = RobotClient.Options(
        refresh_interval=0,
        dial_options=DialOptions(credentials=creds)
    )
    return await RobotClient.at_address('canary-orin-nano-main.7aaz8vjc1j.viam.cloud', opts)


async def close_robot(robot: RobotClient):
    if robot:
        await robot.close()


async def test_gpios(input_pin, output_pin):
    for value in (True, False):
        await output_pin.set(value)
        result = await input_pin.get()
        assert(result == value) # TODO: do this better.


async def test_interrupts(interrupt, output_pin):
    FREQUENCY = 50 # Hertz
    DURATION = 2 # seconds
    ERROR_FACTOR = 0.05

    await output_pin.set(False) # Turn the output off
    starting_count = await interrupt.value()

    await output_pin.set_pwm_frequency(FREQUENCY)
    await output_pin.set_pwm(0.5) # Duty cycle fraction: 0 to 1
    time.sleep(DURATION)
    await output_pin.set(False) # Turn the output off

    ending_count = await interrupt.value()
    total_count = ending_count - starting_count
    expected_count = FREQUENCY * DURATION

    assert(abs(total_count - expected_count) / expected_count <= ERROR_FACTOR)


async def reset_pins(input_pin, output_pin):
    await output_pin.set(False)


async def test_everything(robot):
    board = Board.from_robot(robot, "board")
    input_pin = await board.gpio_pin_by_name(INPUT_PIN)
    interrupt = await board.digital_interrupt_by_name(INPUT_PIN)
    output_pin = await board.gpio_pin_by_name(OUTPUT_PIN)

    await test_gpios(input_pin, output_pin)
    await reset_pins(input_pin, output_pin)
    await test_interrupts(interrupt, output_pin)
    await reset_pins(input_pin, output_pin)


async def main():
    try:
        robot = await connect()
        await test_everything(robot)
        await close_robot(robot)
    finally: # TODO: watch for exceptions
        pass
        #await log_exception()

if __name__ == "__main__":
    asyncio.run(main())
