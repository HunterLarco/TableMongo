# TableMongo. A MongoDB ORM

Contributers&ensp;·&ensp;[Hunter Larco](http://hunterlarco.com)

> TableMongo syntax emulates Google's Python BigTable ORM, making it easier to transition from Google Cloud Platform to a MongoDB based systems.

## Example

```python
import TableMongo as db

class User(db.Model):
  email = db.StringProperty()
  password = db.StringProperty()
  favourite_things = db.StringProperty(multiple=True)

User(
  email='john@doe.com',
  password='p@ssword', 
  favourite_things=['apples', 'pie']
).save()

users = User.query(User.email == 'john@doe.com')
```

## Installation

Installation is super friendly using `pip`

```
$ pip install TableMongo
```

## Documentation

* [Quickstart](./Documentation/quickstart.md)