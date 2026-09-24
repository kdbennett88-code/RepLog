import re
import html

KEYWORDS = {
    'def', 'class', 'return', 'if', 'elif', 'else', 'for', 'while',
    'import', 'from', 'as', 'try', 'except', 'finally', 'with',
    'yield', 'lambda', 'pass', 'break', 'continue', 'in', 'is', 'not',
    'True', 'False', 'None'
}

def safe_escape(code):
    """Escape only the HTML characters that can break the page."""
    return (
        code.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
    )

def highlight_python(code):
    # Escape ONLY <, >, &
    code = safe_escape(code)

    # Comments
    code = re.sub(
        r'(#.*?$)',
        r'<span class="comment">\1</span>',
        code,
        flags=re.MULTILINE
    )

    # Strings — now quotes are REAL quotes
    code = re.sub(
        r'(\".*?\"|\'.*?\')',
        r'<span class="string">\1</span>',
        code
    )

    # Numbers
    code = re.sub(
        r'\b(\d+)\b',
        r'<span class="number">\1</span>',
        code
    )

    # Keywords
    for kw in KEYWORDS:
        code = re.sub(
            fr'(?<![=\w])\b{kw}\b(?![=\w])',
            fr'<span class="keyword">{kw}</span>',
            code
        )

    return code

