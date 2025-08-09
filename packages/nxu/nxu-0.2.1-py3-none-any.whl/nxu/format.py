import black

def format_code(code: str):
    return black.format_str(code, mode=black.Mode())