""" LOCAL IMPORTS """
from .properties import Property, PropertyQuery, SortDescriptor
from .key import Key
import pymongo


class InvalidSortDescriptor(Exception):
  pass


# TODO once used the query iterator is done


class Query(object):
  """
  ' PURPOSE
  '   Is a form of lazy-loading for database queries.
  '   AKA provides iterators and helpful sorting and fetching
  '   actions that don't load memory until needed.
  """
  
  def __init__(self, model, logic_chain):
    """
    ' PURPOSE
    '   Construct the class with the given model and query
    '   logic chain.
    ' PARAMETERS
    '   <Model model>
    '   <LogicOperator logic_chain>
    ' RETURNS
    '   <Query query>
    """
    self._model = model
    self._logic_chain = logic_chain
    self._query = self._query()
  
  def _query(self):
    """
    ' PURPOSE
    '   Loads a pymongo cursor based on the given logic chain's bson.
    ' PARAMETERS
    '   None
    ' RETURNS
    '   <Iterator cursor>
    """
    collection = self._model._collection()
    bson = self._logic_chain.bson()
    cursor = collection.find(bson, projection={ '_id':1 })
    return cursor
  
  def filter(self, *args):
    """
    ' PURPOSE
    '   Combines the logic chain for this query with a new logic chain
    '   and returns the new resulting query object.
    ' PARAMETERS
    '   <PropertyQuery prop_query1>
    '   <PropertyQuery prop_query2>
    '   ...
    '   <PropertyQuery prop_queryN>
    ' RETURNS
    '   <Query query>
    """
    new_login_chain = AND(self.logic_chain, *args)
    return Query(self._model, new_login_chain)
  
  def fetch(self, count=0, offset=0, keys_only=False):
    """
    ' PURPOSE
    '   Returns a subsection of the queried models.
    ' PARAMETERS
    '   <int offset>
    '   <int count>
    '   <bool keys_only>
    ' RETURNS
    '   <list Key key> if keys_only
    '   <list Model model> if not keys_only
    """
    subsection = self._query[offset:offset+count]
    if keys_only:
      return [Key(self._model, str(document['_id'])) for document in subsection]
    return [Key(self._model, str(document['_id'])).get() for document in subsection]
  
  def count(self):
    """
    ' PURPOSE
    '   Returns the count of entities matched by this query.
    ' PARAMETERS
    '   NONE
    ' RETURNS
    '   <int count>
    """
    return self._query.count()
  
  def get(self, keys_only=False):
    """
    ' PURPOSE
    '   Returns the first model in this query or None if there
    '   isn't one.
    ' PARAMETERS
    '   <bool keys_only>
    ' RETURNS
    '   <Key key> if keys_only
    '   <Model model> if not keys_only
    """
    if self.count() == 0:
      return None
    
    key = Key(self._model, str(self._query[0]['_id']))
    if keys_only:
      return key
    return key.get()
  
  def order(self, sort_descriptor):
    if isinstance(sort_descriptor, Property):
      sort_descriptor = +sort_descriptor
    elif not isinstance(sort_descriptor, SortDescriptor):
      raise InvalidSortDescriptor()
    # TODO write this method
  
  def __iter__(self, *args, **kwargs):
    """
    ' PURPOSE
    '   Allows this class to be iterable by delegating to the iter
    '   method.
    ' NOTES
    '   1. see self.iter
    """
    return self.iter(*args, **kwargs)
  
  def iter(self, keys_only=False):
    """
    ' PURPOSE
    '   Is a generator that iterates over all entities matched by
    '   this query.
    ' PARAMETERS
    '   <bool keys_only>
    ' RETURNS
    '   <Key key> if keys_only
    '   <Model model> if not keys_only
    """
    for document in self._query:
      key = Key(self._model, str(document['_id']))
      if keys_only:
        yield key
      yield key.get()
  
  def __repr__(self):
    """
    ' see self.__str__
    """
    return self.__str__()
  
  def __str__(self):
    """
    ' PURPOSE
    '   Condensed, unique representation of the Query data.
    ' PARAMETERS
    '   None
    ' RETURNS
    '   <str str_value>
    """
    return '%s(kind=\'%s\', filters=%s)' % (self.__class__.__name__, self._model.__name__, self._logic_chain)


class LogicOperator(object):
  
  BSON_OPERATORS = {
    '==': '$eq',
    '<': '$lt',
    '>': '$gt',
    '!=': '$ne',
    '<=': '$lte',
    '>=': '$gte',
    'in': '$in',
    'not in': '$nin'
  }


