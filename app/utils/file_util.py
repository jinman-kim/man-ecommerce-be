# utils/file_util.py

import os
import shutil
import json
from typing import Any

def read_json(file_path: str) -> Any:
    """JSON 파일을 읽어서 파이썬 객체로 반환합니다."""
    with open(file_path, 'r') as f:
        return json.load(f)

def write_json(data: Any, file_path: str):
    """파이썬 객체를 JSON 파일로 저장합니다."""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def copy_file(src: str, dst: str):
    """파일을 복사합니다."""
    shutil.copy(src, dst)

def get_file_size(file_path: str) -> int:
    """파일 크기를 바이트 단위로 반환합니다."""
    return os.path.getsize(file_path)
