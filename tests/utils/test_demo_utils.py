# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.

from conversant.prompt_chatbot import PromptChatbot
from conversant.utils import demo_utils


def test_encode_decode_object(mock_prompt_chatbot: PromptChatbot) -> None:
    assert isinstance(
        demo_utils.decode_object(demo_utils.encode_object(mock_prompt_chatbot)),
        PromptChatbot,
    )
