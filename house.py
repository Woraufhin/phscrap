# -*- coding: utf-8 -*-


class House(object):
    """
    This is a house, get used to it
    """

    headers = [u'Título', u'Dirección', u'Precio', u'Info', u'URL']

    def __init__(self, title='', address='',
                 price='', info='', link=''):
        self.title = title
        self.address = address
        self.price = price
        self.info = info
        self.link = link

    @property
    def row(self):
        return [
            self.title,
            self.address,
            self.price,
            self.info,
            self.link,
        ]
