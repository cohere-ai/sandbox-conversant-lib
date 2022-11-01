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
from conversant.prompts.prompt import Prompt


@pytest.fixture
def new_interaction() -> Interaction:
    """Instantiates a fixture for a new Prompt interaction.

    Returns:
        Interaction: New Prompt interaction fixture.
    """
    return {
        "query": "A new query!",
        "context": "A new context!",
        "generation": "A new generation!",
    }


def test_prompt_init(mock_prompt_config: Dict[str, Any]) -> None:
    """Tests Prompt.__init__

    Args:
        mock_prompt_config (Dict[str, Any]): A Prompt config fixture.
    """
    prompt = Prompt(**mock_prompt_config)
    assert prompt.preamble == "This is a prompt."
    assert prompt.example_separator == "<example>\n"
    assert prompt.headers == {
        "query": "<query>",
        "context": "<context>",
        "generation": "<generation>",
    }
    assert prompt.examples == [
        {
            "query": "This is a query.",
            "context": "This is a context.",
            "generation": "This is a generation.",
        },
        {
            "query": "This is a second query.",
            "context": "This is a second context.",
            "generation": "This is a second generation.",
        },
    ]


def test_prompt_from_dict(mock_prompt_config: Dict[str, Any]) -> None:
    """Tests Prompt.from_dict

    Args:
        mock_prompt_config (Dict[str, Any]): A Prompt config fixture.
    """
    prompt = Prompt.from_dict(mock_prompt_config)
    assert prompt.preamble == "This is a prompt."
    assert prompt.example_separator == "<example>\n"
    assert prompt.headers == {
        "query": "<query>",
        "context": "<context>",
        "generation": "<generation>",
    }
    assert prompt.examples == [
        {
            "query": "This is a query.",
            "context": "This is a context.",
            "generation": "This is a generation.",
        },
        {
            "query": "This is a second query.",
            "context": "This is a second context.",
            "generation": "This is a second generation.",
        },
    ]


@pytest.mark.parametrize(
    "config",
    [
        # no preamble
        {"preamble": ""},
        # example separator is not str
        {
            "example_separator": 123,
        },
        # example missing variable
        {
            "examples": [{"query": "This is a query."}],
        },
        # no examples
        {
            "examples": [],
        },
    ],
    ids=[
        "validation-no-preamble",
        "validation-example-separator-not-str",
        "validation-example-missing-variable",
        "validation-no-examples",
    ],
)
def test_prompt_init_fails(
    mock_prompt_config: Dict[str, Any], config: Dict[str, Any]
) -> None:
    """Tests Prompt.__init__ on bad parameters.

    Args:
        mock_prompt_config (Dict[str, Any]): A Prompt config fixture.
        config (Dict[str, Any]): Dictionary of bad parameters.
    """
    mock_prompt_config.update(config)
    with pytest.raises(ValueError):
        _ = Prompt(**mock_prompt_config)


def test_prompt_create_interaction(
    mock_prompt: Prompt, new_interaction: Interaction
) -> None:
    """Tests Prompt.create_interaction

    Args:
        mock_prompt (Prompt): A Prompt fixture.
        new_interaction (Dict[ str, str]): A new Prompt interaction fixture.
    """
    # create from positional arguments only
    generated_interaction = mock_prompt.create_interaction(
        new_interaction["query"],
        new_interaction["context"],
        new_interaction["generation"],
    )
    assert generated_interaction == new_interaction

    # create from keyword arguments only
    generated_interaction = mock_prompt.create_interaction(**new_interaction)
    assert generated_interaction == new_interaction

    # create from mix of positional and keyword arguments
    kwargs = {"generation": "A new generation!"}
    generated_interaction = mock_prompt.create_interaction(
        new_interaction["query"], new_interaction["context"], **kwargs
    )
    assert generated_interaction == new_interaction


def test_prompt_create_interaction_string(
    mock_prompt: Prompt, new_interaction: Interaction
) -> None:
    """Tests Prompt.create_interaction_string

    Args:
        mock_prompt (Prompt): A Prompt fixture.
        new_interaction (Dict[ str, str]): A new Prompt interaction fixture.
    """
    expected = (
        f"{mock_prompt.headers['query']}{new_interaction['query']}\n"
        f"{mock_prompt.headers['context']}{new_interaction['context']}\n"
        f"{mock_prompt.headers['generation']}{new_interaction['generation']}\n"
    )
    # create from positional arguments
    generated_interaction_str = mock_prompt.create_interaction_string(
        new_interaction["query"],
        new_interaction["context"],
        new_interaction["generation"],
    )
    assert generated_interaction_str == expected

    # create from keyword arguments
    generated_interaction_str = mock_prompt.create_interaction_string(**new_interaction)
    assert generated_interaction_str == expected

    # create from mix of positional and keyword arguments
    kwargs = {"generation": "A new generation!"}
    generated_interaction_str = mock_prompt.create_interaction_string(
        new_interaction["query"], new_interaction["context"], **kwargs
    )
    assert generated_interaction_str == expected

    # generated example string is dependent on the insertion order into the examples
    # dictionary
    reordered_example = {}
    reordered_example["context"] = new_interaction["context"]
    reordered_example["query"] = new_interaction["query"]
    reordered_example["generation"] = new_interaction["generation"]
    reordered_expected = (
        f"{mock_prompt.headers['context']}{new_interaction['context']}\n"
        f"{mock_prompt.headers['query']}{new_interaction['query']}\n"
        f"{mock_prompt.headers['generation']}{new_interaction['generation']}\n"
    )
    generated_reordered_example_str = mock_prompt.create_interaction_string(
        **reordered_example
    )
    assert generated_reordered_example_str == reordered_expected


def test_prompt_to_string(mock_prompt: Prompt) -> None:
    """Tests Prompt.to_string

    Args:
        mock_prompt (Prompt): A Prompt fixture.
    """
    expected = (
        f"{mock_prompt.preamble}\n"
        f"{mock_prompt.example_separator}"
        f"{mock_prompt.headers['query']}{mock_prompt.examples[0]['query']}\n"
        f"{mock_prompt.headers['context']}{mock_prompt.examples[0]['context']}\n"
        f"{mock_prompt.headers['generation']}{mock_prompt.examples[0]['generation']}\n"
        f"{mock_prompt.example_separator}"
        f"{mock_prompt.headers['query']}{mock_prompt.examples[1]['query']}\n"
        f"{mock_prompt.headers['context']}{mock_prompt.examples[1]['context']}\n"
        f"{mock_prompt.headers['generation']}{mock_prompt.examples[1]['generation']}"
    )
    assert mock_prompt.to_string() == expected


@pytest.mark.parametrize(
    "new_config",
    [
        {"example_separator": "--"},
        {"preamble": "This is a new preamble."},
    ],
    ids=["new-example-separator", "new-preamble"],
)
def test_prompt_update(mock_prompt: Prompt, new_config: Dict[str, Any]) -> None:
    """Tests Prompt.update

    Args:
        mock_prompt (Prompt): A Prompt fixture.
        new_config (Dict[str, Any]): Dictionary of new params.
    """
    mock_prompt.update(new_config)
    for key in new_config:
        assert getattr(mock_prompt, key) == new_config[key]
