from expanduino.expanduino import Expanduino
from expanduino.classes.meta import MetaSubdevice
from smbus2 import SMBus, i2c_msg, I2cFunc
import os
import time
from retry import retry
import asyncio
import threading
from time import sleep
#import RPi.GPIO as GPIO

class ExpanduinoI2C(Expanduino):
  def __init__(self, bus_num, i2c_addr, interrupt_pin):
    self.bus_num = bus_num
    self.i2c_addr = i2c_addr
    self.interrupt_pin = interrupt_pin
    self.bus = SMBus(bus_num)
    self.lock = threading.Lock()
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
        await asyncio.sleep(0.005)

     
  @property
  def phys(self):
    return "expanduino@i2c-%x-%x" % (self.bus_num, self.i2c_addr)
    
  def _call(self, devNum, cmd, args, parser):
    with self.lock:  # FIXME Should be an asyncio lock
      opcode = (devNum << 4) + cmd
      
      if args is None:
        send_xfer = i2c_msg.write(self.i2c_addr, [opcode])
      else:
        send_xfer = i2c_msg.write(self.i2c_addr, [opcode, len(args)] + args)

      if parser is None:
        i2c_ops = [send_xfer]
      else:
        recvSize = 1
        if hasattr(parser, 'expectedSize'):
          recvSize = parser.expectedSize + 1
        recv_xfer = i2c_msg.read(self.i2c_addr, recvSize)
        i2c_ops = [send_xfer, recv_xfer]
    
      self.bus.i2c_rdwr(*i2c_ops)

      if parser is not None:
        resp = bytes(recv_xfer)
        resp_sz = resp[0]
        resp = resp[1:]
        
        #We don't have the whole response -- Probably because of a dynamic-size field, like a string
        if len(resp) != resp_sz:
          recv_xfer = i2c_msg.read(self.i2c_addr, resp_sz + 1)
          self.bus.i2c_rdwr(recv_xfer)
          resp = bytes(recv_xfer)
          resp_sz = resp[0]
          resp = resp[1:]
        
        #Maybe we transferred more bytes than necessary? just throw away the garbage
        resp = resp[:resp_sz]
            
        return parser(resp)
