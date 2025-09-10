import re
from collections import defaultdict


def parse_multiple_schemas(ddl):
    tables = {}
    table_blocks = re.findall(r'CREATE TABLE (\w+)\s*\((.*?)\);', ddl, re.DOTALL)

    for table_name, body in table_blocks:
        columns = {}
        enums = {}
        lines = [line.strip() for line in body.splitlines() if line.strip() and not line.strip().startswith('--')]

        for line in lines:
            # Remove trailing comma and inline comments
            line = re.sub(r'--.*', '', line).strip().rstrip(',')

            # Skip foreign keys for now
            if line.upper().startswith("FOREIGN KEY"):
                continue

            # ENUM type
            enum_match = re.match(r'(\w+)\s+ENUM\s*\((.+?)\)(.*)', line, re.IGNORECASE)
            if enum_match:
                col_name, enum_values, extras = enum_match.groups()
                enums[col_name] = [val.strip(" '") for val in enum_values.split(',')]
                columns[col_name] = {
                    'type': 'ENUM',
                    'nullable': 'NOT NULL' not in extras.upper(),
                    'default': extract_default(extras),
                }
                continue

            # Generic column with optional constraints
            col_match = re.match(r'(\w+)\s+([A-Z]+)(\((.*?)\))?(.*)', line, re.IGNORECASE)
            if col_match:
                col_name, col_type, _, params, extras = col_match.groups()
                col_info = {
                    'type': col_type.upper(),
                    'nullable': 'NOT NULL' not in extras.upper(),
                }

                # Extract size/scale/precision
                if col_type.upper() == 'VARCHAR' and params:
                    col_info['length'] = int(params)
                elif col_type.upper() == 'DECIMAL' and params:
                    precision, scale = map(int, params.split(','))
                    col_info['precision'] = precision
                    col_info['scale'] = scale

                # Extract default
                default = extract_default(extras)
                if default is not None:
                    col_info['default'] = default

                # Extract CHECK constraints
                check = extract_check(extras)
                if check:
                    col_info['check'] = check

                columns[col_name] = col_info

        tables[table_name] = {
            'columns': columns,
            'enums': enums
        }
    
    return tables

def extract_default(extras):
    match = re.search(r"DEFAULT\s+(['\"]?\w+['\"]?)", extras, re.IGNORECASE)
    return match.group(1).strip("'\"") if match else None

def extract_check(extras):
    match = re.search(r"CHECK\s*\((.+?)\)", extras, re.IGNORECASE)
    return match.group(1).strip() if match else None