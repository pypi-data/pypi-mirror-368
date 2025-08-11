import argparse
import dataclasses
from dataclasses import fields, MISSING, asdict
from typing import Optional, Union, get_origin, get_args, Type, List
import enum
import json
import sys
import types
import inspect
import re

# Global sentinel for not provided values.
NOT_PROVIDED = object()

class NoMetavarFormatter(argparse.HelpFormatter):
    """Custom formatter that removes metavar display for cleaner help output."""
    
    def _format_action_invocation(self, action):
        if not action.option_strings:
            default = self._get_default_metavar_for_positional(action)
            metavar, = self._metavar_formatter(action, default)(1)
            return metavar
        else:
            parts = []
            # Only add option strings, skip metavar
            if action.option_strings:
                parts.extend(action.option_strings)
            return ', '.join(parts)

class SpecialLoadMarker:
    """Marker class used to denote a field that supports JSON config loading."""
    pass

def bool_converter(s):
    """Convert string representations to boolean values (case-insensitive: yes/no, true/false)."""
    if isinstance(s, bool):
        return s
    lower = s.lower()
    if lower in ("yes", "true", "t", "y", "1"):
        return True
    elif lower in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError(f"Invalid boolean value: {s}")

def extract_field_comments(cls: Type) -> dict:
    """
    Extract comments above fields and inline comments from the class's source code.
    Returns a dictionary mapping field names to the concatenated comment string.
    Only effective when the source code is accessible.
    """
    try:
        source = inspect.getsource(cls)
    except Exception:
        return {}
    lines = source.splitlines()
    field_pattern = re.compile(r'^\s*(\w+)\s*:')  # matches "field_name :"
    field_help = {}
    current_comments = []
    in_multiline_comment = False
    multiline_buffer = []
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Handle multiline comments (''' or """)
        if not in_multiline_comment and (stripped.startswith('"""') or stripped.startswith("'''")):
            if stripped.count('"""') >= 2 or stripped.count("'''") >= 2:
                # Single line multiline comment like '''comment'''
                content = stripped[3:-3].strip()
                if content:
                    multiline_buffer.append(content)
            else:
                # Start of multiline comment
                content = stripped[3:].strip()
                if content:
                    multiline_buffer.append(content)
                in_multiline_comment = True
            continue
        
        if in_multiline_comment:
            if stripped.endswith('"""') or stripped.endswith("'''"):
                # End of multiline comment
                content = stripped[:-3].strip()
                if content:
                    multiline_buffer.append(content)
                in_multiline_comment = False
            else:
                # Content inside multiline comment
                if stripped:
                    multiline_buffer.append(stripped)
            continue
        
        # Handle regular comments
        if stripped.startswith('#'):
            comment_text = stripped.lstrip('#').strip()
            current_comments.append(comment_text)
        else:
            # Check if this line contains a field definition
            m = field_pattern.match(line)
            if m:
                field_name = m.group(1)
                all_comments = []
                
                # Add preceding comments
                if current_comments:
                    all_comments.extend(current_comments)
                
                # Add multiline comments
                if multiline_buffer:
                    all_comments.extend(multiline_buffer)
                    multiline_buffer = []
                
                # Check for inline comment
                if '#' in line:
                    comment_start = line.find('#')
                    inline_comment = line[comment_start+1:].strip()
                    if inline_comment:
                        all_comments.append(inline_comment)
                
                if all_comments:
                    field_help[field_name] = " ".join(all_comments)
                
                current_comments = []
            else:
                # Reset comments if we encounter a non-comment, non-field line that's not empty
                if stripped and not stripped.startswith('#'):
                    current_comments = []
                    if multiline_buffer:
                        multiline_buffer = []
    
    return field_help

def get_by_path(d: dict, path: str):
    """Retrieve a value from a nested dictionary 'd' based on a dot-separated path."""
    parts = path.split('.')
    current = d
    for p in parts:
        if isinstance(current, dict) and p in current:
            current = current[p]
        else:
            return None
    return current

def set_by_path(d: dict, path: str, set_value):
    """Set a value in a nested dictionary 'd' based on a dot-separated path."""
    parts = path.split('.')
    current = d
    for p in parts[:-1]:
        if p not in current or not isinstance(current[p], dict):
            current[p] = {}
        current = current[p]
    # Set the final value
    current[parts[-1]] = set_value
    

def remove_by_path(d: dict, path: str):
    """Remove a key from a nested dictionary 'd' based on a dot-separated path."""
    parts = path.split('.')
    current = d
    for p in parts[:-1]:
        if p in current:
            current = current[p]
        else:
            return
    current.pop(parts[-1], None)

def convert_type(typ: Type):
    """
    Return a conversion function for the given type.
    For bool type, use the custom bool_converter;
    for Enum types, match based on the enum member name;
    otherwise, return the type itself.
    """
    if typ is bool:
        return bool_converter
    if isinstance(typ, type) and issubclass(typ, enum.Enum):
        return lambda s: typ[s]
    return typ

def convert_value(value, target_type: Type):
    """
    Convert 'value' to 'target_type'. Supports conversion for bool, Enum, list,
    and basic types. If value is None, returns None.
    """
    if value is None:
        return None

    if get_origin(target_type) in (Union, types.UnionType):
        non_none = [a for a in get_args(target_type) if a is not type(None)]
        if len(non_none) == 1:
            target_type = non_none[0]
    if target_type is bool:
        return bool_converter(value) if isinstance(value, str) else bool(value)
    if isinstance(target_type, type) and issubclass(target_type, enum.Enum):
        if isinstance(value, str):
            return target_type[value]
        return target_type(value)
    if get_origin(target_type) is list:
        inner_type = get_args(target_type)[0]
        # NEW: if the string (after stripping) equals "none" (case-insensitive), return None.
        if isinstance(value, str) and value.strip().lower() == "none":
            return None
        if isinstance(value, str):
            return [convert_value(item.strip(), inner_type) for item in value.split(',')]
        elif isinstance(value, list):
            return [convert_value(item, inner_type) for item in value]
        else:
            raise ValueError(f"Cannot convert {value} to {target_type}")
    try:
        if target_type is str and isinstance(value, str) and value.strip().lower() == "none":
            return None
        return target_type(value)
    except Exception:
        print(f"Error converting value='{value}' to type='{target_type}', thus keep it as type {type(value)}")
        return value

def nest_namespace(ns: dict) -> dict:
    """Convert a flat argparse namespace to a nested dictionary (using dot-separated keys)."""
    nested = {}
    for k, v in ns.items():
        parts = k.split('.')
        current = nested
        for part in parts[:-1]:
            current = current.setdefault(part, {})
        current[parts[-1]] = v
    return nested

def deep_merge(a: dict, b: dict) -> dict:
    """
    Recursively merge dictionaries 'a' and 'b'. Values in 'b' override those in 'a',
    except when the value in 'b' is NOT_PROVIDED.
    """
    result = dict(a)
    for k, v in b.items():
        if v is NOT_PROVIDED:
            continue
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = deep_merge(result[k], v)
        else:
            result[k] = v
    return result

def fill_defaults(d: dict, cls: Type) -> dict:
    """
    Fill in missing values in dictionary 'd' using the default values from the dataclass 'cls'.
    If a required field is missing, raise an error.
    """
    result = dict(d)
    for f in fields(cls):
        if f.name not in result or result[f.name] is NOT_PROVIDED:
            if f.default is MISSING and f.default_factory is MISSING:
                raise ValueError(f"Missing required parameter: {f.name}")
            elif f.default is not MISSING:
                result[f.name] = f.default
            elif f.default_factory is not MISSING:
                result[f.name] = f.default_factory()
        else:
            if dataclasses.is_dataclass(f.type) and isinstance(result[f.name], dict):
                result[f.name] = fill_defaults(result[f.name], f.type)
    return result

def from_dict(cls: Type, d: dict):
    """
    Construct a dataclass instance from dictionary 'd'. Supports nested dataclasses.
    """
    kwargs = {}
    for f in fields(cls):
        if dataclasses.is_dataclass(f.type):
            sub_dict = d.get(f.name, {})
            kwargs[f.name] = from_dict(f.type, sub_dict)
        else:
            if f.name in d:
                kwargs[f.name] = convert_value(d[f.name], f.type)
    return cls(**kwargs)

def collect_field_names(cls: Type, prefix: str = "") -> List[tuple]:
    """
    Recursively collect field names from a dataclass.
    Returns a list of tuples (full_field_name, base_name),
    where full_field_name includes the prefix (e.g. "sampling.gen_n") and base_name is the simple field name (e.g. "gen_n").
    """
    names = []
    for f in fields(cls):
        full_name = f"{prefix}{f.name}"
        if dataclasses.is_dataclass(f.type):
            names.extend(collect_field_names(f.type, prefix=f"{full_name}."))
        else:
            names.append((full_name, f.name))
    return names

def build_alias_map(cls: Type) -> dict:
    """
    Build a global alias map. Traverse all fields (including nested ones) and if a field's base name is unique,
    allow a simplified alias "--<base_name>".
    Returns a dictionary mapping full field names to the simplified option string.
    """
    collected = collect_field_names(cls)
    freq = {}
    for full, base in collected:
        freq[base] = freq.get(base, 0) + 1
    alias_map = {}
    for full, base in collected:
        if freq[base] == 1:
            alias_map[full] = f"--{base}"
    return alias_map

def collect_all_arguments(cls: Type, prefix: str = "", special_fields: set = None, alias_map: dict = None):
    """
    Recursively collect all argument information from a dataclass without adding them to parser.
    Returns a list of dictionaries containing argument information for later sorting.
    """
    if special_fields is None:
        special_fields = set()
    if alias_map is None:
        alias_map = {}
    
    arguments = []
    field_help_map = extract_field_comments(cls)
    
    for f in fields(cls):
        field_type = f.type
        if get_origin(field_type) in (Union, types.UnionType):
            non_none = [a for a in get_args(field_type) if a is not type(None)]
            if len(non_none) == 1:
                field_type = non_none[0]
        full_field_name = f"{prefix}{f.name}"
        
        if dataclasses.is_dataclass(field_type):
            new_prefix = f"{full_field_name}."
            nested_args = collect_all_arguments(field_type, prefix=new_prefix, 
                                              special_fields=special_fields, alias_map=alias_map)
            arguments.extend(nested_args)
        else:
            # Build option strings: always include the fully qualified name.
            option_strings = [f"--{full_field_name}"]
            # If alias_map contains a simplified alias, add it but don't duplicate the full name
            if full_field_name in alias_map:
                simplified_alias = alias_map[full_field_name]
                if simplified_alias != f"--{full_field_name}":
                    option_strings.append(simplified_alias)
            
            dest_name = full_field_name
            if get_origin(field_type) is list:
                inner_type = get_args(field_type)[0]
                def list_converter(s, inner_type=inner_type):
                    # NEW: if the input string is "none" (case-insensitive), return None.
                    if s.strip().lower() == "none":
                        return None
                    # If the input string is empty, return an empty list.
                    if len(s) == 0:
                        return []
                    return [convert_value(item.strip(), inner_type) for item in s.split(',')]
                conv_type = list_converter
            else:
                conv_type = convert_type(field_type)
            
            # Build help text: type and default first, then comments
            type_str = str(field_type).replace("<class '", "").replace("'>", "").replace("<enum '", "").replace("'>", "")
            help_parts = [f"(type: {type_str})"]
            
            # Check if this is a required field
            is_required = f.default is MISSING and f.default_factory is MISSING
            
            # Add default value info
            if is_required:
                help_parts.append("(required)")
            else:
                default_val = f.default if f.default is not MISSING else f.default_factory()
                if not isinstance(default_val, SpecialLoadMarker):
                    help_parts.append(f"(default: {default_val})")
            
            # Add comments at the end if they exist
            extra_help = field_help_map.get(f.name, "")
            if extra_help:
                help_parts.append(extra_help)
            
            help_text = " ".join(help_parts)
            
            kwargs = {
                "dest": dest_name,
                "type": conv_type,
                "help": help_text
            }
            if isinstance(field_type, type) and issubclass(field_type, enum.Enum):
                kwargs["choices"] = list(field_type)
            
            # If the field's default value is special_load() (a SpecialLoadMarker instance), record its path.
            if isinstance(f.default, SpecialLoadMarker):
                special_fields.add(full_field_name)
            
            if is_required:
                kwargs["required"] = True
            else:
                kwargs["default"] = NOT_PROVIDED
            
            # Store argument information for sorting
            arguments.append({
                "option_strings": option_strings,
                "kwargs": kwargs,
                "full_field_name": full_field_name,
                "is_required": is_required,
                "separator_count": full_field_name.count('.'),
                "primary_name": option_strings[0]  # For sorting
            })
    
    return arguments

def add_arguments_from_dataclass(parser: argparse.ArgumentParser, cls: Type, prefix: str = "", 
                                 special_fields: set = None, alias_map: dict = None):
    """
    Recursively add command-line arguments based on the dataclass definition with custom ordering:
    1. Required arguments first
    2. Then by separator depth (fewer separators first)
    3. Then alphabetically by primary option name
    """
    if special_fields is None:
        special_fields = set()
    if alias_map is None:
        alias_map = {}
    
    # Collect all arguments
    all_arguments = collect_all_arguments(cls, prefix, special_fields, alias_map)
    
    # Sort arguments according to the requirements:
    # 1. Required args first (is_required=True comes before is_required=False)
    # 2. Fewer separators first (lower separator_count comes first)  
    # 3. Alphabetically by primary option name
    all_arguments.sort(key=lambda arg: (
        not arg["is_required"],  # Required first (False < True, so required comes first)
        arg["separator_count"],   # Fewer separators first
        arg["primary_name"]       # Alphabetically
    ))
    
    # Add arguments to parser in sorted order
    for arg_info in all_arguments:
        parser.add_argument(*arg_info["option_strings"], **arg_info["kwargs"])

def recursive_process(obj):
    """
    Recursively call the pre_process and post_process methods of a dataclass object.
    Processing order:
    1. Call pre_process() on the current object
    2. Recursively process all nested dataclass fields
    3. Call post_process() on the current object
    """
    if dataclasses.is_dataclass(obj):
        # Step 1: Call pre_process if it exists
        if hasattr(obj, "pre_process") and callable(obj.pre_process):
            obj.pre_process()
        
        # Step 2: Recursively process nested dataclass fields
        for field in fields(obj):
            value = getattr(obj, field.name)
            if dataclasses.is_dataclass(value):
                recursive_process(value)
        
        # Step 3: Call post_process if it exists
        if hasattr(obj, "post_process") and callable(obj.post_process):
            obj.post_process()

def parse_args(cls: Type, pass_in: List[str] = None):
    """
    Parse command-line arguments, supporting:
      - Merging code-provided arguments (pass_in) with sys.argv (command-line arguments take priority);
      - JSON configuration file loading: if a field's default value is special_load() (i.e. a SpecialLoadMarker instance)
        and the user provides a non-empty string, then load that string as a JSON file and merge its configuration.
      - Merging default values (and checking required fields);
      - Recursively calling post-processing methods (process_args/post_process) for all dataclasses;
      - If --help/-h is detected, print the help information and exit.
    Priority: command line > code input > specially loaded JSON config > default values.
    """
    code_args = pass_in if pass_in is not None else []
    cmd_args = sys.argv[1:]
    args_list = code_args + cmd_args

    if any(arg in ('-h', '--help') for arg in args_list):
        full_parser = argparse.ArgumentParser(formatter_class=NoMetavarFormatter)
        alias_map = build_alias_map(cls)
        add_arguments_from_dataclass(full_parser, cls, alias_map=alias_map)
        full_parser.print_help()
        sys.exit(0)

    special_fields = set()
    alias_map = build_alias_map(cls)
    parser = argparse.ArgumentParser(formatter_class=NoMetavarFormatter)
    add_arguments_from_dataclass(parser, cls, special_fields=special_fields, alias_map=alias_map)
    args = parser.parse_args(args_list)
    flat_ns = vars(args)
    nested_args = nest_namespace(flat_ns)

    # Ensure that at most one special load field exists.
    if len(special_fields) > 1:
        raise ValueError(f"At most one special load field is allowed, found: {special_fields}")
    if special_fields:
        special_field_path = next(iter(special_fields))
        special_value = get_by_path(nested_args, special_field_path)
        if isinstance(special_value, str) and special_value.strip() and special_value.strip().lower() == "none":
            special_value = None
            set_by_path(nested_args, special_field_path, None)

        if isinstance(special_value, str) and special_value.strip():
            try:
                with open(special_value, 'r') as f:
                    json_special = json.load(f)
            except Exception as e:
                print(f"Error loading JSON config from {special_value}: {e}", file=sys.stderr)
                json_special = {}
            # Keep the path of the loaded config file
            set_by_path(nested_args, special_field_path, special_value)
            nested_args = deep_merge(json_special, nested_args)
        elif special_value is NOT_PROVIDED:
            # If not provided via command line, set it to None so it doesn't hold the marker instance
            set_by_path(nested_args, special_field_path, None)

    final_dict = fill_defaults(nested_args, cls)
    config = from_dict(cls, final_dict)
    recursive_process(config)
    return config

def to_json(config) -> str:
    """
    Convert a dataclass instance to a JSON string.
    Enum types are converted to their names.
    """
    def default(o):
        if isinstance(o, enum.Enum):
            return o.name
        if isinstance(o, SpecialLoadMarker):
            return None
        raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")
    return json.dumps(asdict(config), indent=4, default=default)

def main():
    print("simpleArgParser: Please use parse_args() in your code to parse configuration.")

if __name__ == "__main__":
    main()
