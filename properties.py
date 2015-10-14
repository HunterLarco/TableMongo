# do not use this class
class Property(object):
  def unpack(self, value):
    return value
  
  def pack(self, value):
    return value


class BooleanProperty(Property):
  def unpack(self, value):
    if value == None: return None
    return value
  
  def pack(self, value):
    if value == None: return None
    if not isinstance(value, bool):
      raise ValueError('BooleanProperty must contain bool instance')
    return value


class TextProperty(Property):
  def unpack(self, value):
    if value == None: return None
    return value
  
  def pack(self, value):
    if value == None: return None
    if not isinstance(value, str):
      raise ValueError('StringProperty must contain str instance')
    return value


class IntegerProperty(Property):
  def unpack(self, value):
    if value == None: return None
    return value
  
  def pack(self, value):
    if value == None: return None
    if not isinstance(value, int):
      raise ValueError('IntegerProperty must contain int instance')
    return value


class FloatProperty(Property):
  def unpack(self, value):
    if value == None: return None
    return value
  
  def pack(self, value):
    if value == None: return None
    if not isinstance(value, float):
      raise ValueError('FloatProperty must contain float instance')
    return value


class KeyProperty(Property):
  def unpack(self, value):
    if value == None: return None
    from .key import Key
    return Key(serial=value)
  
  def pack(self, value):
    if value == None: return None
    from .key import Key
    if not isinstance(value, Key):
      raise ValueError('KeyProperty must contain Key instance')
    return value.serialize()