import datetime
from functions.parse_ddl import parse_multiple_schemas


def validate_json(schema: dict, json_data: dict) -> dict:
    errors = {}
    is_valid = True
    data = json_data.get('data', {})

    for table_name, rows in data.items():
        if table_name not in schema:
            errors[table_name] = [f"Table '{table_name}' not defined in schema."]
            is_valid = False
            continue

        table_schema = schema[table_name]
        table_errors = []

        for i, row in enumerate(rows):
            row_errors = validate_row(row, table_schema)
            if row_errors:
                table_errors.append({f"row_{i}": row_errors})
                is_valid = False

        if table_errors:
            errors[table_name] = table_errors
    
    if is_valid:
        errors = None

    return {'is_valid': is_valid, 'errors': errors}


def validate_row(row, table_schema):
    errors = []
    columns = table_schema['columns']
    enums = table_schema['enums']

    for col_name, col_schema in columns.items():
        value = row.get(col_name)

        # Nullability check
        if value is None:
            if not col_schema.get('nullable', True):
                errors.append(f"Missing or null required field '{col_name}'.")
            continue

        # ENUM validation
        if col_schema['type'] == 'ENUM':
            if col_name in enums and value not in enums[col_name]:
                errors.append(f"Invalid ENUM value for '{col_name}': {value}. Expected: {enums[col_name]}")
            continue

        # Type check
        col_type = col_schema['type']
        try:
            if col_type == 'INT':
                if not isinstance(value, int):
                    raise ValueError("Expected INT")
            elif col_type == 'DECIMAL':
                float_val = float(value)
                if 'precision' in col_schema and 'scale' in col_schema:
                    total_digits = len(str(int(float_val)))
                    decimals = len(str(value).split('.')[-1]) if '.' in str(value) else 0
                    if total_digits > col_schema['precision'] - col_schema['scale'] or decimals > col_schema['scale']:
                        raise ValueError("Exceeds DECIMAL precision or scale")
            elif col_type == 'VARCHAR':
                if not isinstance(value, str):
                    raise ValueError("Expected string")
                if 'length' in col_schema and len(value) > col_schema['length']:
                    raise ValueError(f"Exceeds max length {col_schema['length']}")
            elif col_type == 'DATE':
                datetime.datetime.strptime(value, "%Y-%m-%d")  # Strict date format
            elif col_type == 'TEXT':
                if not isinstance(value, str):
                    raise ValueError("Expected text string")
        except Exception as e:
            errors.append(f"Invalid value for '{col_name}': {value}. Error: {str(e)}")

        # Check constraint evaluation (basic)
        if 'check' in col_schema:
            check_expr = col_schema['check']
            try:
                # Safe eval of the constraint
                if not eval(check_expr, {}, {col_name: value}):
                    errors.append(f"Check constraint failed for '{col_name}': {check_expr}")
            except Exception as e:
                errors.append(f"Error evaluating check constraint for '{col_name}': {str(e)}")

    return errors


ddl = """
-- Create the 'Performance_Reviews' table
CREATE TABLE Performance_Reviews (
    review_id INT PRIMARY KEY AUTO_INCREMENT,
    employee_id INT NOT NULL,
    reviewer_id INT NOT NULL,  -- Self-referencing foreign key
    review_date DATE NOT NULL,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    coverage_amount DECIMAL(10, 2),
    benefit_type VARCHAR(100) NOT NULL,
    comments TEXT,
    goals_set TEXT,
    review_status ENUM('Draft', 'Final', 'Approved') DEFAULT 'Draft',
    FOREIGN KEY (employee_id) REFERENCES Employees(employee_id),
    FOREIGN KEY (reviewer_id) REFERENCES Employees(employee_id)
);
"""

json_data = {
    "data": {
        "Performance_Reviews": [
            {
                "review_id": 1,
                "employee_id": 10,
                "reviewer_id": 12,
                "review_date": "2024-05-12",
                "rating": 6,  
                "coverage_amount": 12345.678,  
                "benefit_type": "Health",
                "comments": "Good progress",
                "goals_set": None,
                "review_status": "Final"
            }
        ]
    }
}


if __name__ == "__main__":
    schema = parse_multiple_schemas(ddl)
    result = validate_json(schema, json_data)

    print(result)