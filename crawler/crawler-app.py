import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,currentdir)
sys.path.insert(0,parentdir)

import website_parsers
import traceback
import logging
import sys
import datetime
import postgres_adapter
import uuid
import argparse
import time

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ChromeOptions

def main():
    logging.info("\n"*5 + "started...")

    crawl_session_id = uuid.uuid4().hex

    db_url = os.getenv('DATABASE_URL', args.db_url)
    postgresAdapter = postgres_adapter.PostgresAdapter(db_url=db_url)
    postgresAdapter.connect()
    postgresAdapter.create_crawler_table_if_not_exists()
    all_urls = set(postgresAdapter.get_all_urls())


    websites_to_crawl = [
        {'source': 'ynet', 'domain': 'https://www.ynet.co.il', 'parser': website_parsers.YnetParser()},
        {'source': 'maariv', 'domain': 'https://www.maariv.co.il', 'parser': website_parsers.MaarivParser()},
        {'source': 'mako', 'domain': 'https://www.mako.co.il', 'parser': website_parsers.MakoParser()},
        {'source': 'walla', 'domain': 'https://www.walla.co.il', 'parser': website_parsers.WallaParser()},
        {'source': 'israelhayom', 'domain': 'https://www.israelhayom.co.il', 'parser': website_parsers.IsraelhayomParser()}
    ]

    logging.info("Started crawling session. Session Id: {0}.\n Websites: {1}.\n Db path: {2}".format(crawl_session_id,
                                                                                                     websites_to_crawl,
                                                                                                     db_url))
    logging.info("-" * 150 + "\n\n")

    opts = ChromeOptions()
    opts.add_argument("--headless")
    opts.add_argument("--disable-extensions")
    opts.add_argument('--disable-gpu')
    opts.add_argument('--no-sandbox')
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--log-level=3")
    opts.add_argument("--silent")
    opts.add_argument("--incognito")
    opts.add_experimental_option("excludeSwitches", ['enable-automation'])

    try:
        driver = webdriver.Chrome(options=opts)
        # driver = webdriver.Firefox(executable_path=args.geckodriver_path, options=opts, service_log_path='crawler/geckodriver.log')
    except Exception:
        driver = webdriver.Chrome(ChromeDriverManager(cache_valid_range=10).install(), options=opts)


    for website in websites_to_crawl:
        logging.info(' ' * 10 + "Crawling for source: {0}, Domain: {1}".format(website['source'], website['domain']))
        domain = website['domain']
        parser = website['parser']

        try:
            driver.get(domain)
            WebDriverWait(driver, timeout=10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, parser.wait_for_homepage_css_selector)))
            homepage_content = driver.find_element_by_tag_name('html').get_attribute('innerHTML')
        except Exception as e:
            logging.error("Error getting domain homepage content: {0}. \n".format(domain) + traceback.format_exc())
            continue

        try:
            links = parser.extract_homepage_links(homepage_content)
        except Exception as e:
            logging.error(
                "Error in extracting links from homepage. domain: {0}. \n".format(domain) + traceback.format_exc())
            continue

        new_links = [link for link in links if link not in all_urls]
        logging.info("Domain: {0}. Number of links extracted from homepage: {1}."
                     " Number of new links: {2}.\n\n\n".format(domain, len(links), len(new_links)))

        inserted_articles_count = 0
        articles_with_missing_properties_count = 0

        for i, link in enumerate(new_links):
            logging.debug("request for: {0}, {1}/{2}".format(link, i + 1, len(new_links)))

            try:
                time.sleep(1)
                driver.delete_all_cookies()
                driver.get(link)
                WebDriverWait(driver, timeout=10).until(EC.presence_of_element_located((By.CSS_SELECTOR, parser.wait_for_article_css_selector)))
                logging.debug("Page content met condition.")
                if parser.execute_script_on_article:
                    logging.debug("Executing script on webpage.")
                    driver.execute_script(parser.execute_script_on_article)

                logging.debug("Retrieving inner html of web page.")
                article_page_content = driver.find_element_by_tag_name('html').get_attribute('innerHTML')

            except TimeoutException as e:
                logging.error("Timeout error for link page content to match condition. Condition: {0}, link: {1}. \n"
                              .format(parser.wait_for_article_css_selector, link) + traceback.format_exc())
                continue
            except Exception as e:
                logging.error("Error getting link content, link: {0}. \n".format(link) + traceback.format_exc())
                continue

            try:
                title, description, body = parser.parse_article_html(article_page_content)
            except Exception as e:
                logging.error("Error in parsing article html. Link: {0}.\n".format(link) + traceback.format_exc())
                continue

            timestamp = datetime.datetime.utcnow()
            try:
                logging.debug("Inserting to db..")
                postgresAdapter.insert_to_crawler(website['source'], domain, link, crawl_session_id, timestamp, title, description, body)
            except Exception as e:
                logging.error("Error inserting article db. Article Link: {0}.\n".format(link) + traceback.format_exc())
                continue

            logging.debug("Inserted to db: {0}.\n".format(link))
            inserted_articles_count += 1
            if title is None or title == '' or description is None or description == '' or body is None or body == '':
                articles_with_missing_properties_count += 1
                logging.warning("Article inserted to db with missing properties. \nLink: {0} \n title={1}\ndescription={2}\n body={3}".
                                format(link, title, description, body))

        logging.info("\n\nFor Domain: {0}. Articles inserted to db / Total links extracted =  {1}/{2}. "
                     "Number of inserted articles with missing properties = {3}.".format(
            domain, inserted_articles_count, len(new_links), articles_with_missing_properties_count))
        logging.info("-" * 100 + "\n\n")

    driver.close()
    driver.quit()
    postgresAdapter.close()
    logging.info("Finished.")


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--log_level", type=str, default="INFO")
        parser.add_argument("--db_url", type=str, default=None)
        # parser.add_argument("--geckodriver_path", type=str, default='crawler/geckodriver-v0.29.0-win64.exe')
        args = parser.parse_args()

        handlers = [logging.FileHandler(filename='crawler/crawler.log'), logging.StreamHandler(sys.stdout)]
        logging.basicConfig(handlers=handlers, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=args.log_level)
        main()
    except Exception as e:
        logging.error("Major error occurred.\n" + traceback.format_exc())
    finally:
        sys.exit()