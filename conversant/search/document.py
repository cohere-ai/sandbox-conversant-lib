# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Document:
    """Schema for documents retrieved by searchers."""

    source_link: str
    doc_id: str
    content: str
    embedding: Optional[List[float]] = None
