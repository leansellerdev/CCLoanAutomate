import os
import shutil
from datetime import datetime

from num2words import num2words

from settings import PDFS_DIR, STATEMENTS_DIR, CASE_DIR, TEMPLATES_DIR


def format_number(num) -> str:
    text = str(num).replace(',', '').replace('.00', '')
    formatted_text = num2words(text, lang='ru_RU')

    return f"{text} ({formatted_text}) тенге"

def calculate_state_duty(amount: int) -> int:
    amount *= 0.03
    return int(amount)

def format_date(date: datetime) -> str:
    months = {
        1: "января",
        2: "февраля",
        3: "марта",
        4: "апреля",
        5: "мая",
        6: "июня",
        7: "июля",
        8: "августа",
        9: "сентября",
        10: "октября",
        11: "ноября",
        12: "декабря"
    }

    formatted_date = date.strftime(f"«%d» {months[date.month]} %Y")

    return formatted_date

def delete_files(iin: str) -> None:
    shutil.rmtree(PDFS_DIR / iin)


def move_files(iin: str) -> None:
    if not os.path.exists(CASE_DIR / iin):
        os.mkdir(CASE_DIR / iin)

    for file in os.listdir(PDFS_DIR / iin):
        shutil.move(PDFS_DIR / iin / file, CASE_DIR / iin / file)

    for file in os.listdir(STATEMENTS_DIR):
        shutil.move(STATEMENTS_DIR / file, CASE_DIR / iin / file)

    for file in os.listdir(TEMPLATES_DIR):
        shutil.copy(TEMPLATES_DIR / file, CASE_DIR / iin / file)
