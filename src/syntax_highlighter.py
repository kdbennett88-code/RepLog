import re
import html

KEYWORDS = {
    'def', 'class', 'return', 'if', 'elif', 'else', 'for', 'while',
    'import', 'from', 'as', 'try', 'except', 'finally', 'with',
    'yield', 'lambda', 'pass', 'break', 'continue', 'in', 'is', 'not',
    'True', 'False', 'None'
}

def highlight_python(code):
    code = html.escape(code)

    code = re.sub(
        r'(#.*?$)',
        r'<span class="comment">\1</span>',
        code,
        flags=re.MULTILINE
    )

    code = re.sub(
        r'(&quot;.*?&quot;|&#x27;.*?&#x27;)',
        r'<span class="string">\1</span>',
        code
    )

    code = re.sub(
        r'\b(\d+)\b',
        r'<span class="number">\1</span>',
        code
    )

    for kw in KEYWORDS:
        code = re.sub(
            fr'(?<![=\w])\b{kw}\b(?![=\w])',
            fr'<span class="keyword">{kw}</span>',
            code
        )

    return code

