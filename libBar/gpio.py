#!/usr/bin/python3
"""
Library to ease the usage of General Purpose I/O (GPIO) pins on the BeagleBone
Black. Check the documentation in each function to learn how to use it.
"""
import os.path

# List of all available GPIO on the basic cape
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

    Keyword arguments
    value -- the state to set all the pins, 0 by default for low, 1 for high
    """
    for pin in GPIO:
        writePin(pin, value)


def _enablePin(pin):
    """
    Fool-proof export of GPIO pins

    Keyword arguments
    pin -- an integer which represent the GPIO number
    """
    if pin not in GPIO:
        raise ValueError

    if not os.path.exists("/sys/class/gpio/gpio{}".format(pin)):
        with open("/sys/class/gpio/export", 'w') as file:
            file.write(str(pin))


def _direction(pin, direction='out'):
    """
    Set the direction of a pin, input or output

    Keyword arguments
    pin -- an integer which represent the GPIO number
    direction -- if the pin is an input or output
    """
    _enablePin(pin)

    _ = "/sys/class/gpio/gpio{}/direction".format(pin)
    with open(_, 'r+') as file:
        if file.read() != direction:
            file.write(direction)


def writePin(pin, value=1):
    """
    Set the state of a pin

    Keyword arguments
    pin -- an integer which represent the GPIO number
    value -- the state to set the pin, 0 by default for low, 1 for high
    """
    if value not in [0, 1]:
        raise ValueError
    _direction(pin, 'out')

    _ = "/sys/class/gpio/gpio{}/value".format(pin)
    with open(_, 'w') as file:
        file.write(str(value))


def readPin(pin):
    """
    Read the state of a pin

    Keyword arguments
    pin -- an integer which represent the GPIO number
    """
    _direction(pin, 'in')

    _ = "/sys/class/gpio/gpio{}/value".format(pin)
    with open(_, 'r') as file:
        return file.read()
