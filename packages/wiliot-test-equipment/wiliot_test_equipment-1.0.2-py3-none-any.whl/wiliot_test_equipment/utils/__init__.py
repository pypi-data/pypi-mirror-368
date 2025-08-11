import re

def parse_h_defines(header_file):
    defines = {}
    with open(header_file, 'r') as file:
        for line in file:
            # Match lines like #define KEY VALUE
            match = re.match(r'#define\s+(\w+)\s+(.+)', line)
            if match:
                key, value = match.groups()
                # Clean value (strip quotes if present)
                value = value.strip().strip('"')
                defines[key] = value
    return defines
