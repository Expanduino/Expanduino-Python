from expanduino.expanduino import Expanduino
import smbus
import os
import time
from retry import retry
from threading import Lock


class ExpanduinoI2C(Expanduino):
  def __init__(self, bus_num, i2c_addr):
    self.lock = Lock()
    self.bus_num = bus_num
    self.i2c_addr = i2c_addr
    self.bus = smbus.SMBus(bus_num)
    Expanduino.__init__(self)
    
  @retry(tries=3)
  def _call(self, devNum, cmd, args, parser):
    opcode = (devNum << 4) + cmd

    with self.lock:
      if args is not None:
        #print(">>", devNum, cmd, args)
        self.bus.write_block_data(self.i2c_addr, opcode, args)
      else:
        #print(">>", devNum, cmd)
        self.bus.write_byte(self.i2c_addr, opcode)
        
      time.sleep(0.005)
      if parser is not None:
        self.bus._set_addr(self.i2c_addr)
        payload = bytes(os.read(self.bus._fd, 32))
        #print(payload)
        payload = payload[1:payload[0]+1]
        #print("<<", payload)
        return parser(payload)
