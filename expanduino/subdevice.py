from enum import IntEnum
from cached_property import cached_property

class Subdevice:
  class Type(IntEnum):
    MISSING      = 0
    META         = 1
    LEDS         = 2
    GPIO         = 3
    LINUX_INPUT  = 4
    HID          = 5
    SERIAL       = 6
    MISC         = 7
    I2C          = 8
    SPI          = 9

  def __init__(self, container, devNum):
    self.container = container
    self.devNum = devNum
    
  def call(self, *args, **kwargs):
    return self.container.call(self.devNum, *args, **kwargs)

  @cached_property
  def type(self):
    return self.container.meta.subdevice_type(self.devNum)

  @cached_property
  def name(self):
    return self.container.meta.subdevice_name(self.devNum)
  
  @cached_property
  def short_name(self):
    return self.container.meta.subdevice_short_name(self.devNum)

  @property
  def phys(self):
    return "%s/%s@%x" % (self.container.phys, self.short_name, self.devNum)

  def handleInterruption(self, data):
    print(self.name, "Got interrupt", data)

  def run(self, loop, is_demo):
    pass

  def __str__(self):
    return "%s (%s@%d - %s - %s)" % (self.name, self.short_name, self.devNum, self.phys, self.type.name)