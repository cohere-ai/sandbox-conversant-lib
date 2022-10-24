# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.

from abc import ABC, abstractmethod
from typing import Iterable, List, Optional

import cohere
import numpy as np

from conversant.search.document import Document


class Searcher(ABC):
    """Searches through documents for ground truth."""

    def __init__(self, client: cohere.Client, documents: Iterable[Document]):
        """Loads a searcher with a Cohere client & documents to search over.

        Args:
            client (cohere.Client): Provides access to Cohere API via the Python SDK
            documents (Iterable[Document]): Iterable cache of local Documents.
        """
        self.co = client
        self.documents = documents

    @abstractmethod
    def search(self, query: str) -> Optional[Document]:
        """Semantic search over local documents.

        Precisely _how_ the cache of local documents is updated
        is left to the implementation in a subclass.
        Args:
            query (str): Input query to match documents against.
        Returns:
            Optional[Document]: Best matching document, if found.
        """

    def _measure_similarity(self, embed_1: List[float], embed_2: List[float]) -> float:
        """Measures similarity between embeddings. Uses cosine similarity.

        Manually computes dot(A,B)/(||A||*||B||), to avoid adding
        more deps. Uses numpy methods for these computations.

        Args:
            embed_1 (List[float]): First embedding in the pair.
            embed_2 (List[float]): Second embedding in the pair.
        Returns:
            float: Similarity between the documents.
        """
        dot_product = np.dot(embed_1, embed_2)
        norm_product = np.linalg.norm(embed_1) * np.linalg.norm(embed_2)

        cos_similarity = dot_product / norm_product

        return cos_similarity

    def embed_documents(self) -> None:
        """Embeds the Searcher's documents."""

        embeddings = self.co.embed(texts=[d.content for d in self.documents]).embeddings

        for document, embedding in zip(self.documents, embeddings):
            document.embedding = embedding
