# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.

from typing import Any, Dict

import pytest

from conversant.chatbot import Interaction
from conversant.prompts.chat_prompt import ChatPrompt


@pytest.fixture
def new_interaction() -> Interaction:
    """Instantiates a fixture for a new ChatPrompt example.

    Returns:
        Interaction: New ChatPrompt interaction fixture.
    """
    return {"user": "Nice to meet you!", "bot": "You too!"}


def test_chat_prompt_init(mock_chat_prompt_config: Dict[str, Any]) -> None:
    """Tests ChatPrompt.__init__

    Args:
        mock_chat_prompt_config (Dict[str, Any]): A ChatPrompt config fixture.
    """
    chat_prompt = ChatPrompt(**mock_chat_prompt_config)
    assert chat_prompt.user_name == "User"
    assert chat_prompt.bot_name == "Mock Chatbot"


def test_chat_prompt_init_from_dict(mock_chat_prompt_config: Dict[str, Any]) -> None:
    """Tests ChatPrompt.from_dict

    Args:
        mock_chat_prompt_config (Dict[str, Any]): A ChatPrompt config fixture.
    """
    chat_prompt = ChatPrompt.from_dict(mock_chat_prompt_config)
    assert chat_prompt.user_name == "User"
    assert chat_prompt.bot_name == "Mock Chatbot"


@pytest.mark.parametrize(
    "config",
    [
        # short preamble
        {"preamble": "short"},
        # headers do not contain user
        {"headers": {"bot": "Mock Chatbot"}},
        # headers do not contain bot
        {"headers": {"user": "User"}},
        # examples have no speakers
        {"examples": [{}]},
        # examples have one speaker
        {"examples": [[{"user": "user utterance"}, {"bot": "bot utterance"}]]},
        # examples have wrong key
        {"examples": [[{"user": "user utterance", "": "bot utterance"}]]},
        # examples have three speakers
        {
            "examples": [
                [
                    {
                        "user": "user utterance",
                        "bot": "bot utterance",
                        "user2": "user2 utterance",
                    }
                ]
            ]
        },
        # examples are prefixed by user and bot names
        {
            "headers": {"user": "Alice", "bot": "Bob"},
            "examples": [[{"user": "Alice: Hey", "bot": "Bob: Hi"}]],
        },
    ],
    ids=[
        "short-preamble",
        "headers-no-user",
        "headers-no-bot",
        "examples-no-speakers",
        "examples-one-speaker",
        "examples-wrong-key",
        "examples-three-speakers",
        "examples-prefixed-with-name",
    ],
)
def test_chat_prompt_init_fails(
    mock_chat_prompt_config: Dict[str, Any], config
) -> None:
    """Tests ChatPrompt.__init__ on bad parameters.

    Args:
        mock_chat_prompt_config (Dict[str, Any]): A ChatPrompt config fixture.
        config (Dict[str, Any]): Dictionary of bad parameters.
    """
    mock_chat_prompt_config.update(config)
    with pytest.raises(ValueError):
        _ = ChatPrompt(**mock_chat_prompt_config)


def test_chat_prompt_create_interaction_string(
    mock_chat_prompt: ChatPrompt, new_interaction: Interaction
) -> None:
    """Tests ChatPrompt.create_interaction_string

    Args:
        mock_chat_prompt (ChatPrompt): A ChatPrompt fixture.
        new_interaction (Interaction): A new ChatPrompt interaction fixture.
    """
    expected = (
        f"{mock_chat_prompt.headers['user']}: {new_interaction['user']}\n"
        f"{mock_chat_prompt.headers['bot']}: {new_interaction['bot']}\n"
    )
    # create from positional arguments
    generated_interaction_str = mock_chat_prompt.create_interaction_string(
        new_interaction["user"], new_interaction["bot"]
    )
    assert generated_interaction_str == expected

    # create from keyword arguments
    generated_interaction_str = mock_chat_prompt.create_interaction_string(
        **new_interaction
    )
    assert generated_interaction_str == expected

    # generated example string is dependent on the insertion order into the examples
    # dictionary
    reordered_interaction = {}
    reordered_interaction["bot"] = new_interaction["bot"]
    reordered_interaction["user"] = new_interaction["user"]
    reordered_expected = (
        f"{mock_chat_prompt.headers['bot']}: {new_interaction['bot']}\n"
        f"{mock_chat_prompt.headers['user']}: {new_interaction['user']}\n"
    )
    generated_reordered_interaction_str = mock_chat_prompt.create_interaction_string(
        **reordered_interaction
    )
    assert generated_reordered_interaction_str == reordered_expected


def test_chat_prompt_to_string(mock_chat_prompt: ChatPrompt) -> None:
    """Tests ChatPrompt.to_string

    Args:
        mock_chat_prompt (ChatPrompt): A ChatPrompt fixture.
    """
    expected = (
        f"{mock_chat_prompt.preamble}\n"
        f"{mock_chat_prompt.example_separator}"
        f"{mock_chat_prompt.headers['user']}: {mock_chat_prompt.examples[0][0]['user']}\n"  # noqa
        f"{mock_chat_prompt.headers['bot']}: {mock_chat_prompt.examples[0][0]['bot']}\n"  # noqa
        f"{mock_chat_prompt.headers['user']}: {mock_chat_prompt.examples[0][1]['user']}\n"  # noqa
        f"{mock_chat_prompt.headers['bot']}: {mock_chat_prompt.examples[0][1]['bot']}\n"  # noqa
        f"{mock_chat_prompt.example_separator}"
        f"{mock_chat_prompt.headers['user']}: {mock_chat_prompt.examples[1][0]['user']}\n"  # noqa
        f"{mock_chat_prompt.headers['bot']}: {mock_chat_prompt.examples[1][0]['bot']}\n"  # noqa
        f"{mock_chat_prompt.headers['user']}: {mock_chat_prompt.examples[1][1]['user']}\n"  # noqa
        f"{mock_chat_prompt.headers['bot']}: {mock_chat_prompt.examples[1][1]['bot']}"
    )
    assert mock_chat_prompt.to_string() == expected
