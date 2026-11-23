#!/usr/bin/env python3
# power_switch.py  -  cabinet ON/OFF toggle -> safe Pi shutdown
# Switch wired to GPIO3 (pin 5) and GND (pin 6). NEVER pin 4 (5V).
from gpiozero import Button
from signal import pause
from time import sleep
import subprocess

switch = Button(3, pull_up=True)     # closed = ON (pin pulled to GND)

def switch_opened():
    sleep(1)                          # must stay open for 1 second
    if not switch.is_pressed:         # still open? then power down
        subprocess.run(["sudo", "shutdown", "-h", "now"])

switch.when_released = switch_opened
# Bonus: grounding GPIO3 wakes a halted Pi, so flipping
# the toggle back ON boots the cabinet again.
pause()
