#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import csv
import codecs
import logging
import argparse
import cStringIO
from time import sleep

import toml

from .scrapers import Scraper, Argencrap, Zonacrap
from .house import House


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

    DATA = '/var/lib/phscrap/scrap.csv'

    def __init__(self, config):
        self.config = config
        self.scrappers = []
        self.houses = []

    def scrap(self):
        logging.info('Entering main loop.')
        logging.debug('Interval between runs is %i' %
                      self.config['settings']['interval'])

        while True:
            for scrapper in self.scrappers:
                self.houses.extend(scrapper.scrap())
            self.write_csv()
            sleep(self.config['settings']['interval'])

    def write_csv(self):
        logging.info('Writing CSV in %s' % self.DATA)
        with open(self.DATA, 'wb') as f:
            writer = UnicodeWriter(f)
            writer.writerows(
                [House.headers] + [x.row for x in set(self.houses)]
            )

    def add_scrappers(self):
        for key, val in self.config['data'].iteritems():
            if key == 'argenprop':
                self.scrappers.extend([Argencrap(url) for url in val])
            if key == 'zonaprop':
                self.scrappers.extend([Zonacrap(url) for url in val])
            else:
                logging.warning('Unknown scraper "%s"' % key)


def parse_args():
    parser = argparse.ArgumentParser(description='Scrapper')
    parser.add_argument(
        '-c', '--config', default='/etc/phscrap/config.toml',
        help='Path to the configuration file'
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


def configure_logging(verbosity, log_file):
    logging.basicConfig(
        level=getattr(logging, verbosity),
        filename=log_file,
        format='[%(asctime)s] [%(levelname)s] %(message)s'
    )


def main():
    args = parse_args()
    config = get_config(args.config)

    configure_logging(
        config['settings']['verbosity'],
        config['settings']['log_file']
    )

    logging.info('Initializing phscraper')
    Scraper.timeout = config['settings']['timeout']
    logging.debug('Timeout for requests is %i' % Scraper.timeout)

    daemon = Daemon(config)
    daemon.add_scrappers()
    daemon.scrap()
