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
from crawlers.crawler_koreatimes import Crawler_koreantimes
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

CHROME_PATH = config["driver_path"]
if config["server"]:
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    CHROME_PATH = config["driver_path_server"]

class Crawler:
    def __init__(self):
        self.driver = None
        self.config = config
        self.logging = logging
        self.wait = None
        self.es = None

    def run(self, site, category):
        self.driver = webdriver.Chrome(executable_path=CHROME_PATH, chrome_options=options)
        self.wait = WebDriverWait(self.driver, 15)
        self.es = ElasticsearchWrapper(self.config)

        news_index = self.config["news"]["index"]
        mappings = self.config["news"]["mappings"]
        
        if not self.es.exist_index(news_index):
            # self.logging.debug(f"index - {news_index} does not exist")
            self.es.create_index(news_index, mappings)

        start_time = time.time()

        self.set_logger(site)
        self.logging.info("parsing started for this site, " + site)

        main = {
            "driver": self.driver,
            "wait": self.wait,
            "logging": self.logging,
            "es": self.es,
            "category": category
        }

        if site == "bbc":
            cralwer = Crawler_bbc(main, config["sites"]["bbc"])

        # if site== "cnn":
        #     cralwer = Crawler_cnn(main, config["sites"]["cnn"])
        
        if site == "koreatimes":
            cralwer = Crawler_koreantimes(main, config["sites"]["koreatimes"])
            
        if site == "npr":
            cralwer = Crawler_npr(main, config["sites"]["npr"])
            
        cralwer.parse()
        end_time = time.time()
        self.logging.debug(f"site : {site} parsing finished, parsing time : {end_time - start_time}")

    def set_logger(self, site):
        log_file_max_bytes = 1024 * 1024 * 100

        self.logging = logging.getLogger('crawl_log')
        fomatter = logging.Formatter('[%(levelname)s] %(asctime)s > %(message)s')

        file_handler = logging.handlers.RotatingFileHandler(filename=f'{self.config["log_dir"] + self.config["log_filename"]}_{site}', maxBytes=log_file_max_bytes,
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
    try:
        site = sys.argv[1]
    except:
        site = 'bbc'   # bbc, cnn, npr, koreatimes
        
    try:
        category = sys.argv[2]
    except:
        category = ''

    service = Crawler()
    service.run(site, category)

    service.close()
