# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.


import json
import os
import re
from typing import List

import emoji
import streamlit as st
from emojificate.filter import emojificate

from conversant.prompt_chatbot import PERSONA_MODEL_DIRECTORY, PromptChatbot
from conversant.prompts.chat_prompt import ChatPrompt


class ParrotChatbot(PromptChatbot):
    """Mock chat function; real use-cases should import
    this functionality via a class that inherits from conversant.chatbot.Chatbot

    This bot simply states the user's query.
    """

    def __init__(self):
        super().__init__(
            client=None,
            prompt=ChatPrompt(
                preamble=(
                    "The Parrot Bot repeats back whatever is said to it "
                    "without using Cohere's large language models."
                ),
                fields=["user", "bot"],
                headers={
                    "user": "User",
                    "bot": "Parrot Bot",
                },
                example_separator="",
                examples=[],
            ),
        )

    def reply(self, query: str) -> str:
        """Replies to a user by stating their query.

        Args:
            query (str): A user's text chat query

        Returns:
            str: a mock reply that repeats the user's query.
        """
        current_prompt = self.get_current_prompt(query)
        self.chat_history.append(self.prompt.create_interaction(query, query))
        self.prompt_history.append(current_prompt)
        return query


@st.cache
def get_twemoji_url_from_shortcode(shortcode: str) -> str:

    """Converts an emoji shortcode to its corresponding Twemoji URL.

    Args:
        shortcode (str): Emoji shortcode.

    Returns:
        str: The string that is the Twemoji URL corresponding to the emoji.
    """
    # Emojize returns the unicode representation of that emoji from its shortcode.
    unicode = emoji.emojize(shortcode, language="alias")
    # Emojificate returns html <img /> tag.
    img_html_tag = emojificate(unicode)
    # Find the URL from the html tag.
    url = re.findall('src="(.*?)"', img_html_tag, re.DOTALL)[0]
    return url


@st.cache(allow_output_mutation=True)
def get_persona_options() -> List[str]:
    """Initializes a list of personas.

    Each persona is a directory in PERSONA_MODEL_DIRECTORY, each with its
    config.json file. The mock parrot persona is also included for testing
    purposes.

    Returns:
        List[str]: A list of persona names.
    """
    # Initialize the list of personas for Streamlit
    persona_names = os.listdir(PERSONA_MODEL_DIRECTORY)
    persona_names_maybe_with_emojis = []
    for persona_name in persona_names:
        persona_path = os.path.join(
            PERSONA_MODEL_DIRECTORY, persona_name, "config.json"
        )
        with open(persona_path) as f:
            persona = json.load(f)
            avatar = (
                emoji.emojize(persona["chatbot_config"]["avatar"], language="alias")
                if "avatar" in persona["chatbot_config"]
                else ""
            )
            persona_names_maybe_with_emojis.append(
                f"{avatar} {persona_name}"
            ) if emoji.is_emoji(avatar) else persona_names_maybe_with_emojis.append(
                persona_name
            )
    persona_options = [""] + sorted(
        persona_names_maybe_with_emojis, reverse=True
    )  # + ["parrot"]
    return persona_options


def style_using_css(style: str) -> None:
    """Utility function to inject CSS style into the Streamlit DOM.

    Args:
        style (str): String representation of CSS style. Assumes it is well-formed.
    """
    st.markdown(f"<style>{style}</style>", unsafe_allow_html=True)


def escape_string(string: str) -> str:
    """Utility function to add '\' to escape sequences in a string.

    Args:
        string (str): Unescaped string.

    Returns:
        str: Escaped string
    """
    return string.encode("unicode_escape").decode("raw_unicode_escape")


def unescape_string(string: str) -> str:
    """Utility function to remove '\' from escape sequences in a string.

    Args:
        string (str): Escaped string.

    Returns:
        str: Unescaped string
    """
    return string.encode("raw_unicode_escape").decode("unicode_escape")
