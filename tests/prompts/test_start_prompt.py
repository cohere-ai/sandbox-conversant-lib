# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.

from typing import Any, Dict, List, Tuple

import jsonschema
import pytest

from conversant.prompts.start_prompt import StartPrompt


def test_start_prompt_init() -> None:
    """Tests proper start prompt initialization."""
    prompt = StartPrompt(
        bot_desc="This is an awesome chatbot.",
        example_turns=[
            ("hi", "hello"),
            ("sup?", "nm"),
        ],
    )

    assert len(prompt.bot_desc) > prompt.MIN_DESC_LEN
    assert prompt.bot_desc == "This is an awesome chatbot."
    assert prompt.example_turns == [
        ("hi", "hello"),
        ("sup?", "nm"),
    ]


def test_start_prompt_init_from_dict(mock_start_prompt_config: Dict[str, Any]) -> None:
    _ = StartPrompt.from_dict(mock_start_prompt_config)


def test_empty_fails() -> None:
    """Test that empty start prompts fail."""
    with pytest.raises(TypeError):
        _ = StartPrompt()


def test_short_desc_fails() -> None:
    """Test that short descriptions fail."""
    with pytest.raises(ValueError):
        _ = StartPrompt(
            bot_desc="abcdefg",
            example_turns=[],
        )


@pytest.mark.parametrize(
    "turns",
    [
        ([("User: Hi",), ("Bot: Hi",)],),
        ([("Hi", "bye", "hello")],),
        ([("Hi", "bye"), ("hello",)],),
        (["hi", "hey"],),
    ],
)
def test_bad_turn_formatting_fails(turns: List[Tuple[str, str]]) -> None:
    """Test that non 2-person & non-tuple dialogue fails."""
    with pytest.raises(ValueError):
        _ = StartPrompt(
            bot_desc="This is a long description of a bot.",
            example_turns=[turns],
        )


def test_bad_start_prompt_config_schema_fails(
    mock_start_prompt_config: Dict[str, Any]
) -> None:
    """Test that wrong types or keys in a prompt config raises validation errors."""
    # Test for wrong types in the prompt config.
    with pytest.raises(jsonschema.exceptions.ValidationError):
        config = mock_start_prompt_config.copy()
        config["bot_desc"] = 123
        _ = StartPrompt.from_dict(config)
    with pytest.raises(jsonschema.exceptions.ValidationError):
        config = mock_start_prompt_config.copy()
        config["example_turns"] = {}
        _ = StartPrompt.from_dict(config)
    with pytest.raises(jsonschema.exceptions.ValidationError):
        config = mock_start_prompt_config.copy()
        config["example_turns"][0] = []
        _ = StartPrompt.from_dict(config)
    with pytest.raises(jsonschema.exceptions.ValidationError):
        config = mock_start_prompt_config.copy()
        config["example_turns"][0] = {"user": 123, "bot": 123}
        _ = StartPrompt.from_dict(config)

    # Test for wrong keys in the start prompt config.
    with pytest.raises(KeyError):
        config = mock_start_prompt_config.copy()
        config["example_turns"][0] = {"usr": "", "bt": ""}
        _ = StartPrompt.from_dict(config)
