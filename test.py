#!/usr/bin/python3.5

from expanduino.transport.i2c import ExpanduinoI2C
from expanduino.subdevice import Subdevice
from expanduino.classes.meta import MetaSubdevice
import time
import asyncio

expanduino = ExpanduinoI2C(bus_num=1, i2c_addr=0x56, interrupt_pin=7)

task = asyncio.ensure_future(expanduino.attach())


while True:
  try:
    asyncio.get_event_loop().run_until_complete(task)
    break
  except KeyboardInterrupt:
    print("KeyboardInterrupt, exiting...")
    task.cancel()
