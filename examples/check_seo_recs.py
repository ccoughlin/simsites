"""
check_seo_recs - demonstrates checking a site against an SEO recommendation
"""
import argparse
import json
import sys
from typing import *
import time

import requests

import simsites.llm.mistral as mistral
from simsites.util import embed, vector_store
import logging

from simsites.util.text_cleaner import strip_site, split_site

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


def create_vector_store(
        site_src: AnyStr,
        local_embed: bool = True,
) -> vector_store.NNVectorStore:
    """
    Creates an in-memory vector store representation of a site's contents.
    :param site_src: HTML source of the site
    :param local_embed: if True (default), uses local embeddings models. Otherwise uses Mistral API.
    :return: populated vector store
    """
    site_text = strip_site(site_src)
    site_as_lines = split_site(site_text)
    vs = vector_store.NNVectorStore(
        embed_function=embed.generate_embeddings if local_embed else mistral.embeddings
    )
    vs.add_texts(site_as_lines)
    return vs


def main(
        search_to_optimize: AnyStr,
        site_src: AnyStr,
        recommendation: AnyStr,
        local_embed: bool = True,
        output_fname: AnyStr = None
) -> None:
    """
    Checks a website's contents against an SEO recommendation for a particular web search.
    :param search_to_optimize: web search to optimize the site against
    :param site_src: HTML source of the site to optimize
    :param recommendation: SEO recommendation for the search in question (i.e. not specific to the site itself)
    :param local_embed: if True (default), uses local embeddings models. If False, uses Mistral embeddings API.
    :param output_fname: if specified, saves the results to a JSON file.
    :return: None
    """
    start = time.time()
    final_results = {
        'search': search_to_optimize,
        'recommendation': recommendation
    }
    site_vector_store = create_vector_store(site_src, local_embed=local_embed)
    most_relevant_site_contents = site_vector_store.get_relevant_texts(query=recommendation)
    final_results['most_relevant_site_contents'] = most_relevant_site_contents
    response = mistral.check_seo_recommendation(
        search=search_to_optimize,
        recommendation=recommendation,
        most_relevant_excerpts=most_relevant_site_contents
    )
    end = time.time()
    elapsed = str(end - start)
    print("Total recommendation runtime {0}".format(elapsed))
    print()
    final_results['runtime'] = elapsed
    print(response)
    final_results['recommendation_check_results'] = response
    if output_fname:
        with open(output_fname, 'w') as fidout:
            json.dump(final_results, fidout, indent=2)
        print("Results saved to '{0}'".format(output_fname))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='seo_recs.py',
        description='Demonstrates checking a site against SEO recommendations'
    )
    parser.add_argument(
        '-o',
        '--output',
        help='Specify an output file',
        required=False
    )
    parser.add_argument(
        '--local_embed',
        help='If specified, uses local embedding model rather than LLM API call.',
        action='store_true'
    )
    args = parser.parse_args()
    if not args.local_embed:
        logging.info("Using remote API embeddings")
    else:
        logging.info("Using local embeddings model")
    search = input("Enter a web search to optimize >> ")
    url = input("Enter a URL to fetch (include http[s]) >> ")
    logging.info("Fetching {0}...".format(url))
    r = requests.get(url, timeout=60)
    if r.status_code == 200:
        site_as_text = r.text
    else:
        logging.error(f"Received status code {r.status_code}, aborting!")
        sys.exit(1)
    main(
        search_to_optimize=search,
        site_src=site_as_text,
        recommendation=input("Enter an SEO recommendation to check the site against >> "),
        local_embed=args.local_embed,
        output_fname=args.output
    )
