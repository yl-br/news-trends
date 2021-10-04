import website_parsers

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager

domain = "https://www.israelhayom.co.il"
parser = website_parsers.IsraelhayomParser()

# sqlite_db = sqlite_adapter.SqliteAdapter(db_name="news.db")
# sqlite_db.connect()
# all_url = sqlite_db.get_all_articles_url()

# driver = webdriver.Firefox(executable_path="../old/geckodriver-v0.29.0-win64.exe")

opts = ChromeOptions()
# opts.add_argument("--headless")
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
except Exception:
    driver = webdriver.Chrome(ChromeDriverManager(cache_valid_range=10).install(), options=opts)

driver.get(domain)
WebDriverWait(driver, timeout=10).until(EC.presence_of_element_located((By.CSS_SELECTOR, parser.wait_for_homepage_css_selector)))
homepage_content = driver.find_element_by_tag_name('html').get_attribute('innerHTML')
links = parser.extract_homepage_links(homepage_content)

print(links)

print(len(links))



for i, link in enumerate(links):
    print("request for: {0}, {1}/{2}".format(link, i + 1, len(links)))
    time.sleep(2)
    driver.delete_all_cookies()
    driver.get(link)
    WebDriverWait(driver, timeout=10).until(EC.presence_of_element_located((By.CSS_SELECTOR, parser.wait_for_article_css_selector)))
    if parser.execute_script_on_article:
        driver.execute_script(parser.execute_script_on_article)

    print('-' * 100)
    article_page_content = driver.find_element_by_tag_name('html').get_attribute('innerHTML')
    title, description, body = parser.parse_article_html(article_page_content)

    print()
    print(title)
    print(description)
    print(body)


driver.close()
driver.quit()