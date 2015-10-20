""" LOCAL IMPORTS """
from .properties import Property


class AND(object):
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
      and_query.append({
        attr_map[partialquery.property]: {
          partialquery.operator: partialquery.property.pack(partialquery.value)
        }
      })
    
    return self._bson
        