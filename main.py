import os

import logging
from datetime import datetime

from core.web import CCLoanWeb
from core.models.debt import Debt
from core.files import fill_statement

from core.utils.telegram import send_logs

# 000526650927
logger = logging.getLogger(__name__)


def main():
    logs_filename = datetime.now().strftime("%d-%m-%Y_%H-%M-%S.txt")

    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s '
               u'[%(asctime)s] - %(name)s - %(message)s',
        filename=logs_filename,
        filemode='w',
        encoding='utf-8'
    )

    debt = Debt()
    cc = CCLoanWeb(debt, headless=False)

    iins = ["860825400664"]  # 860825400664

    try:
        for iin in iins:
            cc.debt.iin = iin
            cc.debt.state_duty = "5000 (пять тысяч) тенге"

            logger.info("Заходим на сайт")
            cc.login()

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

            logger.info(f"Все операции по займу #{debt.credit_id}, ИИН {debt.iin} проведены!")
    except Exception as err:
        message = f"При попытке формирования иска для {debt.credit_id}, ИИН: {debt.iin} произошла ошибка!\n{err}"
        logger.error(message)
        # send_logs(message=message)
    else:
        logger.info("Отправляем логи!")

        message = f"Логи за {logs_filename.replace('.txt', '')}"
        # send_logs(message=message, log_file=logs_filename)

        # is_removed = False

        # while not is_removed:
        #     try:
        #         if os.path.exists(logs_filename):
        #             os.remove(logs_filename)
        #     except PermissionError:
        #         pass
        #     else:
        #         is_removed = True


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit) as error:
        logger.error(error)
