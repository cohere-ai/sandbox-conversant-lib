# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.


import ast
import copy
import os
import sys

import cohere
import emoji
import streamlit as st

from conversant.demo import ui, utils
from conversant.prompt_chatbot import PromptChatbot
from conversant.utils import demo_utils

USER_AVATAR_SHORTCODE = ":bust_in_silhouette:"


def get_reply() -> None:
    """Replies query from the message input, and resets the message input"""
    _ = st.session_state.bot.reply(query=st.session_state.message_input)
    st.session_state.message_input = ""


def initialize_chatbot() -> None:
    """Initializes the chatbot from a selected persona and saves the session state."""
    if st.session_state.persona.startswith("(launched)") and len(sys.argv) > 1:
        st.session_state.bot = demo_utils.decode_chatbot(
            sys.argv[1], client=cohere.Client(os.environ.get("COHERE_API_KEY"))
        )  # Launched via demo_utils.launch_streamlit() utility function
    elif st.session_state.persona == "":
        st.session_state.bot = None
    elif st.session_state.persona == "parrot":
        st.session_state.bot = utils.ParrotChatbot()
    else:
        st.session_state.bot = PromptChatbot.from_persona(
            emoji.replace_emoji(st.session_state.persona, "").strip(),
            client=cohere.Client(os.environ.get("COHERE_API_KEY")),
        )
    if "bot" in st.session_state and st.session_state.bot:
        update_session_with_prompt()
    # Reset the edit_promp_json session state so we don't remain on the JSON editor when
    # changing to another bot. This is because st_ace is unable to write
    # new values from the current session state.
    st.session_state.edit_prompt_json = False


def update_session_with_prompt() -> None:
    """Saves the prompt config dictionary into the session state."""
    if "bot" in st.session_state and st.session_state.bot:
        st.session_state.snapshot_prompt_config = copy.deepcopy(
            st.session_state.bot.prompt.to_dict()
        )
        st.session_state.snapshot_chatbot_config = copy.deepcopy(
            st.session_state.bot.chatbot_config
        )
        st.session_state.snapshot_client_config = copy.deepcopy(
            st.session_state.bot.client_config
        )


def update_prompt_from_json() -> None:
    """Evaluates JSON string and updates the session's bot prompt."""
    if st.session_state.json_editor_input:
        try:
            prompt_config = ast.literal_eval(st.session_state.json_editor_input)
            st.session_state.bot.prompt.update(prompt_config)
            update_session_with_prompt()
            st.session_state.error = ""
        except Exception as e:
            st.session_state.error = e


