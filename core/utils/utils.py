from datetime import datetime

from num2words import num2words


def format_number(num):
    text = str(num).replace(',', '').replace('.00', '')
    formatted_text = num2words(text, lang='ru_RU')

    return f"{text} ({formatted_text}) тенге"


def format_date(date: datetime):
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
