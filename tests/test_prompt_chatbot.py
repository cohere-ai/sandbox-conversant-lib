# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.


import pytest

from conversant.prompt_chatbot import PromptChatbot
from conversant.prompts.start_prompt import StartPrompt


def check_prompt_chatbot_config(prompt_chatbot: PromptChatbot):
    __tracebackhide__ = True
    for key in ["model", "max_tokens", "temperature", "stop_seq"]:
        if key not in prompt_chatbot.client_config:
            pytest.fail(
                f"{key} not in config of {prompt_chatbot.__class__.__name__} but is required for co.generate"
            )


def test_prompt_chatbot_init(mock_prompt_chatbot: PromptChatbot) -> None:
    """Tests end to end that a prompt_chatbot is initialized correctly from class constructor.

    Args:
        mock_prompt_chatbot (PromptChatbot): Bot test fixture
    """
    check_prompt_chatbot_config(mock_prompt_chatbot)
    assert mock_prompt_chatbot.user_name == mock_prompt_chatbot.prompt.user_name
    assert mock_prompt_chatbot.bot_name == mock_prompt_chatbot.prompt.bot_name
    mock_prompt_chatbot.reply(query="What's up?")


def test_prompt_chatbot_init_from_persona(mock_co: object) -> None:
    """Tests end to end that a prompt_chatbot is initalized correctly from persona.

    Args:
        mock_co (object): mock Cohere client.
    """
    prompt_chatbot = PromptChatbot.from_persona("watch-sales-agent", client=mock_co)
    assert isinstance(prompt_chatbot, PromptChatbot)
    assert prompt_chatbot.user_name == prompt_chatbot.prompt.user_name
    assert prompt_chatbot.bot_name == prompt_chatbot.prompt.bot_name
    assert prompt_chatbot.latest_prompt == prompt_chatbot.prompt.to_string()
    check_prompt_chatbot_config(prompt_chatbot)
    prompt_chatbot.reply(query="What's up?")

    with pytest.raises(FileNotFoundError):
        _ = PromptChatbot.from_persona(
            "watch-sales-agent", client=mock_co, persona_dir=""
        )


def test_prompt_chatbot_get_current_prompt(mock_prompt_chatbot: PromptChatbot) -> None:
    """Tests assembly of starter prompts and context.

    Starter prompts should be preserved and context
    should have line-level trimming applied.

    Args:
        prompt_chatbot (PromptChatbot): Bot test fixture
    """

    max_context_examples = mock_prompt_chatbot.chatbot_config["max_context_examples"]
    chat_history = [{"user": "Greetings!", "bot": "I greet you"}] * (
        max_context_examples
    ) + [{"user": "Hello!", "bot": "Hello back"}] * (max_context_examples)
    mock_prompt_chatbot.chat_history = chat_history

    current_prompt = mock_prompt_chatbot.get_current_prompt(query="Hello!")

    expected = (
        # start prompt
        f"{mock_prompt_chatbot.prompt.preamble}\n"
        + f"{mock_prompt_chatbot.prompt.example_separator}"
        + f"{mock_prompt_chatbot.prompt.headers['user']}: {mock_prompt_chatbot.prompt.examples[0]['user']}\n"
        + f"{mock_prompt_chatbot.prompt.headers['bot']}: {mock_prompt_chatbot.prompt.examples[0]['bot']}\n"
        + f"{mock_prompt_chatbot.prompt.example_separator}"
        + f"{mock_prompt_chatbot.prompt.headers['user']}: {mock_prompt_chatbot.prompt.examples[1]['user']}\n"
        + f"{mock_prompt_chatbot.prompt.headers['bot']}: {mock_prompt_chatbot.prompt.examples[1]['bot']}\n"
        # context prompt
        + (
            f"{mock_prompt_chatbot.prompt.example_separator}"
            f"{mock_prompt_chatbot.prompt.headers['user']}: Hello!\n"
            f"{mock_prompt_chatbot.prompt.headers['bot']}: Hello back\n"
        )
        * max_context_examples
        # query prompt
        + (
            f"{mock_prompt_chatbot.prompt.example_separator}"
            f"{mock_prompt_chatbot.prompt.headers['user']}: Hello!\n"
            f"{mock_prompt_chatbot.prompt.headers['bot']}:"
        )
    )
    assert current_prompt == expected


def test_missing_persona_fails(mock_co: object) -> None:
    """Tests failure on missing persona.
    Args:
        mock_co (object): mock Cohere client
    """
    with pytest.raises(FileNotFoundError):
        _ = PromptChatbot.from_persona("invalid_persona", mock_co)
