from abc import ABCMeta, abstractmethod

import bs4
import requests

from house import House


class Scraper(object):

    __metaclass__ = ABCMeta

    TIMEOUT = 30

    def __init__(self, url):
        self.url = url

    @abstractmethod
    def scrap(self):
        """
        Should return a list of Houses
        """
        pass

    def request(self):
        r = requests.get(self.url, timeout=self.TIMEOUT)
        r.raise_for_status()
        return r.text


class Argenscrap(Scraper):

    URL = 'http://www.argenprop.com'

    def __init__(self, url):
        Scraper.__init__(self, url)
        self.soup = self.get_soup()

    def get_soup(self):
        html = bs4.BeautifulSoup(self.request(), 'html.parser')
        return html.find_all('li', {'class': 'avisoitem'})

    def scrap(self):
        cols = [
            self.get_title(),
            self.get_address(),
            self.get_price(),
            self.get_info(),
            self.get_url()
        ]

        rows = zip(*cols)
        return [House(*row) for row in rows]

    def get_title(self):
        return [e.find('h3').get_text().strip()
                for e in self.soup]

    def get_address(self):
        return [e.find('h2').get_text().strip()
                for e in self.soup]

    def get_info(self):
        return [e.find('div', {'class': 'datoscomunes'})
                 .get_text()
                 .replace('\n', ' ')
                for e in self.soup]

    def get_price(self):
        return [e.find('p', {'class': 'list-price'})
                 .get_text()
                 .replace('\n', ' ')
                for e in self.soup]

    def get_url(self):
        return [self.URL + e.find('a').get('href')
                for e in self.soup]
