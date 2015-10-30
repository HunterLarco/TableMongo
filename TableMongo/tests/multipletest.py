import db


class Child(db.Model):
  name = db.StringProperty()
  age = db.FloatProperty()

  def __str__(self):
    return 'CHILD: %s, %s' % (self.name, self.age)


class Parent(db.Model):
  children = db.ModelProperty(Child, multiple=True)

  def __str__(self):
    return 'PARENT: %s' % (self.children)


def test():
  Parent.delete_all()
  Child.delete_all()
  
  children = [
    Child(name='Thing1', age=3.),
    Child(name='Thing2', age=3.5),
    Child(name='Thing3', age=4.)
  ]
  
  for child in children:
    child.save()
  
  Parent(children=children).save()

  parent = Parent.fetch()[0]
  for child in parent.children:
    print(child)

if __name__ == '__main__':
  test()