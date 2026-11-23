#!/usr/bin/env python3
# gpio_volume.py - cabinet volume buttons -> ALSA "PCM" mixer
# Vol+ GPIO26 (pin 37)   Vol- GPIO19 (pin 35)   GND pin 39
from gpiozero import Button
from signal import pause
import subprocess

up   = Button(26, pull_up=True, bounce_time=0.05)
down = Button(19, pull_up=True, bounce_time=0.05, hold_time=2)
held = False

def mixer(value):
    subprocess.run(["amixer", "-q", "sset", "PCM", value])

def down_held():                # hold Vol- 2 s -> jump to 100%
    global held; held = True; mixer("100%")

def down_released():            # quick tap     -> down 5%
    global held
    if not held: mixer("5%-")
    held = False

up.when_pressed    = lambda: mixer("5%+")
down.when_held     = down_held
down.when_released = down_released
pause()
