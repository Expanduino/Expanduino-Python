#!/usr/bin/python

from expanduino.subdevice import Subdevice
from expanduino.codec import *
from enum import IntEnum
from time import time
import math
import evdev
import asyncio
from collections import namedtuple, defaultdict
from cached_property import cached_property
import struct
import io

class LinuxInputSubdevice(Subdevice):
  class Command(IntEnum):
    ID                   = 0
    NUM_COMPONENTS       = 1
    COMPONENT_TYPE       = 2
    COMPONENT_ABS_INFO   = 3
    GET_COMPONENT_VALUE  = 4
    SET_COMPONENT_VALUE  = 5

  AbsInfo = namedtuple('AbsInfo', ['max', 'min', 'fuzz', 'flat'])
  
  class Component:
    def __init__(self, subdevice, componentNum):
      self.subdevice = subdevice
      self.componentNum = componentNum

    @cached_property
    def type(self):
      return self.subdevice.call(LinuxInputSubdevice.Command.COMPONENT_TYPE, args=[self.componentNum], parser=parsePacked("HH"))
    
    @cached_property
    def abs_info(self):
      try:
        return LinuxInputSubdevice.AbsInfo(*self.subdevice.call(LinuxInputSubdevice.Command.COMPONENT_ABS_INFO, args=[self.componentNum], parser=parsePacked("iiii")))
      except struct.error:
        return None
      
    @property
    def value(self):
      return self.subdevice.call(LinuxInputSubdevice.Command.GET_COMPONENT_VALUE, args=[self.componentNum], parser=parsePacked("i"))[0]
    
    @value.setter
    def value(self, value):
      return self.subdevice.call(LinuxInputSubdevice.Command.SET_COMPONENT_VALUE, args=[self.componentNum, value], encoder=encodePacked("Bi"))
    
    def __str__(self):
      type = self.type
      return "#%-3d %-20s = %-5d %s" % (self.componentNum, evdev.ecodes.bytype[type[0]][type[1]], self.value, self.abs_info or "")
  
  def __init__(self, container, devNum):
    Subdevice.__init__(self, container, devNum)
    self.uinput = None
    
  @cached_property
  def components(self):
    num_components = self.call(LinuxInputSubdevice.Command.NUM_COMPONENTS, parser=parseByte)
    return [
      LinuxInputSubdevice.Component(self, i) 
      for i in range(num_components)
    ]
  
  @cached_property
  def components_by_type(self):
    return {
      component.type : component
      for component in self.components
    }

  def handleInterruption(self, data):
    if not self.uinput:
      return
    if not data:
      return
    
    def unpack(stream, fmt):
      size = struct.calcsize(fmt)
      buf = stream.read(size)
      if len(buf) != size:
        return None
      return struct.unpack(fmt, buf)

    stream = io.BytesIO(data)
    components = self.components
    while True:
      e = unpack(stream, '>Bi')
      if not e:
        break
      component = components[e[0]]
      self.uinput.write(component.type[0], component.type[1], e[1])        
    self.uinput.syn()
    
    
  
  async def attach(self):
    events = defaultdict(list)
    for component in self.components:
      print("  ", component)
      ev_type = component.type[0]
      ev_code = component.type[1]
      if ev_type == evdev.ecodes.EV_ABS:
        abs_info = component.abs_info
        ev_code = (ev_code, evdev.AbsInfo(max=abs_info.max, min=abs_info.min, fuzz=abs_info.fuzz, flat=abs_info.flat, value=0, resolution=0))
      events[ev_type].append(ev_code)
    
    self.uinput = evdev.UInput(events=events, name=self.name, phys=self.phys)
    try:
      with self.uinput:
        self.interruptionEnabled = True
        with self.with_interruptions():
          async for ev in self.uinput.read_iter():
            component = self.components_by_type[(ev.type, ev.code)]
            component.value = ev.value
    finally:
      self.uinput = None
