# board_canaries
Code to run on every board, to run canary tests

## To set up a new board:
- Create a new robot, likely in the `viam-hardware-testing` org, in the "Board Canaries" location.
- Add a board to that robot, whose type matches your physical hardware.
- in the `Auth/Network` tab of the config set the bind address to port 9090.
- Install Viam on the physical board, per the Setup tab in the robot you just created. **However,** put the config file in `/etc/viam-canary.json` instead of just `/etc/viam.json`.
- Jump together 2 pins on your board. Ideally, one of them (the "output" pin) will also have hardware PWM enabled.
  - If you have a board whose GPIO pins cannot also do hardware PWM but you want to test hardware PWM separately, jump together a second set of pins. One set will be to test GPIO input and output, and the other will test hardware PWM output and digital interrupt input.
  - Also jump together 2 more gpio pins to test software PWM.
- Clone this repo onto the board.
- Run `sudo ./install.sh`
- Follow the instructions printed at the end of that script:
  - Copy `canary_config.example.py` into `canary_config.py`. Edit it to use the right location and secret, and the pins on the board you jumped together in the earlier step.
  - Copy `slack_reporter_config.example.py` into `slack_reporter_config.py`. Edit it so it can report to the correct Slack channel. To check that you set it up right, try running `./check_slack_connectivity.py`: if you did it right, you'll get a message in that Slack channel.
