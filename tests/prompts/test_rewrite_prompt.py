# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.

from typing import Any, Dict

import jsonschema
import pytest

from conversant.prompts.rewrite_prompt import RewritePrompt


def test_rewrite_prompt_init() -> None:
    """Tests proper start prompt initialization."""
    prompt = RewritePrompt(
        example_separator="--",
        fact_header="<<FACTUAL_PARAGRAPH>>",
        conversation_header="<<CONVERSATION>>",
        rewrite_header="<<PLEASE REWRITE THIS>>",
        preamble="test preamble",
        examples=[
            {
                "fact": "this is a fact",
                "conversation": "this is a wrong message",
                "rewrite": "this is a message based on fact",
            }
        ],
    )

    assert len(prompt.examples) >= prompt.MIN_NUM_EXAMPLES
    assert prompt.preamble == "test preamble"
    assert prompt.examples == [
        {
            "fact": "this is a fact",
            "conversation": "this is a wrong message",
            "rewrite": "this is a message based on fact",
        }
    ]


def test_rewrite_prompt_init_from_dict(
    mock_rewrite_prompt_config: Dict[str, Any]
) -> None:
    _ = RewritePrompt.from_dict(mock_rewrite_prompt_config)


def test_empty_fails() -> None:
    """Test that empty rewrite prompts fail."""
    with pytest.raises(TypeError):
        _ = RewritePrompt()


def test_no_example_fails() -> None:
    """Test that fails when no example is given."""
    with pytest.raises(ValueError):
        _ = RewritePrompt(
            example_separator="--",
            fact_header="<<FACTUAL_PARAGRAPH>>",
            conversation_header="<<CONVERSATION>>",
            rewrite_header="<<PLEASE REWRITE THIS>>",
            preamble="test preamble",
            examples=[],
        )


def test_bad_rewrite_prompt_config_schema_fails(
    mock_rewrite_prompt_config: Dict[str, Any]
) -> None:
    """Test that wrong types or keys in a prompt config raises validation errors."""
    # Test for wrong types in the prompt config.
    with pytest.raises(jsonschema.exceptions.ValidationError):
        config = mock_rewrite_prompt_config.copy()
        config["preamble"] = 123
        _ = RewritePrompt.from_dict(config)
    with pytest.raises(jsonschema.exceptions.ValidationError):
        config = mock_rewrite_prompt_config.copy()
        config["examples"] = {}
        _ = RewritePrompt.from_dict(config)
    with pytest.raises(jsonschema.exceptions.ValidationError):
        config = mock_rewrite_prompt_config.copy()
        config["examples"][0] = []
        _ = RewritePrompt.from_dict(config)
    with pytest.raises(jsonschema.exceptions.ValidationError):
        config = mock_rewrite_prompt_config.copy()
        config["examples"][0] = {"fact": 123, "conversation": 123, "rewrite": 123}
        _ = RewritePrompt.from_dict(config)
