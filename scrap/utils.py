import re


def format_string(string):
    """We don't want tabs, extra whitespaces,
    trailing white spaces, new lines, grrr

    """

    formatted = re.sub(r'\ +', ' ', string) \
                  .strip() \
                  .replace('\t', '') \
                  .replace('\n', ' ')
    return formatted
