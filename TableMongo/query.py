""" LOCAL IMPORTS """
from .properties import Property, PropertyQuery


class LogicOperator(object):
  pass


class AND(LogicOperator):
  """
  ' PURPOSE
  '   Concatinates many property queries into a
  '   single and statement.
  ' EXAMPLE USAGE
  '   -> db.AND(User.email == 'john@doe.com', User.age < 25)
  """
  
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
  
  def bson(self, modelcls):
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
    
    attr_map = {}
    
    for attr in vars(modelcls):
      val = getattr(modelcls, attr)
      if isinstance(val, Property):
        attr_map[val] = attr
    
    self._bson = { '$and': [] }
    and_query = self._bson['$and']
    
    for partialquery in self._partialqueries:
      if isinstance(partialquery, PropertyQuery):
        and_query.append({
          attr_map[partialquery.property]: {
            partialquery.operator: partialquery.property._pack(partialquery.value)
          }
        })
      elif isinstance(partialquery, LogicOperator):
        and_query.append(partialquery.bson(modelcls))
    
    return self._bson


class OR(LogicOperator):
  """
  ' PURPOSE
  '   Concatinates many property queries into a
  '   single or statement.
  ' EXAMPLE USAGE
  '   -> db.OR(User.email == 'john@doe.com', User.age < 25)
  """
  
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
  
  def bson(self, modelcls):
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
    
    attr_map = {}
    
    for attr in vars(modelcls):
      val = getattr(modelcls, attr)
      if isinstance(val, Property):
        attr_map[val] = attr
    
    self._bson = { '$or': [] }
    or_query = self._bson['$or']
    
    for partialquery in self._partialqueries:
      if isinstance(partialquery, PropertyQuery):
        or_query.append({
          attr_map[partialquery.property]: {
            partialquery.operator: partialquery.property._pack(partialquery.value)
          }
        })
      elif isinstance(partialquery, LogicOperator):
        or_query.append(partialquery.bson(modelcls))
    
    return self._bson