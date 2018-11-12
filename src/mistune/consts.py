HTML_TAGNAME = r'[A-Za-z][A-Za-z0-9-]*'
HTML_ATTRIBUTES = (
    r'(?:\s+[a-zA-Z_:][a-zA-Z0-9:._-]*'  # attribute name
    r'''(?:\s*=\s*(?:[^"'=<>`\x00-\x20]+|'[^']*'|"[^"]*"))?'''
    r')*'
)
