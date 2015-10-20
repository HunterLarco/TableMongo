""" LOCAL IMPORTS """
from .key import Key
from .model import Model
from .properties import *
from .query import *


def start_development_server(port=8000, debug=False, threading=True):
  """
  ' PURPOSE
  '   Begins a local server that allows one to easily browse
  '   the database in the browser.
  ' PARAMETERS
  '   optional <int port> the local port to host the server on
  '   optional <bool debug> allow verbose debugging or not
  '   optional <bool threading> start the server on a new thread or not
  ' RETURNS
  '   Nothing
  """
  # the inspector requires flask modules to be installed in order
  # to run. Hence the import is only called when beginning the
  # inspection server so that one can use the db library without
  # requiring flask. The inspector will simply be un-usable.
  from . import inspector

  if threading:
    from threading import Thread
    Thread(target=inspector.run, args=(port,debug)).start()
  else:
    inspector.run(port=port, debug=debug)