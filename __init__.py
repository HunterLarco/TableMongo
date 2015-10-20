from .key import Key
from .model import Model
from .properties import *


def start_development_server(port=8000, debug=False, threading=True):
  from . import inspector
  # placed here so that when a flask server isn't running one can still use the db library
  if threading:
    from threading import Thread
    Thread(target=inspector.run, args=(port,debug)).start()
  else:
    inspector.run(port=port, debug=debug)