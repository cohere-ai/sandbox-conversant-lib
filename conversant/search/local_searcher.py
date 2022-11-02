# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.

import logging
from typing import Iterable, Optional

import cohere

from conversant.search.document import Document
from conversant.search.searcher import Searcher


class LocalSearcher(Searcher):
    """Searches only a user-provided local document cache."""

    def __init__(self, client: cohere.Client, documents: Iterable[Document]):
        """Loads a searcher with a Cohere client & documents to search over.

        Args:
            client (cohere.Client): Provides access to Cohere API via the Python SDK
            documents (Iterable[Document]): Iterable cache of local Documents.
        """
        super().__init__(client, documents)

    def search(self, query: str, threshold: float = -1e6) -> Optional[Document]:
        """Searches by finding most similar doc in local docs.

        Does not make any updates to local doc cache. Only returns a document
        if the similarity is above the threshold.

        Args:
            query (str): Query to check docs against.
            threshold (float): Minimum similarity needed to return a document.

        Returns:
            Optional[Document]: Most similar doc to query. None if threshold not met.
        """

        embedded_query = self.co.embed(texts=[query]).embeddings[0]
        similarities = [
            self._measure_similarity(embedded_query, d.embedding)
            for d in self.documents
        ]

        max_similarity = max(similarities)

        if max_similarity < threshold:
            logging.warning(
                f"Max search similarity {max_similarity} below threshold {threshold}; "
                "no document returned."
            )
            return None

        logging.info(f"Search result found for query: {query}")
        nearest_idx = similarities.index(max_similarity)
        nearest_doc = self.documents[nearest_idx]

        return nearest_doc
