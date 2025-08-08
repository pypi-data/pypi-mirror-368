import requests
import logging
from .cache import _URLCacheDB
import random

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, 
    format='%(levelname)s: %(name)s: %(message)s'
)

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0',
    'Mozilla/5.0 (iPad; CPU OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_6_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:101.0) Gecko/20100101 Firefox/101.0',
    'Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.101 Mobile Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
]

BASE_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'DNT': '1',
}

class URLCache:
    def __init__(self, databse_path: str = 'url_cache.db'):
        self.url_cache_db = _URLCacheDB(databse_path)

    def get_url(self, url: str) -> str:
        check = self.url_cache_db.get(url)
        if check is None:
            live = self.__get_url(url)
            self.url_cache_db.put(url, live)
            return live
        return check

    def __get_url(self, url: str) -> str:
        headers = BASE_HEADERS.copy()
        headers['User-Agent'] = random.choice(USER_AGENTS)
        output = requests.get(url, headers=headers)
        if output.status_code == 403:
            logger.error("403: Access Denied")
            raise Exception("403: Access Denied")
        if output.status_code == 429:
            raise Exception("429: Too Many Requests")
        if output.status_code == 200:
            return output.text
        logger.error("Unknown Exception: %s", output.status_code)
        raise Exception("Unknown Exception: " + str(output.status_code))

    def seen_before(self, url: str) -> bool:
        check = self.url_cache_db.get(url)
        if check is None:
            return False
        return True

if __name__ == '__main__':
    raise Exception("Do not run this directly.")