#!/usr/bin/env python

import io
import logging
import argparse
import collections
from time import sleep

import toml

from .scrapers import Scraper, Argencrap, Zonacrap
from .house import House
from .utils import write_csv, find_differences, send_email


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
            self.houses.extend(set(scrapper.scrap()))

        diff = find_differences(self.config['settings']['out'], self.houses)
        write_csv(self.config['settings']['out'], self.houses)
        send_email(
            self.config['emailing']['enable'] and not \
            self.config['settings']['single_run'],
            self.config['emailing']['login'],
            self.config['emailing']['passwd'],
            self.config['emailing']['receivers'],
            diff
        )


    def add_scrappers(self):
        for key, val in self.config['data'].iteritems():
            if key == 'argenprop':
                self.scrappers.extend([Argencrap(url) for url in val])
            elif key == 'zonaprop':
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
