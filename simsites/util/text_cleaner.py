"""
text_cleaner - functions for cleaning text
"""
from typing import *
from bs4 import BeautifulSoup
from cleantext import clean


def split_site(site_text: AnyStr) -> List[AnyStr]:
    results = list()
    for line in site_text.split('\n'):
        stripped_line = line.strip()
        if len(stripped_line) > 0:
            results.append(stripped_line)
    return results


def sanitize_text(raw: AnyStr) -> AnyStr:
    """
    Sanitizes text input - tries to fix Unicode, normalize line breaks, etc.
    :param raw: raw text
    :return: hopefully cleaner text
    """
    return clean(
        raw,
        fix_unicode=True,               # fix various unicode errors
        to_ascii=True,                  # transliterate to closest ASCII representation
        lower=False,                    # lowercase text
        no_line_breaks=False,           # fully strip line breaks as opposed to only normalizing them
        no_urls=False,                  # replace all URLs with a special token
        no_emails=False,                # replace all email addresses with a special token
        no_phone_numbers=False,         # replace all phone numbers with a special token
        no_numbers=False,               # replace all numbers with a special token
        no_digits=False,                # replace all digits with a special token
        no_currency_symbols=False,      # replace all currency symbols with a special token
        no_punct=False,                 # remove punctuations
        replace_with_punct="",          # instead of removing punctuations you may replace them
        replace_with_url="<URL>",
        replace_with_email="<EMAIL>",
        replace_with_phone_number="<PHONE>",
        replace_with_number="<NUMBER>",
        replace_with_digit="0",
        replace_with_currency_symbol="<CUR>",
        lang="en"                       # set to 'de' for German special handling
    )


def strip_site(site_src: AnyStr, sanitize: bool = True) -> AnyStr:
    """
    Extract text contents from HTML source.
    :param site_src: HTML source
    :param sanitize: if True (default), try to sanitize the text (fix Unicode, normalize line breaks, etc.)
    :return: text of the site
    """
    soup = BeautifulSoup(site_src, 'html.parser')
    site_text = soup.get_text()
    if sanitize:
        site_text = sanitize_text(site_text)
    return site_text
