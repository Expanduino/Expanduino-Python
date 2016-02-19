#!/usr/bin/python

from expanduino.subdevice import Subdevice
from expanduino.codec import *
from enum import IntEnum
from time import time
from cached_property import cached_property
import asyncio
import os
import termios
import re
from fcntl import ioctl
from ..utils import run_coroutines, create_link, forever, fd_reader

EXTPROC = 0o200000
TIOCPKT_IOCTL = 64

BAUD_CONSTANTS = {
  getattr(termios, x): int(x[1:])
  for x in filter(lambda x: re.match("B\\d+", x), dir(termios)) 
}
CHARACTER_SIZE_CONSTANTS = {
  getattr(termios, x): int(x[2:])
  for x in filter(lambda x: re.match("CS\\d+", x), dir(termios)) 
}

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
        attr = termios.tcgetattr(self.ptyMaster)
        attr[3] |= EXTPROC
        termios.tcsetattr(self.ptyMaster, termios.TCSANOW, attr)
        ioctl(self.ptyMaster, termios.TIOCPKT, b'\1')
        
        
        def got_packet(packet):

          if packet[0] == termios.TIOCPKT_DATA:
            self.write(packet[1:])

          if packet[0] & TIOCPKT_IOCTL:
            attr = termios.tcgetattr(self.ptyMaster)
            
            # Dont let the slave clear the EXTPROC flag (e.g., screen does so)
            # IMO, allowing the slave fd to do this sounds pretty dumb
            if not attr[3] & EXTPROC:
              attr[3] |= EXTPROC
              termios.tcsetattr(self.ptyMaster, termios.TCSANOW, attr)
            
            ibaud = BAUD_CONSTANTS[attr[4]]
            obaud = BAUD_CONSTANTS[attr[5]]
            
            #FIXME: Pty driver assumes 8 bits, no parity, ALWAYS
            #https://github.com/torvalds/linux/blob/master/drivers/tty/pty.c#L290-L291
            
            bits = CHARACTER_SIZE_CONSTANTS[attr[2] & termios.CSIZE]
            
            if attr[2] & termios.PARENB:
              if attr[2] & termios.PARODD:
                parity = 'O'  
              else:
                parity = 'E'
            else:
              parity = 'N'
              
              
            if attr[2] & termios.CSTOPB:
              stop_bits = 2
            else:
              stop_bits = 1
            
            
            
            print("Changed %s config: %d:%d  %d%s%d" % (self, ibaud, obaud, bits, parity, stop_bits))
            #TODO: Reconfigure the port
        
        async with create_link(os.ttyname(self.ptySlave), "/dev/ttyExpanduino%d") as link:
          async with fd_reader(self.ptyMaster, n=20, callback=got_packet):
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
