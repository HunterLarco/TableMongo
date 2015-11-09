import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import TableMongo as db


if __name__ == '__main__':
  db.inspector.run()