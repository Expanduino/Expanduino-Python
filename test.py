#!/usr/bin/python3.5

from expanduino.transport.i2c import ExpanduinoI2C
from expanduino.subdevice import Subdevice
from expanduino.classes.meta import MetaSubdevice
import time
import asyncio
import signal
loop = asyncio.get_event_loop()


expanduino = ExpanduinoI2C(bus_num=1, i2c_addr=0x56, interrupt_pin=7)

task = asyncio.ensure_future(expanduino.attach())


def quit(*args):
  print("Exiting...")
  task.cancel()
loop.add_signal_handler(signal.SIGINT, quit)
loop.add_signal_handler(signal.SIGTERM, quit)

try:
  loop.run_until_complete(task)
finally:
  loop.close()