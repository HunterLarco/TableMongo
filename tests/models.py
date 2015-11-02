import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import TableMongo as db


class User(db.Model):
  email = db.StringProperty(required=True)
  password = db.StringProperty(required=True)

  def hash_password(self, password):
    from hashlib import sha256
    return sha256(password).hexdigest()

  def set_password(self, password):
    self.password = self.hash_password(password)

  def compare_password(self, password):
    return self.password == self.hash_password(password)


class Coordinate(object):

  def __init__(self, x=0, y=0):
    self.x = x
    self.y = y
  
  def __repr__(self):
    return 'Coordinate(x=%s, y=%s)' % (self.x, self.y)

class CoordinateProperty(db.Property):
  
  @staticmethod
  def type():
    return Coordinate

  def pack(self, value):
    return [value.x, value.y]

  def unpack(self, value):
    return Coordinate(value[0], value[1])


class Trip(db.Model):
  waypoints = CoordinateProperty(multiple=True, default=[])
  author = db.ModelProperty(User, required=True)