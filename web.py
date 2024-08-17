import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from secrets import login, password


class CCLoanWeb:
    url = "https://ccloan.kz/administrator/index.php?r=User/Action/Login"

    USERNAME_XPATH = '//*[@id="UserLoginForm_username"]'
    PASSWORD_XPATH = '//*[@id="UserLoginForm_password"]'
    ENTER_TO_XPATH = '//*[@id="login-form"]/div[4]/input'

    CREDITS_XPATH = '//*[@id="nav"]/li[3]/a'
    IIN_FIELD_NAME = '//*[@id="credit-grid"]/table/thead/tr[2]/td[18]/input'

    CREDITS_TBODY_XPATH = '//*[@id="credit-grid"]/table/tbody'

    def __init__(self, detach=False):
        self.options = webdriver.ChromeOptions()

        if detach:
            self.options.add_experimental_option('detach', True)

        self.driver = webdriver.Chrome(options=self.options)
        self.wait = WebDriverWait(self.driver, 10)

        self.username = login
        self.password = password

    def login(self, maximized=True):
        self.driver.get(self.url)

        if maximized:
            self.driver.maximize_window()

        self.wait.until(EC.presence_of_element_located((By.XPATH, self.ENTER_TO_XPATH)))

        # Логинимся
        self.driver.find_element(By.XPATH, self.USERNAME_XPATH).send_keys(self.username)
        self.driver.find_element(By.XPATH, self.PASSWORD_XPATH).send_keys(self.password)

        self.driver.find_element(By.XPATH, self.ENTER_TO_XPATH).click()

    def find_client(self, iin):
        self.wait.until(EC.presence_of_element_located((By.XPATH, self.CREDITS_XPATH)))

        # Переходим на вкладку с кредитами
        self.driver.find_element(By.XPATH, self.CREDITS_XPATH).click()
        self.wait.until(EC.presence_of_element_located((By.XPATH, self.IIN_FIELD_NAME)))

        # Ищем кредит по ИИН
        iin_field = self.driver.find_element(By.XPATH, self.IIN_FIELD_NAME)
        iin_field.send_keys(iin)
        iin_field.send_keys(Keys.ENTER)

        time.sleep(5)

        credit = self.driver.find_element(By.XPATH, self.CREDITS_TBODY_XPATH).find_element(By.TAG_NAME, "tr")
        credit_id = credit.find_elements(By.TAG_NAME, "td")[1].text
        credit_url = f"https://ccloan.kz/administrator/index.php?r=credit/view&id={credit_id}"

        return credit_url

    def parse_credit(self, credit_url):
        self.driver.get(credit_url)

        docs = self.driver.find_elements(By.CLASS_NAME, "_document_url_div")[1:3]
        docs_url = [doc.find_element(By.TAG_NAME, "a").get_attribute("href") for doc in docs]

        docs_table = self.driver.find_elements(By.CLASS_NAME, "items")[0]
        docs = docs_table.find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, "tr")

        for doc in docs:
            if "Уведомление о просрочки" in doc.find_elements(By.TAG_NAME, "td")[4].text:
                doc_url = doc.find_elements(By.TAG_NAME,
                                            "td")[2].find_element(By.CLASS_NAME,
                                                                  "ClientSiteDocumentDownload").get_attribute("href")
                docs_url.append(doc_url)
                break

        return docs_url

    def cc_loan_parse(self, iin):
        self.login()
        credit_url = self.find_client(iin)

        urls = self.parse_credit(credit_url)

        print(urls)
