from . import inspector

from .key import Key
from .model import Model
from .properties import *


def start_development_server(port=8000):
  from threading import Thread
  Thread(target=inspector.run, args=(port,)).start()