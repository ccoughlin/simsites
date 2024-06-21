simsites
=
This repo is a proof of concept of an idea for using Generative AI (GenAI) for Search Engine Optimization (SEO).

The process starts off by fetching the top search results for a query, clustering their contents, and having the LLM make a set of observations based on what it finds in the clusters:

![Screenshot 2024-06-21 164911](https://github.com/ccoughlin/simsites/assets/922923/10c15ebe-2d8c-4ed8-ad7b-153cdb4139d9)

Next, the site to be optimized is fetched, and the LLM is asked to make recommendations for improving the site's rank in the search, based on what it observed about the contents of the top search results:

![Screenshot 2024-06-21 170703](https://github.com/ccoughlin/simsites/assets/922923/38b6eb84-a567-49ec-9829-d078af61703e)

Outline of the process:
1. Conduct a web search and fetch the contents of e.g. the first 10 results.
2. Clean the contents and cluster the text.
3. Find the largest clusters and their centroids; the theory is that the largest clusters represent the words or phrases used most often in top results and the centroids are good representations of each cluster.
4. Present the centroids to the LLM along with the original search, and have the LLM make recommendations based on the search and the words that seem to show up the most often in the top results.
