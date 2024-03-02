"""
embed.py - generate embeddings locally instead of making calls to an API.
"""
from typing import *
import logging

from sentence_transformers import SentenceTransformer
from torch import Tensor

MULTILINGUAL_EMBEDDING_MODEL = SentenceTransformer("paraphrase-multilingual-mpnet-base-v2")
ENGLISH_EMBEDDING_MODEL = SentenceTransformer("all-mpnet-base-v2")

DEFAULT_EMBEDDING_MODEL = MULTILINGUAL_EMBEDDING_MODEL


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
        model = DEFAULT_EMBEDDING_MODEL
    return model.encode(
        lines,
        batch_size=64,
        show_progress_bar=False,
        convert_to_tensor=True
    )
