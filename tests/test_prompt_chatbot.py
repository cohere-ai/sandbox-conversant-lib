# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.

import itertools

import pytest

from conversant.prompt_chatbot import PromptChatbot


def check_prompt_chatbot_config(prompt_chatbot: PromptChatbot) -> None:
    """Checks that required parameters are in the chatbot and client config.

    Args:
        prompt_chatbot (PromptChatbot): The instance of PromptChatbot to check.
    """
    __tracebackhide__ = True
    for key in [
        "model",
        "max_tokens",
        "temperature",
        "frequency_penalty",
        "presence_penalty",
        "stop_sequences",
    ]:
        if key not in prompt_chatbot.client_config:
            pytest.fail(
                f"{key} not in config of {prompt_chatbot.__class__.__name__} "
                "but is required for co.generate"
            )

    for key in ["max_context_examples", "avatar"]:
        if key not in prompt_chatbot.chatbot_config:
            pytest.fail(
                f"{key} not in chatbot config of {prompt_chatbot.__class__.__name__} "
                "but is required."
            )


def test_prompt_chatbot_init(mock_prompt_chatbot: PromptChatbot) -> None:
    """Tests end to end that a PromptChatbot is initialized correctly from constructor.

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


@pytest.mark.parametrize(
    "max_context_examples, history_length",
    list(
        itertools.product(list(range(0, 20, 4)), list(range(0, 50, 10))),
    ),
)
def test_prompt_chatbot_get_current_prompt(
    mock_prompt_chatbot: PromptChatbot, max_context_examples: int, history_length: int
) -> None:
    """Tests assembly of prompts and context.

    Prompts should be preserved and context
    should have line-level trimming applied.

    Args:
        prompt_chatbot (PromptChatbot): Bot test fixture
        max_context_examples (int): The maximum number of examples to keep as context.
        history_length (int): The length of the chat history.
    """
    chat_history = [
        {"user": f"Hello! {i}", "bot": f"Hello back! {i}"}
        for i in range(1, history_length + 1)
    ]
    mock_prompt_chatbot.chat_history = chat_history
    mock_prompt_chatbot.configure_chatbot(
        {
            "max_context_examples": max_context_examples,
        }
    )

    current_prompt = mock_prompt_chatbot.get_current_prompt(query="Hello!")
    expected = (
        # chat prompt
        f"{mock_prompt_chatbot.prompt.preamble}\n"
        + f"{mock_prompt_chatbot.prompt.example_separator}"
        + f"{mock_prompt_chatbot.prompt.headers['user']}: {mock_prompt_chatbot.prompt.examples[0][0]['user']}\n"  # noqa
        + f"{mock_prompt_chatbot.prompt.headers['bot']}: {mock_prompt_chatbot.prompt.examples[0][0]['bot']}\n"  # noqa
        + f"{mock_prompt_chatbot.prompt.headers['user']}: {mock_prompt_chatbot.prompt.examples[0][1]['user']}\n"  # noqa
        + f"{mock_prompt_chatbot.prompt.headers['bot']}: {mock_prompt_chatbot.prompt.examples[0][1]['bot']}\n"  # noqa
        + f"{mock_prompt_chatbot.prompt.example_separator}"
        + f"{mock_prompt_chatbot.prompt.headers['user']}: {mock_prompt_chatbot.prompt.examples[1][0]['user']}\n"  # noqa
        + f"{mock_prompt_chatbot.prompt.headers['bot']}: {mock_prompt_chatbot.prompt.examples[1][0]['bot']}\n"  # noqa
        + f"{mock_prompt_chatbot.prompt.headers['user']}: {mock_prompt_chatbot.prompt.examples[1][1]['user']}\n"  # noqa
        + f"{mock_prompt_chatbot.prompt.headers['bot']}: {mock_prompt_chatbot.prompt.examples[1][1]['bot']}\n"  # noqa
        # context prompt
        + f"{mock_prompt_chatbot.prompt.example_separator}"
        + "".join(
            [
                (
                    f"{mock_prompt_chatbot.prompt.headers['user']}: Hello! {i}\n"
                    f"{mock_prompt_chatbot.prompt.headers['bot']}: Hello back! {i}\n"
                )
                for i in (
                    list(range(1, history_length + 1))[-max_context_examples:]
                    if max_context_examples > 0
                    else []
                )
            ]
        )
        # query prompt
        + (
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


def test_update_max_context_fails(
    mock_prompt_chatbot: PromptChatbot, mock_co: object
) -> None:
    """Tests failure on updating max_context_examples

    when prompt_size has more than 2048 tokens, even changing max_context_size

    Args:
        mock_prompt_chatbot (PromptChatbot): Bot test fixture
        mock_co (object): mock Cohere client.

    """
    with pytest.raises(ValueError):

        chat_history = [{"user": "a " * 100, "bot": "b " * 100} for _ in range(5)]
        mock_prompt_chatbot.chat_history = chat_history
        mock_prompt_chatbot.prompt_size_history = [
            mock_co.tokenize(
                mock_prompt_chatbot.prompt.create_interaction_string(interaction)
            ).length
            for interaction in chat_history
        ]

        max_context_examples = 10
        current_prompt = mock_prompt_chatbot.get_current_prompt(query="a " * 2048)
        prompt_size = mock_co.tokenize(current_prompt).length
        mock_prompt_chatbot._update_max_context_examples(
            prompt_size, max_context_examples
        )


def test_update_max_context_warn(
    mock_prompt_chatbot: PromptChatbot, mock_co: object
) -> None:
    """Tests function update_max_context_examples with warnings

    prompt_size with more than 2048 tokens, but if change the max_context_examples
    the size reduces and gets smaller than 2048

    Args:
        mock_prompt_chatbot (PromptChatbot): Bot test fixture
        mock_co (object): mock Cohere client.

    """
    with pytest.warns(UserWarning):
        chat_history = [{"user": "a " * 90, "bot": "b " * 90} for _ in range(12)]
        mock_prompt_chatbot.chat_history = chat_history
        mock_prompt_chatbot.prompt_size_history = [
            mock_co.tokenize(
                mock_prompt_chatbot.prompt.create_interaction_string(interaction)
            ).length
            for interaction in chat_history
        ]

        max_context_examples = 10
        current_prompt = mock_prompt_chatbot.get_current_prompt(query="q " * 200)
        prompt_size = mock_co.tokenize(current_prompt).length
        updated_max_context_examples = mock_prompt_chatbot._update_max_context_examples(
            prompt_size, max_context_examples
        )

        expected = max_context_examples - 1
        assert updated_max_context_examples == expected
