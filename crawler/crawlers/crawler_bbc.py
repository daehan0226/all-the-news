import time, sys
from datetime import datetime
from random import uniform
import random


from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class Crawler_bbc:
    def __init__(self, main, site):
        self.driver = main["driver"]
        self.wait = main["wait"]
        self.logging = main["logging"]
        self.es = main["es"]
        self.url = site[0]
        self.categories = site[1]
        self.category = main["category"]

    def parse(self):
        if self.category == "":
            self.category = random.choice(self.categories)

        try:
            parse_url = self.url + category
            self.logging.debug("parsing started from this url : " + parse_url)
            self.driver.get(parse_url)

            parsed_urls = []

            page = 0
            click_cnt = 0

            while True:
                self.driver.get(parse_url)
                time.sleep(uniform(2, 3))
                
                if not self.click_more_btn(page):
                    break

                urls = self.get_news_urls(category, parsed_urls)
                self.logging.info(f"current page : {page}, parsed urls count : {len(parsed_urls)}")

                for idx, url in enumerate(urls):
                    self.logging.info(f"parsing {idx + 1} / {len(urls)}")

                    if self.es.has_url_parsed("news", url):
                        self.logging.info("This url has been parsed.")
                        continue

                    article = self.parse_article(url, category)
                    
                    if article:
                        result = self.upload_article(article)

                        if result:
                            parsed_urls.append(url)
                
                page += 1

        except Exception as e:
            _, _, tb = sys.exc_info()
            self.logging.error(f'parse except,  {tb.tb_lineno},  {e.__str__()}')
    
    def click_more_btn(self, click_cnt):
        try:  
            while click_cnt > 0: 
                btn_el = self.wait.until(EC.presence_of_all_elements_located((
                    By.CSS_SELECTOR,
                    'button.lx-stream-show-more__button'
                ))) 
                self.driver.find_element_by_css_selector('button.lx-stream-show-more__button').click()
                time.sleep(uniform(2, 3))
                click_cnt -= 1
            
            return True

        except Exception as e:
            _, _, tb = sys.exc_info()
            self.logging.debug(f'click more btn except,  {tb.tb_lineno},  {e.__str__()}')
            return False
    
    def parse_article(self, url, category):
        self.driver.get(url)
        time.sleep(uniform(3, 4))
        title = ""
        content = ""
        date = ""

        title_el = 'div.story-body> h1.story-body__h1'
        para_el = 'div.story-body__inner > p'
        date_el = 'li.mini-info-list__item > div'

        try: 
            try:
                title = self.driver.find_element(
                    By.CSS_SELECTOR,
                    title_el
                ).get_attribute('textContent').strip()

            except Exception as e:
                _, _, tb = sys.exc_info()
                self.logging.error('get article title except ' + str(tb.tb_lineno) + ', ' + e.__str__())

            try:
                paragraphs = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    para_el
                )

                for paragraph in paragraphs:
                    content += paragraph.get_attribute('textContent').strip()

            except Exception as e:
                _, _, tb = sys.exc_info()
                self.logging.error('get article content except ' + str(tb.tb_lineno) + ', ' + e.__str__())

            try:
                date = self.driver.find_element(
                    By.CSS_SELECTOR,
                    date_el
                ).get_attribute("data-seconds")

            except Exception as e:
                _, _, tb = sys.exc_info()
                self.logging.error('get article date except ' + str(tb.tb_lineno) + ', ' + e.__str__())

            story = {
                "title": title,
                "content": content,
                "published_at": int(date),
                "category": category,
                "url": self.driver.current_url
            }

            return story

        except Exception as e:
            _, _, tb = sys.exc_info()
            self.logging.error('parse article info except ' + str(tb.tb_lineno) + ', ' + e.__str__())
            return False

    def upload_article(self, article):
        article["site"] = "bbc"
        article["crawled_at"] = datetime.now().timestamp() # # time.time()
        
        try:
            doc_id = self.es.insert_doc("news",article)
            self.logging.debug("insert new doc to es, doc_id : " + doc_id)
            return True
        
        except:
            return False

    def get_news_urls(self, category, parsed_urls):
        time.sleep(uniform(1, 2))
        urls = []

        try:
            news_list = self.wait.until(EC.presence_of_all_elements_located((
                By.CSS_SELECTOR,
                'div.lx-stream > div.lx-stream__feed > article.lx-stream-post'
            ))) 

            for news in news_list:
                try:
                    url = news.find_element(
                        By.CSS_SELECTOR,
                        'div.lx-stream-post-body > a.lx-stream-asset__cta'
                    ).get_attribute('href')

                    # self.url = "https://www.bbc.com/news/" // is a base_url for news
                    if not url.startswith(self.url):
                        # print('diffent category, url : ', url)
                        continue

                    if not url in parsed_urls:
                        urls.append(url)

                except:
                    pass
                    # short article - does not have an article page.
                    # self.parse_short_article(news, category)
                    # print('short article')

        except Exception as e:
            _, _, tb = sys.exc_info()
            self.logging.error('parse urls except ' + str(tb.tb_lineno) + ', ' + e.__str__())
        
        return urls

    # def parse_short_article(self, news, category):
    #     title = ""
    #     content = ""
    #     date = ""

    #     title_ele = 'span.lx-stream-post__header-text'
    #     content_ele = 'pre.lx-media-asset__summary'

    #     time_ele = 'div.lx-stream-post__meta > time > span.qa-meta-time'
    #     date_ele = 'div.lx-stream-post__meta > time > span.qa-meta-date'

    #     try:

    #         try:
    #             title = news.find_element(
    #                 By.CSS_SELECTOR,
    #                 title_ele
    #             ).get_attribute('textContent').strip()

    #         except Exception as e:
    #             _, _, tb = sys.exc_info()
    #             self.logging.error('parse short article title except ' + str(tb.tb_lineno) + ', ' + e.__str__())

    #         try:
    #             content = news.find_element(
    #                 By.CSS_SELECTOR,
    #                 content_ele
    #             ).get_attribute('textContent').strip()

    #         except Exception as e:
    #             _, _, tb = sys.exc_info()
    #             self.logging.error('parse short article content except ' + str(tb.tb_lineno) + ', ' + e.__str__())
            
    #         try:
    #             date = self.driver.find_element(
    #                 By.CSS_SELECTOR,
    #                 date_ele
    #             ).get_attribute('textContent').strip()

    #         except Exception as e:
    #             _, _, tb = sys.exc_info()                
    #             date = str(datetime.now().day) + ' ' + datetime.now().strftime('%B') # date info does not exsit if the news was published today
    #             self.logging.debug('get short article date except ' + str(tb.tb_lineno) + ', ' + e.__str__())

    #         try:
    #             time = self.driver.find_element(
    #                 By.CSS_SELECTOR,
    #                 time_ele
    #             ).get_attribute('textContent').strip()

    #         except Exception as e:
    #             _, _, tb = sys.exc_info()
    #             self.logging.error('get short article time except ' + str(tb.tb_lineno) + ', ' + e.__str__())

    #         date = f"2020 {date} {time}"
    #         print(title, content, category)
    #         print(date)
    #         date = datetime.strptime(date, '%Y %d %B %H:%M')

    #         story = {
    #             "title": title,
    #             "content": content,
    #             "published_at": date.timestamp(),
    #             "category": category,
    #             "url": self.driver.current_url + title
    #         }

    #         self.upload_article(story)

    #     except Exception as e:
    #         _, _, tb = sys.exc_info()
    #         self.logging.error('get short article parse except ' + str(tb.tb_lineno) + ', ' + e.__str__())
