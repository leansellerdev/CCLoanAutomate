import time
import sys
import traceback
from datetime import datetime, timedelta

from loguru import logger

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from core.web import CCLoanWeb
from core.models.debt import Debt
from core.files import fill_statement
from core.utils.utils import delete_files, move_files
from core.telegram import send_logs
from core.database import SQLiteDatabase


db = SQLiteDatabase("db.sqlite3")


def main():

    debt = Debt()
    cc = CCLoanWeb(debt, headless=False)

    # total_iins = db.count_iins()

    try:
        logger.info("Заходим на сайт")
        cc.login()

        for _ in range(50):
            iin_data = db.select_iin()
            iin = iin_data[1]
            iin_id = iin_data[0]

            cc.debt.iin = iin

            logger.info("Переходим на главную страницу")
            cc.main_page()

            logger.info(f"Ищем клиента с ИИН: {iin}")
            credit_url = cc.find_client(iin)

            if credit_url is None:
                continue

            logger.info("Берем ссылки на документы")
            urls = cc.parse_credit_urls(credit_url)

            logger.info("Собираем информацию по кредиту")
            try:
                cc.parse_credit_info()
            except IndexError:
                continue

            logger.info("Скачиваем документы по кредиту")
            cc.get_pdfs(iin, urls)

            logger.info(f"Заполняем исковое заявление для ИИН: {iin}, Имя клиента: {debt.name}")
            fill_statement(debt)

            folder_name = f'{iin}_{debt.paybox}'

            logger.info(f"Перемещаем файлы в итоговую папку")
            move_files(folder_name)

            logger.info(f"Удаляем файлы")
            delete_files(folder_name)

            logger.info(f"Все операции по займу #{debt.credit_id}, ИИН {debt.iin} проведены!")
            db.update_iin_status(id=iin_id, status=1)
            time.sleep(5)
    except Exception:
        message = (f"При попытке формирования иска для {debt.credit_id}, ИИН: {debt.iin} "
                   f"произошла ошибка!\n{traceback.format_exc()}")
        logger.error(traceback.format_exc())
        send_logs(message=message)
        return
    else:
        cc.driver.quit()


trigger = CronTrigger(hour=9, start_date=datetime.now() + timedelta(seconds=5))
scheduler = BlockingScheduler(logger=logger)


if __name__ == '__main__':
    try:
        # main()
        scheduler.add_job(func=main, id='main', trigger=trigger)
        scheduler.start()
    except (KeyboardInterrupt, SystemExit) as error:
        logger.error(error)
