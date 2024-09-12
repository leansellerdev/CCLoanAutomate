import os
import shutil
from datetime import datetime

from num2words import num2words

from settings import PDFS_DIR, STATEMENTS_DIR


def format_number(num) -> str:
    text = str(num).replace(',', '').replace('.00', '')
    formatted_text = num2words(text, lang='ru_RU')

    return f"{text} ({formatted_text}) тенге"


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

def delete_uploaded_files(iin: str) -> None:
    os.remove(STATEMENTS_DIR / f"Исковое_Заявление_{iin}.docx")
    shutil.rmtree(PDFS_DIR / iin)