import logging
import itertools
from abc import ABCMeta, abstractmethod

import bs4
import requests

from .house import House


class Scraper(object):

    __metaclass__ = ABCMeta

    TIMEOUT = 30
    TRACK = itertools.count(1).next

    def __init__(self, url):
        self.id = self.TRACK()
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

    def __str__(self):
        return '{} #{}'.format(
            self.__class__.__name__,
            self.id
        )


class Zonacrap(Scraper):

    URL = 'http://www.zonaprop.com.ar'

    def __init__(self, url):
        Scraper.__init__(self, url)
        self.soup = self.get_soup()

    def get_soup(self):
        html = bs4.BeautifulSoup(self.request(), 'html.parser')
        return html.find_all('li', {'class': 'post'})

    def scrap(self):
        cols = [
            self.get_title(),
            self.get_address(),
            self.get_price(),
            self.get_info(),
            self.get_url()
        ]

        rows = zip(*cols)
        logging.info('[%s] Found %i houses' % (self, len(rows)))

        return [House(*row) for row in rows]

    def get_title(self):
        return [e.find('h4').get_text().strip()
                for e in self.soup]

    def get_address(self):
        return [e.find('div', {'class': 'post-text-location'})
                 .get_text()
                 .replace('\n', ' ')
                for e in self.soup]

    def get_info(self):
        return [e.find('ul', {'class': 'misc unstyled'})
                 .get_text()
                 .replace('\n', ' ')
                for e in self.soup]

    def get_price(self):
        return [e.find('span', {'class': 'precio-valor'})
                 .get_text()
                 .strip()
                for e in self.soup]

    def get_url(self):
        return [self.URL +
                e.find('div', {'class': 'post-text-desc'})
                 .find('a').get('href')
                for e in self.soup]


class Argencrap(Scraper):

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
        logging.info('[%s] Found %i houses' % (self, len(rows)))

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
