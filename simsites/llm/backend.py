"""
backend - makes the requests to the LLM API.
"""
import json
from typing import *
import logging

import requests

USER_ROLE = 'user'
SYSTEM_ROLE = 'system'
AVAILABLE_ROLES = [USER_ROLE, SYSTEM_ROLE]


def get_headers(api_key: str) -> dict[str, str]:
    """
    Generates the default request headers.
    :param api_key: LLM API key
    :return: dict
    """
    return {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }


def gen_chat_message(content: AnyStr, role: AnyStr) -> Dict:
    """
    Generates a chat message: dict with a role and content.
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


def user_message(content: AnyStr, **kwargs) -> Dict:
    """
    Generates a user message
    :param content: content of the message
    :return: dict
    """
    msg = gen_chat_message(role=USER_ROLE, content=content)
    if kwargs:
        msg.update(kwargs)
    return msg


def system_message(content: AnyStr) -> Dict:
    """
    Generates a system message.
    :param content: content of the message
    :return: dict
    """
    return gen_chat_message(role=SYSTEM_ROLE, content=content)


def request(
    url: AnyStr,
    data: Dict[AnyStr, Any],
    headers: Dict[AnyStr, AnyStr] = None,
    timeout: int = 30
) -> Any:
    """
    Makes a request to the LLM API.
    :param url: URL to hit
    :param data: data to be sent w. the request
    :param headers: request headers (if any)
    :param timeout: request timeout in seconds
    :return: JSON string response from the API if successful, otherwise None
    """
    result = None
    try:
        r = requests.post(
            url=url,
            headers=headers,
            json=data,
            timeout=timeout
        )
        if r.status_code == 200:
            result = r.text
        else:
            logging.error("LLM API returned {0}".format(r.status_code))
    finally:
        return result


def get_completions(
        messages: List[Dict],
        api_key: AnyStr,
        completions_url: AnyStr,
        model: AnyStr,
        timeout: int = 30
) -> AnyStr:
    """
    Makes a chat completion request to the LLM API.
    :param api_key: LLM API key
    :param messages: list of messages to send w. the request
    :param completions_url: Completions URL
    :param model: model to target
    :param timeout: request timeout in seconds
    :return: model's response, or None if an error occurred.
    """
    assistant_response = None
    try:
        response = request(
            url=completions_url,
            headers=get_headers(api_key=api_key),
            data={
                'model': model,
                'messages': messages
            },
            timeout=timeout
        )
        if get_completions:
            payload = json.loads(response)
            choices = payload['choices']
            assistant_response = choices[0]['message']['content']
        else:
            logging.error("No Mistral completion request received returning None")
    except Exception as err:
        logging.exception(err)
    finally:
        return assistant_response


def get_embeddings(
        api_key: AnyStr,
        embeddings_url: AnyStr,
        model: AnyStr,
        lines: List[AnyStr],
        chunk_size: int = 25
) -> list[list[float]]:
    """
    Generates embeddings for a list of strings.
    :param api_key: API key
    :param embeddings_url: LLM Embeddings API endpoint
    :param model: model to target
    :param lines: lines to embed.
    :param chunk_size: number of lines per "chunked" call to API. Defaults to 25.
    :return: list of lists of floats
    """
    embeddings = list()
    try:
        for chunk in [lines[i: i + chunk_size] for i in range(0, len(lines), chunk_size)]:
            embeddings_response = request(
                url=embeddings_url,
                headers=get_headers(api_key=api_key),
                data={
                    'model': model,
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
