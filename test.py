#!/usr/bin/python3.5

from expanduino.transport.i2c import ExpanduinoI2C
from expanduino.subdevice import Subdevice
from expanduino.classes.meta import MetaSubdevice
import time
import asyncio

loop = asyncio.get_event_loop()

expanduino = ExpanduinoI2C(bus_num=1, i2c_addr=0x56, interrupt_pin=7)
expanduino.run(loop, True)

try:
  loop.run_forever()
except KeyboardInterrupt:
  pass
