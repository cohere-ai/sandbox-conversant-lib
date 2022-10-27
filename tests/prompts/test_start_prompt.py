# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.

from typing import Any, Dict

import pytest

from conversant.prompts.start_prompt import StartPrompt


@pytest.fixture
def new_example() -> Dict[str, str]:
    """Instantiates a fixture for a new StartPrompt example.

    Returns:
        Dict[str, str]: New StartPrompt example fixture.
    """
    return {"user": "Nice to meet you!", "bot": ""}


def test_start_prompt_init(mock_start_prompt_config: Dict[str, Any]) -> None:
    """Tests StartPrompt.__init__

    Args:
        mock_start_prompt_config (Dict[str, Any]): A StartPrompt config fixture.
    """
    start_prompt = StartPrompt(**mock_start_prompt_config)
    assert start_prompt.user_name == "User"
    assert start_prompt.bot_name == "Mock Chatbot"
    assert start_prompt.stop_sequences == ["\nUser:", "\nMock Chatbot:"]


def test_start_prompt_init_from_dict(mock_start_prompt_config: Dict[str, Any]) -> None:
    """Tests StartPrompt.from_dict

    Args:
        mock_start_prompt_config (Dict[str, Any]): A StartPrompt config fixture.
    """
    start_prompt = StartPrompt.from_dict(mock_start_prompt_config)
    assert start_prompt.user_name == "User"
    assert start_prompt.bot_name == "Mock Chatbot"
    assert start_prompt.stop_sequences == ["\nUser:", "\nMock Chatbot:"]


@pytest.mark.parametrize(
    "config",
    [
        # short preamble
        {"preamble": "short"},
        # fields missing user
        {"fields": ["bot"]},
        # fields missing bot
        {"fields": ["user"]},
        # headers do not contain user
        {"headers": {"bot": "Mock Chatbot"}},
        # headers do not contain bot
        {"headers": {"user": "User"}},
        # examples have no speakers
        {"examples": [{}]},
        # examples have one speaker
        {"examples": [{"user": "user utterance"}, {"bot": "bot utterance"}]},
        # examples have wrong field
        {"examples": [{"user": "user utterance", "": "bot utterance"}]},
        # examples have three speakers
        {
            "examples": [
                {
                    "user": "user utterance",
                    "bot": "bot utterance",
                    "user2": "user2 utterance",
                }
            ]
        },
        # examples are prefixed by user and bot names
        {
            "headers": {"user": "Alice", "bot": "Bob"},
            "examples": [{"user": "Alice: Hey", "bot": "Bob: Hi"}],
        },
    ],
    ids=[
        "short-preamble",
        "fields-no-user",
        "fields-no-bot",
        "headers-no-user",
        "headers-no-bot",
        "examples-no-speakers",
        "examples-one-speaker",
        "examples-wrong-field",
        "examples-three-speakers",
        "examples-prefixed-with-name",
    ],
)
def test_start_prompt_init_fails(
    mock_start_prompt_config: Dict[str, Any], config
) -> None:
    """Tests StartPrompt.__init__ on bad parameters.

    Args:
        mock_start_prompt_config (Dict[str, Any]): A StartPrompt config fixture.
        config (Dict[str, Any]): Dictionary of bad parameters.
    """
    mock_start_prompt_config.update(config)
    with pytest.raises(ValueError):
        _ = StartPrompt(**mock_start_prompt_config)


def test_start_prompt_create_example_string(
    mock_start_prompt: StartPrompt, new_example: Dict[str, str]
) -> None:
    """Tests StartPrompt.create_example_string

    Args:
        mock_start_prompt (StartPrompt): A StartPrompt fixture.
        new_example (Dict[ str, str]): A new StartPrompt example fixture.
    """
    expected = (
        f"{mock_start_prompt.example_separator}"
        f"{mock_start_prompt.headers['user']}: {new_example['user']}\n"
        f"{mock_start_prompt.headers['bot']}: \n"
    )
    # create from positional arguments
    generated_example_str = mock_start_prompt.create_example_string(
        new_example["user"], new_example["bot"]
    )
    assert generated_example_str == expected

    # create from keyword arguments
    generated_example_str = mock_start_prompt.create_example_string(**new_example)
    assert generated_example_str == expected


def test_start_prompt_to_string(mock_start_prompt: StartPrompt) -> None:
    """Tests StartPrompt.to_string

    Args:
        mock_start_prompt (StartPrompt): A StartPrompt fixture.
    """
    expected = (
        f"{mock_start_prompt.preamble}\n"
        f"{mock_start_prompt.example_separator}"
        f"{mock_start_prompt.headers['user']}: {mock_start_prompt.examples[0]['user']}\n"
        f"{mock_start_prompt.headers['bot']}: {mock_start_prompt.examples[0]['bot']}\n"
        f"{mock_start_prompt.example_separator}"
        f"{mock_start_prompt.headers['user']}: {mock_start_prompt.examples[1]['user']}\n"
        f"{mock_start_prompt.headers['bot']}: {mock_start_prompt.examples[1]['bot']}"
    )
    assert mock_start_prompt.to_string() == expected
