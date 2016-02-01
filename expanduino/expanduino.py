from expanduino.classes.meta import MetaSubdevice
from expanduino.classes.leds import LedsSubdevice
from expanduino.classes.linuxinput import LinuxInputSubdevice
from expanduino.subdevice import Subdevice
from expanduino.codec import defaultEncoder
from cached_property import cached_property

class Expanduino:
  def __init__(self):
    self.meta = MetaSubdevice(self, 0)
    
  def call(self, devNum, cmd, args=None, encoder=defaultEncoder, parser=None):
    if args is not None:
      args = list(encoder(args))
    return self._call(devNum, cmd, args, parser)

  @property
  def vendor_name(self):
    return self.meta.vendor_name
  
  @property
  def product_name(self):
    return self.meta.product_name
  
  @property
  def short_name(self):
    return self.meta.short_name
  
  @property
  def serial_number(self):
    return self.meta.serial_number

  def reset(self):
    return self.meta.reset()
  
  @cached_property
  def subdevices(self):
    subdevice_classes = {
      Subdevice.Type.META: MetaSubdevice,
      Subdevice.Type.LEDS: LedsSubdevice,
      Subdevice.Type.LINUX_INPUT: LinuxInputSubdevice,
    }
    
    subdevices = [
      subdevice_classes.get(self.meta.subdevice_type(i), Subdevice)(self, i)
      for i in range(self.meta.num_subdevices)
    ]
    
    return subdevices

  def demo(self, sched):
    print("Vendor:", self.vendor_name)
    print("Product:", self.product_name)
    print("Short name:", self.short_name)
    print("S/N:", self.serial_number)

    for subdevice in self.subdevices:
      print(subdevice)
      subdevice.demo(sched)
