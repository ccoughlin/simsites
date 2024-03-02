"""
mistral - code for working w. Mistral AI
"""
from typing import *
import os
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

MISTRAL_API_KEY = os.environ["MISTRAL_API_KEY"]
MISTRAL_MEDIUM = "mistral-medium-latest"
MISTRAL_LARGE = "mistral-large-latest"
DEFAULT_MISTRAL_MODEL = MISTRAL_LARGE

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


def make_seo_recommendations(search: AnyStr, keywords: List[AnyStr]) -> Any:
    client = MistralClient(api_key=MISTRAL_API_KEY)
    messages = [
        ChatMessage(
            role="system",
            content=MISTRAL_SEO_KEYWORDS_PROMPT.format(keywords=keywords, search=search)
        ),
        ChatMessage(
            role="user",
            content="What do these keywords for the top search results for this search tell me about optimizing my "
                    "site for the same search?"
        )
    ]
    chat_response = client.chat(
        model=DEFAULT_MISTRAL_MODEL,
        messages=messages
    )
    return chat_response.choices[0].message.content
