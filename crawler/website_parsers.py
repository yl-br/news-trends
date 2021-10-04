from bs4 import BeautifulSoup
import json

class YnetParser():
    def __init__(self):
        self.wait_for_homepage_css_selector = 'a'
        self.wait_for_article_css_selector = 'script[type="application/ld+json"]'
        self.execute_script_on_article = None

    def extract_homepage_links(self, home_page_html):
        soup = BeautifulSoup(home_page_html, 'html.parser')
        link_tags = soup.find_all('a')

        all_links = list(set([tag.get('href') for tag in link_tags]))
        filter_only_articles_links = lambda url: url is not None and "ynet.co.il" in url and "/article/" in url  # Change 'news/article' to only 'article'.
        articles_links = list(filter(filter_only_articles_links, all_links))

        return articles_links

    def parse_article_html(self, article_html):
        soup = BeautifulSoup(article_html, 'html.parser')

        script_tag = soup.find('script', {"type": "application/ld+json"})
        json_object = json.loads(script_tag.string, strict=False)

        title = json_object.get('headline', None)
        description = json_object.get('description', None)
        body = json_object.get('articleBody', None)

        return title, description, body


class MaarivParser():
    def __init__(self):
        self.wait_for_homepage_css_selector = 'a'
        self.wait_for_article_css_selector = 'script[type="application/ld+json"]'
        self.execute_script_on_article = None

    def extract_homepage_links(self, home_page_html):
        soup = BeautifulSoup(home_page_html, 'html.parser')
        link_tags = soup.find_all('a')

        all_links = list(set([tag.get('href') for tag in link_tags]))
        filter_only_articles_links = lambda url: url is not None and "maariv.co.il" in url and '/breaking-news' not in url and "/Article-" in url  # Change 'news/article' to only 'article'.
        articles_links = list(filter(filter_only_articles_links, all_links))

        return articles_links


    def parse_article_html(self, article_html):
        soup = BeautifulSoup(article_html, 'html.parser')

        script_tags = soup.find_all('script', {"type": "application/ld+json"})
        json_objects = [json.loads(tag.string, strict=False) for tag in script_tags]
        json_object = next((x for x in json_objects if 'articleBody' in x.keys()), {})

        title = json_object.get('headline', None)
        description = json_object.get('description', None)
        body = json_object.get('articleBody', None)

        return title, description, body


class IsraelhayomParser():
    def __init__(self):
        self.wait_for_homepage_css_selector = 'a'
        self.wait_for_article_css_selector = 'script[type="application/ld+json"]'
        self.execute_script_on_article = None

    def extract_homepage_links(self, home_page_html):
        soup = BeautifulSoup(home_page_html, 'html.parser')
        link_tags = soup.find_all('a')

        all_links = list(set([tag.get('href') for tag in link_tags]))
        all_links = [link.replace('?obOrigUrl=true', '') for link in all_links if link]
        filter_only_articles_links = lambda url: url is not None and "israelhayom.co.il" in url and "/article/" in url  # Change 'news/article' to only 'article'.
        articles_links = list(filter(filter_only_articles_links, all_links))

        return articles_links

    def parse_article_html(self, article_html):
        soup = BeautifulSoup(article_html, 'html.parser')

        script_tag = soup.find('script', {"type": "application/ld+json"})

        json_object = json.loads(script_tag.string, strict=False)

        title = json_object.get('headline', None)
        description = json_object.get('description', None)

        content_div = soup.find('div', {'class': 'text-content'}) or soup.find('div', {'class': 'content'})

        #body_divs = content_div.select("div.field-item.even > div")
        text_tags = content_div.findAll('p', {'class': None, 'style': None}, recursive=True) + content_div.findAll('div', {'class': None, 'style': None}, recursive=True)

        body = " ".join([tag.text for tag in text_tags])
        body = body.strip('/n') if body else None

        return title, description, body

class MakoParser():
    def __init__(self):
        self.wait_for_homepage_css_selector = 'a'
        self.wait_for_article_css_selector = 'section.article-body'
        self.execute_script_on_article = None

    def extract_homepage_links(self, home_page_html):
        soup = BeautifulSoup(home_page_html, 'html.parser')
        link_tags = soup.find_all('a')

        all_links = list(set([tag.get('href') for tag in link_tags]))

        filter_only_articles_links = lambda url: url is not None and "/Article-" in url and '/horoscope/' not in url

        articles_links = list(filter(filter_only_articles_links, all_links))

        articles_links = [link if "mako.co.il" in link else "http://www.mako.co.il" + link for link in articles_links]

        return articles_links

    def parse_article_html(self, article_html):
        soup = BeautifulSoup(article_html, 'html.parser')

        script_tag = soup.find('script', {"type": "application/ld+json"})

        json_object = json.loads(script_tag.string, strict=False)

        title = json_object.get('headline', None)

        description = soup.select('span[itemprop="description"]')[0]['content']

        articleBody = soup.find('section', {'class': 'article-body'})

        #body_divs = content_div.select("div.field-item.even > div")
        body_divs = articleBody.findChildren('p')

        body = " ".join([div.text for div in body_divs])
        body = body.strip('/n') if body else None

        return title, description, body


class WallaParser():
    def __init__(self):
        self.wait_for_homepage_css_selector = 'a'
        self.wait_for_article_css_selector = 'section.article-content'
        self.execute_script_on_article = """
            Array.prototype.slice.call(document.getElementsByTagName('video')).forEach(
              function(item) {
                item.remove();
            });
            Array.prototype.slice.call(document.getElementsByTagName('a')).forEach(
              function(item) {
                item.remove();
            });
            Array.prototype.slice.call(document.getElementsByClassName('css-1tkogwg')).forEach(
              function(item) {
                item.remove();
            });
            Array.prototype.slice.call(document.getElementsByClassName('ob-widget-items-container')).forEach(
              function(item) {
                item.remove();
            });
            Array.prototype.slice.call(document.getElementsByClassName('recommended')).forEach(
              function(item) {
                item.remove();
            });
        """

    def extract_homepage_links(self, home_page_html):
        soup = BeautifulSoup(home_page_html, 'html.parser')
        link_tags = soup.find_all('a')

        all_links = list(set([tag.get('href') for tag in link_tags]))

        filter_only_articles_links = lambda url: url is not None and "/item" in url

        articles_links = list(filter(filter_only_articles_links, all_links))

        return articles_links

    def parse_article_html(self, article_html):
        soup = BeautifulSoup(article_html, 'html.parser')

        script_tag = soup.find('script', {"type": "application/ld+json"})

        json_object = json.loads(script_tag.string, strict=False)

        title = json_object.get('headline', None)
        description = json_object.get('description', None)

        articleBody = soup.find('section', {'class': 'article-content'})

        body_divs = articleBody.findChildren('p')

        body = " ".join([div.text for div in body_divs])
        body = body.strip('/n') if body else None

        return title, description, body