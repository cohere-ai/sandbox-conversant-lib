# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.


import os
import re
import sys

import cohere
import emoji
import streamlit as st
import streamlit_chat as stchat
from emojificate.filter import emojificate

from conversant.prompt_chatbot import PERSONA_MODEL_DIRECTORY, PromptChatbot
from conversant.prompts.start_prompt import StartPrompt
from conversant.utils import demo_utils

USER_AVATAR_SHORTCODE = ":bust_in_silhouette:"


def get_reply():
    # Generate a bot reply in response to the user's input
    _ = st.session_state.bot.reply(query=st.session_state.user_input)

    # Reset user input
    st.session_state.user_input = ""


def initialize_chatbot():
    # Initialize a bot from the chosen persona
    if st.session_state.persona.startswith("from launch_demo") and len(sys.argv) > 1:
        # Launched via demo_utils.launch_streamlit() utility function
        st.session_state.bot = demo_utils.decode_object(sys.argv[1])
    elif st.session_state.persona == "":
        st.session_state.bot = None
    elif st.session_state.persona == "parrot":
        st.session_state.bot = ParrotChatbot()
    else:
        st.session_state.bot = PromptChatbot.from_persona(
            st.session_state.persona, client=cohere.Client(st.secrets.COHERE_API_KEY)
        )


@st.cache
def get_twemoji_url_from_shortcode(shortcode: str) -> str:
    """Converts an emoji shortcode to its corresponding Twemoji URL.

    Args:
        shortcode (str): Emoji shortcode
    """
    # Emojize returns the unicode representation of that emoji from its shortcode.
    unicode = emoji.emojize(shortcode)
    # Emojificate returns html <img /> tag.
    img_html_tag = emojificate(unicode)
    # Find the URL from the html tag.
    url = re.findall('src="(.*?)"', img_html_tag, re.DOTALL)[0]
    return url


# This decorator allows Streamlit to compute and cache the results
# of this function.
@st.cache
def get_personas():
    # Initialize the list of personas for Streamlit
    persona_options = [""] + os.listdir(PERSONA_MODEL_DIRECTORY) + ["parrot"]
    return persona_options


class ParrotChatbot:
    """Mock chat function; real use-cases should import
    this functionality via a class that inherits from conversant.chatbot.Chatbot

    This bot simply states the user's query.
    """

    def __init__(self):
        self.prompt = StartPrompt(
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
        )
        self.chat_history = []

    def reply(self, query: str) -> str:
        """Replies to a user by stating their query.

        Args:
            user_input (str): A user's text chat query

        Returns:
            str: a mock reply
        """
        self.chat_history.append(self.prompt.create_example(query, query))
        return query


# This ensures rendering is prevented upon import of this file.
if __name__ == "__main__":

    st.set_page_config(
        page_title="Conversational personas using Cohere",
        page_icon="🎭",
    )

    # Styles Streamlit in a way that allows messages to be scrollable
    # and anchored to the bottom of the chat history.
    with open("app/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # This initializes empty Streamlit containers as placeholders.
    chat_history_placeholder = st.empty()
    user_input_placeholder = st.empty()
    persona_selection_placeholder = st.empty()

    # Initialize the user's avatar
    st.session_state.user_avatar = get_twemoji_url_from_shortcode(USER_AVATAR_SHORTCODE)

    # List of available personas to choose from.
    st.session_state.persona_options = get_personas()

    # Load a PromptChatbot from command line argument if available.
    if len(sys.argv) > 1 and "bot" not in st.session_state:

        # The PromptChatbot passed in should be a base64 encoding of a pickled
        # PromptChatbot object.
        bot = demo_utils.decode_object(sys.argv[1])
        if bot.__class__ != PromptChatbot:
            raise TypeError("base64 string passed in is not of class PromptChatbot")
        else:
            st.session_state.bot = bot
            st.session_state.persona_options.insert(
                0, f"from launch_demo: {st.session_state.bot.persona_name}"
            )

    # Initialize the chatbot with a selected persona.
    with persona_selection_placeholder.container():
        st.selectbox(
            "Choose a chatbot persona:",
            options=st.session_state.persona_options,
            key="persona",
            on_change=initialize_chatbot,
        )

        # Show persona description
        if "bot" in st.session_state and st.session_state.bot:
            st.write(
                f"**More info about your conversations with \
                    {st.session_state.bot.bot_name}:**"
            )
            st.write(f"> {st.session_state.bot.prompt.preamble}")

            # Add disclaimer
            if st.session_state.persona != "parrot":
                st.write(
                    "_Each persona is powered by [Cohere's](https://cohere.com) large \
                    language models, and these examples are meant purely for \
                    demonstrative purposes. These personas are works of fiction, are \
                    not factually grounded, and should not be taken too seriously!_"
                )

    # Check if bot has been initialized in the Streamlit session.
    if "bot" in st.session_state and st.session_state.bot:

        # List of Dict[str, str] dialogue turns.
        # Each dictionary contains a "speaker_name" and "utterance" key.
        # Let the chatbot begin the dialogue if the chat_history is empty.
        if st.session_state.bot.chat_history == []:

            # We can get the chatbot to begin the conversation with this
            st.session_state.bot.reply(
                query="Hello",
            )

        # Places the chat history in a Streamlit container.
        with chat_history_placeholder.container():

            # Iterate through the chat_history. This is done in reverse order to
            # ensure that recent messages displayed are anchored at the bottom
            # of the Streamlit demo.
            for i, turn in enumerate(st.session_state.bot.chat_history[::-1]):

                # If we are at the first conversation turn, we remove the
                # injected user utterance of "Hello" from displaying.
                if i == len(st.session_state.bot.chat_history) - 1:
                    if "bot" in turn:
                        stchat.message(turn["bot"], key=f"{i}_bot")
                else:

                    # Streamlit renders & runs logic by stepping through
                    # Python files procedurally. This is why you have to
                    # render all chat messages in the chat_history. We use streamlit_chat
                    # to render them.
                    if "bot" in turn:
                        stchat.message(turn["bot"], key=f"{i}_bot")
                    if "user" in turn:
                        stchat.message(
                            turn["user"],
                            is_user=True,
                            key=f"{i}_user",
                            avatar_style=st.session_state.user_avatar,
                        )

        # Places the user input in a Streamlit container.
        with user_input_placeholder.container():

            # You could capture the value in a local var
            # but using "key" instead captures in the
            # session_state dictionary. The on_change allows us
            # to add a callback get_reply that is called when user_input
            # is given.
            st.text_input(
                label=f"Chat with {st.session_state.bot.bot_name}!",
                placeholder="[Type something and press ENTER]",
                key="user_input",
                on_change=get_reply,
            )
