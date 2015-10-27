class PropertyQuery(object):
  """
  ' PURPOSE
  '   An instance of this class is created every time
  '   a property is compared to any value. This is used
  '   to track query filters. See the Model class for details.
  """

  def __init__(self, prop, val, operator):
    """
    ' PURPOSE
    '   Initializes this class with the compared property,
    '   compared value, and comparison operator in BSON format.
    ' PARAMETERS
    '   <Property prop>
    '   <object val>
    '   <str operator>
    ' RETURNS
    '   <PropertyQuery propquery>
    """
    self.property = prop
    self.value = val
    self.operator = operator



"""
' WARNING: DO NOT USE THIS CLASS AS A MODEL PROPERTY
"""
class Property(object):
  """
  ' PURPOSE
  '   Property is the base class for all Model properties.
  '   It's function is to dictate how to pack values in order
  '   to store their value in a JSON document as well as to dictate
  '   how to unpack the same data.
  """

  def unpack(self, value):
    """
    ' PURPOSE
    '   Unpacks a saved value into its original form.
    ' PARAMETERS
    '   <object value> packed value
    ' RETURNS
    '   <object value> unpacked value
    """
    raise ValueError('All properties must be a subclass of Property and have overridden unpack')

  def pack(self, value):
    """
    ' PURPOSE
    '   Packs a value into a JSON safe form.
    ' PARAMETERS
    '   <object value> unpacked value
    ' RETURNS
    '   <object value> packed value
    """
    raise ValueError('All properties must be a subclass of Property and have overridden pack')

  def __hash__(self):
    """
    ' PURPOSE
    '   Allows properties to comply with dicts.
    ' PARAMETERS
    '   None
    ' RETURNS
    '   Nothing
    """
    return id(self)

  def __eq__(self, other):
    """
    ' PURPOSE
    '   When this property is compared with a value, a PropertyQuery
    '   is returned which will late be used to construct a query request.
    ' PARAMETERS
    '   <object other>
    ' RETURNS
    '   <PropertyQuery propquery>
    """
    return PropertyQuery(self, other, '$eq')

  def __lt__(self, other):
    """
    ' PURPOSE
    '   When this property is compared with a value, a PropertyQuery
    '   is returned which will late be used to construct a query request.
    ' PARAMETERS
    '   <object other>
    ' RETURNS
    '   <PropertyQuery propquery>
    """
    return PropertyQuery(self, other, '$lt')

  def __gt__(self, other):
    """
    ' PURPOSE
    '   When this property is compared with a value, a PropertyQuery
    '   is returned which will late be used to construct a query request.
    ' PARAMETERS
    '   <object other>
    ' RETURNS
    '   <PropertyQuery propquery>
    """
    return PropertyQuery(self, other, '$gt')

  def __ne__(self, other):
    """
    ' PURPOSE
    '   When this property is compared with a value, a PropertyQuery
    '   is returned which will late be used to construct a query request.
    ' PARAMETERS
    '   <object other>
    ' RETURNS
    '   <PropertyQuery propquery>
    """
    return PropertyQuery(self, other, '$ne')

  def __le__(self, other):
    """
    ' PURPOSE
    '   When this property is compared with a value, a PropertyQuery
    '   is returned which will late be used to construct a query request.
    ' PARAMETERS
    '   <object other>
    ' RETURNS
    '   <PropertyQuery propquery>
    """
    return PropertyQuery(self, other, '$lte')

  def __ge__(self, other):
    """
    ' PURPOSE
    '   When this property is compared with a value, a PropertyQuery
    '   is returned which will late be used to construct a query request.
    ' PARAMETERS
    '   <object other>
    ' RETURNS
    '   <PropertyQuery propquery>
    """
    return PropertyQuery(self, other, '$gte')


""" BASIC PROPERTIES BELOW """
# [Ben-G] TODO: These properties have a lot of redundant code that is mostly
# independent of the underlying type of the Property. I feel like 70% of this
# code can be removed.
# Property should be a wrapper around any type that is serializable, the code
# should then be identical for any serializable
# (checking for none + type checking)
class BooleanProperty(Property):

  def unpack(self, value):
    if value == None: return None
    return value

  def pack(self, value):
    if value == None: return None
    if not isinstance(value, bool):
      raise ValueError('BooleanProperty must contain bool instance')
    return value


class StringProperty(Property):
  def unpack(self, value):
    if value == None: return None
    return value

  def pack(self, value):
    if value == None: return None
    if not isinstance(value, str):
      raise ValueError('StringProperty must contain str instance')
    return value


class ByteStringProperty(Property):
  def unpack(self, value):
    if value == None: return None
    return value.encode('utf-8')

  def pack(self, value):
    if value == None: return None
    if not isinstance(value, bytes):
      raise ValueError('ByteStringProperty must contain bytes instance')
    return value.decode('utf-8')


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
