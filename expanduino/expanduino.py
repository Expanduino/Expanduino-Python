from expanduino.classes.meta import MetaSubdevice
from expanduino.classes.leds import LedsSubdevice
from expanduino.classes.linuxinput import LinuxInputSubdevice
from expanduino.classes.serial import SerialSubdevice
from expanduino.subdevice import Subdevice
from expanduino.codec import defaultEncoder
from cached_property import cached_property
from .utils import run_coroutines

class Expanduino:
  def __init__(self):
    self.meta = MetaSubdevice(self, 0)
    
  def call(self, devNum, cmd, args=None, encoder=defaultEncoder, parser=None):
    if args is not None:
      args = list(encoder(args))
    return self._call(devNum, cmd, args, parser)

  @property
  def phys(self):
    return "expanduino"
  
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
      Subdevice.Type.LEDS: LedsSubdevice,
      Subdevice.Type.LINUX_INPUT: LinuxInputSubdevice,
      Subdevice.Type.SERIAL: SerialSubdevice,
    }
    
    subdevices = [self.meta] + [
      subdevice_classes.get(self.meta.subdevice_type(i), Subdevice)(self, i)
      for i in range(1, self.meta.num_subdevices)
    ]
    
    return subdevices


  # Attaches this device in the OS (Using UInput, PTY, etc)
  # The coroutine will be executed on the event loop until the program quits, when it get cancelled
  async def attach(self):
    print("Vendor:", self.vendor_name)
    print("Product:", self.product_name)
    print("Short name:", self.short_name)
    print("S/N:", self.serial_number)

    coroutines = []
    for subdevice in self.subdevices:
      print(subdevice)
      coroutines.append(subdevice.attach())
    await run_coroutines(*coroutines) 
