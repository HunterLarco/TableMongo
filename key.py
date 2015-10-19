import base64

class Key(object):
  
  @classmethod
  def get_model(self, modelname):
    models = Model.__subclasses__()
    for model in models:
      if modelname == model.__name__:
        return model
        break
    else:
      raise ValueError('Invalid modelname')
  
  def __init__(self, model=None, id=None, urlsafe=None, serial=None):
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
    return '%s:%s' % (self.model.__name__, self.id)
  
  def urlsafe(self):
    base_string = self.serialize()
    encoded = base64.b64encode(bytes(base_string, 'utf8'))
    formatted = encoded.decode('utf-8') 
    return formatted
  
  # returns true if any deleted
  def delete(self):
    from .model import rawdb, ObjectId
    collection = getattr(rawdb, self.model.__name__)
    result = collection.remove({ '_id': ObjectId(self.id) })
    return result['n']
  
  def get(self):
    try:
      return self.model(key=self)
    except:
      return None
  
  def __repr__(self):
    return '<db.Key %s>' % self.serialize()
  
  def __str__(self):
    return '<db.Key %s>' % self.serialize()


from .model import Model