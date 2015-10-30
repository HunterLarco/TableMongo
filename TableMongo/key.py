""" GLOBAL IMPORTS """
import base64


""" LOCAL IMPORTS """
# At the bottom of the file


class Key(object):
  """
  ' PURPOSE
  '   Key instances identify entities saved via the datastore
  '   and can grab the data at any time while also adding the
  '   data to the corresponding subclass of Model.
  '
  ' EXAMPLE USAGE
  '   Keys can be created many different ways, one of the unique
  '   and easy things about them is they don't need to specify a
  '   Model upfront. For example, the following code grabs an entity
  '   and then instantiates the corresponding Model subclass with
  '   the entity's data and functions already added in.
  '
  '   ->  entity = Key(urlsafe = 'askjhd872hd92jio34==').get()
  """

  @classmethod
  def get_model(self, modelname):
    """
    ' PURPOSE
    '   Given a model's name, return the actual class
    ' PARAMETERS
    '   <str modelname> exact Model subclass name
    ' RETURNS
    '   <class MyModel extends Model>
    ' NOTES
    '   1. The subclass must have already been imported and thus
    '      already exists in memory.
    """
    models = Model.__subclasses__()
    for model in models:
      if modelname == model.__name__:
        return model
        break
    else:
      raise ValueError('Invalid modelname')

  def __init__(self, model=None, id=None, urlsafe=None, serial=None):
    """
    ' PURPOSE
    '   Instantiates a new Key via either serial representation, urlsafe,
    '   or model class and id.
    ' PARAMETERS
    '   optional <class MyModel extends Model model>
    '   optional <str id>
    '   optional <str urlsafe>
    '   optional <str serial>
    ' RETURNS
    '   <Key key>
    """
    if serial:
      try:
        modelname, self.id = tuple(serial.split(':'))
      except:
        raise ValueError('Malformed serialized key')
      self.model = self.get_model(modelname)
    elif urlsafe:
      try:
        decoded = base64.b64decode(urlsafe).decode('utf-8')
        modelname, self.id = tuple(decoded.split(':'))
      except:
        raise ValueError('Malformed urlsafe key')
      self.model = self.get_model(modelname)
    elif model and id:
      self.model, self.id = (model, id)
    else:
      raise ValueError('Expected model and id or urlsafe')

  def serialize(self):
    """
    ' PURPOSE
    '   Returns a serialized version of this key.
    '   Can be used to instantiate a clone of this key.
    ' PARAMETERS
    '   None
    ' RETURNS
    '   <str serialized>
    """
    return '%s:%s' % (self.model.__name__, self.id)

  def urlsafe(self):
    """
    ' PURPOSE
    '   Returns a urlsafe version of this key (base64 serialization).
    '   Can be used to instantiate a clone of this key.
    ' PARAMETERS
    '   None
    ' RETURNS
    '   <str urlsafe>
    """
    base_string = self.serialize()
    encoded = base64.b64encode(bytes(base_string, 'utf8'))
    formatted = encoded.decode('utf-8')
    return formatted

  def delete(self):
    """
    ' PURPOSE
    '   Deletes the entity associated with this key.
    ' PARAMETERS
    '   None
    ' RETURNS
    '   <int deleted> the number of deleted entities
    """
    from .model import rawdb, ObjectId
    collection = getattr(rawdb, self.model.__name__)
    result = collection.remove({ '_id': ObjectId(self.id) })
    return result['n']

  def get(self):
    """
    ' PURPOSE
    '   Gets the entity associated with this key. May return None.
    ' PARAMETERS
    '   None
    ' RETURNS
    '   <MyModel extends Model entity> if entity exists
    '   None if entity does not exist.
    """
    try:
      return self.model(key=self)
    except:
      return None

  def __repr__(self):
    """
    ' PURPOSE
    '   Condensed, unique representation of the Key data.
    ' PARAMETERS
    '   None
    ' RETURNS
    '   <str repr_value>
    """
    return '<db.Key %s>' % self.serialize()

  def __str__(self):
    """
    ' PURPOSE
    '   Condensed, unique representation of the Key data.
    ' PARAMETERS
    '   None
    ' RETURNS
    '   <str str_value>
    """
    return '<db.Key %s>' % self.serialize()


""" LOCAL IMPORTS (to allow circular imports) """
from .model import Model
