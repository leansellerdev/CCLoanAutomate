import os
import time
from datetime import datetime

from num2words import num2words

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.keys import Keys

from secrets import login, password

from core.models.debt import Debt
from core.utils.utils import format_number, format_date


class CCLoanWeb:
    url = "https://ccloan.kz/administrator/index.php?r=User/Action/Login"

    USERNAME_XPATH = '//*[@id="UserLoginForm_username"]'
    PASSWORD_XPATH = '//*[@id="UserLoginForm_password"]'
    ENTER_TO_XPATH = '//*[@id="login-form"]/div[4]/input'

    CREDITS_XPATH = '//*[@id="nav"]/li[3]/a'
    IIN_FIELD_NAME = '//*[@id="credit-grid"]/table/thead/tr[2]/td[18]/input'

    CREDITS_TBODY_XPATH = '//*[@id="credit-grid"]/table/tbody'

    def __init__(self, debt: Debt,  detach=False):
        self.options = webdriver.ChromeOptions()

        if detach:
            self.options.add_experimental_option('detach', True)

        self.prefs = {"download.default_directory": os.getcwd() + r"\pdfs",
                      "download.prompt_for_download": False,
                      "download.directory_upgrade": True,
                      "plugins.always_open_pdf_externally": True}

        self.options.add_experimental_option("prefs", self.prefs)

        self.driver = webdriver.Chrome(options=self.options)
        self.wait = WebDriverWait(self.driver, 10)

        self.username = login
        self.password = password

        self.debt = debt

    def login(self, maximized=True):
        self.driver.get(self.url)

        if maximized:
            self.driver.maximize_window()

        self.wait.until(ec.presence_of_element_located((By.XPATH, self.ENTER_TO_XPATH)))

        # Логинимся
        self.driver.find_element(By.XPATH, self.USERNAME_XPATH).send_keys(self.username)
        self.driver.find_element(By.XPATH, self.PASSWORD_XPATH).send_keys(self.password)

        self.driver.find_element(By.XPATH, self.ENTER_TO_XPATH).click()

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
        credit_id = credit.find_elements(By.TAG_NAME, "td")[1].text
        credit_url = f"https://ccloan.kz/administrator/index.php?r=credit/view&id={credit_id}"

        return credit_url

    def parse_credit_urls(self, credit_url):
        self.driver.get(credit_url)

        docs = self.driver.find_elements(By.CLASS_NAME, "_document_url_div")[1:3]
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

    def parse_credit_info(self):
        fathers_name = self.driver.find_element(By.XPATH, '//*[@id="content"]/div[1]').text.split()[-7]
        name = self.driver.find_element(By.XPATH, '//*[@id="content"]/div[1]').text.split()[-8]
        surname = self.driver.find_element(By.XPATH, '//*[@id="content"]/div[1]').text.split()[-9]

        if fathers_name.lower() != 'кредит':
            self.debt.name = " ".join([surname, name, fathers_name])
        if surname.isdigit():
            self.debt.name = " ".join([name, fathers_name])

        # Номер телефона
        for elem in self.driver.find_elements(By.CLASS_NAME, "_document_url_div"):
            if "Мобильный телефон клиента" in elem.text:
                self.debt.phone_number = elem.text.split()[-1]

            if "Кредит в днях" in elem.text:
                self.debt.credit_duration = elem.text.split()[-1]

        self.debt.credit_id = self.driver.find_element(By.XPATH, '//*[@id="yw1"]/tbody/tr[1]/td').text
        self.debt.date_of_credit = self.driver.find_element(By.XPATH, '//*[@id="yw1"]/tbody/tr[14]/td').text

        self.debt.date_of_credit = datetime.strptime(self.debt.date_of_credit, "%Y-%m-%d")
        self.debt.date_of_credit = format_date(self.debt.date_of_credit)

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

        self.debt.final_summa = (int(self.debt.summa.replace(',', '').replace('.00', '')) +
                                 int(self.debt.credit_reward.replace(',',
                                                                     '').replace('.00', '')))

        self.debt.summa = format_number(self.debt.summa)
        self.debt.credit_reward = format_number(self.debt.credit_reward)
        self.debt.credit_fee = format_number(self.debt.credit_fee)
        self.debt.notarial_fee = format_number(self.debt.notarial_fee)
        self.debt.final_summa = format_number(self.debt.final_summa)

    def get_pdfs(self, iin, urls):
        pdfs_path = os.getcwd() + fr"\pdfs"

        if not os.path.exists(pdfs_path + fr"\{iin}"):
            os.mkdir(pdfs_path + fr"\{iin}")

        for i, url in enumerate(urls):
            self.driver.get(url)

            time.sleep(2)
            file_downloaded = False

            while not file_downloaded:
                files = os.listdir(pdfs_path)

                paths = [os.path.join(os.getcwd() + fr"\pdfs", basename) for basename in files]
                latest_file = max(paths, key=os.path.getctime)

                try:
                    if i == 0:
                        os.rename(latest_file, pdfs_path + fr"\{iin}\dogovor_{iin}.pdf")
                    if i == 1:
                        os.rename(latest_file, pdfs_path + fr"\{iin}\dolg_{iin}.pdf")
                    if i == 2:
                        os.rename(latest_file, pdfs_path + fr"\{iin}\uvedomlenie_{iin}.pdf")
                except (PermissionError, FileNotFoundError):
                    pass
                else:
                    file_downloaded = True

    def cc_loan_parse(self, iin):

        self.debt.iin = iin

        self.login()
        credit_url = self.find_client(iin)

        urls = self.parse_credit_urls(credit_url)

        self.parse_credit_info()
        self.get_pdfs(iin, urls)