class AND(LogicOperator):
  """
  ' PURPOSE
  '   Concatinates many property queries into a
  '   single and statement.
  ' EXAMPLE USAGE
  '   -> db.AND(User.email == 'john@doe.com', User.age < 25)
  """
  
  def flipped(self):
    """
    ' PURPOSE
    '   Returns a new AND filter containing the inverted
    '   comparison of this AND. AKA flips the logic of this filter.
    ' PARAMETERS
    '   None
    ' RETURNS
    '   <AND inverted_and>
    """
    partialqueries = [query.flipped() for query in self._partialqueries]
    return OR(*partialqueries)
  
  def __init__(self, *partialqueries):
    """
    ' PURPOSE
    '   Initializes the AND with given property queries.
    ' PARAMETERS
    '   <PropertyQuery propquery1>
    '   <PropertyQuery propquery2>
    '   ...
    '   <PropertyQuery propqueryN>
    ' RETURNS
    '   <AND and>
    ' NOTES
    '   1. May also take LogicOperator objects as arguments.
    """
    self._bson = None
    self._partialqueries = partialqueries
  
  def bson(self):
    # TODO make each property aware of it's name
    """
    ' PURPOSE
    '   Given a Model subclass class. Convert the property queries
    '   into a PyMongo compatible BSON query.
    '   * see https://docs.mongodb.org/manual/reference/operator/query/ *
    ' PARAMETERS
    '   <class MyModel extends Model>
    ' RETURNS
    '   <dict bson>
    ' NOTES
    '   1. Caches the result (memoize)
    """
    if not self._partialqueries: return {}
    if self._bson: return self._bson
    
    self._bson = { '$and': [] }
    and_query = self._bson['$and']
    
    for partialquery in self._partialqueries:
      if isinstance(partialquery, PropertyQuery):
        and_query.append({
          partialquery.property._name: {
            self.BSON_OPERATORS[partialquery.operator]: partialquery.property._pack(partialquery.value)
          }
        })
      elif isinstance(partialquery, LogicOperator):
        and_query.append(partialquery.bson())
    
    return self._bson
  
  def __repr__(self):
    """
    ' see self.__str__
    """
    return self.__str__()
  
  def __str__(self):
    """
    ' PURPOSE
    '   Condensed, unique representation of the AND data.
    ' PARAMETERS
    '   None
    ' RETURNS
    '   <str str_value>
    """
    parts = []
    
    for part in self._partialqueries:
      parts.append(repr(part))
    
    return 'AND(%s)' % ', '.join(parts)


class OR(LogicOperator):
  """
  ' PURPOSE
  '   Concatinates many property queries into a
  '   single or statement.
  ' EXAMPLE USAGE
  '   -> db.OR(User.email == 'john@doe.com', User.age < 25)
  """
  
  def flipped(self):
    """
    ' PURPOSE
    '   Returns a new OR filter containing the inverted
    '   comparison of this OR. AKA flips the logic of this filter.
    ' PARAMETERS
    '   None
    ' RETURNS
    '   <OR inverted_or>
    """
    partialqueries = [query.flipped() for query in self._partialqueries]
    return AND(*partialqueries)
  
  def __init__(self, *partialqueries):
    """
    ' PURPOSE
    '   Initializes the OR with given property queries.
    ' PARAMETERS
    '   <PropertyQuery propquery1>
    '   <PropertyQuery propquery2>
    '   ...
    '   <PropertyQuery propqueryN>
    ' RETURNS
    '   <OR or>
    ' NOTES
    '   1. May also take LogicOperator objects as arguments.
    """
    self._bson = None
    self._partialqueries = partialqueries
  
  def bson(self):
    """
    ' PURPOSE
    '   Given a Model subclass class. Convert the property queries
    '   into a PyMongo compatible BSON query.
    '   * see https://docs.mongodb.org/manual/reference/operator/query/ *
    ' PARAMETERS
    '   <class MyModel extends Model>
    ' RETURNS
    '   <dict bson>
    ' NOTES
    '   1. Caches the result (memoize)
    """
    if not self._partialqueries: return {}
    if self._bson: return self._bson
    
    self._bson = { '$or': [] }
    or_query = self._bson['$or']
    
    for partialquery in self._partialqueries:
      if isinstance(partialquery, PropertyQuery):
        or_query.append({
          partialquery.property._name: {
            self.BSON_OPERATORS[partialquery.operator]: partialquery.property._pack(partialquery.value)
          }
        })
      elif isinstance(partialquery, LogicOperator):
        or_query.append(partialquery.bson())
    
    return self._bson
  
  def __repr__(self):
    """
    ' see self.__str__
    """
    return self.__str__()
  
  def __str__(self):
    """
    ' PURPOSE
    '   Condensed, unique representation of the OR data.
    ' PARAMETERS
    '   None
    ' RETURNS
    '   <str str_value>
    """
    parts = []
    
    for part in self._partialqueries:
      parts.append(repr(part))
    
    return 'OR(%s)' % ', '.join(parts)


class NOT(LogicOperator):
  """
  ' PURPOSE
  '   Concatinates many property queries into a
  '   single not statement.
  ' EXAMPLE USAGE
  '   -> db.NOT(db.AND(User.email == 'john@doe.com', User.age < 25))
  """
  
  def __init__(self, logic_operator):
    """
    ' PURPOSE
    '   Initializes the NOT with a single logic operator.
    ' PARAMETERS
    '   <LogicOperator logic_operator>
    ' RETURNS
    '   <NOT not>
    """
    self._bson = None
    self._logic_operator = logic_operator
  
  def flipped(self):
    """
    ' PURPOSE
    '   Returns a new LogicOperator filter containing the inverted
    '   comparison of this NOT. AKA flips the logic of this filter.
    ' PARAMETERS
    '   None
    ' RETURNS
    '   <LogicOperator inverted_not>
    """
    return self._logic_operator
  
  def bson(self):
    """
    ' PURPOSE
    '   Given a Model subclass class. Convert the property queries
    '   into a PyMongo compatible BSON query.
    '   * see https://docs.mongodb.org/manual/reference/operator/query/ *
    ' PARAMETERS
    '   <class MyModel extends Model>
    ' RETURNS
    '   <dict bson>
    ' NOTES
    '   1. Caches the result (memoize)
    """
    if not isinstance(self._logic_operator, LogicOperator):
      raise ValueError('Expected subclass of LogicOperator. Instead got: %s' % type(self._logic_operator))
    
    if not self._logic_operator: return {}
    if self._bson: return self._bson
    
    # De Morgan's Law
    not_query = self._logic_operator.flipped()
    return not_query.bson()
  
  def __repr__(self):
    """
    ' see self.__str__
    """
    return self.__str__()
  
  def __str__(self):
    """
    ' PURPOSE
    '   Condensed, unique representation of the NOT data.
    ' PARAMETERS
    '   None
    ' RETURNS
    '   <str str_value>
    """
    return 'NOT(%s)' % self._logic_operator

