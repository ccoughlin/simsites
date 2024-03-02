"""
search_keywords - demonstrates conducting a search and returning keywords from the top sites found for that search.
"""
import argparse
import json
from typing import *
import time
from simsites import cluster
from simsites.llm.mistral import make_seo_recommendations
from simsites.util import ddgs
import logging
logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


def main(search_to_optimize: AnyStr, site_sources: List[AnyStr], output_fname: AnyStr = None):
    """
    Runs a demo of the process - given a search, perform the search to retrieve the top 10 search results. Cluster
    the text contents of the sites and return both the most common keywords found in these sites, plus LLM
    recommendations based on these keywords.
    :param search_to_optimize: web search to optimize
    :param site_sources: source of e.g. the top 10 search results for the site.
    :param output_fname: if specified, writes the results to this file.
    :return:
    """
    start = time.time()
    llm_recommendations = list()
    clustered_site_contents = cluster.cluster_sites(site_sources=site_sources)
    top_5 = cluster.top_keywords(
        clusters=clustered_site_contents['clusters'],
        sentences=clustered_site_contents['lines']
    )
    print('Clustering sites complete!')
    print("Here are the Top 5 most common sets of keywords (ordered most common first):\n\n")
    for top_set in top_5:
        print("Keywords:")
        print(','.join(top_set))
        print('\n')
        response = make_seo_recommendations(
            keywords=top_set,
            search=search_to_optimize
        )
        print("Recommendations from the LLM:")
        print(response)
        llm_recommendations.append(response)
        print('- - -' * 10)
    if output_fname:
        with open(output_fname, 'w') as fidout:
            json.dump(
                {
                    'search': search_to_optimize,
                    'keywords': top_5,
                    'recommendations': llm_recommendations
                },
                fidout,
                indent=2
            )
        print("Results saved to '{0}'".format(output_fname))
    print("Total recommendation runtime {0}".format(time.time() - start))
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='search_keywords.py',
        description='Demonstrates clustering & recommendations'
    )
    parser.add_argument(
        '-s',
        '--search',
        help='Conduct a search and use top 10 results as demo input',
        required=False
    )
    parser.add_argument(
        '-o',
        '--output',
        help='Specify an output file',
        required=False
    )
    args = parser.parse_args()
    if args.search is None:
        search = input("Enter a search to perform >> ")
    else:
        search = args.search
    print("Performing search: '{0}'".format(search))
    sites = ddgs.fetch_results(
        search=search
    )
    print("Clustering {0} site(s) found for search '{1}'".format(
        len(sites),
        search
    ))
    main(
        site_sources=sites,
        search_to_optimize=search,
        output_fname=args.output
    )
