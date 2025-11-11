"""
Модели данных и вспомогательные функции
"""
from datetime import datetime
from typing import Optional
from database import Child, Group, Teacher # Import Peewee models


def format_date(date_str: str) -> str:
    """Форматировать дату в читаемый вид"""
    if not date_str:
        return ""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%d-%m-%Y")
    except:
        return date_str


def validate_date(date_str: str) -> bool:
    """Проверить корректность даты"""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except:
        return False
