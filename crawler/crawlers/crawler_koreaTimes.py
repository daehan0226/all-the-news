import time, sys, datetime
from random import uniform

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class Crawler_koreantimes:
    def __init__(self, main, site):
        self.driver = main["driver"]
        self.wait = main["wait"]
        self.logging = main["logging"]
        self.es = main["es"]
        self.url = site[0]
        self.categories = site[1]

    def parse(self):
        for category in self.categories:
            try:
                page = 1
                while True:
                    current_page = f"{self.url}{category[1]}_{page}.html"
                    self.logging.info(f"current article list page : {current_page}")

                    self.driver.get(current_page)
                    time.sleep(uniform(1, 2))
                    urls = self.get_news_urls()

                    for idx, url in enumerate(urls):
                        self.logging.info(f"parsing {idx + 1} / {len(urls)}")
                        if self.es.has_url_parsed("news", url):
                            self.logging.info("This url has been parsed.")
                            continue

                        self.get_article_data(url, category[0])   # es에 저장하면서 이미 있는 데이터에서 break

                    page += 1
                    
            except Exception as e:
                _, _, tb = sys.exc_info()
                self.logging.error(f'parse except,  {tb.tb_lineno},  {e.__str__()}')


    def get_article_data(self, url, category):
        title = ""
        content = ""
        date = ""

        news_content_el = 'div.all_section'

        title_el = 'div.view_headline'
        para_el = 'div.view_article > div > div > div#startts > span'
        date_el = 'div.date_div > div.view_date'

        time.sleep(uniform(1, 2))
        self.driver.get(url)
        time.sleep(uniform(1, 2))

        news_content = self.wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR,
                news_content_el
            )))
        
        try:
            title = news_content.find_element(
                By.CSS_SELECTOR,
                title_el
            ).get_attribute('textContent').strip()

            paragraphs = news_content.find_elements(
                By.CSS_SELECTOR,
                para_el
            )

            date = news_content.find_elements(
                By.CSS_SELECTOR,
                date_el
            )

            date = date[0].get_attribute('textContent').strip().split(": ")[1]
            date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M')

            for paragraph in paragraphs:
                try:
                    content += paragraph.get_attribute('textContent').strip()
                except:
                    print("this element does not have text")   

        except Exception as e:
            _, _, tb = sys.exc_info()
            self.logging.error(f'parse article excpet from url : {url},  {tb.tb_lineno},  {e.__str__()}')

        if title and content:
            article = {
                "site" : "koreatimes",
                "url" : url,
                "title" : title,
                "content" : content,
                "category" :category,
                "crawled_at" :  datetime.datetime.now().timestamp(),
                "published_at" : date.timestamp()
            }

            result = self.es.insert_doc("news", article)
            self.logging.debug("insert new doc to es, doc_id : " + result)
        else:
            self.logging.error(f'fail to parse article data from this url, {url}')

    def get_news_urls(self):
        time.sleep(uniform(1, 2))
        urls = []

        news_list_el = 'div.section_main_left > div.list_article_area'

        news_list = self.wait.until(EC.presence_of_all_elements_located((
            By.CSS_SELECTOR,
            news_list_el
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

    