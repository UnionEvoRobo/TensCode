import numpy
"""
Holds various constants for use throughout the Objects package.
"""
MOTOR_COUNT         = 3
MOTOR_LOWER_BOUND   = -128
MOTOR_UPPER_BOUND   = 128
DISCRETIZATION      = 1
RUN_TIME            = 1
GREEN_LOWER_BOUND   = numpy.array([35, 100, 100], numpy.uint8)
GREEN_UPPER_BOUND   = numpy.array([45, 255, 255], numpy.uint8)
ORANGE_LOWER_BOUND  = numpy.array([10, 100, 100], numpy.uint8)
ORANGE_UPPER_BOUND  = numpy.array([12, 255, 255], numpy.uint8)
PINK_LOWER_BOUND    = numpy.array([170, 100, 100], numpy.uint8)
PINK_UPPER_BOUND    = numpy.array([180, 255, 255], numpy.uint8)
