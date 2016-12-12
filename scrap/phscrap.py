#!/usr/bin/env python

import io
import logging
import argparse
import collections
from time import sleep

import toml

from .scrapers import Scraper, Argencrap, Zonacrap
from .unicode_csv import UnicodeReader, UnicodeWriter
from .house import House


class ConfigException(Exception):
    """Something went wrong with config"""
    pass


class Daemon(object):

    def __init__(self, config):
        self.config = config
        self.scrappers = []
        self.houses = []

    def scrap(self):
        if not self.config['settings']['single_run']:
            logging.info('Entering main loop.')
            logging.debug('Interval between runs is %i',
                          self.config['settings']['interval'])
            while True:
                self._scrap()
                sleep(self.config['settings']['interval'])
        else:
            self._scrap()

    def _scrap(self):
        logging.info('Scraping.')
        for scrapper in self.scrappers:
            self.houses.extend(scrapper.scrap())
        self.write_csv()

    def write_csv(self):
        logging.info('Writing CSV in %s', self.config['settings']['out'])
        with open(self.config['settings']['out'], 'wb') as f:
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
                logging.warning('Unknown scraper "%s"', key)


def parse_args():
    parser = argparse.ArgumentParser(description='Scrapper')
    parser.add_argument(
        '-c', '--config', default='/etc/phscrap/config.toml',
        help='Path to the configuration file'
    )
    parser.add_argument(
        '-o', '--out', default=None,
        help='Path to the csv file'
    )
    parser.add_argument(
        '-s', '--single-run', action='store_true',
        help='Run scraper once'
    )
    parser.add_argument(
        '-v', '--verbosity',
        default=None,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Verbosity level default: INFO'
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


def configure_logging(verbosity, log_file, single_run):
    params = {
        'level': getattr(logging, verbosity),
        'format': '[%(asctime)s] [%(levelname)s] %(message)s'
    }

    if not single_run:
        params['filename'] = log_file

    logging.basicConfig(**params)


def _non_default(key, value, config):
    """True when value is valid or new for the config"""
    return value not in (None, tuple(), list()) or key not in config


def _deep_merge(base, override):
    for k, v in override.items():
        if v and isinstance(v, collections.Mapping):
            base[k] = _deep_merge(base.get(k, {}), v)
        else:
            # Override config has value or is new
            if _non_default(k, v, base):
                base[k] = v
    return base


def main():
    args = parse_args()
    config = _deep_merge(get_config(args.config), {'settings': args.__dict__})
    configure_logging(
        config['settings']['verbosity'],
        config['settings']['log_file'],
        config['settings']['single_run']
    )

    logging.info('Initializing phscraper')
    Scraper.timeout = config['settings']['timeout']
    logging.debug('Timeout for requests is %i', Scraper.timeout)

    daemon = Daemon(config)
    daemon.add_scrappers()
    daemon.scrap()
