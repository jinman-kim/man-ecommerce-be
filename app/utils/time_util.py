from datetime import datetime, timedelta, timezone
import pytz

def get_current_time() -> datetime:
    """
    현재 한국 표준시(KST)를 반환합니다.
    
    Returns:
        datetime: 한국 시간대의 현재 datetime 객체
    """
    korea_timezone = pytz.timezone("Asia/Seoul")
    return datetime.now(korea_timezone).strftime('%Y-%m-%d %H:%M:%S')


def get_timestamp():
    """현재 시간을 UNIX 타임스탬프로 반환합니다."""
    return int(datetime.now().timestamp())

def format_time(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """특정 형식으로 시간을 포맷하여 반환합니다."""
    return dt.strftime(fmt)

def add_days(days: int) -> datetime:
    """현재 시간에서 특정 일수를 더한 날짜를 반환합니다."""
    return datetime.now() + timedelta(days=days)

def parse_iso(iso_str: str) -> datetime:
    """ISO 형식의 문자열을 datetime 객체로 변환합니다."""
    return datetime.fromisoformat(iso_str)


if __name__ == "__main__":
    current_time = get_current_time()
    print(current_time)
