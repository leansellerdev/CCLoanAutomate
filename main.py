import time
import sys

from loguru import logger

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

    total_iins = db.count_iins()

    try:
        logger.info("Заходим на сайт")
        cc.login()

        for _ in range(total_iins):
            iin_data = db.select_iin()
            iin = iin_data[1]
            iin_id = iin_data[0]

            cc.debt.iin = iin

            logger.info("Переходим на главную страницу")
            cc.main_page()

            logger.info(f"Ищем клиента с ИИН: {iin}")
            credit_url = cc.find_client(iin)

            logger.info("Берем ссылки на документы")
            urls = cc.parse_credit_urls(credit_url)

            logger.info("Собираем информацию по кредиту")
            cc.parse_credit_info()

            logger.info("Скачиваем документы по кредиту")
            cc.get_pdfs(iin, urls)

            logger.info(f"Заполняем исковое заявление для ИИН: {iin}, Имя клиента: {debt.name}")
            fill_statement(debt)

            logger.info(f"Перемещаем файлы в итоговую папку")
            move_files(iin)

            logger.info(f"Удаляем файлы")
            delete_files(iin)

            logger.info(f"Все операции по займу #{debt.credit_id}, ИИН {debt.iin} проведены!")
            db.update_iin_status(id=iin_id, status=1)
            time.sleep(5)
    except Exception as err:
        message = (f"При попытке формирования иска для {debt.credit_id}, ИИН: {debt.iin} "
                   f"произошла ошибка!\n{err.with_traceback(err.__traceback__)}")
        logger.error(str(err), exc_info=True)
        send_logs(message=message)

        sys.exit(1)
    else:
        cc.driver.quit()


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit) as error:
        logger.error(error)
