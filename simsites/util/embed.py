"""
embed.py - generate embeddings locally instead of making calls to an API.
"""
from typing import *
import logging

from sentence_transformers import SentenceTransformer
from torch import Tensor

MULTILINGUAL_EMBEDDING_MODEL = "paraphrase-multilingual-mpnet-base-v2"
ENGLISH_EMBEDDING_MODEL = "all-mpnet-base-v2"


def get_local_embedder(multi_lang: bool = True) -> SentenceTransformer:
    """
    Returns a SentenceTransformer embedder model to embed strings on the local device. Will use a GPU if
    available but not required.
    :param multi_lang: if True (default), return an embedding model that supports multiple languages (perhaps at
    the expense of performance). If False, returns an English-only model that may perform slightly better.
    :return:
    """
    if multi_lang:
        model_name = MULTILINGUAL_EMBEDDING_MODEL
    else:
        model_name = ENGLISH_EMBEDDING_MODEL
    logging.info("Returning {0}".format(model_name))
    return SentenceTransformer(model_name)


def generate_embeddings(
        lines: List[AnyStr],
        model: SentenceTransformer = None
) -> List[Tensor]:
    """
    Generates embeddings for a list of strings.
    :param lines: lines to embed.
    :param model: SentenceTransformer model. If not specified, defaults to DEFAULT_EMBEDDING_MODEL.
    :return: list of PyTorch Tensors
    """
    if not model:
        model = get_local_embedder()
    return model.encode(
        lines,
        batch_size=64,
        show_progress_bar=False,
        convert_to_tensor=True
    )
