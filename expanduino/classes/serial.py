#!/usr/bin/python

from expanduino.subdevice import Subdevice
from expanduino.codec import *
from enum import IntEnum
from time import time
from cached_property import cached_property
import asyncio
import os
from ..utils import run_coroutines, create_link, forever, fd_reader

class SerialSubdevice(Subdevice):
  class Command(IntEnum):
    NUM_SERIALS  = 0,
    NAME         = 1,
    WRITE        = 2,
    READ         = 3,
    AVAILABLE    = 4
  
  class Serial:
    def __init__(self, subdevice, serialNum):
      self.subdevice = subdevice
      self.serialNum = serialNum
      self.ptyMaster = None
      self.ptySlave = None
      self.ptyLink = None
      
    @cached_property
    def name(self):
      return self.subdevice.call(SerialSubdevice.Command.NAME, args=[self.serialNum], parser=parseString)
      
    @property
    def available(self):
      return self.subdevice.call(SerialSubdevice.Command.AVAILABLE, args=[self.serialNum], parser=parseByte)
    
    def read(self, n):
      return self.subdevice.call(SerialSubdevice.Command.READ, args=[self.serialNum, n], parser=parseBytes)
    
    def write(self, data):
      self.subdevice.call(SerialSubdevice.Command.WRITE, args=bytes([self.serialNum]) + bytes(data))
    
    def __str__(self):
      return "#%-3d %s" % (self.serialNum, self.name)
    
    async def attach(self):
      if self.ptyMaster:
        return
      
      self.ptyMaster, self.ptySlave = os.openpty()
      try:
        async with create_link(os.ttyname(self.ptySlave), "/dev/ttyExpanduino%d") as link:
          async with fd_reader(self.ptyMaster, n=20, callback=self.write):
            await forever()
        
      finally:
        os.close(self.ptySlave)
        os.close(self.ptyMaster)
        self.ptyMaster = None
    
    def handleInterruption(self, data):
      if self.ptyMaster:
        os.write(self.ptyMaster, data)
  
  def __init__(self, container, devNum):
    Subdevice.__init__(self, container, devNum)

  def handleInterruption(self, data):
    if data:
      serialNum = data[0]
      payload = data[1:]
      if serialNum < len(self.serials):
        self.serials[serialNum].handleInterruption(payload)

  @cached_property
  def serials(self):
    num_serials = self.call(SerialSubdevice.Command.NUM_SERIALS, parser=parseByte)
    return [
      SerialSubdevice.Serial(self, i) 
      for i in range(num_serials)
    ]

  async def attach(self):
    serials = self.serials

    with self.with_interruptions():
      coroutines = []
      for serial in serials:
        print("  ", serial)
        coroutines.append(serial.attach())
      await run_coroutines(*coroutines)
