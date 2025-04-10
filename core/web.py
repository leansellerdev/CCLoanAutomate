import os
import time
from datetime import datetime
from loguru import logger

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.keys import Keys

from secrets import login, password
from settings import PDFS_DIR

from core.models.debt import Debt
from core.utils.utils import calculate_state_duty, calculate_service


class CCLoanWeb:
    login_url = "https://ccloan.kz/administrator/index.php?r=User/Action/Login"
    main_page_url = 'https://ccloan.kz/administrator/index.php?r=site/index'

    USERNAME_XPATH = '//*[@id="UserLoginForm_username"]'
    PASSWORD_XPATH = '//*[@id="UserLoginForm_password"]'
    ENTER_TO_XPATH = '//*[@id="login-form"]/div[4]/input'

    CREDITS_XPATH = '//*[@id="nav"]/li[3]/a'
    IIN_FIELD_NAME = '//*[@id="credit-grid"]/table/thead/tr[2]/td[18]/input'

    CREDITS_TBODY_XPATH = '//*[@id="credit-grid"]/table/tbody'

    def __init__(self, debt: Debt,  detach=False, headless=False):
        self.options = webdriver.ChromeOptions()

        if headless:
            self.options.add_argument("--headless")
            self.options.add_argument("--disable-gpu")
            self.options.add_argument("--no-sandbox")
            self.options.add_argument("--disable-dev-shadow")

        if detach:
            self.options.add_experimental_option('detach', True)

        self.prefs = {"download.default_directory": os.getcwd() + r"\pdfs",
                      "download.prompt_for_download": False,
                      "download.directory_upgrade": True,
                      "plugins.always_open_pdf_externally": True}

        self.options.add_experimental_option("prefs", self.prefs)

        self.driver = self.__init_driver()
        self.wait = WebDriverWait(self.driver, 10)

        self.username = login
        self.password = password

        self.debt = debt

    def __init_driver(self) -> webdriver.Chrome:
        driver = webdriver.Chrome(options=self.options)

        return driver

    def login(self, maximized=True):
        self.driver.get(self.login_url)

        if maximized:
            self.driver.maximize_window()

        self.wait.until(ec.presence_of_element_located((By.XPATH, self.ENTER_TO_XPATH)))

        # Логинимся
        self.driver.find_element(By.XPATH, self.USERNAME_XPATH).send_keys(self.username)
        self.driver.find_element(By.XPATH, self.PASSWORD_XPATH).send_keys(self.password)

        self.driver.find_element(By.XPATH, self.ENTER_TO_XPATH).click()

    def main_page(self) -> None:
        self.driver.get(self.main_page_url)

    def find_client(self, iin):
        self.wait.until(ec.presence_of_element_located((By.XPATH, self.CREDITS_XPATH)))

        # Переходим на вкладку с кредитами
        self.driver.find_element(By.XPATH, self.CREDITS_XPATH).click()
        self.wait.until(ec.presence_of_element_located((By.XPATH, self.IIN_FIELD_NAME)))

        # Ищем кредит по ИИН
        iin_field = self.driver.find_element(By.XPATH, self.IIN_FIELD_NAME)
        iin_field.send_keys(iin)
        iin_field.send_keys(Keys.ENTER)

        time.sleep(5)

        credit = self.driver.find_element(By.XPATH, self.CREDITS_TBODY_XPATH).find_element(By.TAG_NAME, "tr")
        credit_status = credit.find_elements(By.TAG_NAME, "td")[11].text
        if credit_status != 'Отмена исп. листа/надписи':
            return

        credit_id = credit.find_elements(By.TAG_NAME, "td")[1].text
        credit_url = f"https://ccloan.kz/administrator/index.php?r=credit/view&id={credit_id}"

        self.debt.paybox = credit.find_elements(By.TAG_NAME, "td")[3].text

        return credit_url

    def parse_credit_urls(self, credit_url):
        self.driver.get(credit_url)

        docs = self.driver.find_elements(By.CLASS_NAME, "_document_url_div")[1:3]
        if 'Доп. соглашение об изменениях условий договора' in docs[1].text:
            docs.pop(1)
            docs.append(self.driver.find_elements(By.CLASS_NAME, "_document_url_div")[3])

        docs_url = [doc.find_element(By.TAG_NAME, "a").get_attribute("href") for doc in docs]

        docs_table = self.driver.find_elements(By.CLASS_NAME, "items")[0]
        docs = docs_table.find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, "tr")

        for doc in docs:
            if "Уведомление о просрочки" in doc.find_elements(By.TAG_NAME, "td")[4].text:
                doc_url = doc.find_elements(By.TAG_NAME,
                                            "td")[2].find_element(
                    By.CLASS_NAME,
                    "ClientSiteDocumentDownload").get_attribute("href")

                docs_url.append(doc_url)
                break

        return docs_url

    def parse_credit_info(self) -> None:
        document_urls_xpath = '//*[@id="content"]/div[1]'

        name_block = self.driver.find_element(By.XPATH, document_urls_xpath)
        names = name_block.find_elements(By.CLASS_NAME, '_document_url_div')[14].text.split()

        if len(names) < 3 and names[-1].isdigit():
            names = name_block.find_elements(By.CLASS_NAME, '_document_url_div')[15].text.split()
        try:
            fathers_name = names[2]
        except IndexError:
            fathers_name = ""
        name = names[1]
        surname = names[0]

        if fathers_name == 'нет':
            fathers_name = ""

        if fathers_name.lower() != 'кредит':
            self.debt.name = " ".join([surname, name, fathers_name])
        if surname.isdigit():
            self.debt.name = " ".join([name, fathers_name])

        # Номер телефона
        for elem in self.driver.find_elements(By.CLASS_NAME, "_document_url_div"):
            if "Мобильный телефон клиента" in elem.text:
                self.debt.phone_number = elem.text.split()[-1][1:]

            if "Кредит в днях" in elem.text:
                self.debt.credit_duration = elem.text.split()[-1]

        self.debt.credit_id = self.driver.find_element(By.XPATH, '//*[@id="yw1"]/tbody/tr[1]/td').text
        self.debt.date_of_credit = self.driver.find_element(By.XPATH, '//*[@id="yw1"]/tbody/tr[14]/td').text

        self.debt.date_of_credit = datetime.strptime(self.debt.date_of_credit, "%Y-%m-%d")

        tables = self.driver.find_elements(By.XPATH, '//*[@id="content"]/table/tbody')

        for table in tables:
            if table.find_element(By.TAG_NAME, "td").text == 'Разница в транзакциях':
                rows = table.find_elements(By.TAG_NAME, "tr")

                for row in rows:
                    if row.find_elements(By.TAG_NAME, "td")[0].text.lower() == 'од':
                        self.debt.summa = row.find_elements(By.TAG_NAME, "td")[1].text

                    if row.find_elements(By.TAG_NAME, "td")[0].text.lower() == 'вознаграждение':
                        self.debt.credit_reward = row.find_elements(By.TAG_NAME, "td")[1].text

                    if row.find_elements(By.TAG_NAME, "td")[0].text.lower() == 'пеня за просрочку':
                        self.debt.credit_fee = row.find_elements(By.TAG_NAME, "td")[1].text

                    if row.find_elements(By.TAG_NAME, "td")[0].text.lower() == 'нотариальные услуги':
                        self.debt.notarial_fee = row.find_elements(By.TAG_NAME, "td")[1].text

                    if row.find_elements(By.TAG_NAME, "td")[0].text.lower() == 'одноразовы штраф за просрочку':
                        self.debt.penalty = row.find_elements(By.TAG_NAME, "td")[1].text


        self.debt.final_summa = int((float(self.debt.summa.replace(',', '')) +
                                     float(self.debt.credit_reward.replace(',','')) +
                                     float(self.debt.credit_fee.replace(',', '')) +
                                     float(self.debt.penalty.replace(',', ''))
                                     ))
        self.debt.notarial_plus_mainsumma = int((float(self.debt.summa.replace(',', '')) +
                                     float(self.debt.credit_reward.replace(',','')) +
                                     float(self.debt.credit_fee.replace(',', '')) +
                                     float(self.debt.penalty.replace(',', '')) +
                                     float(self.debt.notarial_fee.replace(',', ''))
                                     ))
        self.debt.service = calculate_service(amount=self.debt.final_summa, notarial=int(
                                                                      float(self.debt.notarial_fee.replace(',', '')
                                                                            )))
        self.debt.state_duty = calculate_state_duty(amount=self.debt.final_summa,
                                                                  notarial=int(
                                                                      float(self.debt.notarial_fee.replace(',', '')
                                                                            )))

    def get_pdfs(self, iin, urls):
        folder_name = f'{iin}_{self.debt.paybox}'

        if not os.path.exists(PDFS_DIR / folder_name):
            os.mkdir(PDFS_DIR / folder_name)

        for i, url in enumerate(urls):
            self.driver.get(url)

            time.sleep(2)
            file_downloaded = False

            while not file_downloaded:
                files = os.listdir(PDFS_DIR)

                paths = [os.path.join(PDFS_DIR, basename) for basename in files]
                latest_file = max(paths, key=os.path.getctime)

                try:
                    try:
                        if i == 0:
                            os.rename(
                                latest_file,
                                PDFS_DIR / f"{folder_name}/Договор_о_предоставлении_микрокредита_{iin}_{self.debt.credit_id}.pdf"
                            )
                        if i == 1:
                            os.rename(
                                latest_file,
                                PDFS_DIR / f"{folder_name}/Рассчет_задолженности_{iin}_{self.debt.credit_id}.pdf"
                            )
                        if i == 2:
                            os.rename(latest_file, PDFS_DIR / f"{folder_name}/Досудебная_претензия_{iin}_{self.debt.credit_id}.pdf")
                    except FileExistsError:
                        os.remove(latest_file)
                        logger.info(f"Файлы по займу #{self.debt.credit_id} уже созданы!")
                except (PermissionError, FileNotFoundError):
                    pass
                else:
                    file_downloaded = True
