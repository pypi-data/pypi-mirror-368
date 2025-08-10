# lib/_texio.py
import json, pathlib

def read_text(path):
    return pathlib.Path(path).read_text(encoding="utf-8")

def write_text(path, s):
    pathlib.Path(path).write_text(s, encoding="utf-8")

def emit_human(header, items):
    lines=[header]
    lines+=items
    return "\n".join(lines)

def emit_json(**kwargs):
    return kwargs

def write_outputs(human_log, json_obj, output_path, json_path):
    if output_path:
        write_text(output_path, human_log)
    else:
        print(human_log)

    if json_path:
        write_text(json_path, json.dumps(json_obj, indent=2))
    else:
        print(json.dumps(json_obj, indent=2))