# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.


import os
import sys

import cohere
import streamlit as st
import streamlit_chat as stchat

from conversant.prompt_chatbot import PERSONA_MODEL_DIRECTORY, PromptChatbot
from conversant.prompts.start_prompt import StartPrompt
from conversant.utils import demo_utils


def get_reply():

    # Generate a bot reply in response to the user's input
    response = st.session_state.bot.reply(query=st.session_state.user_input)
    _ = response.get('data')

    # Stores the reply status value and the output message
    st.session_state.reply_status = response['status']
    st.session_state.output_message = response.get('output_message')

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
    st.session_state.reply_status = 'Success'
    st.session_state.output_message = None


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
        self.chatlog = []
        self.user_name = "User"
        self.bot_name = "Parrot Bot"
        self.start_prompt = StartPrompt(
            bot_desc=(
                "The Parrot Bot repeats back whatever is said to it "
                "without using Cohere's large language models."
            ),
            example_turns=[],
        )

    def reply(self, query: str) -> str:
        """Replies to a user by stating their query.

        Args:
            user_input (str): A user's text chat query

        Returns:
            str: a mock reply
        """
        formatted_query = {
            "speaker_name": self.user_name,
            "utterance": query,
        }
        formatted_response = {
            "speaker_name": self.bot_name,
            "utterance": query,
        }
        self.chatlog.append(formatted_query)
        self.chatlog.append(formatted_response)
        return formatted_response


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
    chatlog_placeholder = st.empty()
    user_input_placeholder = st.empty()
    persona_selection_placeholder = st.empty()

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
                f"**More info about your conversations with {st.session_state.bot.bot_name}:**"
            )
            st.write(f"> {st.session_state.bot.start_prompt.bot_desc}")

            # Add disclaimer
            if st.session_state.persona != "parrot":
                st.write(
                    "_Each persona is powered by [Cohere's](https://cohere.com) large language models, \
                    and these examples are meant purely for demonstrative purposes. \
                    These personas are works of fiction, are not factually grounded, and \
                    should not be taken too seriously!_"
                )

    # Check if bot has been initialized in the Streamlit session.
    if "bot" in st.session_state and st.session_state.bot:

        # List of Dict[str, str] dialogue turns.
        # Each dictionary contains a "speaker_name" and "utterance" key.
        # Let the chatbot begin the dialogue if the chatlog is empty.
        if st.session_state.bot.chatlog == []:

            # We can get the chatbot to begin the conversation with this
            st.session_state.bot.reply(
                query="Hello",
            )
            st.session_state.bot.chatlog.pop(0)  # Remove injected user utterance

        # Places the chat history in a Streamlit container.
        with chatlog_placeholder.container():

            # Check status of the reply and show an output message
            if st.session_state.reply_status == 'Error':
                st.error(st.session_state.output_message)
            elif st.session_state.reply_status == 'Warning':
                st.warning(st.session_state.output_message)

            # Iterate through the chatlog. This is done in reverse order to
            # ensure that recent messages displayed are anchored at the bottom
            # of the Streamlit demo.
            for i, turn in enumerate(st.session_state.bot.chatlog[::-1]):

                # Streamlit renders & runs logic by stepping through
                # Python files procedurally. This is why you have to
                # render all chat messages in the chatlog. We use streamlit_chat
                # to render them.
                if turn["speaker_name"] == st.session_state.bot.bot_name:
                    stchat.message(turn["utterance"], key=f"{i}_bot")
                elif turn["speaker_name"] == st.session_state.bot.user_name:
                    stchat.message(
                        turn["utterance"],
                        is_user=True,
                        key=f"{i}_user",
                        avatar_style="gridy",
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
