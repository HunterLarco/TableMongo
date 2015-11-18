from router import SimpleServer, RequestHandler
import os
from jinja2 import Template


class MainHandler(RequestHandler):
  
  def get(self):
    # self.send_response(200)
    # self.send_header('Content-Type', 'text/html')
    # self.end_headers()
    
    file = open(os.path.join(os.path.dirname(__file__), 'templates/main.html'), 'rb')
    html = file.read()
    
    template = Template(html)
    templated = template.render(models=['Test Jinja2'])
    
    self.write(templated)
  
  def post(self):
    raise NotImplemented


def run(port=8080, host='', debug=False):
  SimpleServer([
    ('/.*', MainHandler)
  ], debug=debug, port=port, host=host).serve()