from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import time
import os

# Serve files from this directory (where app.py lives)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/':
            self.serve_file('pages/index.html', 'text/html')
        elif self.path == '/projects':
            self.serve_file('pages/projects.html', 'text/html')
        elif self.path == '/posts':
            self.serve_file('pages/posts.html', 'text/html')
        elif self.path.startswith('/static'):
            self.serve_static(self.path)
        elif self.path == '/warp':
            self.serve_file('pages/warp.html', 'text/html')
        else:
            self.send_error(404, "Page not found")

    def serve_file(self, relative_path, content_type):
        full_path = os.path.join(BASE_DIR, relative_path)
        try:
            with open(full_path, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.end_headers()
            time.sleep(1)
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404, "File not found")

    def serve_static(self, path):
        # path looks like /static/style.css -> strip leading slash
        relative_path = path.lstrip('/')
        content_type = 'text/css' if path.endswith('.css') else 'application/octet-stream'
        self.serve_file(relative_path, content_type)


if __name__ == '__main__':
    server = ThreadingHTTPServer(('127.0.0.1', 8010), Handler)
    print("Serving on port 8010...")
    server.serve_forever()
