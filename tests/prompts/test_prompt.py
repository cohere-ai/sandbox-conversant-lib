# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.

from typing import Any, Dict

import pytest

from conversant.prompts.prompt import Prompt


@pytest.fixture
def new_example() -> Dict[str, str]:
    """Instantiates a fixture for a new Prompt example.

    Returns:
        Dict[str, str]: New Prompt example fixture.
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
    assert prompt.fields == ["query", "context", "generation"]
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
    assert prompt.stop_sequences == ["query", "context", "generation"]


def test_prompt_from_dict(mock_prompt_config: Dict[str, Any]) -> None:
    """Tests Prompt.from_dict

    Args:
        mock_prompt_config (Dict[str, Any]): A Prompt config fixture.
    """
    prompt = Prompt.from_dict(mock_prompt_config)
    assert prompt.preamble == "This is a prompt."
    assert prompt.example_separator == "<example>\n"
    assert prompt.fields == ["query", "context", "generation"]
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
    assert prompt.stop_sequences == ["query", "context", "generation"]


@pytest.mark.parametrize(
    "config",
    [
        # no preamble
        {"preamble": ""},
        # example separator is not str
        {
            "example_separator": 123,
        },
        # headers missing fields
        {
            "fields": ["query", "context", "generation", "new-field"],
        },
        # example missing header
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
        "validation-headers-missing-field",
        "validation-example-missing-header",
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


def test_prompt_create_example(
    mock_prompt: Prompt, new_example: Dict[str, str]
) -> None:
    """Tests Prompt.create_example

    Args:
        mock_prompt (Prompt): A Prompt fixture.
        new_example (Dict[ str, str]): A new Prompt example fixture.
    """
    # create from positional arguments only
    generated_example = mock_prompt.create_example(
        new_example["query"], new_example["context"], new_example["generation"]
    )
    assert generated_example == new_example

    # create from keyword arguments only
    generated_example = mock_prompt.create_example(**new_example)
    assert generated_example == new_example

    # create from mix of positional and keyword arguments
    kwargs = {"generation": "A new generation!"}
    generated_example = mock_prompt.create_example(
        new_example["query"], new_example["context"], **kwargs
    )
    assert generated_example == new_example


def test_prompt_create_example_string(
    mock_prompt: Prompt, new_example: Dict[str, str]
) -> None:
    """Tests Prompt.create_example_string

    Args:
        mock_prompt (Prompt): A Prompt fixture.
        new_example (Dict[ str, str]): A new Prompt example fixture.
    """
    expected = (
        f"{mock_prompt.example_separator}"
        f"{mock_prompt.headers['query']}{new_example['query']}\n"
        f"{mock_prompt.headers['context']}{new_example['context']}\n"
        f"{mock_prompt.headers['generation']}{new_example['generation']}\n"
    )
    # create from positional arguments
    generated_example_str = mock_prompt.create_example_string(
        new_example["query"], new_example["context"], new_example["generation"]
    )
    assert generated_example_str == expected

    # create from keyword arguments
    generated_example_str = mock_prompt.create_example_string(**new_example)
    assert generated_example_str == expected

    # create from mix of positional and keyword arguments
    kwargs = {"generation": "A new generation!"}
    generated_example_str = mock_prompt.create_example_string(
        new_example["query"], new_example["context"], **kwargs
    )
    assert generated_example_str == expected


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
