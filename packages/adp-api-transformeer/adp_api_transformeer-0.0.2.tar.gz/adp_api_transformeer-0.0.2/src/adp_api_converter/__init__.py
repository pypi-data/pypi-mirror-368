import sys
import json
import yaml
import argparse
import os


def load_spec(file_path):
    with open(file_path, 'r') as f:
        if file_path.endswith(('.yaml', '.yml')):
            return yaml.safe_load(f)
        elif file_path.endswith('.json'):
            return json.load(f)
        else:
            raise ValueError("Unsupported file format. Please provide a .json or .yaml file.")

def generate_operation_id(method, path):
    clean_path = path.strip('/').replace('/', '_').replace('{', '').replace('}', '')
    return f"{method}_{clean_path}"+"-{{consumerphase}}"

def add_missing_attributes(spec):
    if 'info' not in spec or not isinstance(spec['info'], dict):
        spec['info'] = {}
    spec['info']['title'] = '{{apiTitle}}'

    paths = spec.get('paths', {})
    for path, methods in paths.items():
        for method, operation in methods.items():
            if not isinstance(operation, dict):
                continue
            if 'operationId' not in operation:
                operation['operationId'] = generate_operation_id(method, path)
            if 'summary' not in operation:
                operation['summary'] = f"{method.upper()} {path}"
    return spec

def save_as_json(spec, output_path):
    with open(output_path, 'w') as f:
        json.dump(spec, f, indent=2)
def convert_api_spec():
    parser = argparse.ArgumentParser(description="Modify OpenAPI spec and output as JSON.")
    parser.add_argument("input_file", help="Path to the input OpenAPI spec file (JSON or YAML).")
    parser.add_argument("output_file", nargs='?', default="openapi.json", help="Path to the output JSON file.")
    args = parser.parse_args()
    input_path = os.path.abspath(args.input_file)
    output_path = os.path.abspath(args.output_file)
    spec = load_spec(input_path)
    modified_spec = add_missing_attributes(spec)
    save_as_json(modified_spec, output_path)
    print(f"Modified OpenAPI spec saved to {output_path}")

