# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.

import pytest

from conversant.search.searcher import Searcher


def test_initialization_err() -> None:
    """Tests that Searcher is an abstract class."""

    with pytest.raises(TypeError):
        _ = Searcher()


def test_req_embedded_docs(mock_searcher: Searcher) -> None:
    """Similarity should fail on unembedded docs.

    Args:
        mock_searcher (Searcher): Search fixture.
    """

    with pytest.raises(TypeError):
        mock_searcher._measure_similarity(
            mock_searcher.documents[0].embedding,
            mock_searcher.documents[0].embedding,
        )


def test_self_similarity(mock_searcher: Searcher) -> None:
    """Self similarity should be 1.0.

    Args:
        mock_searcher (Searcher): Search fixture.
    """

    mock_searcher.embed_documents()

    similarity = mock_searcher._measure_similarity(
        mock_searcher.documents[0].embedding,
        mock_searcher.documents[0].embedding,
    )

    assert similarity == pytest.approx(1.0)


def test_anti_sim(mock_searcher: Searcher) -> None:
    """Anti-similarity should be less than self-sim.

    Args:
        mock_searcher (Searcher): Search fixture.
    """

    mock_searcher.embed_documents()

    self_similarity = mock_searcher._measure_similarity(
        mock_searcher.documents[0].embedding,
        mock_searcher.documents[0].embedding,
    )

    anti_similarity = mock_searcher._measure_similarity(
        mock_searcher.documents[0].embedding,
        [-e for e in mock_searcher.documents[0].embedding],
    )

    assert anti_similarity < self_similarity
