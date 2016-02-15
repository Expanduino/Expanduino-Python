from expanduino.expanduino import Expanduino
from expanduino.classes.meta import MetaSubdevice
import smbus
import os
import time
from retry import retry
from threading import Lock
import asyncio
import RPi.GPIO as GPIO

class ExpanduinoI2C(Expanduino):
  def __init__(self, bus_num, i2c_addr, interrupt_pin):
    self.lock = Lock()
    self.bus_num = bus_num
    self.i2c_addr = i2c_addr
    self.interrupt_pin = interrupt_pin
    self.bus = smbus.SMBus(bus_num)
    Expanduino.__init__(self)
    
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(interrupt_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    self.interruption_future = asyncio.Future()
    GPIO.add_event_detect(interrupt_pin, GPIO.FALLING, callback=self.interrupted)
    
    asyncio.ensure_future(self.handle_interruptions())

  def interrupted(self, _):
    try:
      self.interruption_future.set_result(None)
    except asyncio.futures.InvalidStateError:
      pass

  async def handle_interruptions(self):
    while True:
      if GPIO.input(self.interrupt_pin) == 1:
        self.interruption_future = asyncio.Future()
        if GPIO.input(self.interrupt_pin) == 1:
          await asyncio.wait([self.interruption_future], timeout=0.01)
        
      payload = self.meta.call(MetaSubdevice.Command.GET_INTERRUPTION, parser=bytes)
      #print("Interrupt!", payload)
      if payload:
        self.subdevices[payload[0]].handleInterruption(payload[1:])
      #else:
        #print("-")
    

     
  @property
  def phys(self):
    return "expanduino@i2c-%x-%x" % (self.bus_num, self.i2c_addr)
    
  @retry(tries=5)
  def _call(self, devNum, cmd, args, parser):
    opcode = (devNum << 4) + cmd

    with self.lock:
      time.sleep(0.005)
      if args is not None:
        #print(">>", devNum, cmd, args)
        self.bus.write_block_data(self.i2c_addr, opcode, args)
      else:
        #print(">>", devNum, cmd)
        self.bus.write_byte(self.i2c_addr, opcode)
        
      time.sleep(0.005)
      if parser is not None:
        self.bus._set_addr(self.i2c_addr)
        payload = bytes(os.read(self.bus._fd, 120))
        #print(payload)
        payload = payload[1:payload[0]+1]
        #print("<<", payload)
        return parser(payload)
