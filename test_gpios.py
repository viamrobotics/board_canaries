#!/usr/bin/env python3

import asyncio
from parameterized import parameterized
import subprocess
import time
import unittest

from viam.components.board import Board
from viam.robot.client import RobotClient
from viam.rpc.dial import DialOptions

import canary_config as conf
import slack_reporter


class GpioTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        opts = RobotClient.Options(
            refresh_interval=0,
            dial_options=DialOptions(credentials=conf.creds)
        )

        try:
            self.robot = await RobotClient.at_address(conf.address, opts)
        except ConnectionError:
            # There's some race condition in the Python SDK that causes
            # reconnection to fail sometimes. See if we can figure out what
            # the RDK server is doing that causes this trouble. Send a SIGUSR1
            # (signal 10), which should log stack traces from all goroutines.
            # The tricky part here is that there might be 2 RDK servers
            # running: the "normal" one on port 8080 and the board canary one
            # on port 9090. We want to only send the signal to the latter.
            subprocess.run(["pkill", "-10", "-f", "viam-canary.json"],
                           shell=True)
            slack_reporter.report_message(
                "connection error during canary tests. Retrying...")
            time.sleep(5)
            self.robot = await RobotClient.at_address(conf.address, opts)

        self.board = Board.from_robot(self.robot, "board")
        self.input_pin = await self.board.gpio_pin_by_name(conf.INPUT_PIN)
        self.output_pin = await self.board.gpio_pin_by_name(conf.OUTPUT_PIN)

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

        self.hw_pwm_pin = await self.board.gpio_pin_by_name(HW_PWM_PIN)
        self.hw_interrupt = await self.board.digital_interrupt_by_name(HW_INTERRUPT_PIN)

        # We also need a software pwm pin and interrupt pin pair to test software pwm.
        self.sw_pwm_pin = await self.board.gpio_pin_by_name(conf.SW_PWM_PIN)
        self.sw_interrupt = await self.board.digital_interrupt_by_name(conf.SW_INTERRUPT_PIN)

    async def asyncTearDown(self):
        await self.output_pin.set(False)
        await self.robot.close()

    @parameterized.expand(((True,), (False,)))
    async def test_gpios(self, value):
        await self.output_pin.set(value)
        result = await self.input_pin.get()
        self.assertEqual(result, value)

    @parameterized.expand((("hw",), ("sw",)))
    async def test_interrupts_and_pwm(self, pwm):
        FREQUENCY = 40 # Hertz
        DURATION = 2 # seconds

        if pwm == "hw":
            pwm_pin = self.hw_pwm_pin
            interrupt = self.hw_interrupt
            error_factor = 0.05
        else:
            pwm_pin = self.sw_pwm_pin
            interrupt = self.sw_interrupt
            error_factor = 0.10  # Software PWM can get really inaccurate

        # In order to diagnose a flaky test, we're going to record all tick-related data.
        should_stop = asyncio.Event()
        ticks = []
        tick_stream = await self.board.stream_ticks([interrupt])
        counter_task = asyncio.create_task(self.record_tick_data(tick_stream, ticks, should_stop))

        await pwm_pin.set_pwm_frequency(FREQUENCY)
        await pwm_pin.set_pwm(0.5) # Duty cycle fraction: 0 to 1

        # Sometimes a board has a small delay between when you set the PWM and
        # when the signal starts outputting. To hopefully compensate for this,
        # we'll wait a short while before we start counting cycles.
        await asyncio.sleep(0.5)

        starting_count = await interrupt.value()
        await asyncio.sleep(DURATION)
        should_stop.set()
        await counter_task
        await pwm_pin.set(False) # Turn the output off again

        print("data from tick stream:")
        for tick in ticks:
            print(tick)

        ending_count = await interrupt.value()

        total_count = ending_count - starting_count
        expected_count = FREQUENCY * DURATION
        allowable_error = expected_count * error_factor
        self.assertAlmostEqual(total_count, expected_count, delta=allowable_error)

    @staticmethod
    async def record_tick_data(tick_stream, data, should_stop):
        async for tick in tick_stream:
            data.append((tick.time, tick.high, tick.pin_name))
            if should_stop.is_set():
                return


if __name__ == "__main__":
    unittest.main()
