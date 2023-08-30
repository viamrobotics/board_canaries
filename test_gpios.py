#!/usr/bin/env python3

import asyncio
import unittest

from viam.components.board import Board
from viam.robot.client import RobotClient
from viam.rpc.dial import DialOptions

import canary_config as conf


class GpioTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        opts = RobotClient.Options(
            refresh_interval=0,
            dial_options=DialOptions(credentials=conf.creds)
        )
        self.robot = await RobotClient.at_address(conf.address, opts)

    async def asyncTearDown(self):
        await output_pin.set(False)
        await self.robot.close()


async def test_gpios(input_pin, output_pin):
    for value in (True, False):
        print("Testing GPIO pin going {}...".format("high" if value else "low"))
        await output_pin.set(value)
        result = await input_pin.get()
        assert(result == value) # TODO: do this better.


async def test_interrupts(interrupt, output_pin):
    print("Testing interrupts...")
    FREQUENCY = 50 # Hertz
    DURATION = 2 # seconds
    ERROR_FACTOR = 0.05

    await output_pin.set(False) # Turn the output off
    starting_count = await interrupt.value()

    await output_pin.set_pwm_frequency(FREQUENCY)
    await output_pin.set_pwm(0.5) # Duty cycle fraction: 0 to 1
    await asyncio.sleep(DURATION)
    await output_pin.set(False) # Turn the output off again

    ending_count = await interrupt.value()
    total_count = ending_count - starting_count
    expected_count = FREQUENCY * DURATION

    assert(abs(total_count - expected_count) / expected_count <= ERROR_FACTOR)


async def test_everything(robot):
    board = Board.from_robot(robot, "board")
    input_pin = await board.gpio_pin_by_name(conf.INPUT_PIN)
    interrupt = await board.digital_interrupt_by_name(conf.INPUT_PIN)
    output_pin = await board.gpio_pin_by_name(conf.OUTPUT_PIN)

    await test_gpios(input_pin, output_pin)
    await reset_pins(input_pin, output_pin)
    await test_interrupts(interrupt, output_pin)
    await reset_pins(input_pin, output_pin)
    print("Success!")


async def main():
    try:
        robot = await connect()
        await test_everything(robot)
        await close_robot(robot)
    finally: # TODO: watch for exceptions
        pass

if __name__ == "__main__":
    asyncio.run(main())
