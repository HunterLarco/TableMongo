import unittest
from models import *


class TestCases(unittest.TestCase):
  
  def setUp(self):
    pass
  
  def test_meta_class(self):
    arr_equals = lambda a, b: len(set(a) ^ set(b)) == 0
    
    user_props = User.properties().names()
    assert arr_equals(user_props, ['email', 'password'])
    
    trip_props = Trip.properties().names()
    assert arr_equals(trip_props, ['author', 'waypoints'])
  
  def test_property_options(self):
    pass

  def test_saving(self):
    User.delete_all()
    Trip.delete_all()
    
    user = User(email='john@doe.com')
    user.set_password('p@ssword')
    user.save()
    
    trip = Trip(author=user)
    trip.waypoints = [Coordinate(4,5), Coordinate(10,8)]
    trip.save()
    
    trip = Trip(author=user)
    trip.waypoints = [Coordinate(0,1), Coordinate(-4,1), Coordinate(-4,5)]
    trip.save()
    
    user = User(email='jane@doe.com')
    user.set_password('n0tp@ssword')
    user.save()
    
    Trip(author=user, waypoints=[Coordinate(1,2)]).save()

  def test_getting(self):
    User.delete_all()
    Trip.delete_all()
    
    user = User(email='jack@doe.com')
    user.set_password('lolpass')
    user.save()
    
    user = User.get_by_id(user.key.id)
    assert user.email == 'jack@doe.com'
    assert user.compare_password('lolpass')
    
    user = User(key=user.key)
    assert user.email == 'jack@doe.com'
    assert user.compare_password('lolpass')
    
    user = user.key.get()
    assert user.email == 'jack@doe.com'
    assert user.compare_password('lolpass')
    
    user = User(id=user.key.id)
    assert user.email == 'jack@doe.com'
    assert user.compare_password('lolpass')

  def test_querying(self):
    User.delete_all()
    Trip.delete_all()
    
    # setup
    
    user = User(email='john@doe.com')
    user.set_password('p@ssword')
    user.save()
    
    trip = Trip(author=user)
    trip.waypoints = [Coordinate(4,5), Coordinate(10,8)]
    trip.save()
    
    trip = Trip(author=user)
    trip.waypoints = [Coordinate(0,1), Coordinate(-4,1), Coordinate(4,5)]
    trip.save()
    
    user = User(email='jane@doe.com')
    user.set_password('n0tp@ssword')
    user.save()
    
    Trip(author=user, waypoints=[Coordinate(-4,1)]).save()
    
    # tests
    
    query = User.query(User.email == 'john@doe.com')
    
    assert query.count() == 1
    assert query.get().compare_password('p@ssword')
    
    query = Trip.query(Trip.waypoints == [Coordinate(4,5)])
    
    assert query.count() == 2
    
    query = Trip.query(Trip.waypoints != [Coordinate(4,5)])
    
    assert query.count() == 1
    
    query = Trip.query(Trip.author == user)
    
    assert query.count() == 1
    assert query.get().author.email == 'jane@doe.com'
    
    query1 = Trip.query(Trip.waypoints == [Coordinate(4,5), Coordinate(-4,1)])
    query2 = Trip.query(db.OR(Trip.waypoints == Coordinate(4,5), Trip.waypoints == Coordinate(-4,1)))
    
    assert query1.count() == 1
    assert query2.count() == 3
    
    

    
    

if __name__ == '__main__':
  unittest.main()