class PropertyList(tuple):
  
  def names(self):
    return tuple([prop.name() for prop in self])
  
  def __contains__(self, value):
    for prop in self:
      if prop.name() == value:
        return True
    return False


class PropertyQuery(object):
  """
  ' PURPOSE
  '   An instance of this class is created every time
  '   a property is compared to any value. This is used
  '   to track query filters. See the Model class for details.
  """
  
  INVERSE_OPERTORS = {
    '==': '!=',
    '<': '>=',
    '>': '<=',
    '!=': '==',
    '<=': '>',
    '>=': '<',
    'in': 'not in',
    'not in': 'in'
  }
  
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
  
  def flipped(self):
    """
    ' PURPOSE
    '   Returns a new PropertyQuery object containing the
    '   inverted comparison of this PropertyQuery. AKA flips the
    '   operator.
    ' PARAMETERS
    '   None
    ' RETURNS
    '   <PropertyQuery prop_query>
    """
    return PropertyQuery(self.property, self.value, self.INVERSE_OPERTORS[self.operator])
  
  def __repr__(self):
    """
    ' see self.__str__
    """
    return self.__str__()
  
  def __str__(self):
    """
    ' PURPOSE
    '   Condensed, unique representation of the PropertyQuery data.
    ' PARAMETERS
    '   None
    ' RETURNS
    '   <str str_value>
    """
    return 'PropertyQuery(%s %s %s)' % (self.property, self.operator, repr(self.value))



class SortDescriptor(object):
  """
  ' PURPOSE
  '   Used to describe sort directions. Created whenever a property
  '   is negated or positive-thing : +Property or -Property.
  """
  
  DESCENDING = 'down'
  ASCENDING = 'up'
  
  def __init__(self, prop, direction):
    """
    ' PURPOSE
    '   Initializes this class with the original property as
    '   well as direction based on the class variables.
    ' PARAMETERS
    '   <Property prop>
    '   <str direction>
    ' RETURNS
    '   Nothing
    """
    self.property = prop
    self.direction = direction


