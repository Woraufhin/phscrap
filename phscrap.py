#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import io
import csv
import codecs
import argparse
import cStringIO

import toml

from scrapers import Scraper, Argenscrap


class ConfigException(Exception):
    """
    Something went wrong with config
    """
    pass


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        data = self.encoder.encode(data)
        self.stream.write(data)
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


class Daemon(object):

    headers = [u'Título', u'Dirección', u'Precio', u'Info', u'URL']

    def __init__(self, config):
        self.config = config
        self.scrappers = []
        self.houses = []

    def scrap(self):
        for scrapper in self.scrappers:
            self.houses.extend(scrapper.scrap())
        self.write_csv()

    def write_csv(self):
        with open(os.path.expanduser('~/new_sample.csv'), 'wb') as f:
            writer = UnicodeWriter(f)
            writer.writerows([self.headers] + [e.row for e in self.houses])

    def add_scrappers(self):
        for key, val in self.config['data'].iteritems():
            if key == 'argenprop':
                self.scrappers.extend([Argenscrap(url) for url in val])


def parse_args():
    parser = argparse.ArgumentParser(description='Scrapper')
    parser.add_argument(
        '-c', '--config', default=None,
        help='Path to the configuration file'
    )
    parser.add_argument(
        '-u', '--url',
        action='append',
        help='List of urls'
    )
    return parser.parse_args()


def get_config(path):
    try:
        with io.open(path, encoding='utf-8') as f:
            return toml.load(f)
    except TypeError:
        raise ConfigException('Config cannot be None')
    except IOError as e:
        raise ConfigException(e)


def main():
    args = parse_args()

    config = get_config(args.config)
    Scraper.timeout = config['settings']['timeout']

    daemon = Daemon(config)
    daemon.add_scrappers()
    daemon.scrap()
