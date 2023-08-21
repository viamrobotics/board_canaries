# board_canaries
Code to run on every board, to run canary tests

## To set up a new board:
- Create a new robot, likely in the `viam-hardware-testing` org, in the "Board Canaries" location.
- Add a board to that robot, whose type matches your physical hardware.
- Install Viam on the physical board, per the Setup tab in the robot you just created.
- Jump together 2 pins on your board. Ideally, one of them (the "output" pin) will also have hardware PWM enabled.
- Clone this repo onto the board.
- Copy `canary_config.example.py` into `canary_config.py`. Edit it to use the viam location and secret, and the pins on the board you jumped together.
- More to come soon!
