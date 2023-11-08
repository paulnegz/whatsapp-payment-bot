from datetime import timedelta, datetime, date
# import re
from functools import wraps
from time import sleep
import hashlib


MONTH = 30
MONTH_PRICE = 1_800


def get_current_date():
    return datetime.today()


def get_hash(file_path):
    sha1_hash = hashlib.sha1()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            sha1_hash.update(chunk)
    sha1_digest = sha1_hash.hexdigest()
    return sha1_digest


def add_days(day: int, date: str) -> datetime:
    return date + timedelta(days=int(day))


def delete_decimal(n: str) -> int:
    index = n.find('.')
    if index == -1:
        return int(n)
    return int(n[:index])


def create_date(date: str) -> datetime:
    return datetime.fromisoformat(date)
