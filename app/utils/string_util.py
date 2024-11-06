import re
import hashlib

def to_snake_case(s: str) -> str:
    """CamelCase 문자열을 snake_case로 변환합니다."""
    return re.sub(r'(?<!^)(?=[A-Z])', '_', s).lower()

def to_camel_case(s: str) -> str:
    """snake_case 문자열을 CamelCase로 변환합니다."""
    return ''.join(word.capitalize() if i != 0 else word for i, word in enumerate(s.split('_')))

def generate_hash(value: str) -> str:
    """문자열의 SHA256 해시를 생성합니다."""
    return hashlib.sha256(value.encode()).hexdigest()

def clean_text(text: str) -> str:
    """문자열에서 특수문자를 제거하고 공백을 정리합니다."""
    return re.sub(r'[^\w\s]', '', text).strip()

