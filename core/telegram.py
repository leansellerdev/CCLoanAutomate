import requests

from settings import LOG_FILE_PATH, TG_BOT_TOKEN, PROJECT_NAME

LOGS_CHAT_ID = '-4751461230'


def get_uodates():
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/getUpdates"

    response = requests.get(url)
    return response.json()


def send_logs(log_file: str = LOG_FILE_PATH, message: str = 'log'):
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendDocument"

    message = f'Процесс: {PROJECT_NAME}\n' + message

    with open(log_file, 'rb') as send_file:
        response = requests.post(
            url,
            data={
                'chat_id': LOGS_CHAT_ID,
                'caption': message,
            },
            files={
                'document': send_file,
            }
        )

    return response
