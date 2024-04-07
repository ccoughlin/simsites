"""
search_keywords - demonstrates conducting a search and returning keywords from the top sites found for that search.
"""
import argparse
import json
from typing import *
import time
from simsites import cluster
import simsites.llm.openai as openai
from simsites.util import serpapi, embed
import logging
logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


def main(
        search_to_optimize: AnyStr,
        site_sources: List[AnyStr],
        local_embed: bool = True,
        output_fname: AnyStr = None):
    """
    Runs a demo of the process - given a search, perform the search to retrieve the top 10 search results. Cluster
    the text contents of the sites and return both the most common keywords found in these sites, plus LLM
    recommendations based on these keywords.
    :param search_to_optimize: web search to optimize
    :param site_sources: source of e.g. the top 10 search results for the site.
    :param local_embed: if True (default), use a local model to generate embeddings. If False, uses an LLM API call.
    :param output_fname: if specified, writes the results to this file.
    :return:
    """
    start = time.time()
    clustered_site_contents = cluster.cluster_sites(
        site_sources=site_sources,
        embed_function=embed.generate_embeddings if local_embed else openai.embeddings
    )
    top_5 = cluster.top_keywords(
        clusters=clustered_site_contents['clusters'],
        sentences=clustered_site_contents['lines']
    )
    final_results = {
        'search': search_to_optimize,
        'recommendations': list()
    }
    print('Clustering sites complete!')
    print("Here are the Top 5 most common sets of keywords (ordered most common first):\n\n")
    for top_set in top_5:
        print("Keywords:")
        print(','.join([line[:25] for line in top_set]))
        print('\n')
        response = openai.make_seo_recommendations(
            keywords=top_set,
            search=search_to_optimize
        )
        print("Recommendations from the LLM:")
        print(response)
        print('- - -' * 10)
        final_results['recommendations'].append({
            'cluster_keywords': top_set,
            'llm_recommendations': response
        })
    end = time.time()
    elapsed = str(end - start)
    print("Total recommendation runtime {0}".format(elapsed))
    print()
    final_results['runtime'] = elapsed
    if output_fname:
        with open(output_fname, 'w') as fidout:
            json.dump(final_results, fidout, indent=2)
        print("Results saved to '{0}'".format(output_fname))


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
    if args.search is None:
        search = input("Enter a search to perform >> ")
    else:
        search = args.search
    print("Performing search: '{0}'".format(search))
    sites = serpapi.fetch_results(
        search=search
    )
    print("Clustering {0} site(s) found for search '{1}'".format(
        len(sites),
        search
    ))
    main(
        site_sources=sites,
        search_to_optimize=search,
        local_embed=args.local_embed,
        output_fname=args.output
    )
