# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.

from conversant.search.document import Document
from conversant.search.local_searcher import LocalSearcher


def test_no_match(mock_local_searcher: LocalSearcher) -> None:
    """Tests impossible thresholds can't be met.

    Args:
        searcher (LocalSearcher): Searcher object.
    """
    mock_local_searcher.embed_documents()

    self_sim = mock_local_searcher._measure_similarity(
        mock_local_searcher.documents[0].embedding,
        mock_local_searcher.documents[0].embedding,
    )

    search_result = mock_local_searcher.search(
        query="hello world",
        threshold=self_sim + 1.0,  # Impossible threshold
    )

    assert search_result is None


def test_match(mock_local_searcher: LocalSearcher) -> None:
    """Tests zero-threshold always gives a match.

    Args:
        searcher (LocalSearcher): Searcher object.
    """
    search_result = mock_local_searcher.search(
        query="hello world", threshold=0.0  # Threshold-free
    )

    assert isinstance(search_result, Document)
