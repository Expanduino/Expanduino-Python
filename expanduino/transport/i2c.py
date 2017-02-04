from expanduino.expanduino import Expanduino
from expanduino.classes.meta import MetaSubdevice
import smbus
import os
import time
from retry import retry
import asyncio
#import RPi.GPIO as GPIO

class ExpanduinoI2C(Expanduino):
  def __init__(self, bus_num, i2c_addr, interrupt_pin):
    self.bus_num = bus_num
    self.i2c_addr = i2c_addr
    self.interrupt_pin = interrupt_pin
    self.bus = smbus.SMBus(bus_num)
    Expanduino.__init__(self)
    
    

  async def attach_interruptions(self):
    #GPIO.setmode(GPIO.BOARD)
    #GPIO.setup(self.interrupt_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    #interruption_future = asyncio.Future()
    
    #def interrupted(_):
      #try:
        #interruption_future.set_result(None)
      #except asyncio.futures.InvalidStateError:
        #pass
    #GPIO.add_event_detect(self.interrupt_pin, GPIO.FALLING, callback=interrupted)
    
    #try:
      #while True:
        #if GPIO.input(self.interrupt_pin) == 1:
          #interruption_future = asyncio.Future()
          #if GPIO.input(self.interrupt_pin) == 1:
            ##await asyncio.wait([self.interruption_future], timeout=0.01)
            #await interruption_future
          
        #payload = self.meta.call(MetaSubdevice.Command.GET_INTERRUPTION, parser=bytes)
        #if payload:
          #self.subdevices[payload[0]].handleInterruption(payload[1:])
          
    #finally:
      #GPIO.remove_event_detect(self.interrupt_pin)
      #GPIO.setup(self.interrupt_pin, GPIO.IN)

    while True:
      payload = self.meta.call(MetaSubdevice.Command.GET_INTERRUPTION, parser=bytes)
      if payload:
        self.subdevices[payload[0]].handleInterruption(payload[1:])    
      else:
        await asyncio.sleep(0.01)

     
  @property
  def phys(self):
    return "expanduino@i2c-%x-%x" % (self.bus_num, self.i2c_addr)
    
  @retry(tries=5)
  def _call(self, devNum, cmd, args, parser):
    opcode = (devNum << 4) + cmd
    
    send = [opcode];
    if (args is not None):
      send += [len(args)] + args
    self.bus._set_addr(self.i2c_addr)
    #print(">>", send)
    os.write(self.bus.fd, bytes(send))
    
    #time.sleep(0.1)
    #if args is not None:
      #print(">>", devNum, cmd, args)
      #self.bus.write_block_data(self.i2c_addr, opcode, args)
    #else:
      #print(">>", devNum, cmd)
      #self.bus.write_byte(self.i2c_addr, opcode)
      
    #time.sleep(0.001)
    if parser is not None:
      #self.bus._set_addr(self.i2c_addr)
      payload = bytes(os.read(self.bus.fd, 32))
      payload = payload[1:payload[0]+1]
      #print("<<", payload)
      return parser(payload)
