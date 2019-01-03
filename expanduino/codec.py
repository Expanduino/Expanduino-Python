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

def parseBool(x):
  return bool(x[0])
parseBool.expectedSize=1

def parseByte(x):
    return x[0]
parseByte.expectedSize=1

def parseEnum(enum):
  ret = lambda x: enum(x[0])
  ret.expectedSize = 1
  return ret

def parsePacked(pattern):
  pattern = ">" + pattern
  ret = lambda x: struct.unpack(pattern, x)
  ret.expectedSize = struct.calcsize(pattern)
  return ret
  
def parseBytes(x):
  return x

def parseString(x):
  return str(x, "utf8")
