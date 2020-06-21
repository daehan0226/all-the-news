import logging, json
from logging import handlers

import time
import sys
import simplejson
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

from libs.elasticsearch_wrapper import ElasticsearchWrapper
from crawlers.crawler_bbc import Crawler_bbc
from crawlers.crawler_cnn import Crawler_cnn
from crawlers.crawler_koreaTimes import Crawler_koreanTimes
from crawlers.crawler_npr import Crawler_npr

json_config = open("./config/config.json").read()
config = simplejson.loads(json_config)

# chrome과 함께 실행할 옵션 객체 생성
options = Options()

# chrome 브라우저 실행 환경 셋팅
prefs = {
    'profile.default_content_setting_values.notifications': 2,
    'profile.default_content_setting_values.popups': 2,
    'profile.default_content_settings.state.flash': 0,
    'profile.managed_default_content_settings.images': 2,
    'download.prompt_for_download': False
}

options.add_experimental_option("prefs", prefs)
# options.binary_location = '/opt/google/chrome/google-chrome'
options.add_argument('--disable-gpu')
options.add_argument('--disable-infobars')
options.add_argument('--ignore-certificate-errors-spki-list')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
options.add_argument('--disable-popup-blocking')
# options.add_argument('--kiosk')
options.add_argument('--start-maximized')
# options.add_argument('--user-data-dir=' + CHROME_PROFILE)
options.add_argument(
    "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36")

class Crawler:
    def __init__(self):
        self.driver = None
        self.config = config
        self.logging = logging
        self.wait = None
        self.es = None

    def run(self):
        self.set_logger()
        CHROME_PATH = self.config["driver_path"]
        self.driver = webdriver.Chrome(executable_path=CHROME_PATH, chrome_options=options)
        self.wait = WebDriverWait(self.driver, 15)
        self.es = ElasticsearchWrapper(self.config)

        news_index = self.config["news"]["index"]
        mappings = self.config["news"]["mappings"]
        
        if not self.es.exist_index(news_index):
            self.logging.debug(f"index - {news_index} does not exist")
            self.es.create_index(news_index, mappings)

        for site in self.config["sites"]:
            start_time = time.time()
            self.logging.info("parsing started for this site, " + site[0])

            # if site[0] == "bbc":
            #     cralwer = Crawler_bbc(self.driver, self.wait, self.logging, self.es, site)
            #     cralwer.parse()

            # if site[0] == "cnn":
            #     cralwer = Crawler_cnn(self.driver, self.wait, self.logging, self.es, site)
            #     cralwer.parse()
            
            if site[0] == "koreatimes":
                cralwer = Crawler_koreanTimes(self.driver, self.wait, self.logging, self.es, site)
                cralwer.parse()

            # if site[0] == "npr":
            #     cralwer = Crawler_npr(self.driver, self.wait, self.logging, self.es, site)
            #     cralwer.parse()
            
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
    main.run()

    main.close()