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
        # not have GPIO functionality on the PWM pins or vice versa). We need
        # two pairs of pins: GPIO (output) pairing with GPIO (input), and PWM
        # (output) pairing with digital interrupt (input). For boards whose
        # pins can have multiple functions, you can just define the first pair
        # and we'll reuse it for both. but if you want to define the two pairs
        # separately, you can.
        try:
            HW_INTERRUPT_PIN = conf.HW_INTERRUPT_PIN
        except AttributeError:
            HW_INTERRUPT_PIN = conf.INPUT_PIN

        try:
            HW_PWM_PIN = conf.HW_PWM_PIN
        except AttributeError:
            HW_PWM_PIN = conf.OUTPUT_PIN
            

        self.hw_pwm_pin = await board.gpio_pin_by_name(HW_PWM_PIN)
        self.hw_interrupt = await board.digital_interrupt_by_name(HW_INTERRUPT_PIN)

        # We also need a software pwm pin and interrupt pin pair to test software pwm.
        self.sw_pwm_pin = await board.gpio_pin_by_name(conf.SW_PWM_PIN)
        self.sw_interrupt = await board.digital_interrupt_by_name(conf.SW_INTERRUPT_PIN)

    async def asyncTearDown(self):
        await self.output_pin.set(False)
        await self.robot.close()

    @parameterized.expand(((True,), (False,)))
    async def test_gpios(self, value):
        await self.output_pin.set(value)
        result = await self.input_pin.get()
        self.assertEqual(result, value)
    
    @parameterized.expand((("hw"), ("sw")))
    async def test_interrupts(self, pwm):
        FREQUENCY = 50 # Hertz
        DURATION = 2 # seconds

        if pwm == "hw":
            pwm_pin = self.hw_pwm_pin
            interrupt = self.hw_interrupt
            error_factor = 0.05
        else:
            pwm_pin = self.sw_pwm_pin
            interrupt = self.sw_interrupt
            error_factor = 0.07

        await pwm_pin.set_pwm_frequency(FREQUENCY)
        await pwm_pin.set_pwm(0.5) # Duty cycle fraction: 0 to 1

        # Sometimes a board has a small delay between when you set the PWM and
        # when the signal starts outputting. To hopefully compensate for this,
        # we'll wait a short while before we start counting cycles.
        await asyncio.sleep(0.5)

        starting_count = await interrupt.value()
        await asyncio.sleep(DURATION)
        await pwm_pin.set(False) # Turn the output off again
        ending_count = await interrupt.value()

        total_count = ending_count - starting_count
        expected_count = FREQUENCY * DURATION
        allowable_error = expected_count * error_factor
        self.assertAlmostEqual(total_count, expected_count, delta=allowable_error)


if __name__ == "__main__":
    unittest.main()
