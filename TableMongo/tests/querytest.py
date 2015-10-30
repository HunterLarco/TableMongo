import db


class Person(db.Model):
  name = db.StringProperty()
  age = db.FloatProperty()
  things = db.StringProperty(multiple=True)
  
  def __str__(self):
    return 'PERSON: %s, %s' % (self.name, self.age)


def test():
  Person.delete_all()

  Person(name='Jane Doe', age=18.2, things=['Chair','Laptop','Tea','Book']).save()
  Person(name='John Doe', age=22.9, things=['Laptop','TV','Book']).save()
  Person(name='Uncle Doe', age=40.1, things=['Chair','TV']).save()
  Person(name='Uncle Doe', age=34.1, things=['Chair','Tea']).save()
  Person(name='Aunty Doe', age=42.6, things=['Tea','Book']).save()

  print([str(person) for person in Person.fetch(Person.name == 'Uncle Doe')])
  print([str(person) for person in Person.fetch(Person.name == 'Uncle Doe', Person.age < 35.)])
  print([str(person) for person in Person.fetch(Person.name == 'Uncle Doe', Person.age > 35.)])
  print([str(person) for person in Person.fetch(Person.name == 'Uncle Doe', Person.age > 30.)])
  print([str(person) for person in Person.fetch(18. < Person.age, Person.age < 25.)])
  
  # print(18. < Person.age < 25.)
  # print(18. < Person.age and Person.age < 25.)
  # print((18 < Person.age).and(Person.age < 25.0).or(Person.name == 'Aunty Doe'))
  
  print('eq',[str(person) for person in Person.fetch(Person.things == ['Chair', 'Tea'])])  # AND
  print('ne',[str(person) for person in Person.fetch(Person.things != ['Chair', 'Tea'])])  # NAND

if __name__ == '__main__':
  test()