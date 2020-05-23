import time, sys
from random import uniform

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class Crawler_bbc:
    def __init__(self, driver, wait, logging, es, url):
        self.driver = driver
        self.wait = wait
        self.logging = logging
        self.es = es
        self.url = url

    def parse(self):
        self.logging.debug("parsing started from this url : " + self.url)
        self.driver.get(self.url)
        time.sleep(uniform(1, 2))
        stories = []

        start_time = time.time()
        stories.extend(self.get_story_data())
        end_time = time.time()
        self.logging.info("parsing title, summary of top stories takes : " + str(end_time - start_time))

        for story in stories:
            start_time = time.time()
            self.get_story_text(story)
            end_time = time.time()
            self.logging.info("parsing text of the story takes : " + str(end_time - start_time) + "story url : " + story["url"])

    def get_story_text(self, story):
        self.driver.get(story["url"])
        time.sleep(uniform(1, 2))
        text = ""

        try:
            paragraphs = self.wait.until(EC.presence_of_all_elements_located((
                By.CSS_SELECTOR,
                'div.story-body__inner > p'
            )))

            for paragraph in paragraphs:
                text += paragraph.get_attribute('textContent').strip()

            story["text"] = text
            story["site"] = "bbc"
            doc_id = story["url"].split('/')[-1]

            result = self.es.insert_doc("news", "docs", doc_id, story)
            self.logging.debug("insert new doc to es, doc_id : " + result)

        except Exception as e:
            _, _, tb = sys.exc_info()
            self.logging.error('get story text except ' + str(tb.tb_lineno) + ', ' + e.__str__())

    def get_story_data(self):
        story_data =[]

        try:
            top_story_container = self.wait.until(EC.presence_of_all_elements_located((
                By.CSS_SELECTOR,
                 'div#news-top-stories-container'
            )))

            time.sleep(uniform(1, 2))

            for s_summary_container in top_story_container:

                stories = s_summary_container.find_elements(
                    By.CSS_SELECTOR,
                    'div.gel-layout__item'
                )

                for story in stories:
                    try:
                        title = story.find_element(
                            By.CSS_SELECTOR,
                            'h3.gs-c-promo-heading__title'
                        ).get_attribute('textContent').strip()

                        summary = story.find_element(
                            By.CSS_SELECTOR,
                            'p.gs-c-promo-summary'
                        ).get_attribute('textContent').strip()

                        url = story.find_element(
                            By.CSS_SELECTOR,
                            'a.gs-c-promo-heading'
                        ).get_attribute('href')

                        story_data.append({
                            "title": title,
                            "summary": summary,
                            "url": url
                        })
                    except:
                        print('not title, text tag in story container')

            if len(story_data) == 0:
                self.logging.error("no top stories : " + self.url)
            else:
                self.logging.info("insert top story data, story count : " + str(len(story_data)))

        except Exception as e:
            _, _, tb = sys.exc_info()
            self.logging.error("no top stories : " + self.url)
            self.logging.error('get top stories except ' + str(tb.tb_lineno) + ', ' + e.__str__())

        return story_data