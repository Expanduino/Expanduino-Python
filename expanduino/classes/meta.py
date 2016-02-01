#!/usr/bin/python

from expanduino.subdevice import Subdevice
from expanduino.codec import *
from enum import IntEnum
from functools import lru_cache
from cached_property import cached_property

class MetaSubdevice(Subdevice):
  class Command(IntEnum):
    VENDOR_NAME          = 0
    PRODUCT_NAME         = 1
    SHORT_NAME           = 2
    SERIAL_NUMBER        = 3
    RESET                = 4
    GET_INTERRUPTS       = 5
    NUM_SUBDEVICES       = 6
    SUBDEVICE_TYPE       = 7
    SUBDEVICE_NAME       = 8
    SUBDEVICE_SHORT_NAME = 9
  
  def __init__(self, container, devNum):
    Subdevice.__init__(self, container, devNum)
    
  @cached_property
  def vendor_name(self):
    return self.call(MetaSubdevice.Command.VENDOR_NAME, parser=parseString)
  
  @cached_property
  def product_name(self):
    return self.call(MetaSubdevice.Command.PRODUCT_NAME, parser=parseString)
  
  @cached_property
  def short_name(self):
    return self.call(MetaSubdevice.Command.SHORT_NAME, parser=parseString)
  
  @cached_property
  def serial_number(self):
    return self.call(MetaSubdevice.Command.SERIAL_NUMBER, parser=parseString)

  def reset(self):
    self.call(MetaSubdevice.Command.RESET)

  @cached_property
  def num_subdevices(self):
    return self.call(MetaSubdevice.Command.NUM_SUBDEVICES, parser=parseByte)

  def subdevice_type(self, devNum):
    return self.call(MetaSubdevice.Command.SUBDEVICE_TYPE, args=[devNum], parser=parseEnum(Subdevice.Type))

  def subdevice_name(self, devNum):
    return self.call(MetaSubdevice.Command.SUBDEVICE_NAME, args=[devNum], parser=parseString)

  def subdevice_short_name(self, devNum):
    return self.call(MetaSubdevice.Command.SUBDEVICE_SHORT_NAME, args=[devNum], parser=parseString)
  
