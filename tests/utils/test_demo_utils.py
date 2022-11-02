# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.
import cohere

from conversant.prompt_chatbot import PromptChatbot
from conversant.utils import demo_utils


def test_encode_decode_chatbot(
    mock_prompt_chatbot: PromptChatbot, mock_co: cohere.Client
) -> None:
    assert isinstance(
        demo_utils.decode_chatbot(
            demo_utils.encode_chatbot(mock_prompt_chatbot), client=mock_co
        ),
        PromptChatbot,
    )
