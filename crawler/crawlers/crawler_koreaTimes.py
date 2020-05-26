import time, sys
from random import uniform

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class Crawler_koreanTimes:
    def __init__(self, driver, wait, logging, es, site):
        self.driver = driver
        self.wait = wait
        self.logging = logging
        self.es = es
        self.sites = site[1]

    def parse(self):
        for site in self.sites:
            print(site[1])
            self.logging.debug("parsing started from this url : " + site[1])
            self.driver.get(f"https://www.koreatimes.co.kr/www/{site[1]}.html")
            time.sleep(uniform(1, 2))

            news_container = self.wait.until(EC.presence_of_all_elements_located((
                By.CSS_SELECTOR,
                'div.section_main_left'
            )))
            
            while True:      

                
                time.sleep(uniform(1, 2))
                # get_current_page_news(news_container)


                self.driver.get(get_next_page_url())


    def get_next_page_url(self):
        cur_url = self.driver.current_url
        cur_page = int(cur_url[33:-5].split('_')[-1])
        next_page = cur_page + 1

        return f"https://www.koreatimes.co.kr/www/sublist_129_{next_page}.html"



    # def get_current_page_news(self, news_container):

        # for news in news_container:


    