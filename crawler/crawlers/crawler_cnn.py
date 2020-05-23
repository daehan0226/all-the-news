from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class Crawler_cnn:
    def __init__(self, driver, wait, logging, es, url):
        self.driver = driver
        self.wait = wait
        self.logging = logging
        self.es = es
        self.url = url

    def parse(self):
        self.logging.debug("parsing started from this url : " + self.url)
        self.driver.get(self.url)


