from http.server import HTTPServer, BaseHTTPRequestHandler

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'(h1)Hello from my Python server </h1>')

server = HTTPServer(('127.0.0.1', 8000),Handler)
print('Serving on port 8000')
server.serve_forever()
