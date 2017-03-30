#!/usr/bin/python3
"""
Library to ease the usage of General Purpose I/O (GPIO) pins on the BeagleBone
Black. Check the documentation in each function to learn how to use it.
"""
import os.path

GPIO = [
    20, 26, 27, 44,
    45, 46, 47, 48,
    49, 60, 61, 65,
    66, 67, 68, 69,
    112, 115, 117,
]


def all(value=0):
    """
    Set a value for all or remove all floating led
    """
    for pin in GPIO:
        writePin(pin, value)


def _enablePin(pin):
    """
    Fool-proof export of GPIO pins
    """
    if pin not in GPIO:
        raise ValueError

    if not os.path.exists("/sys/class/gpio/gpio{}".format(pin)):
        with open("/sys/class/gpio/export", 'w') as file:
            file.write(str(pin))


def _direction(pin, direction='out'):
    """
    Set pin direction
    """
    _enablePin(pin)

    _ = "/sys/class/gpio/gpio{}/direction".format(pin)
    with open(_, 'r+') as file:
        if file.read() != direction:
            file.write(direction)


def writePin(pin, value=1):
    """
    Write pin
    """
    if value not in [0, 1]:
        raise ValueError
    _direction(pin, 'out')

    _ = "/sys/class/gpio/gpio{}/value".format(pin)
    with open(_, 'w') as file:
        file.write(str(value))


def readPin(pin):
    """
    Read pin
    """
    _direction(pin, 'in')

    _ = "/sys/class/gpio/gpio{}/value".format(pin)
    with open(_, 'r') as file:
        return file.read()
