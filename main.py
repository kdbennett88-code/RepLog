from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import time
import os
# Import modules
from src.syntax_highlighter import highlight_python
from src.list_repo import list_repo_files
from src.render_source_file import render_source_file
from src import db   

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJ_DIR = os.path.join(BASE_DIR, "mirror")

IGNORE_NAMES = {"__pycache__", "venv", ".env", ".git", ".gitignore"}
IGNORE_EXTENSION = {".db", ".json", ".pyc"}

class Handler(BaseHTTPRequestHandler):

    # Helper: read query parameters
    def get_query_param(self, key, default=None):
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)
        return qs.get(key, [default])[0]

    # Helper: redirect
    def redirect(self, location):
        self.send_response(302)
        self.send_header("Location", location)
        self.end_headers()

    # Helper: admin check
    def is_admin(self):
        return self.client_address[0] == "127.0.0.1"

    # Helper: serve static or HTML
    def serve_file(self, relative_path, content_type):
        full_path = os.path.join(BASE_DIR, relative_path)
        try:
            with open(full_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-type", content_type)
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404, "[0] File not found")

    def serve_static(self, path):
        relative_path = path.lstrip("/")
        content_type = "text/css" if path.endswith(".css") else "application/octet-stream"
        self.serve_file(relative_path, content_type)

    # Iterates through the current directory and will filter out the dot files along wit# making sure that I and generating a new html page.
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
            self.send_error(404, "Cannot list directory[4]")
     
     # Will serve the html page with my projects repo present for the user      
    def serve_project_file(self, full_path):
        # Block dotfiles
        if os.path.basename(full_path).startswith("."):
            self.send_error(403, "Forbidden[5]")
            return
        # Block extensions
        for ext in IGNORE_EXTENSION:
            if full_path.endswith(ext):
                self.send_error(403, "Forbidden[6]")
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
            self.send_error(403, "File not found[7]")

    # -----------------------------
    # GET ROUTING
    # -----------------------------
    def do_GET(self):
        print("PATH:", repr(self.path))
        # Basic pages
        if self.path == "/":
            return self.serve_file("pages/index.html", "text/html")
        elif self.path == "/homelab":
            return self.serve_file("pages/homelab.html", "text/html")
        elif self.path == "/projects":
            return self.serve_file("pages/projects.html", "text/html")
        elif self.path == '/new_post':
            return self.serve_file('pages/new_post.html', 'text/html')

        # -----------------------------
        # Dynamic posts list
        # -----------------------------
        elif '/post' in self.path:
            
            posts = db.list_posts()
            html_posts = ""

            for p in posts:
                post_id = p[0]
                title = p[1]
                
                html_posts += (
                    f"<div class='card'>"
                    f"<a href='/post?id={post_id}' class='projects'>{title}</a>"
                    f"</div>"
                )
            print(html_posts)
            page_path = os.path.join(BASE_DIR, "pages", "posts.html")
            with open(page_path, "r") as f:
                page = f.read()

            page = page.replace("{{posts}}", html_posts)
            

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(page.encode())
            return

        # -----------------------------
        # Single post + replies
        # -----------------------------
        elif self.path.startswith("/post-reply"):
            post_id = self.get_query_param("id")
            if not post_id:
                return self.send_error(400, "[1] Missing post id")
            post_id = int(post_id)
            post = db.get_post(post_id)
            if not post:
                return self.send_error(404, "[2] Post not found")
            title = post[1]
            content = post[2]
            replies = db.list_replies(post_id)
            reply_html = ""
            for r in replies:
                reply_id = r[0]
                reply_content = r[2]
                reply_html += (
                    f"<div class='card'>{reply_content}"
                    f"<form action='/delete_reply' method='POST'>"
                    f"<input type='hidden' name='reply_id' value='{reply_id}'>"
                    f"<input type='hidden' name='post_id' value='{post_id}'>"
                    f"<button type='submit'>Delete</button>"
                    f"</form></div>"
                )
            page_path = os.path.join(BASE_DIR, "pages", "post-reply.html")
            with open(page_path, "r") as f:
                page = f.read()

            page = page.replace("{{title}}", title)
            page = page.replace("{{content}}", content)
            page = page.replace("{{id}}", str(post_id))
            page = page.replace("{{replies}}", reply_html)
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(page.encode())
            return

        # New post page (admin only)
        elif self.path == "/new_post":
            if not self.is_admin():
                return self.send_error(403, "[3] Forbidden")

            return self.serve_file("pages/new_post.html", "text/html")

        # Repo browser
        elif self.path.startswith('/projects/'):
            relative = self.path.replace('/projects/', '')
            full_path = os.path.join(PROJ_DIR, relative)
            # prevent directory traversal
            safe_path = os.path.normpath(full_path)
            if not safe_path.startswith(PROJ_DIR):
                return self.send_error(403, "[4] Forbidden")

        # Directory listing
            elif os.path.isdir(full_path):
                return self.list_directory(full_path)

        # File serving
            return self.serve_project_file(full_path)

        if self.path == "/repo":
            files = list_repo_files()
            html = "<html><body><h2>Repo Browser</h2><ul>"
            for f in files:
                link = f"/repo/file?name={f['name']}"
                html += f'<li><a href="{link}">{f["name"]}</a></li>'

            html += "</ul></body></html>"

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode())
            return

        elif self.path.startswith("/repo/file"):
            qs = parse_qs(urlparse(self.path).query)
            name = qs.get("name", [""])[0]
            full_path = os.path.join(PROJ_DIR, name)
            if not os.path.isfile(full_path):
                return self.send_error(404, "[5] File not found")

            html = render_source_file(full_path)

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode())
            return

        # Static files
        elif self.path.startswith("/static"):
            return self.serve_static(self.path)

        # Unknown route
        else:
            self.send_error(404, "[6] Page not found")

    # POST ROUTING
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode()
        params = {}
        for pair in body.split("&"):
            if "=" in pair:
                k, v = pair.split("=", 1)
                params[k] = v.replace("+", " ")

        # Create post (admin only)
        if self.path == "/create_post":
            if not self.is_admin():
                return self.send_error(403, "[7] Forbidden")
            title = params.get("title", "")
            content = params.get("content", "")
            db.create_post(title, content)
            return self.redirect("/posts")

        # Reply to post
        elif self.path == "/reply":
            post_id = int(params.get("post_id"))
            content = params.get("content", "")
            db.create_reply(post_id, content)
            return self.redirect(f"/post-reply?id={post_id}")

        # Delete reply (admin only)
        elif self.path == "/delete_reply":
            if not self.is_admin():
                return self.send_error(403, "[8] Forbidden")
            reply_id = int(params.get("reply_id"))
            post_id = int(params.get("post_id"))
            db.delete_reply(reply_id)
            return self.redirect(f"/post-reply?id={post_id}")

        # Unknown POST route
        else:
            self.send_error(404, "[10] Not Found")

# Server start
if __name__ == "__main__":
    db.init_db()

    server = ThreadingHTTPServer(("127.0.0.1", 8010), Handler)

    print("Serving..")
    server.serve_forever()
