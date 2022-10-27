# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.

from typing import Any, Dict

import pytest

from conversant.prompts.rewrite_prompt import RewritePrompt


@pytest.fixture
def new_example() -> Dict[str, str]:
    """Instantiates a fixture for a new RewritePrompt example.

    Returns:
        Dict[str, str]: New RewritePrompt example fixture.
    """
    return {
        "conversation": "Otters are plants.",
        "fact": "Otters are mammals.",
        "rewrite": "Otters are mammals.",
    }


def test_rewrite_prompt_init(mock_rewrite_prompt_config: Dict[str, Any]) -> None:
    """Tests RewritePrompt.__init__

    Args:
        mock_rewrite_prompt_config (Dict[str, Any]): A RewritePrompt config fixture.
    """
    _ = RewritePrompt(**mock_rewrite_prompt_config)


def test_rewrite_prompt_init_from_dict(
    mock_rewrite_prompt_config: Dict[str, Any]
) -> None:
    """Tests RewritePrompt.from_dict

    Args:
        mock_rewrite_prompt_config (Dict[str, Any]): A RewritePrompt config fixture.
    """
    _ = RewritePrompt.from_dict(mock_rewrite_prompt_config)


@pytest.mark.parametrize(
    "config",
    [
        # short preamble
        {"preamble": "short"},
        # no examples
        {"examples": []},
    ],
    ids=[
        "short-preamble",
        "no-examples",
    ],
)
def test_rewrite_prompt_init_fails(
    mock_rewrite_prompt_config: Dict[str, Any], config
) -> None:
    """Tests RewritePrompt.__init__ on bad parameters.

    Args:
        mock_rewrite_prompt_config (Dict[str, Any]): A RewritePrompt config fixture.
        config (Dict[str, Any]): Dictionary of bad parameters.
    """
    mock_rewrite_prompt_config.update(config)
    with pytest.raises(ValueError):
        _ = RewritePrompt(**mock_rewrite_prompt_config)


def test_rewrite_prompt_create_example_string(
    mock_rewrite_prompt: RewritePrompt, new_example: Dict[str, str]
) -> None:
    """Tests RewritePrompt.create_example_string

    Args:
        mock_rewrite_prompt (RewritePrompt): A RewritePrompt fixture.
        new_example (Dict[ str, str]): A new RewritePrompt example fixture.
    """
    expected = (
        f"{mock_rewrite_prompt.example_separator}"
        f"{mock_rewrite_prompt.headers['conversation']}\n"
        f"{new_example['conversation']}\n"
        f"{mock_rewrite_prompt.headers['fact']}\n"
        f"{new_example['fact']}\n"
        f"{mock_rewrite_prompt.headers['rewrite']}\n"
        f"{new_example['rewrite']}\n"
    )
    # create from positional arguments
    generated_example_str = mock_rewrite_prompt.create_example_string(
        new_example["conversation"], new_example["rewrite"], new_example["fact"]
    )
    assert generated_example_str == expected

    # create from keyword arguments
    generated_example_str = mock_rewrite_prompt.create_example_string(**new_example)
    assert generated_example_str == expected

    # create from mix of positional and keyword arguments
    kwargs = {"rewrite": "Otters are mammals."}
    generated_example_str = mock_rewrite_prompt.create_example_string(
        new_example["conversation"], new_example["fact"], **kwargs
    )
    assert generated_example_str == expected

    # generated example string is dependent on the insertion order into the examples
    # dictionary
    reordered_example = {}
    reordered_example["fact"] = new_example["fact"]
    reordered_example["conversation"] = new_example["conversation"]
    reordered_example["rewrite"] = new_example["rewrite"]
    reordered_expected = (
        f"{mock_rewrite_prompt.example_separator}"
        f"{mock_rewrite_prompt.headers['fact']}\n"
        f"{new_example['fact']}\n"
        f"{mock_rewrite_prompt.headers['conversation']}\n"
        f"{new_example['conversation']}\n"
        f"{mock_rewrite_prompt.headers['rewrite']}\n"
        f"{new_example['rewrite']}\n"
    )
    generated_reordered_example_str = mock_rewrite_prompt.create_example_string(
        **reordered_example
    )
    assert generated_reordered_example_str == reordered_expected


def test_rewrite_prompt_to_string(mock_rewrite_prompt: RewritePrompt) -> None:
    """Tests RewritePrompt.to_string

    Args:
        mock_rewrite_prompt (RewritePrompt): A RewritePrompt fixture.
    """
    expected = (
        f"{mock_rewrite_prompt.preamble}\n"
        f"{mock_rewrite_prompt.example_separator}"
        f"{mock_rewrite_prompt.headers['conversation']}\n"
        f"{mock_rewrite_prompt.examples[0]['conversation']}\n"
        f"{mock_rewrite_prompt.headers['fact']}\n"
        f"{mock_rewrite_prompt.examples[0]['fact']}\n"
        f"{mock_rewrite_prompt.headers['rewrite']}\n"
        f"{mock_rewrite_prompt.examples[0]['rewrite']}\n"
        f"{mock_rewrite_prompt.example_separator}"
        f"{mock_rewrite_prompt.headers['conversation']}\n"
        f"{mock_rewrite_prompt.examples[1]['conversation']}\n"
        f"{mock_rewrite_prompt.headers['fact']}\n"
        f"{mock_rewrite_prompt.examples[1]['fact']}\n"
        f"{mock_rewrite_prompt.headers['rewrite']}\n"
        f"{mock_rewrite_prompt.examples[1]['rewrite']}"
    )
    assert mock_rewrite_prompt.to_string() == expected
