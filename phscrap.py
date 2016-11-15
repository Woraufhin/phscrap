#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import csv
import codecs
import cStringIO

import bs4
import requests

from scrapers import Argenscrap


URL = 'http://www.argenprop.com/Departamentos-tipo-casa-Alquiler-Almagro-' + \
      'Barrio-Norte-2-Dormitorios-Capital-Federal/mQ2KrbQ1KpQ1KprQ2KpaQ13' + \
      '5Kaf_801Kaf_817Kaf_100000001Kaf_800000002Kaf_800000004Kaf_80000000' + \
      '5Kaf_800000008Kaf_800000010Kaf_800000011Kaf_800000020Kaf_800000021' + \
      'Kaf_800000029Kaf_800000040Kaf_900000001Kaf_900000002Kaf_900000003K' + \
      'af_900000004Kaf_900000005Kaf_900000006Kaf_900000008Kaf_900000009Ka' + \
      'f_900000007Kaf_900000010Kaf_900000011Kaf_900000012Kaf_900000013Kaf' + \
      '_900000014Kaf_900000015Kaf_900000016Kaf_900000033Kaf_900000034Kaf_' + \
      '900000036Kaf_900000038Kaf_900000037Kaf_900000035Kaf_500000001Kaf_7' + \
      '3KvnQVistaResultadosKvncQVistaGrilla'


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


r = requests.get(URL)
r.raise_for_status()

soup = bs4.BeautifulSoup(r.text, 'html.parser')

lis = soup.find_all('li', {'class': 'avisoitem'})

headers = [u'Título', u'Dirección', u'Precio', u'Info', u'URL']

argenscrap = Argenscrap(lis)
houses = argenscrap.scrap()

with open(os.path.expanduser('~/sample.csv'), 'wb') as f:
    writer = UnicodeWriter(f)
    writer.writerows([headers] + [e.row for e in houses])
