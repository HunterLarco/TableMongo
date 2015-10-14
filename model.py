from .properties import Property
from .key import Key

from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.errors import InvalidId

mongo = MongoClient('localhost', 27017)
rawdb = mongo.develop_database


class Model(object):
  
  # limit = 0 means no limit
  @classmethod
  def fetch(cls, limit=0):
    collection = getattr(rawdb, cls.__name__)
    cursor = collection.find(limit=limit, projection=[])
    
    documents = []
    
    if limit == 0:
      limit = cursor.count()
    
    for i in range(limit):
      document = cursor.next()
      documents.append(cls(id=str(document['_id'])))
      
    documents.reverse()
    return documents
  
  @classmethod
  def key_from_id(cls, id):
    return Key(cls, id)
  
  @classmethod
  def get_properties(cls):
    properties = []
    for attr in vars(cls):
      val = getattr(cls, attr)
      if isinstance(val, Property):
        properties.append((attr, val.__class__))
    return properties
  
  
  def __init__(self, key=None, id=None):
    
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
    
    self.__load__()
    
    if self.key:
      self.kind = self.key.model.__name__
  
  
  def packed(self, meta=False):
    json = {}
    for attr in self._properties:
      packer = getattr(self.__class__, attr)
      json[attr] = packer.pack(getattr(self, attr))
    if meta:
      json['key'] = self.key.serialize()
      json['id'] = self.key.id
    return json
  
  
  def __load__(self):
    if not self.key: return
    
    collection = getattr(rawdb, self.__class__.__name__)
    entity = collection.find_one({'_id': ObjectId(self.key.id)})
    if not entity:
      raise ValueError('Entity does not exist')
    
    reserved = ['_id']
    for key, value in entity.items():
      if not key in reserved:
        packer = getattr(self.__class__, key)
        setattr(self, key, packer.unpack(value))
  
  
  def put(self):
    collection = getattr(rawdb, self.__class__.__name__)
    if self.key == None:
      saved = collection.insert_one(self.packed())
      id = saved.inserted_id
      self.key = Key(self.__class__, id)
      self.kind = self.key.model.__name__
    else:
      collection.replace_one({
        '_id': ObjectId(self.key.id)
      }, self.packed())
  
  
  def delete(self):
    self.key.delete()