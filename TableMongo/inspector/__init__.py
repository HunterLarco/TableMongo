def run(port=8000, debug=False):
  print('db development server running on port %s' % port)
  
  import SimpleHTTPServer
  import SocketServer

  import urlparse

  class MyRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    
    def do_GET(self):
      
      print(dir(self.request))

      # Parse query data & params to find out what was passed
      parsedParams = urlparse.urlparse(self.path)
      queryParsed = urlparse.parse_qs(parsedParams.query)

      # request is either for a file to be served up or our test
      if parsedParams.path == "/test":
        self.processMyRequest(queryParsed)
      else:
        # Default to serve up a local file 
        SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self);

    def processMyRequest(self, query):

      self.send_response(200)
      self.send_header('Content-Type', 'text/html')
      self.end_headers()

      import os

      file = open(os.path.join(os.path.dirname(__file__), 'templates/main.html'), 'rb')
      html = file.read()
      self.wfile.write(html)
      self.wfile.close();

  if not debug:
    MyRequestHandler.log_message = lambda *args, **kwargs: None

  Handler = MyRequestHandler
  server = SocketServer.TCPServer(('', port), Handler)

  try:
    server.serve_forever()
  except KeyboardInterrupt:
    pass
    server.server_close()
