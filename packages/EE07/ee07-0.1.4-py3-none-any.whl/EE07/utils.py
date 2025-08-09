import re

def extract_chem_functions(code: str):
    """Find EE07-specific chemical functions using regex"""
    pattern = r"(react\(.+?\)|bind\(.+?\)|structure\(.+?\)|release\(.+?\)|delay\(.+?\)|trig\(.+?\))"
    return re.findall(pattern, code)

def clean_cpp_code(code: str):
    """Remove or comment out EE07-only functions before compiling in g++"""
    lines = code.splitlines()
    cleaned = []
    for line in lines:
        if any(f in line for f in ['react(', 'bind(', 'structure(', 'release(', 'delay(', 'trig(']):
            cleaned.append(f"// [EE07] {line}")
        else:
            cleaned.append(line)
    return "\n".join(cleaned)
