#!/usr/bin/python3

from expanduino.transport.i2c import ExpanduinoI2C
from expanduino.subdevice import Subdevice
from expanduino.classes.meta import MetaSubdevice
import time
from sched import scheduler
root = ExpanduinoI2C(1, 0x56)

sched = scheduler(time.time, time.sleep)
root.demo(sched)
sched.run()