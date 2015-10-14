#!flask/bin/python
from flask import Flask, redirect, abort
app = Flask(__name__)

from flask import send_from_directory
from flask import request
from flask import render_template



@app.route('/')
def main():
  models = get_models()
  return redirect('/kind/%s' % models[0], code=302)


@app.route('/kind/<string:kind>')
def kindviewer(kind):
  models = get_models()
  
  if not kind in models:
    return abort(404)
  models.remove(kind)
  models = [kind] + models
  
  model = get_model(kind)
  documents = get_documents(model)
  properties = get_properties(model)
  
  return render_template('main.html', models=models, documents=documents, properties=properties)


@app.route('/entity/<string:serialized_key>')
def entityviewer(serialized_key):
  entity = get_entity(serialized_key)
  properties = get_properties(entity)
  packed = entity.packed(meta=True)
  return render_template('entity.html', entity=packed, properties=properties, kind=entity.kind)


@app.route('/images/<path:filename>')
def staticimages(filename):
    return send_from_directory(app.root_path + '/images/', filename)


@app.route('/resources/<path:filename>')
def staticresources(filename):
    return send_from_directory(app.root_path + '/resources/', filename)






def get_models():
  from ..model import Model
  return [model.__name__ for model in Model.__subclasses__()]

def get_model(modelname):
  from ..key import Key
  return Key.get_model(modelname)

def get_entity(serialized_key):
  from ..key import Key
  return Key(serial=serialized_key).get()

def get_properties(model):
  return model.get_properties()

def get_documents(model):
  return [model.packed(meta=True) for model in model.fetch()]





def run(port=8000, debug=False):
  import logging
  log = logging.getLogger('werkzeug')
  log.setLevel(logging.ERROR)
  
  app.run(port=port, debug=debug)
  print('db development server running on port %s' % port)

if __name__ == '__main__':
  run(debug=True)
  