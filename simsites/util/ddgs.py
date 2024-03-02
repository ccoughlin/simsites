"""
ddgs_search - DuckDuckGo search
"""
import requests
from duckduckgo_search import DDGS
from typing import *
import logging


def search_ddgs(
        search: AnyStr,
        proxies: Dict[AnyStr, AnyStr] = None,
        timeout: int = 30,
        max_results: int = 10) -> List[Dict[AnyStr, AnyStr]]:
    """
    Conducts a search on DuckDuckGo and returns the results.
    :param search: search to perform
    :param proxies: optional proxies dict e.g. {'http': 'https://addr.to/proxy', 'https': 'https://addr.to/proxy'}
    :param timeout: request timeout in seconds. Defaults to 30.
    :param max_results: maximum number of results to return (defaults to 10)
    :return: list of dicts with search params.
    """
    with DDGS(proxies=proxies, timeout=timeout) as ddgs:
        return [r for r in ddgs.text(search, timelimit='y', max_results=max_results)]


def fetch_results(
        search: AnyStr,
        proxies: Dict[AnyStr, AnyStr] = None,
        timeout: int = 30,
        max_results: int = 10) -> List[AnyStr]:
    """
    Conducts a search on DuckDuckGo and returns the results.
    :param search: search to perform
    :param proxies: optional proxies dict e.g. {'http': 'https://addr.to/proxy', 'https': 'https://addr.to/proxy'}
    :param timeout: request timeout in seconds. Defaults to 30.
    :param max_results: maximum number of results to return (defaults to 10)
    :return: source of each search result. If a site couldn't be retrieved (e.g. blocked), returns DDG's search body
    for that site instead.
    """
    site_sources = list()
    search_results = search_ddgs(search=search, proxies=proxies, timeout=timeout, max_results=max_results)
    for search_result in search_results:
        r = requests.get(search_result['href'])
        if r.status_code == 200:
            site_sources.append(r.text)
        else:
            logging.warning("Received status code {0} for {1}, using search result body".format(
                r.status_code,
                search_result['href']
            ))
            site_sources.append(search_result['body'])
    return site_sources