class BadValueError(Exception):
  pass


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
  
  @staticmethod
  def type():
    return None
  
  def kind(self):
    return self._kind
  
  def name(self):
    return self._name
  
  def is_multiple(self):
    return self._multiple
  
  def default(self):
    return self._default 
  
  def is_required(self):
    return self._required
  
  def _load_meta(self, kind=None, name=None):
    self._kind = kind
    self._name = name
  
  def __init__(self, multiple=False, default=None, required=False):
    if not default is None and required:
      raise ValueError('A property cannot have a default value and be required')
    
    self._multiple = multiple
    self._default = default
    self._required = required
  
  def _pack(self, value):
    """
    ' PURPOSE
    '   Private method called by the db classes in order to pack
    '   a property. The normal 'pack' method packs a single value
    '   whereas '_pack' acounts for multiple values and delegates
    '   to 'pack' while forming an array for saving. Thus meaning
    '   no additional code needs to be written per property to support
    '   the multiple keyword.
    ' PARAMETERS
    '   <object value> value to pack
    ' RETURNS
    '   <list object value> if self.multiple
    '   <object value> if not self.multiple
    """
    if value == None:
      if self._required: raise BadValueError('Entity has uninitialized properties: %s' % self._name)
      
      if self._default == None: return None
      else: return self._pack(self._default)
    
    if self._multiple:
      if not isinstance(value, list): raise BadValueError('%s expected list or tuple, got %s' % (self, value))
      return [self._checktype(obj) for obj in value]
    
    return self._checktype(value)
  
  def _checktype(self, value):
    """
    ' PURPOSE
    '   Checks that the given value is the correct type based on the
    '   self.type() method.
    ' PARAMETERS
    '   <object value>
    ' RETURNS
    '   <object packed_value>
    ' ERRORS
    '   BadValueError ~ if incorrect type
    """
    if not self.type() is None and not isinstance(value, self.type()):
      raise BadValueError('%s expected type %s. Got %s' % (self, self.type().__name__, value))
    return self.pack(value)
  
  def _unpack(self, value):
    """
    ' PURPOSE
    '   Private method called by the db classes in order to unpack
    '   a property. The normal 'unpack' method packs a single value
    '   whereas '_unpack' acounts for multiple values and delegates
    '   to 'unpack' while forming an array for saving. Thus meaning
    '   no additional code needs to be written per property to support
    '   the multiple keyword.
    ' PARAMETERS
    '   <object value> value to unpack
    ' RETURNS
    '   <list object value> if self.multiple
    '   <object value> if not self.multiple
    """
    if value == None:
      if self._default == None: return None
      else: return self._unpack(self._default)
    
    if self._multiple:
      if not isinstance(value, list): return [self.unpack(value)]
      return [self.unpack(obj) for obj in value]
    else: return self.unpack(value)
  
  def unpack(self, value):
    """
    ' PURPOSE
    '   Unpacks a saved value into its original form.
    ' PARAMETERS
    '   <object value> packed value
    ' RETURNS
    '   <object value> unpacked value
    """
    raise NotImplementedError()
      
  def pack(self, value):
    """
    ' PURPOSE
    '   Packs a value into a JSON safe form.
    ' PARAMETERS
    '   <object value> unpacked value
    ' RETURNS
    '   <object value> packed value
    """
    raise NotImplementedError()
  
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
  
  """ COMPARISON OPERATORS BELOW """
  """
  ' PURPOSE
  '   When this property is compared with a value, a PropertyQuery
  '   is returned which will late be used to construct a query request.
  ' PARAMETERS
  '   <object other>
  ' RETURNS
  '   <PropertyQuery propquery>
  ' NOTES
  '   1. If a multiple property is being compared, all of the values
  '      being compared to are AND'd. Hence Prop == ['a', 'b'] finds
  '      entities where the Prop equals 'a' AND 'b'.
  '   2. Using the logic from Note N.1, Prop != ['a', 'b'] returns the
  '      compliment of Prop == ['a', 'b'].
  """
  
  def __eq__(self, other):
    if self._multiple: return self._contains(other)
    return PropertyQuery(self, other, '==')
  
  def __lt__(self, other):
    return PropertyQuery(self, other, '<')
  
  def __gt__(self, other):
    return PropertyQuery(self, other, '>')
  
  def __ne__(self, other):
    if self._multiple: return self._not_contains(other)
    return PropertyQuery(self, other, '!=')
  
  def __le__(self, other):
    return PropertyQuery(self, other, '<=')
  
  def __ge__(self, other):
    return PropertyQuery(self, other, '>=')
  
  def __neg__(self):
    return SortDescriptor(self, SortDescriptor.DESCENDING)
  
  def __pos__(self):
    return SortDescriptor(self, SortDescriptor.ASCENDING)
  
  def _contains(self, other):
    if not self._multiple:
      raise BadValueError('Expected multiple property to sort using in: %s' % self._name)
    from .query import AND
    if not isinstance(other, list): other = [other]
    return AND(*[PropertyQuery(self, [item], 'in') for item in other])
  
  def _not_contains(self, other):
    from .query import NOT
    return NOT(self._contains(other))
  
  def __repr__(self):
    """
    ' see self.__str__
    """
    return self.__str__()
  
  def __str__(self):
    """
    ' PURPOSE
    '   Condensed, unique representation of the Property's data.
    ' PARAMETERS
    '   None
    ' RETURNS
    '   <str str_value>
    """
    return '%s(\'%s\')' % (self.__class__.__name__, self._name)



""" BASIC PROPERTIES BELOW """

class BooleanProperty(Property):
  
  @staticmethod
  def type():
    return bool
  
  def unpack(self, value):
    return value
  
  def pack(self, value):
    return value


class StringProperty(Property):
  
  @staticmethod
  def type():
    return str
  
  def unpack(self, value):
    return value
  
  def pack(self, value):
    return value


class ByteStringProperty(Property):
  
  @staticmethod
  def type():
    return bytes
  
  def unpack(self, value):
    return value.encode('utf-8')
  
  def pack(self, value):
    return value.decode('utf-8')


class IntegerProperty(Property):
  
  @staticmethod
  def type():
    return int
  
  def unpack(self, value):
    return int(value)
  
  def pack(self, value):
    return value


class FloatProperty(Property):
  
  @staticmethod
  def type():
    return float
  
  def unpack(self, value):
    return float(value)
  
  def pack(self, value):
    return value


from .key import Key
class KeyProperty(Property):
  
  @staticmethod
  def type():
    return Key
  
  def unpack(self, value):
    return Key(serial=value)
  
  def pack(self, value):
    return value.serialize()


class ModelProperty(KeyProperty):
  
  def type(self):
    return self._type
  
  def __init__(self, model, *args, **kwargs):
    super(ModelProperty, self).__init__(*args, **kwargs)
    self._type = model
  
  def unpack(self, value):
    return super(ModelProperty, self).unpack(value).get()
  
  def pack(self, value):
    return super(ModelProperty, self).pack(value.key)

