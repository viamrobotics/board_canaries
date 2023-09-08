#!/usr/bin/env python3

import asyncio
from parameterized import parameterized
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
        board = Board.from_robot(self.robot, "board")
        self.input_pin = await board.gpio_pin_by_name(conf.INPUT_PIN)
        self.output_pin = await board.gpio_pin_by_name(conf.OUTPUT_PIN)

        # Most boards have combination GPIO/PWM/interrupt pins. However, rarely
        # they are separated to different pins (e.g., the Beaglebone AI-64 does
        # not have GPIO functionality on the PWM pins or vice versa). If you
        # define them separately, define these extra variables in the config.
        # Otherwise, we'll reuse the same inputs and outputs.
        try:
            INTERRUPT_PIN = conf.INTERRUPT_PIN
        except AttributeError:
            INTERRUPT_PIN = conf.INPUT_PIN

        try:
            PWM_PIN = conf.PWM_PIN
        except AttributeError:
            PWM_PIN = conf.OUTPUT_PIN

        self.pwm_pin = await board.gpio_pin_by_name(PWM_PIN)
        self.interrupt = await board.digital_interrupt_by_name(INPUT_PIN)

    async def asyncTearDown(self):
        await self.output_pin.set(False)
        await self.robot.close()

    @parameterized.expand(((True,), (False,)))
    async def test_gpios(self, value):
        await self.output_pin.set(value)
        result = await self.input_pin.get()
        self.assertEqual(result, value)

    async def test_interrupts(self):
        FREQUENCY = 50 # Hertz
        DURATION = 2 # seconds
        ERROR_FACTOR = 0.05

        await self.pwm_pin.set(False) # Turn the output off
        starting_count = await self.interrupt.value()

        await self.pwm_pin.set_pwm_frequency(FREQUENCY)
        await self.pwm_pin.set_pwm(0.5) # Duty cycle fraction: 0 to 1
        await asyncio.sleep(DURATION)
        await self.pwm_pin.set(False) # Turn the output off again

        ending_count = await self.interrupt.value()
        total_count = ending_count - starting_count
        expected_count = FREQUENCY * DURATION
        allowable_error = expected_count * ERROR_FACTOR
        self.assertAlmostEqual(total_count, expected_count, delta=allowable_error)


if __name__ == "__main__":
    unittest.main()
