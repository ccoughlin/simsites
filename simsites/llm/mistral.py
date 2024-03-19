"""
mistral - code for working w. Mistral AI
"""
import json
import os
from typing import *
import logging
import requests


MISTRAL_API_KEY = os.environ["MISTRAL_API_KEY"]
MISTRAL_COMPLETIONS_URL = "https://api.mistral.ai/v1/chat/completions"
MISTRAL_MEDIUM = "mistral-medium-latest"
MISTRAL_LARGE = "mistral-large-latest"
DEFAULT_MISTRAL_MODEL = MISTRAL_LARGE

MISTRAL_EMBEDDINGS = "mistral-embed"
MISTRAL_EMBEDDINGS_URL = "https://api.mistral.ai/v1/embeddings"

MISTRAL_SEO_KEYWORDS_PROMPT = '''
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


MISTRAL_CHECK_RECOMMENDATION_PROMPT = '''
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


USER_ROLE = 'user'
SYSTEM_ROLE = 'system'
AVAILABLE_ROLES = [USER_ROLE, SYSTEM_ROLE]

REQUEST_HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': f'Bearer {MISTRAL_API_KEY}'
}


def gen_mistral_message(content: AnyStr, role: AnyStr) -> Dict:
    """
    Generates a Mistral message: dict with a role and content.
    :param content: content of the message
    :param role: role, must be one of "AVAILABLE_ROLES"
    :return: dict
    """
    if role not in AVAILABLE_ROLES:
        logging.error("Role '{0}' not available, must be one of {1}".format(role, AVAILABLE_ROLES))
    else:
        return {
            'role': role,
            'content': content
        }


def user_message(content: AnyStr, json_response: bool = False) -> Dict:
    """
    Generates a Mistral user message
    :param content: content of the message
    :param json_response: if True, adds the 'response_format' parameter to the message required for JSON responses
    from Mistral
    :return: dict
    """
    msg = gen_mistral_message(role=USER_ROLE, content=content)
    if json_response:
        msg['response_format'] = {"type": "json_object"}
    return msg


def system_message(content: AnyStr) -> Dict:
    """
    Generates a Mistral system message.
    :param content: content of the message
    :return: dict
    """
    return gen_mistral_message(role=SYSTEM_ROLE, content=content)


def request(
    url: AnyStr,
    data: Dict[AnyStr, Any],
    timeout: int = 30
) -> Any:
    """
    Makes a request to the Mistral API.
    :param url: URL to hit
    :param data: data to be sent w. the request
    :param timeout: request timeout in seconds
    :return: JSON string response from the API if successful, otherwise None
    """
    result = None
    try:
        r = requests.post(
            url=url,
            headers=REQUEST_HEADERS,
            json=data,
            timeout=timeout
        )
        if r.status_code == 200:
            result = r.text
        else:
            logging.error("Mistral API returned {0}".format(r.status_code))
    finally:
        return result


def completions(
        messages: List[Dict],
        model: AnyStr = DEFAULT_MISTRAL_MODEL,
        timeout: int = 30
) -> AnyStr:
    """
    Makes a chat completion request to the Mistral API.
    :param messages: list of messages to send w. the request
    :param model: model to target, defaults to "DEFAULT_MISTRAL_MODEL"
    :param timeout: request timeout in seconds
    :return: model's response, or None if an error occurred.
    """
    assistant_response = None
    # TODO: include check for first & second messages - if first is system, second must be user
    try:
        response = request(
            url=MISTRAL_COMPLETIONS_URL,
            data={
                'model': model,
                'messages': messages
            },
            timeout=timeout
        )
        if completions:
            payload = json.loads(response)
            choices = payload['choices']
            assistant_response = choices[0]['message']['content']
        else:
            logging.error("No Mistral completion request received returning None")
    except Exception as err:
        logging.exception(err)
    finally:
        return assistant_response


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
    embeddings = list()
    try:
        for chunk in [lines[i: i + chunk_size] for i in range(0, len(lines), chunk_size)]:
            embeddings_response = request(
                url=MISTRAL_EMBEDDINGS_URL,
                data={
                    'model': MISTRAL_EMBEDDINGS,
                    'input': chunk
                }
            )
            if embeddings_response:
                payload = json.loads(embeddings_response)
                embeddings.extend([embedding['embedding'] for embedding in payload['data']])
    except Exception as err:
        logging.exception(err)
    finally:
        return embeddings


def make_seo_recommendations(search: AnyStr, keywords: List[AnyStr]) -> Any:
    """
    Makes SEO recommendations for a given search, based on the list of keywords.
    :param search: search to consider
    :param keywords: list of keywords for that search e.g. topk most common words used in first 10 search results.
    :return: Mistral LLM's suggestions
    """
    return completions(
        messages=[
            system_message(MISTRAL_SEO_KEYWORDS_PROMPT.format(keywords=keywords, search=search)),
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
                MISTRAL_CHECK_RECOMMENDATION_PROMPT.format(
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