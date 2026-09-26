import os
from src.syntax_highlighter import highlight_python

def render_source_file(full_path):
    with open(full_path) as f:
        raw = f.read()

    highlighted = highlight_python(raw)

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body class="code-body">
        <pre><code>{highlighted}</code></pre>
    </body>
    </html>
    """
