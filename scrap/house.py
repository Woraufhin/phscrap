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

    def __hash__(self):
        return hash(self.title) ^ hash(self.address)

    def __eq__(self, other):
        """Override the default equals behaviour"""
        if isinstance(other, self.__class__):
            return [self.title, self.address] == [other.title, other.address]
        return NotImplemented

    @property
    def row(self):
        return [
            self.title,
            self.address,
            self.price,
            self.info,
            self.link,
        ]
