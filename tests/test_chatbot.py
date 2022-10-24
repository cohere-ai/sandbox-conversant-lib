# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.

import pytest
from conversant.chatbot import Chatbot


def test_initialization_err() -> None:
    """Tests that Chatbot is an abstract class."""
    with pytest.raises(TypeError):
        _ = Chatbot()
