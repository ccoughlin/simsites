"""
serpapi - functions for working with SerpApi
"""
import json
import os
import logging

import requests

SERPAPI_KEY = os.environ['SERPAPI_KEY']
SERPAPI_HTML_URL = 'https://serpapi.com/search.html'
SERPAPI_JSON_URL = 'https://serpapi.com/search.json'


def get_params(query: str, location: str = None, country: str = "us", search_language: str = "en") -> dict:
    """
    Constructs the SerpApi parameters object.
    :param query: search to run
    :param location: location of the search. Likely defaults to proxy location if not specified.
    :param country: country of the search, defaults to "us"
    :param search_language: language of the search, defaults to "en"
    :return: dict
    """
    params = {
        "api_key": SERPAPI_KEY,
        "engine": "google",
        "q": query,
        "google_domain": "google.com",
        "gl": country,
        "hl": search_language
    }
    if location:
        params["location"] = location
    return params


def search_google(
        search: str,
        location: str = None,
        country: str = 'us',
        search_language: str = 'en',
        timeout: int = 60,
        as_json: bool = True
) -> str:
    """
    Executes a search through the SerpApi API.
    :param search: search to run
    :param location: location of the search. Likely defaults to proxy location if not specified.
    :param country: country of the search, defaults to "us"
    :param search_language: language of the search, defaults to "en"
    :param timeout: request timeout in seconds
    :param as_json: if True (default), makes request to SerpApi JSON URL. If False, request is sent to SerpAPI HTML URL.
    :return: string
    """
    result = None
    try:
        r = requests.get(
            url=SERPAPI_JSON_URL if as_json else SERPAPI_HTML_URL,
            params=get_params(
                query=search,
                location=location,
                country=country,
                search_language=search_language
            ),
            timeout=timeout
        )
        if r.status_code == 200:
            result = r.text
        else:
            logging.error("SERPAPI returned {0}".format(r.status_code))
    finally:
        return result


def get_organic_search_results(
        search: str,
        location: str = None,
        country: str = 'us',
        search_language: str = 'en',
        timeout: int = 60,
) -> list:
    """
    Performs a SerpApi Google search and returns the organic results.
    :param search: search to run
    :param location: location of the search. Likely defaults to proxy location if not specified.
    :param country: country of the search, defaults to "us"
    :param search_language: language of the search, defaults to "en"
    :param timeout: request timeout in seconds
    :return: list of results, each result is a dict
    """
    results = list()
    try:
        search_results = search_google(
            search=search,
            location=location,
            country=country,
            search_language=search_language,
            timeout=timeout
        )
        if search_results:
            search_obj = json.loads(search_results)
            results = search_obj['organic_results']
        else:
            logging.warning("No search results received returning None")
    finally:
        return results
