from abc import ABCMeta, abstractmethod

from house import House


class Scraper(object):

    __metaclass__ = ABCMeta

    def __init__(self, soup):
        self.soup = soup

    @abstractmethod
    def scrap(self):
        """
        Should return a list of Houses
        """
        pass


class Argenscrap(Scraper):

    URL = 'http://www.argenprop.com'

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
