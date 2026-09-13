from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import time
import os

# Serve files from this directory (where app.py lives)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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
    
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode()
    # Parse form data (key=value&key=value)
        params = {}
        for pair in body.split("&"):
            if "=" in pair:
                k, v = pair.split("=", 1)
                params[k] = v.replace("+", " ")
        # Route: create a new post (admin only)
        if self.path == "/create_post":
            if not self.is_admin():
                self.send_error(403, "Forbidden")
                return

            title = params.get("title", "")
            content = params.get('content', '')
            create_post(title, content)

            self.redirect("/posts")
            return
            # Route: reply to a post (public)
        if self.path == "/reply":
            post_id = int(params.get("post_id"))
            content = params.get("content", "")
            create_reply(post_id, content)

            self.redirect(f'/post?id={post_id}')
            return
        # if no route matched
        self.send_error(404, 'Not Found')

    def redirect(self, location):
        self.send_response(302)
        self.send_header("Location", location)
        self.end_headers()

    def is_admin(self):
        #only allow posting from localhost
        return self.client_address[0] == "127.0.0.1"

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
