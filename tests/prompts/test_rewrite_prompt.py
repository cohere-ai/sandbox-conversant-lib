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


@pytest.fixture
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
        f"\n{mock_rewrite_prompt.example_separator}\n"
        f"{mock_rewrite_prompt.headers['conversation']}\n"
        f"{new_example['conversation']}\n"
        f"{mock_rewrite_prompt.headers['fact']}\n"
        f"{new_example['fact']}\n"
        f"{mock_rewrite_prompt.headers['rewrite']}\n"
        f"{new_example['rewrite']}"
    )
    # create from positional arguments
    filled_template = mock_rewrite_prompt.create_example_string(
        new_example["conversation"], new_example["rewrite"], new_example["fact"]
    )
    assert filled_template == expected
    # create from keyword arguments
    filled_template = mock_rewrite_prompt.create_example_string(**new_example)
    assert filled_template == expected


def test_rewrite_prompt_to_string(mock_rewrite_prompt: RewritePrompt) -> None:
    """Tests RewritePrompt.to_string

    Args:
        mock_rewrite_prompt (RewritePrompt): A RewritePrompt fixture.
    """
    expected = (
        f"{mock_rewrite_prompt.preamble}\n\n"
        f"{mock_rewrite_prompt.example_separator}\n"
        f"{mock_rewrite_prompt.headers['conversation']}\n"
        f"{mock_rewrite_prompt.examples[0]['conversation']}\n"
        f"{mock_rewrite_prompt.headers['fact']}\n"
        f"{mock_rewrite_prompt.examples[0]['fact']}\n"
        f"{mock_rewrite_prompt.headers['rewrite']}\n"
        f"{mock_rewrite_prompt.examples[0]['rewrite']}\n"
        f"{mock_rewrite_prompt.example_separator}\n"
        f"{mock_rewrite_prompt.headers['conversation']}\n"
        f"{mock_rewrite_prompt.examples[1]['conversation']}\n"
        f"{mock_rewrite_prompt.headers['fact']}\n"
        f"{mock_rewrite_prompt.examples[1]['fact']}\n"
        f"{mock_rewrite_prompt.headers['rewrite']}\n"
        f"{mock_rewrite_prompt.examples[1]['rewrite']}"
    )
    assert mock_rewrite_prompt.to_string() == expected
