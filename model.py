""" LOCAL IMPORTS """
from .properties import Property, PropertyQuery
from .key import Key
from . import query


""" MONGO IMPORTS """
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.errors import InvalidId


""" MONGO DATABASE """
mongo = MongoClient('localhost', 27017)
rawdb = mongo.develop_database


class Model(object):
  """
  ' PURPOSE
  '   The Model class is the superclass to all other database
  '   entries. It mediates saving data, typing data, and queries.
  '
  ' EXAMPLE USAGE
  '   The following code creates a new model called 'User'. In
  '   this case it contains a string fullname, string email, and
  '   float age.
  '   
  '   -> class User(db.Model):
  '   ->   fullname = db.StringProperty()
  '   ->   email = db.StringProperty()
  '   ->   age = db.FloatProperty()
  '
  '   This code creates a new user, adds values, then saves the
  '   entity.
  '
  '   -> user = User()
  '   -> user.fullname = 'John Doe'
  '   -> user.email = 'john@doe.com'
  '   -> user.age = 21.75
  '   -> user.save()
  '
  '   This code accomplishes the same thing shorthand.
  '
  '   -> user = User(fullname = 'John Doe', email = 'john@doe.com', age = 21.75)
  '   -> user.save()
  '
  '   This code queries for the first 10 users with the name 'Jane Doe'
  '   and an age '18 < age < 25'
  '
  '   -> matches = User.fetch(User.fullname == 'Jane Doe', User.age < 25, User.age > 18, count=10)
  """
  
  @classmethod
  def delete_all(cls):
    """
    ' PURPOSE
    '   Deletes all entities created by the current model.
    ' PARAMETERS
    '   None
    ' RETURNS
    '   <int deleted> the count of entities deleted
    """
    collection = getattr(rawdb, cls.__name__)
    deleted = collection.count()
    collection.drop()
    return deleted
  
  # count = 0 means no limit
  @classmethod
  def fetch(cls, *args, count=0, keys_only=False):
    """
    ' PURPOSE
    '   Fetches entities from this model using the provided
    '   filters. A filter is created by comparing a model's
    '   property at a class level to the desired filter.
    '
    '   For example. This code queries a User model by email
    '   and by age.
    '
    '   -> class User(db.Model):
    '   ->   fullname = db.StringProperty()
    '   ->   email = db.StringProperty()
    '   ->   age = db.FloatProperty()
    '   ->
    '   -> matches = User.fetch(User.email == 'john@doe.com', User.age < 25)
    '
    ' PARAMETERS
    '   <PropertyQuery prop_query1>
    '   <PropertyQuery prop_query2>
    '   ...
    '   <PropertyQuery prop_queryN>
    '   optional <int count> The max amount of entities to fetch.
    '                        if left untouched returns all entities
    '                        matching the fiters.
    '   optional <bool keys_only> If true, returns the keys of matching
    '                             entities instead of the model instances.
    ' RETURNS
    '   <list MyModel extends db.Model> if not keys_only
    '   <list db.Key> if keys_only
    """
    # TODO change to a smart generator. Allowing indexed gets
    # but will simply iterate to the index to get it.
    bson = query.AND(*args).bson(cls)
    
    collection = getattr(rawdb, cls.__name__)
    cursor = collection.find(bson, limit=count, projection={ '_id':1 })
    
    documents = []
    
    for document in cursor:
      if keys_only: documents.append(Key(cls, str(document['_id'])))
      else: documents.append(cls(id=str(document['_id'])))
      
    documents.reverse()
    return documents
  
  @classmethod
  def key_from_id(cls, id):
    """
    ' PURPOSE
    '   Forms a Key instance from an identifier
    ' PARAMETERS
    '   <str id>
    ' RETURNS
    '   <Key key>
    """
    return Key(cls, id)
  
  @classmethod
  def get_by_id(cls, id):
    """
    ' PURPOSE
    '   Returns the entity or None associated with the given identifier.
    ' PARAMETERS
    '   <str identifier>
    ' RETURNS
    '   <MyModel extends db.Model entity> if entity exists
    '   None if entity does not exist
    '   
    """
    return cls.key_from_id(id).get()
  
  @classmethod
  def get_properties(cls):
    """
    ' PURPOSE
    '   Returns a list of properties associated with this model.
    ' PARAMETERS
    '   None
    ' RETURNS
    '   <list (str name, Property type)>
    ' NOTES
    '   1. The returned list contains tuples where the first item
    '      is the string name of the property for example 'email' or 'age'
    '      while the second item is the actual PropertyClass, for example
    '      StringProperty or FloatProperty.
    """
    properties = []
    for attr in vars(cls):
      val = getattr(cls, attr)
      if isinstance(val, Property):
        properties.append((attr, val.__class__))
    return properties
  
  def __init__(self, key=None, id=None, **kwargs):
    """
    ' PURPOSE
    '   Intializes an entity. If given a key or identifier
    '   the entity will load the data associate with the provided
    '   key or identifier. Otherwise no previous data is
    '   assumed and the save method will create a new database entry.
    ' PARAMETERS
    '   optional <Key key>
    '   optional <str id>
    '   optional **kwargs
    ' RETURNS
    '   <MyModel extends Model entity>
    ' NOTES
    '   1. The optional kwargs correspond to entity properties for shorthand
    '      entity creation. For example...
    '
    '      -> Model(prop1 = 'Test', float1 = 2.4)
    '     
    '      Now this entity will be initialized with the properties for 'prop1'
    '      and 'float1' already filled in.
    """
    self._properties = []
    for attr in vars(self.__class__):
      val = getattr(self.__class__, attr)
      if isinstance(val, Property):
        self._properties.append(attr)
        setattr(self, attr, None)
    
    if key:
      self.key = key
    elif id:
      self.key = self.key_from_id(id)
    else:
      self.key = None
    
    self._load()
    
    if self.key:
      self.kind = self.__class__.__name__
    
    for prop, value in kwargs.items():
      if prop in self._properties:
        setattr(self, prop, value)
  
  def packed(self, meta=False):
    """
    ' PURPOSE
    '   Returns a packed version of this entities data. This method
    '   is used to format data for save transactions.
    ' PARAMETERS
    '   optional <bool meta> Whether to add entity meta data to the
    '                        packed dictionary (id and serialized key).
    ' RETURNS
    '   <dict data>
    """
    json = {}
    for attr in self._properties:
      packer = getattr(self.__class__, attr)
      json[attr] = packer._pack(getattr(self, attr))
    if meta:
      json['key'] = self.key.serialize()
      json['id'] = self.key.id
    return json
  
  def _load(self):
    """
    ' PURPOSE
    '   A private method used to load pre-saved entity data when
    '   initialized via key or identifier.
    ' PARAMETERS
    '   None
    ' RETURNS
    '   None
    """
    if not self.key: return
    
    collection = getattr(rawdb, self.__class__.__name__)
    entity = collection.find_one({'_id': ObjectId(self.key.id)})
    if not entity:
      raise ValueError('Entity does not exist')
    
    reserved = ['_id']
    for key, value in entity.items():
      if not key in reserved:
        packer = getattr(self.__class__, key)
        setattr(self, key, packer._unpack(value))
  
  def save(self):
    """
    ' PURPOSE
    '   Saves the entity.
    ' PARAMETERS
    '   None
    ' RETURNS
    '   Nothing
    ' NOTES
    '   1. New entities have no key value until this method
    '      has been executed successfuly.
    """
    collection = getattr(rawdb, self.__class__.__name__)
    if self.key == None:
      # create new database entry
      saved = collection.insert_one(self.packed())
      id = saved.inserted_id
      self.key = Key(self.__class__, id)
      self.kind = self.key.model.__name__
    else:
      # update database entry
      collection.replace_one({
        '_id': ObjectId(self.key.id)
      }, self.packed())
    return self
  
  def delete(self):
    """
    ' PURPOSE
    '   Deletes thie entity.
    ' PARAMETERS
    '   None
    ' RETURNS
    '   Nothing
    """
    self.key.delete()
