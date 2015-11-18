import SimpleHTTPServer
import SocketServer
import urlparse
import re


_SimpleServerInstance = None


class NullHandlerException(Exception):
  pass
class UnknownRequestMethod(Exception):
  pass


class BaseHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
  def _handleRequest(self, method):
    if _SimpleServerInstance is None: return
    _SimpleServerInstance._route(self, method, self.path)
  
  def do_GET(self):
    self._handleRequest('GET')
  
  def do_POST(self):
    self._handleRequest('POST')
  
  @classmethod
  def serve(cls, port=8080, host=''):
    server = SocketServer.TCPServer((host, port), cls)
    return server


class SimpleServer(object):
  def __init__(self, routemap, debug=False, port=8080, host=''):
    global _SimpleServerInstance
    _SimpleServerInstance = self
    
    self._server = None
    self._routemap = routemap
    self._debug = debug
    self._port = port
    self._host = host
  
  def _route(self, basehandler, method, path):
    parsedPath = urlparse.urlparse(path)
    
    for regex, handler in self._routemap:
      if re.match(regex+'$', parsedPath.path):
        requesthandler = handler(basehandler)
        break
    else:
      raise NullHandlerException('No handler matches path: {}'.format(path))
    
    requesthandler._trigger(method)
  
  def serve(self):
    server = BaseHandler.serve(port=self._port, host=self._host)
    self._server = server
    server.serve_forever()
  
  def close(self):
    server.server_close()


class RequestHandler(object):
  def __init__(self, basehandler):
    self._basehandler = basehandler
  
  def write(self, text):
    self._basehandler.wfile.write(text)
  
  def _closeWrites(self):
    self._basehandler.wfile.close()
  
  def _trigger(self, method):
    method = method.lower()
    if method == 'get':
      self.get()
    elif method == 'post':
      self.post()
    else:
      raise UnknownRequestMethod('Unknown request method %s' % method)
    self._closeWrites()
  
  def get(self):
    raise NotImplemented
  
  def post(self):
    raise NotImplemented
