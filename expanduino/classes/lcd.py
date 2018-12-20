#!/usr/bin/python

from expanduino.subdevice import Subdevice
from expanduino.codec import *
from enum import IntEnum
from time import time
from cached_property import cached_property
import math
import asyncio
import os
from ..utils import create_link, forever, fd_reader

class LcdSubdevice(Subdevice):
  class Command(IntEnum):
    CMD             = 0,
    READ_TEXT       = 1,
    WRITE_TEXT      = 2,
    GET_BRIGHTNESS  = 3,
    SET_BRIGHTNESS  = 4
  
  def cmd(self, cmd):
    chunk_size = 8
    args = [cmd]
    while len(args):
      n = self.call(LcdSubdevice.Command.CMD, args=args[:chunk_size], parser=parseByte)
      args = args[n:]

  def write(self, text):
    chunk_size = 8
    while len(text):
      n = self.call(LcdSubdevice.Command.WRITE_TEXT, args=text[:chunk_size], parser=parseByte)
      text = text[n:]
    
  def read(self, n):
    return self.call(LcdSubdevice.Command.READ_TEXT, args=[n], parser=parseBytes)
    
  @property
  def brightness(self):
    return self.call(LcdSubdevice.Command.GET_BRIGHTNESS, parser=parseByte) / 255
  
  @brightness.setter
  def brightness(self, value):
    value = round(max(0, min(255, 255 * value)))
    return self.call(LcdSubdevice.Command.SET_BRIGHTNESS, args=[value])

  async def attach(self):
    ptyMaster, ptySlave = os.openpty()
    try:
      current_data = b''
      def got_data(data):
        nonlocal current_data
        current_data += data
        
        while len(current_data) >= 1:
            if current_data[0] == 0:
                self.reset()
                current_data = current_data[1:]
                
            elif current_data[0] == 1:
                if len(current_data) < 2:
                  break
                self.cmd(current_data[1])
                current_data = current_data[2:]
                
            elif current_data[0] == 2:
                if len(current_data) < 2:
                  break
                self.brightness = current_data[1] / 255
                current_data = current_data[2:]
                
            elif current_data[0] == 3:
                if len(current_data) < 2:
                  break
                l = current_data[1]
                if len(current_data) < l+2:
                  break
                self.write(current_data[2:l+2])
                current_data = current_data[l+2:]
            else:
                # Oops?
                self.write(b'?')
                current_data = current_data[1:]
      
      async with create_link(os.ttyname(ptySlave), "/dev/xcharlcd%d") as link:
        async with fd_reader(ptyMaster, n=20, callback=got_data):
          await forever()
      
    finally:
      os.close(ptySlave)
      os.close(ptyMaster)
