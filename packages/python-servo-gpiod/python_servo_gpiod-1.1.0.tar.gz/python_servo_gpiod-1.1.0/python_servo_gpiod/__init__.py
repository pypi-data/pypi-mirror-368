"""
Python Servo Control Library using gpiod

A comprehensive Python implementation for controlling servo motors using the gpiod
library on Raspberry Pi and other Linux systems with GPIO support.

Author: Svndsn
License: MIT
"""

from .servo import Servo, ServoError

__version__ = "1.1.0"
__author__ = "Svndsn"
__email__ = "simon.egeris.svendsen@gmail.com"
__license__ = "MIT"

__all__ = ["Servo", "ServoError"]
