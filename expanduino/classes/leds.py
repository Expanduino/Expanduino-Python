#!/usr/bin/python

from expanduino.subdevice import Subdevice
from expanduino.codec import *
from enum import IntEnum
from time import time
from cached_property import cached_property
import math
import asyncio

class LedsSubdevice(Subdevice):
  class Command(IntEnum):
    NUM_LEDS       = 0
    NAME           = 1
    GET_BRIGHTNESS = 2
    SET_BRIGHTNESS = 3
  
  class Led:
    def __init__(self, subdevice, ledNum):
      self.subdevice = subdevice
      self.ledNum = ledNum
      
    @cached_property
    def name(self):
      return self.subdevice.call(LedsSubdevice.Command.NAME, args=[self.ledNum], parser=parseString)
      
    @property
    def brightness(self):
      return self.subdevice.call(LedsSubdevice.Command.GET_BRIGHTNESS, args=[self.ledNum], parser=parseByte) / 255
    
    @brightness.setter
    def brightness(self, value):
      value = round(max(0, min(255, 255 * value)))
      return self.subdevice.call(LedsSubdevice.Command.SET_BRIGHTNESS, args=[self.ledNum, value])
    
    def __str__(self):
      return "#%d %s = %.0f%%" % (self.ledNum, self.name, self.brightness*100)
  
  def __init__(self, container, devNum):
    Subdevice.__init__(self, container, devNum)

  @cached_property
  def leds(self):
    num_leds = self.call(LedsSubdevice.Command.NUM_LEDS, parser=parseByte)
    return [
      LedsSubdevice.Led(self, i) 
      for i in range(num_leds)
    ]

  def run(self, loop, is_demo):
    leds = self.leds
    for led in leds:
      print("  %s" % led)

    if is_demo:
      timeBegin = time()
      async def blink():
        while True:
          #print("blink()")
          elapsed = time() - timeBegin
          for i, led in enumerate(leds):
            #led.brightness = 0.5 + 0.5*math.sin(2 * math.pi * (elapsed + 1.0*i/len(leds)))
            pass
          await asyncio.sleep(0.05)
      asyncio.ensure_future(blink())
      
