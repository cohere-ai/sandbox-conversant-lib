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
                f"{key} not in config of {prompt_chatbot.__class__.__name__} \
                    but is required for co.generate"
            )


def test_prompt_chatbot_init(mock_prompt_chatbot: PromptChatbot) -> None:
    """Tests end to end that a prompt_chatbot is initialized
    correctly from class constructor.

    Args:
        mock_prompt_chatbot (PromptChatbot): Bot test fixture
    """
    check_prompt_chatbot_config(mock_prompt_chatbot)
    mock_prompt_chatbot.reply(query="What's up?")


def test_prompt_chatbot_init_from_persona(mock_co: object) -> None:
    """Tests end to end that a prompt_chatbot is initalized correctly from persona.

    Args:
        mock_co (object): mock Cohere client.
    """
    prompt_chatbot = PromptChatbot.from_persona("watch-sales-agent", client=mock_co)
    assert isinstance(prompt_chatbot, PromptChatbot)
    check_prompt_chatbot_config(prompt_chatbot)
    prompt_chatbot.reply(query="What's up?")


def test_too_short_desc_fails(mock_co: object) -> None:
    """Tests that short descriptions raise an error.

    Args:
        mock_co (object): mock Cohere client.
    """
    with pytest.raises(ValueError):
        _ = PromptChatbot(
            client=mock_co,
            start_prompt=StartPrompt(
                bot_desc="abc",
                example_turns=[],
            ),
        )


def test_prefixed_turns_fails(mock_co: object) -> None:
    """Tests failure on prefixed dialogue turns.

    Args:
        mock_co (object): mock Cohere client.
    """

    user_name = "Alice"
    bot_name = "Bob"

    with pytest.raises(ValueError):
        _ = PromptChatbot(
            client=mock_co,
            start_prompt=StartPrompt(
                bot_desc="This is a long description.",
                example_turns=[
                    (f"{user_name}: Hey", f"{bot_name}: Hi"),
                ],
            ),
            user_name=user_name,
            bot_name=bot_name,
        )


def test_prompt_assembly(mock_prompt_chatbot: PromptChatbot) -> None:
    """Tests assembly of starter prompts and context.

    Starter prompts should be preserved and context
    should have line-level trimming applied.

    Args:
        prompt_chatbot (PromptChatbot): Bot test fixture
    """

    max_lines = mock_prompt_chatbot.chatbot_config["max_context_lines"]
    new_lines = ["User: Greetings!"] * (max_lines) + ["User: Hello!"] * (max_lines)

    prompt = mock_prompt_chatbot._assemble_prompt(
        new_lines=new_lines,
    )

    assert prompt == (
        f"Below is a series of chats between {mock_prompt_chatbot.bot_name} "
        + f"and {mock_prompt_chatbot.user_name}."
        + f"{mock_prompt_chatbot.bot_name} responds to {mock_prompt_chatbot.user_name} "
        + "based on the <<DESCRIPTION>>.\n"
        + "<<DESCRIPTION>>\n"
        + mock_prompt_chatbot.start_prompt.bot_desc
        + "\n<<CONVERSATION>>\n"
        + "User: hi\n"
        + "Bot: hello\n"
        + "<<CONVERSATION>>"
        + f"\n{mock_prompt_chatbot.user_name}: Hello!" * max_lines
        + f"\n{mock_prompt_chatbot.bot_name}:"
    )


def test_missing_persona_fails(mock_co: object) -> None:
    """Tests failure on missing persona.
    Args:
        mock_co (object): mock Cohere client
    """
    with pytest.raises(FileNotFoundError):
        _ = PromptChatbot.from_persona("invalid_persona", mock_co)
