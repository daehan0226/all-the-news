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
        self.url = site[1]
        self.categories = site[2]

    def parse(self):
        for category in self.categories:
            try:
                page = 1
                while True:
                    current_page = f"{self.url}{category[1]}_{page}.html"
                    self.logging.info(f"current article list page : {current_page}")

                    time.sleep(uniform(1, 2))
                    self.driver.get(current_page)
                    urls = self.get_news_urls()

                    for idx, url in enumerate(urls):
                        self.logging.info(f"parsing {idx + 1} / {len(urls)}")
                        self.get_article_data(url, category[0])   # es에 저장하면서 이미 있는 데이터에서 break

                    page += 1
                    
            except Exception as e:
                _, _, tb = sys.exc_info()
                self.logging.error(f'parse except,  {tb.tb_lineno},  {e.__str__()}')


    def get_article_data(self, url, category):
        text = ""

        time.sleep(uniform(1, 2))
        self.driver.get(url)
        time.sleep(uniform(1, 2))

        news_content = self.wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR,
                'div.all_section'
            )))
        
        try:
            title = news_content.find_element(
                By.CSS_SELECTOR,
                'div.view_headline'
            ).get_attribute('textContent').strip()

            paragraphs = news_content.find_elements(
                By.CSS_SELECTOR,
                'div.view_article > div > div > div#startts > span'
            )

            date = news_content.find_elements(
                By.CSS_SELECTOR,
                'div.date_div > div.view_date'
            )

            date = date[0].get_attribute('textContent').strip().split(": ")[1]

            for paragraph in paragraphs:
                try:
                    text += paragraph.get_attribute('textContent').strip()
                except:
                    print("this element does not have text")   

        except Exception as e:
            _, _, tb = sys.exc_info()
            self.logging.error(f'parse article excpet from url : {url},  {tb.tb_lineno},  {e.__str__()}')

        if title and text:
            article = {
                "site" : "koreaTimes",
                "url" : url,
                "title" : title,
                "text" : text,
                "category" :category,
                "crawled_at" : time.time(),
                "published_at" : date
            }

            doc_id = url
            print(doc_id, article)

            result = self.es.insert_doc("news", "_doc", doc_id, article)
            self.logging.debug("insert new doc to es, doc_id : " + result)
        else:
            self.logging.error(f'fail to parse article data from this url, {url}')


    def get_news_urls(self):
        time.sleep(uniform(1, 2))
        urls = []

        news_list = self.wait.until(EC.presence_of_all_elements_located((
            By.CSS_SELECTOR,
            'div.section_main_left > div.list_article_area'
        ))) 

        for news in news_list:
            try:
                url = news.find_element(
                    By.CSS_SELECTOR,
                    'div.list_article_headline > a'
                ).get_attribute('href')
                urls.append(url)
            except:
                print('no url')
        
        return urls

    