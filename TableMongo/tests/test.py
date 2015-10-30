import db
import server






def TestKeysandIds():
  class Test(db.Model):
  
    value1 = db.StringProperty()
    value2 = db.StringProperty()
  
  entity = Test()
  entity.value1 = 'Test'
  entity.save()
  print(entity)

  print(entity.packed())
  print(entity.value1)
  print(Test.value1)

  print(entity.key)

  urlsafe = entity.key.urlsafe()
  print(urlsafe)

  key = db.Key(urlsafe=urlsafe)
  print(key)

  entity = key.get()
  print(entity)

  print(entity.packed())
  print(entity.value1)
  print(Test.value1)


  class Test(db.Model):
  
    value1 = db.Property()
    value2 = db.Property()
    value3 = db.Property()


  print(db.Model.__subclasses__())

  entity = Test(id=key.id)
  entity.value3 = 4
  entity.save()
  print(entity)

  print(entity.packed())
  print(entity.value3)


  print(key.serialize())
  entity = db.Key(serial=key.serialize()).get()
  print(entity)
  print(entity.packed())

  entity.delete()

  # should throw error
  entity = Test(id=key.id)
  


class Reference(db.Model):
  value1 = db.StringProperty()
  value2 = db.BooleanProperty()
  other = db.KeyProperty()


def TestPropertyPacking():
  
  entity = Reference()
  entity.value1 = 'E1V1'
  entity.value2 = True
  entity.save()
  
  print('First Entity Key   : %s' % entity.key)
  
  entity2 = Reference()
  entity2.value1 = 'E2V1'
  entity2.value2 = False
  entity2.other = entity.key
  entity2.save()

  print('Second Entity Key  : %s' % entity2.key)
  
  print('First Entity JSON  : %s' % entity.packed())
  print('Second Entity JSON : %s' % entity2.packed())




if __name__ == '__main__':
  db.start_development_server()
  # TestKeysandIds()
  TestPropertyPacking()
  
  