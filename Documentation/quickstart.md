# Quickstart

TableMongo is primarily based on the Model class. To demonstrate it's abilities we'll use it to build the infrastructure for a Trip Planner app backend.

### Installing TableMongo

Installation is super friendly using `pip`

```
$ pip install TableMongo
```

### Creating users

Lets quickly create a model. You can think of models as database "layouts". They dictate what types of data gets stored as well as what collection they belong to. In the following example we create a User collection that contains the fields email and password, both of which are strings.

```python
import TableMongo as db

class User(db.Model):
  email = db.StringProperty()
  password = db.StringProperty()
```

However storing plaintext passwords is bad practice, lets change that. We can add custom methods to each model like so.

```python
import TableMongo as db

class User(db.Model):
  email = db.StringProperty()
  password = db.StringProperty()
  
  def hash_password(self, password):
    from hashlib import sha256
    return sha256(password).hexdigest()
  
  def set_password(self, password):
    self.password = self.hash_password(password)
  
  def compare_password(self, password):
    return self.password == self.hash_password(password)
```

Now we can quickly create users and query them by their email.

```python
import TableMongo as db

#longhand
user = User()
user.email = 'john@doe.com'
user.set_password('p@ssword')
user.save()

#shorthand
user = User(email='john@doe.com')
user.set_password('p@assword')
user.save()

#query
users = User.fetch(User.email == 'john@doe.com')
```

### Creating trips

The trip model is not so different, but now lets create a new property that can store coordinates.

```python
import TableMongo as db


class Coordinate(object):

  def __init__(self, x=0, y=0):
    self.x = x
    self.y = y


class CoordinateProperty(db.Property):

  def pack(self, value):
    if value == None: return None
    if not isinstance(value, Coordinate):
      raise ValueError('CoordinateProperty must contain coordinate instance')
    return [value.x, value.y]
  
  def unpack(self, value):
    if value == None: return None
    return Coordinate(value[0], value[1])


class Trip(db.Model):
  waypoints = CoordinateProperty(multiple=True)
  author = db.ModelProperty(User)
```

We can now easily query trips by the user that created them and save multiple coordinates in them.

```python
user = User.fetch(User.email == 'john@doe.com')[0]

coordinates = [Coordinate(4, 5), Coordinate(8, -2)]
trip = Trip(author=user, waypoints=coordinates)
trip.save()

user_trips = Trip.fetch(Trip.author == user)
```

### Summary

Models are powerful tools to store data, reference functions, and create new properties.