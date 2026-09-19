from src.syntax_highlighter import highlight_python
from src.list_repo import list_repo_files
from src.render_source_file import render_source_file
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import time
import os

# Serve files from this directory (where app.py lives)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJ_DIR = os.path.join(BASE_DIR, "mirror")

# What I need list_directory to ignore when parsin the repo
IGNORE_NAMES = {
        "__pycache__",
        "venv",
        ".env",
        ".git",
        ".gitignore"
        }
IGNORE_EXTENSION = {
        ".db",
        ".json",
        ".pyc"
        }

class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/':
            self.serve_file('pages/index.html', 'text/html')
        elif self.path == '/projects':
            self.serve_file('pages/projects.html', 'text/html')
# This is the start of when the user may be lookning through my projects repo's

        elif self.path.startswith('/projects/'):
            relative = self.path.replace("/projects/", "")
            full_path = os.path.join(PROJ_DIR, relative)
# Not neccessary but is smart for extra safety in ensuring the user cant travel outside
# of my actual replog repo... May have to come back to this and strengthen.

            safe_path = os.path.normpath(full_path)
            if not safe_path.startswith(PROJ_DIR):
                self.send_error(403, "Forbidden[00]")

            if os.path.isdir(full_path):
                return self.list_directory(full_path)
            else:
                return self.serve_project_file(full_path)

            try:
                with open(full_path, "rb") as f:
                    content. f.read()
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(content)
            except:
                self.send_error(404, 'File not found[0]')
# This block is going to be accessing my src/personal repo, and going through the 
# highlighting and repo file finder etc.. slightly confusing but is making sense..
        elif self.path == '/repo':
            files = list_repo_files()
            html = "<html><body><h2>Repo Browser</h2><ul>"
            for f in files:
                link = f"/repo/file?name={f['name']}</a></li>"
                html += f'<li><a href="{link}">{f["name"]}</a></li>'
            html += "</ul></body></html>"

            self.send_response(200)
            self.send_headers()
            self.wfile.write(html.encode())

        elif self.path.startswith('/repo/file'):
            from urllib.parse import urlparse, parse_qs

            qs = parse_qs(urlparse(self.path).query)
            name = qs.get("name", [""])[0]

            full_path = os.path.join(PROJ_DIR, name)

            if not os.path.isfile(full_path):
                self.send_error(404, "File not found[0.5]")
                return

            html = render_source_file(full_path)
            send.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode())

        elif self.path == '/posts':
            self.serve_file('pages/posts.html', 'text/html')
        elif self.path.startswith('/static'):
            self.serve_static(self.path)
        elif self.path == '/warp':
            self.serve_file('pages/warp.html', 'text/html')
        else:
            self.send_error(404, "Page not found[1]")
    
# list_directory, and serve_project_file are both helper functions for being able to 
# serve proper src files and expose my own native repo and not have to depend on github.

    def list_directory(self, path):
        try:
            entries = os.listdir(path)
            entries.sort()
            
            filtered = []
            for name in entries:
                if name.startswith('.'):
                    continue
                if name in IGNORE_NAMES:
                    continue
                for ext in IGNORE_EXTENSION:
                    if name.endswith(ext):
                        break
                else:
                    filtered.append(name)
            html = "<html><body><h2><Directory listings</h2><ul>"
            for name in filtered:
                link = f"{self.path.rstrip('/')}/{name}"
                html += f'<li><a href="{link}">{name}</a></li>'
            html += "</ul></body></html>"
                
            
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode())
        except Exception:
            self.send_error(404, "Cannot list directory[2]")

    def serve_project_file(self, full_path):
        # Block dotfiles
        if os.path.basename(full_path).startswith("."):
            self.send_error(403, "Forbidden[3]")
            return
        # Block extensions
        for ext in IGNORE_EXTENSION:
            if full_path.endswith(ext):
                self.send_error(403, "Forbidden[4]")
                return
# Try to parse the html and pass files through the highlight_python function and use
# HTML injection... Study all this!!
        try:
            with open(full_path, "r") as f:
                raw = f.read()
            highlighted = highlight_python(raw)
            html = f"""
            <html>
            <head>
                <link rel="stylesheet" href="/static/style.css">
            </head>
            <body class="code-body">
                <pre><code>{highlighted}</code></pre>
            </body>
            </html>
            """
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode())
        except FileNotFoundError:
            self.send_error(403, "File not found[5]")


# Data base logic being invoked I need to go over this and then test the functions still.

    
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
                self.send_error(403, "Forbidden[4]")
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
        self.send_error(404, 'Not Found[5]')

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
