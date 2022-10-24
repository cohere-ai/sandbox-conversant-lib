# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.

import pytest

from conversant.search.document import Document


def test_empty_document() -> None:
    """Tests that empty documents fail."""

    with pytest.raises(TypeError):
        _ = Document()


def test_document_embed_optional() -> None:
    """Tests that document embeddings are optional."""

    my_doc = Document(
        source_link="http://some-url",
        doc_id="123",
        content="hello world.",
    )

    assert my_doc.embedding is None
