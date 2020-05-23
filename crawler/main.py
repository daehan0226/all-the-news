import logging
from logging import handlers

import time
import sys
import simplejson
from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

from crawlers.crawler_bbc import Crawler_bbc
from crawlers.crawler_cnn import Crawler_cnn

json_config = open("./config/config.json").read()
config = simplejson.loads(json_config)

class Crawler:
    def __init__(self):
        self.driver = None
        self.config = config
        self.logging = logging
        self.wait = None

    def run(self):
        CHROME_PATH = self.config["driver_path"]
        self.driver = webdriver.Chrome(executable_path=CHROME_PATH)
        self.wait = WebDriverWait(self.driver, 15)

        for site in self.config["sites"]:
            start_time = time.time()
            self.logging.info("parsing started for this site, " + site[0])

            if site[0] == "bbc":
                cralwer = Crawler_bbc(self.driver, self.wait, self.logging, site[1])
                cralwer.parse()
                end_time = time.time()

            if site[0] == "cnn":
                cralwer = Crawler_cnn(self.driver, self.wait, self.logging, site[1])
                cralwer.parse()
                end_time = time.time()

            self.logging.debug("parsing finished, parsing time : " + str(end_time - start_time))

    def set_logger(self):
        log_file_max_bytes = 1024 * 1024 * 100

        self.logging = logging.getLogger('crawl_log')
        fomatter = logging.Formatter('[%(levelname)s] %(asctime)s > %(message)s')

        file_handler = logging.handlers.RotatingFileHandler(filename=self.config["log_dir"] + self.config["log_filename"], maxBytes=log_file_max_bytes,
                                                    encoding='utf-8')

        # 각 핸들러에 포매터를 지정한다.
        file_handler.setFormatter(fomatter)

        # 로거 인스턴스에 스트림 핸들러와 파일핸들러를 붙인다.
        self.logging.addHandler(file_handler)

        # 로거 표현 범위 지정 DEBUG > INFO > WARNING > ERROR > Critical
        self.logging.setLevel(logging.DEBUG)

    def close(self):
        # 브라우저가 실행 중이면 닫음
        if not (self.driver is None):
            try:
                self.driver.quit()
            except:
                pass

if __name__ == "__main__":
    main = Crawler()
    main.set_logger()
    main.run()

    main.close()