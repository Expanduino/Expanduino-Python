from enum import IntEnum
from cached_property import cached_property

class Subdevice:
  class Type(IntEnum):
    MISSING      =  0
    META         =  1
    LEDS         =  2
    GPIO         =  3
    LINUX_INPUT  =  4
    HID          =  5
    SERIAL       =  6
    MISC         =  7
    I2C          =  8
    SPI          =  9
    LCD          = 10

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
  
  @property
  def interruptionEnabled(self):
    return self.container.meta.subdevice_get_interrupt_enabled(self.devNum)
  
  @interruptionEnabled.setter
  def interruptionEnabled(self, enabled):
    self.container.meta.subdevice_set_interrupt_enabled(self.devNum, enabled)
  
  def reset(self):
    self.container.meta.subdevice_reset(self.devNum)
  
  def with_interruptions(self):
    class Context:
      def __init__(self, subdevice):
        self.subdevice = subdevice
        self.old_value = None
      
      def __enter__(self):
        self.old_value = self.subdevice.interruptionEnabled
        self.subdevice.interruptionEnabled = True

      def __exit__(self, exc_type, exc, tb):
        self.subdevice.interruptionEnabled = self.old_value
        self.old_value = None
    return Context(self)


  def handleInterruption(self, data):
    print(self.name, "Got interrupt", data)

  async def attach(self):
    pass

  def __str__(self):
    return "%s (%s@%d - %s - %s)" % (self.name, self.short_name, self.devNum, self.phys, self.type.name)