# This ensures rendering is prevented upon import of this file.
if __name__ == "__main__":
    st.set_page_config(
        page_title="Conversational personas using Cohere",
        page_icon="🎭",
        layout="wide",
    )

    # Streamlit's default elements are not easy to style. Instead, we have to
    # define styling in a custom CSS file and inject it into the Streamlit DOM.
    # This is brittle and dependent on the DOM structure. Any changes to the layout
    # will break the styling defined in this file.
    with open(f"{os.path.dirname(__file__)}/styles.css") as f:
        utils.style_using_css(f.read())

    # We use the :bust_in_silhouette: emoji as a neutral user avatar.
    st.session_state.user_avatar = utils.get_twemoji_url_from_shortcode(
        USER_AVATAR_SHORTCODE
    )

    # Each persona is a directory in PERSONA_MODEL_DIRECTORY, each with its
    # config.json file.
    st.session_state.persona_options = utils.get_persona_options()

    # Check if COHERE_API_KEY is not set from secrets.toml or os.environ
    if "COHERE_API_KEY" not in os.environ:
        raise KeyError(
            "COHERE_API_KEY not found in st.secrets or os.environ. Please set it in "
            ".streamlit/secrets.toml or as an environment variable."
        )

    # A chatbot can be passed in as a base64 encoding of a pickled PromptChatbot object.
    # This is only used when calling the launch_demo() method of a PromptChatbot object.
    # The chatbot is then injected into the list of available personas in this streamlit
    # demo.
    if len(sys.argv) > 1 and "bot" not in st.session_state:

        # The PromptChatbot passed in should be a base64 encoding of a pickled
        # PromptChatbot object.
        bot = demo_utils.decode_chatbot(
            sys.argv[1], cohere.Client(os.environ.get("COHERE_API_KEY"))
        )
        if not isinstance(bot, PromptChatbot):
            raise TypeError("base64 string passed in is not of class PromptChatbot")
        else:
            st.session_state.bot = bot
            st.session_state.persona_options.insert(
                0, f"(launched) {st.session_state.bot.persona_name}"
            )

    # Adding a header to direct users to sign up for Cohere, explore the playground,
    # and check out our git repo.
    st.header("🎭 Conversational Personas using Cohere")
    with st.expander("About", expanded="bot" not in st.session_state):
        st.markdown(
            """
        This demo app is using 
        [**conversant**](https://github.com/cohere-ai/sandbox-conversant-lib), an 
        open-source framework for building chatbots on top of Cohere’s large 
        language models. 

        Cohere provides access to advanced Large Language Models and NLP tools through 
        one easy-to-use API. 
        """
            "[**Get started for free!**]"
            "(https://dashboard.cohere.ai/welcome/register?utm_source=cohere-owned&utm_"
            "medium=content&utm_campaign=sandbox&utm_term=streamlit&utm_content=conversant)"
        )

    # Page control flow logic is determined from the sidebar.
    with st.sidebar:
        st.selectbox(
            "Choose a chatbot persona:",
            options=st.session_state.persona_options,
            key="persona",
            on_change=initialize_chatbot,
        )
        st.checkbox(
            "Edit prompt",
            value=False,
            key="edit_prompt",
            on_change=update_session_with_prompt,
        )
        if st.session_state.edit_prompt:
            st.checkbox(
                "Use JSON editor",
                value=False,
                key="edit_prompt_json",
                on_change=update_session_with_prompt,
            )

        # Initialize a settings container in the sidebar. This allows us to place
        # Streamlit elements within this placeholder later in this script.
        settings_placeholder = st.empty()

    # Initialize a chat container as the middle of 3 vertical columns.
    # Only visible when the edit prompt checkbox is not selected.
    _, chat_placeholder, _ = st.columns([1, 1, 1])
    with chat_placeholder.container():
        chat_history_placeholder = st.empty()
        message_input_placeholder = st.empty()

    # Initialize a prompt json and string view as 2 vertical columns.
    # Only visible when the edit prompt checkbox is selected.
    prompt_json_column, prompt_string_column = st.columns([1, 1])
    with prompt_json_column:
        prompt_json_edit_placeholder = st.empty()
        prompt_json_view_placeholder = st.empty()
    with prompt_string_column:
        prompt_string_placeholder = st.empty()

    # Check if bot has been initialized in the Streamlit session.
    if "bot" in st.session_state and st.session_state.bot:

        # Initialize the bot avatar
        bot_avatar_string = st.session_state.bot.chatbot_config["avatar"]
        st.session_state.bot_avatar = (
            utils.get_twemoji_url_from_shortcode(bot_avatar_string)
            if emoji.is_emoji(emoji.emojize(bot_avatar_string, language="alias"))
            else bot_avatar_string
        )

        # Editor view for the prompt
        if st.session_state.edit_prompt:

            # Edit the prompt using a JSON editor
            if st.session_state.edit_prompt_json:

                # The prompt JSON editor needs to be drawn first so that
                # the displayed form values in the sidebar take reference from
                # the editor.
                with prompt_json_edit_placeholder.container():
                    ui.draw_prompt_json_editor(
                        max_height=955
                    )  # st_ace only accepts hardcoded pixel values
                    update_prompt_from_json()

                with settings_placeholder.container():
                    with st.expander("Client Config"):
                        ui.draw_client_config_form()
                    with st.expander("Chatbot Config"):
                        ui.draw_chatbot_config_form()
                    ui.draw_prompt_form(disabled=True)

                with prompt_string_placeholder.container():
                    ui.draw_prompt_view(json=False)

            # Edit the prompt using a form in the sidebar
            else:

                # The settings form needs to be drawn first so that
                # the displayed JSON values in prompt JSON placeholder
                # take reference from the form.
                with settings_placeholder.container():
                    with st.expander("Client Config"):
                        ui.draw_client_config_form()
                    with st.expander("Chatbot Config"):
                        ui.draw_chatbot_config_form()
                    ui.draw_prompt_form(disabled=False)

                with prompt_json_view_placeholder.container():
                    ui.draw_prompt_view(json=True)

                with prompt_string_placeholder.container():
                    ui.draw_prompt_view(json=False)

        # Chat view with the persona
        else:

            # We can get the chatbot to begin the conversation with this.
            # The session's state needs to be manually updated since we are not
            # refreshing the entire Streamlit app.
            if not st.session_state.bot.chat_history:
                st.session_state.bot.reply(
                    query="Hello",
                )
                update_session_with_prompt()

            # Draw UI elements for the sidebar
            with settings_placeholder.container():

                with st.expander("Client Config"):
                    ui.draw_client_config_form()
                with st.expander("Chatbot Config"):
                    ui.draw_chatbot_config_form()

                with st.expander("Prompt (JSON)"):
                    ui.draw_prompt_view(json=True)

                with st.expander("Prompt (string)", expanded=True):
                    ui.draw_prompt_view(json=False)

            # Draw chat history.
            with chat_history_placeholder.container():
                ui.draw_chat_history()

            # Draw the message input field and a disclaimer.
            with message_input_placeholder.container():
                st.text_input(
                    label=f"Chat with {st.session_state.bot.prompt.bot_name}!",
                    placeholder="Type a message",
                    key="message_input",
                    on_change=get_reply,
                )
                ui.draw_disclaimer()

            # When in chat view, anchor elements from the bottom so that
            # the message input field is at the bottom (more natural).
            utils.style_using_css(
                """div.css-18e3th9.egzxvld2 > div:nth-child(1) > div:nth-child(1) > div:nth-child(6) { /* # noqa */
                    margin-top: auto;
                }
            """
            )
