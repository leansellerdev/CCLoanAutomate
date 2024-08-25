import requests
from secrets import tg_bot_token


def get_uodates():
    token = tg_bot_token
    url = f"https://api.telegram.org/bot{token}/getUpdates"

    response = requests.get(url)
    return response.json()


def send_logs(message, log_file=None):
    token = tg_bot_token
    chat_id = "-4553001971"

    if log_file:
        url = f"https://api.telegram.org/bot{token}/sendDocument"
        with open(log_file, "rb") as sendfile:
            response = requests.post(
                url,
                data={
                    "chat_id": chat_id,
                    "caption": message
                },
                files={"document": sendfile}
            )
    else:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        response = requests.get(
            url,
            params={'chat_id': chat_id, 'text': message}
        )

    if response.status_code != 200:
        return f"Ошибка при отправке логов: {response.text}"

    return response.text
