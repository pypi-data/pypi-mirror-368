# __init__.py
from .all_name import get_name_usages_with_location
from .invalid_name import _is_illegal_name
import os
import codecs
import __main__
import sys
import types
import linecache
import inspect
from typing import List, Dict, Tuple

def detect_file_encodings(file_path: str) -> List[str]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No such a file: {file_path}")
    
    common_encodings = [
        'utf-8', 'utf-16', 'utf-16-le', 'utf-16-be',
        'utf-32', 'utf-32-le', 'utf-32-be',
        'ascii', 'latin1', 'iso-8859-1',
        'gbk', 'gb18030', 'big5',
        'shift_jis', 'euc-jp',
        'cp1251', 'cp1252', 'cp1250',
    ]
    
    successful_encodings = []
    
    for encoding in common_encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                f.read()
            successful_encodings.append(encoding)
        except Exception:
            continue
    
    return successful_encodings or []

def raise_name_error_with_frame(name: str, filename: str, line_no: int):
    line = linecache.getline(filename, line_no).strip()
    sys.stderr.write(f"""Traceback (most recent call last):
  File "{__main__.__file__}", line {line_no}, in <module>
    {line}
NameError: name '{name}' is illegal. Please don't try to define a female.""")
    
    sys.exit(1)

if hasattr(__main__, "__file__"):
    filename = __main__.__file__
    name_locations = {}
    for encoding in detect_file_encodings(filename):
        with open(filename, 'r', encoding=encoding) as f:
            try:
                code = f.read()
                name_info = get_name_usages_with_location(code)
                for name, (line_no, _) in name_info.items():
                    if name not in name_locations:
                        name_locations[name] = line_no
            except Exception:
                continue
    
    for name, line_no in name_locations.items():
        if _is_illegal_name(name):
            raise_name_error_with_frame(name, filename, line_no)
