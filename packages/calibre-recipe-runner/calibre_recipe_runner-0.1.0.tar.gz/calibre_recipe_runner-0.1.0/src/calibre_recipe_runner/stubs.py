import re
import time
import requests
from bs4 import BeautifulSoup
import feedparser
from datetime import datetime
from urllib.parse import urljoin
from dateutil.parser import parse as dateutil_parse
import tempfile


class BasicNewsRecipe:
    title = "Generic Recipe"
    oldest_article = 7  # days
    max_articles_per_feed = 100
    no_stylesheets = True
    encoding = 'utf-8'
    language = 'en'
    remove_javascript = True
    use_embedded_content = False
    keep_only_tags = []
    remove_tags = []
    feeds = []
    needs_subscription = False
    username = None
    password = None
    login_url = None
    login_form_id = None
    login_success_url = None
    login_failed_url = None
    extra_css = ''
    remove_empty_feeds = True
    use_embedded_content = False
    encoding = 'utf-8'
    keep_only_tags = []
    remove_tags = []
    preprocess_regexps = []
    postprocess_regexps = []

    session = requests.Session()

    def __init__(self):
        self.toc_thumbnail = {}

    def get_feeds(self):
        return self.feeds

    def parse_index(self):
        articles = []
        for feed in self.get_feeds():
            parsed = feedparser.parse(feed['url'])
            for entry in parsed.entries[:self.max_articles_per_feed]:
                articles.append({
                    'title': entry.title,
                    'url': entry.link,
                    'date': entry.get('published', ''),
                })
        return articles

    def index_to_soup(self, url):
        html = self.download_to_string(url)
        return BeautifulSoup(html, 'html.parser')

    def tag_to_string(self, tag):
        return tag.get_text(strip=True)

    def cleanup(self):
        pass

    def postprocess_html(self, soup, url):
        return soup

    def preprocess_html(self, soup, url):
        return soup

    def download_to_string(self, url):
        response = requests.get(url)
        response.encoding = self.encoding
        return response.text

    def absolute_url(self, base, link):
        return urljoin(base, link)

    def print_version(self, url):
        return url  # Override in recipe if needed

    def populate_article_metadata(self, article, soup, first):
        # Stub: recipes may extract author, summary, etc.
        article['author'] = None
        article['summary'] = None

    def get_article_url(self, article):
        return article.get('url')

    def get_article_title(self, article):
        return article.get('title')

    def get_article_date(self, article):
        return article.get('date', datetime.now().isoformat())

    def abort_article(self, msg):
        raise Exception(f"Article aborted: {msg}")

    def add_toc_thumbnail(self, article, src):
        self.toc_thumbnail[article['url']] = src

    def soup_from_url(self, url):
        return self.index_to_soup(url)

    def soup_from_html(self, html):
        return BeautifulSoup(html, 'html.parser')

    def get_browser(self):
        """Return a requests.Session object to mimic Calibre's browser."""
        return self.session

    def get(self, url, **kwargs):
        """Wrapper for GET requests."""
        response = self.session.get(url, **kwargs)
        response.encoding = self.encoding
        return response.text

    def post(self, url, data=None, **kwargs):
        """Wrapper for POST requests."""
        response = self.session.post(url, data=data, **kwargs)
        response.encoding = self.encoding
        return response.text

    def login(self):
        """Stub for login flow."""
        if self.login_url and self.username and self.password:
            print(f"🔐 Logging in to {self.login_url} as {self.username}")
            # You can customize this to match actual login forms
            payload = {
                'username': self.username,
                'password': self.password
            }
            self.session.post(self.login_url, data=payload)

    def extract_text(self, soup, selector):
        """Extract text using CSS selector."""
        tag = soup.select_one(selector)
        return tag.get_text(strip=True) if tag else ''

    def extract_all(self, soup, selector):
        """Extract all matching tags."""
        return soup.select(selector)

    def apply_regexps(self, html, regexps):
        """Apply regex substitutions."""
        for pattern, repl in regexps:
            html = re.sub(pattern, repl, html)
        return html

    def preprocess(self, html):
        """Apply preprocessing regexps."""
        return self.apply_regexps(html, self.preprocess_regexps)

    def postprocess(self, html):
        """Apply postprocessing regexps."""
        return self.apply_regexps(html, self.postprocess_regexps)

    def sleep(self, seconds):
        """Sleep between requests."""
        time.sleep(seconds)

    def debug(self, msg):
        """Print debug messages."""
        print(f"[DEBUG] {msg}")


class HTMLParser:
    def __init__(self):
        self.data = []

    def handle_starttag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        pass

    def handle_data(self, data):
        self.data.append(data)

    def get_data(self):
        return ''.join(self.data)


class Browser:
    def __init__(self):
        self.session = requests.Session()

    def open(self, url):
        response = self.session.get(url)
        response.raise_for_status()
        return response.text

    def open_novisit(self, url):
        return self.open(url)

    def set_cookie(self, name, value):
        self.session.cookies.set(name, value)

    def set_header(self, name, value):
        self.session.headers[name] = value

    def login(self, url, data):
        return self.session.post(url, data=data).text


def parse_date(date_str):
    try:
        return dateutil_parse(date_str)
    except Exception:
        return None


class Recipe:
    title = "Stub Recipe"
    description = "This is a stubbed recipe"


class Log:
    def __init__(self):
        pass

    def info(self, msg):
        print(f"[INFO] {msg}")

    def error(self, msg):
        print(f"[ERROR] {msg}")

    def warn(self, msg):
        print(f"[WARN] {msg}")


class Image:
    def __init__(self, path):
        self.path = path

    def resize(self, width, height):
        print(f"Resizing {self.path} to {width}x{height}")

    def save(self, out_path):
        print(f"Saving image to {out_path}")


class PersistentTemporaryFile:
    def __init__(self, mode='w+b', suffix='', prefix='tmp', dir=None):
        self._file = tempfile.NamedTemporaryFile(
            mode=mode, suffix=suffix, prefix=prefix, dir=dir, delete=False
        )
        self.name = self._file.name

    def write(self, data):
        return self._file.write(data)

    def read(self):
        return self._file.read()

    def close(self):
        return self._file.close()

    def flush(self):
        return self._file.flush()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def classes(*args):
    return list(args)


