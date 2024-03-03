"""
cluster - clusters websites
"""
from typing import *
import logging
from sentence_transformers import util

from simsites.util.embed import generate_embeddings
from simsites.util.text_cleaner import strip_site, split_site


def cluster_sites(
        site_sources: List[AnyStr],
        embed_function: Any = generate_embeddings,
        min_cluster_size: int = 5,
        threshold: float = 0.75
) -> Dict[AnyStr, Any]:
    """
    Clusters the text from one or more websites.
    :param site_sources: HTML source for the sites to cluster.
    :param embed_function: function to generate embeddings, should accept a list of strings and return a list of floats
    or tensors.
    Defaults to local embeddings with the "generate_embeddings" function if not specified.
    :param min_cluster_size: minimum cluster size in lines: groupings below this are considered outliers and not
    returned.
    :param threshold: clustering (similarity) threshold to consider two strings as members of the same cluster.
    Defaults to 0.75.
    :return: dict of the form
    {
        'lines': [text from the sites],
        'embeddings': [tensor embeddings of the site text],
        'clusters': clusters identified. Clusters are ordered from largest to smallest; first element of each cluster
        is the cluster centroid (~ most common string in the cluster).
    }

    """
    lines = list()
    for src in site_sources:
        site_text = strip_site(src)
        site_as_lines = split_site(site_text)
        if len(site_as_lines) > 0:
            lines.extend(site_as_lines)
    if len(lines) > 0:
        site_embeddings = embed_function(lines)
        clusters = util.community_detection(site_embeddings, min_community_size=min_cluster_size, threshold=threshold)
        return {
            'lines': lines,
            'embeddings': site_embeddings,
            'clusters': clusters
        }
    else:
        logging.warning("No text received returning None")


def top_keywords(clusters, sentences, num_clusters: int = 5, num_terms: int = 5) -> List[List[AnyStr]]:
    """
    Returns a list of the top N keywords from the largest K clusters.
    :param clusters: clusters
    :param sentences: sentences that were clustered.
    :param num_clusters: number of clusters to examine, defaults to 5.
    :param num_terms: number of terms to return per cluster, defaults to 5.
    :return: list of K clusters, each with N top keywords.
    """
    results = list()
    for i, cluster in enumerate(clusters[:num_clusters]):
        cluster_keywords = list()
        for sentence_id in cluster:
            sentence = sentences[sentence_id]
            if sentence not in cluster_keywords:
                cluster_keywords.append(sentence)
            if len(cluster_keywords) >= num_terms:
                break
        results.append(cluster_keywords)
    return results

