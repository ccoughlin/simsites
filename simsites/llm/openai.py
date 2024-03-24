"""
openai - code for working w. OpenAI API
"""
import os
from typing import *

from simsites.llm.backend import get_completions, get_embeddings, system_message, user_message

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
OPENAI_COMPLETIONS_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_GPT35_TURBO = "gpt-3.5-turbo-0125"
OPENAI_GPT4_TURBO = "gpt-4-turbo-preview"
DEFAULT_OPENAI_MODEL = OPENAI_GPT4_TURBO

OPENAI_EMBEDDINGS = "text-embedding-3-small"
OPENAI_EMBEDDINGS_URL = "https://api.openai.com/v1/embeddings"

OPENAI_SEO_KEYWORDS_PROMPT = '''
You are an expert Search Engine Optimization (SEO) Consultant. You are helping a client optimize their site contents to improve their search engine ranking for a specific search. You performed the search and clustered key terms from the top 10 search results for that same search. Your task is to explain these keywords to your customer in easy to understand terms, that they can then use to improve the contents of their own site.


Base your recommendations ONLY on the search that was performed and the list of keywords that were found for that particular search. 

If the keywords don't seem to be relevant to the search, offer general guidance on SEO for that particular search.

DO NOT MAKE UP A NEW SEARCH OR NEW KEYWORDS! Once you have a set of recommendations for the search, your answer is complete.

==================================================
EXAMPLES

Example 1
Search: Pet groomer near me
Keywords: ['55441, 55442, 55446, 55447', 'MN', '55369', 'MN 55447', 'MN 55447', 'MN 55447', 'MN 55447', 'MN 55447', 'MN 55447', 'MN 55447']
Your Answer: ZIP codes, specifically Minnesota ZIP codes. For a commercial website, it's often important to indicate your location and the areas that you service. This might help boost your search engine rank for searches that target specific geographic locations such as "pet groomers near me."

Example 2
Search: Best local plumber
Keywords: ['"I recommend them to anyone looking for a new furnace or maintenance work."', 'Excellent Service as usual.', 'Ben was professional & attentive to my needs.', 'Great service', "Ma
tt & Conner installed a new furnace and Air conditioner. They were on time, completed the install on schedule and very thorough responding to questions about the new systems. They'
re a very good team.", 'Great service!!!', 'Excellent service-Seasonal Check Up', 'Timely, great service', 'Connor was great, timely and cleaned up after installation', 'Excellent service accomplished in a timely fashion with courteous and friendly technicians.']
Your Answer: Positive customer testimonials. These may help boost your search engine rank by a) showing that you do indeed provide the product or service that the prospective customer is looking for and b) the search engine may factor review sentiment into your site's rank in the results.

Example 3
Search: Emergency plumbing service
Keywords: ['SCHEDULE SERVICE', 'Schedule Service Now', 'Book Service Today', 'Ask an Expert', 'Schedule service today', 'request service', 'FREE Second Opinion', 'Get a second opinion from our experts at no cost.', 'Schedule Service Now', 'Need service now?']
Your Answer: Link to schedule a service appointment. Remember, a prospective client is looking for a product or service. A clear link to schedule service is a clear signal to the search engine that you offer the service.
==================================================


Search: {search}
Keywords: {keywords}
Your Answer:
'''


OPENAI_CHECK_RECOMMENDATION_PROMPT = '''
You are an expert Search Engine Optimization (SEO) Consultant. You are helping a client optimize their site contents to improve their search engine ranking for a specific search. You have come up with a recommendation, based on your analysis of the top search results for that particular site.

You will be shown excerpts from your client's website that were found to be the most similar to your recommendation. Your task is to examine these excerpts and decide if they meet the criteria for your recommendation. If the excerpts do satisfy the conditions of your recommendation, you can respond to your client that they have done a good job implementing your recommendation.

If the excerpts do not seem to satisfy the criteria for your recommendation or otherwise do not seem relevant, you should offer suggestions to your client on how they can improve their site based on your recommendation.

Here is the web search that your client seeks your help with.

Search: {search}

Here is the recommendation you made for sites that want to optimize their search rankings against this search.

Recommendation: {recommendation}

And here are the most relevant excerpts from your client's current web site.

{excerpts}
'''

'''
curl https://api.openai.com/v1/chat/completions   -H "Content-Type: application/json"   -H "Authorization: Bearer $OPENAI_API_KEY"   -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {
        "role": "system",
        "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."
      },
      {
        "role": "user",
        "content": "Compose a poem that explains the concept of recursion in programming."
      }
    ]
  }'
'''


def completions(
        messages: List[Dict],
        model: AnyStr = DEFAULT_OPENAI_MODEL,
        timeout: int = 30
) -> AnyStr:
    """
    Makes a chat completion request to the OpenAI API.
    :param messages: list of messages to send w. the request
    :param model: model to target, defaults to "DEFAULT_OPENAI_MODEL"
    :param timeout: request timeout in seconds
    :return: model's response, or None if an error occurred.
    """
    # TODO: include check for first & second messages - if first is system, second must be user
    return get_completions(
        api_key=OPENAI_API_KEY,
        messages=messages,
        completions_url=OPENAI_COMPLETIONS_URL,
        model=model,
        timeout=timeout
    )


def embeddings(
        lines: List[AnyStr],
        chunk_size: int = 25
) -> list[list[float]]:
    """
    Generates embeddings for a list of strings.
    :param lines: lines to embed.
    :param chunk_size: number of lines per "chunked" call to API. Defaults to 25.
    :return: list of lists of floats
    """
    return get_embeddings(
        api_key=OPENAI_API_KEY,
        embeddings_url=OPENAI_EMBEDDINGS_URL,
        model=OPENAI_EMBEDDINGS,
        lines=lines,
        chunk_size=chunk_size
    )


def make_seo_recommendations(search: AnyStr, keywords: List[AnyStr]) -> Any:
    """
    Makes SEO recommendations for a given search, based on the list of keywords.
    :param search: search to consider
    :param keywords: list of keywords for that search e.g. topk most common words used in first 10 search results.
    :return: LLM's suggestions
    """
    return completions(
        messages=[
            system_message(OPENAI_SEO_KEYWORDS_PROMPT.format(keywords=keywords, search=search)),
            user_message(
                "What do these keywords for the top search results for this search tell me about optimizing my "
                "site for the same search?"
            )
        ]
    )


def check_seo_recommendation(search: AnyStr, recommendation: AnyStr, most_relevant_excerpts: List[AnyStr]) -> Any:
    return completions(
        messages=[
            system_message(
                OPENAI_CHECK_RECOMMENDATION_PROMPT.format(
                    search=search,
                    recommendation=recommendation,
                    excerpts=most_relevant_excerpts
                )
            ),
            user_message(
                "Does my website meet the conditions you detailed in your SEO recommendations?"
            )
        ]
    )
