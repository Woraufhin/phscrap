""" Utils for app """

import re
import os
import smtplib
import logging
from email.mime.text import MIMEText

from .house import House
from .unicode_csv import UnicodeReader, UnicodeWriter


def format_string(string):
    """ We don't want tabs, extra whitespaces,
    trailing white spaces, new lines, grrr

    """

    formatted = re.sub(r'\ +', ' ', string) \
                  .strip() \
                  .replace('\t', '') \
                  .replace('\n', ' ')
    return formatted


def find_differences(path, data):
    """ We read the old csv, load the houses,
        and then proceed to diff the sets.

    """
    if os.path.exists(path):
        with open(path, 'r') as csv_file:
            rows = UnicodeReader(csv_file)
            next(rows, None)  # skip the headers
            houses = [House(*row) for row in rows]

        diff = set(data).difference(houses)

        if diff:
            logging.info('Found %i new entries this run:', len(diff))
            for h in diff:
                logging.info('\t%s, %s', h.price, h.address)
        else:
            logging.info('No new entries found')

        return diff
    else:
        logging.warning(
            'Not calculating diff. File {} does not exist'.format(path)
        )

    return None


def write_csv(path, houses):
    """ Write csv with information from row
        property

    """

    logging.info('Writing CSV in %s', path)
    with open(path, 'wb') as f:
        writer = UnicodeWriter(f)
        writer.writerows(
            [House.headers] + [x.row for x in houses]
        )


def send_email(enable, login, passwd, to, data):
    if enable:
        if data:
            logging.info('Sending email to %r', to)
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(login, passwd)

            body = '\n'.join(' - '.join(e.row) for e in data)
            message = MIMEText(body, 'plain', 'utf-8')
            message['Subject'] = 'Nuevos ranchos'
            message['From'] = 'PH Scrap <{}>'.format(login)
            message['To'] = ', '.join(to)

            server.sendmail(login, to, message.as_string())
            server.quit()
        else:
            logging.warning('Nothing to email')
    else:
        logging.warning('Emailing feature is disabled')
