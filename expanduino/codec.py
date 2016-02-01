import struct

def encodePacked(pattern):
  def f(args):
    return struct.pack(">" + pattern, *args)
  return f

def encodeByte(x):
  return bytes([x])

def encodeString(x):
  return bytes(x, "utf8")

def defaultEncoder(x):
  if isinstance(x, str):
    return parseString(x)
  elif isinstance(x, bytes):
    return x
  elif isinstance(x, list):
    return bytes(x)
  else:
    raise TypeError("defaultEncoder supports String, Bytes and LIst<Byte>")




def parsePacked(pattern):
  def f(args):
    return struct.unpack(">" + pattern, args)
  return f

def parseByte(x):
  return x[0]

def parseInt(x):
  return x[0]

def parseEnum(enum):
  return lambda x: enum(x[0])

def parseString(x):
  return str(x, "utf8")
