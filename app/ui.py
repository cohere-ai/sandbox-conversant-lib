# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.


from collections import defaultdict

import streamlit as st
from streamlit_ace import st_ace
from streamlit_chat import message as st_message


def draw_chat_history() -> None:
    """Renders the chat history in Streamlit.

    The messages are rendered using streamlit-chat, a custom Streamlit component
    for a chatbot UI.
    Reference: https://github.com/AI-Yash/st-chat
    """
    # The chat history is iterated in reverse order to ensure that recent messages
    # displayed are anchored at the bottom of the Streamlit demo.
    for i, turn in enumerate(st.session_state.bot.chat_history[::-1]):

        # If we are at the first conversation turn, we remove the
        # injected user utterance of "Hello" from displaying.
        if i == len(st.session_state.bot.chat_history) - 1:
            if "bot" in turn:
                st_message(turn["bot"], key=f"{i}_bot")
        else:
            if "bot" in turn:
                st_message(turn["bot"], key=f"{i}_bot")
            if "user" in turn:
                st_message(
                    turn["user"],
                    is_user=True,
                    key=f"{i}_user",
                    avatar_style=st.session_state.user_avatar,
                )


def draw_disclaimer() -> None:
    """Adds a disclaimer about the personas in this demo."""
    if st.session_state.persona != "parrot":
        st.write(
            "_Each persona is powered by [Cohere](https://cohere.com)'s large language models, \
            and these examples are meant purely for demonstrative purposes. \
            These personas are works of fiction, are not factually grounded, and \
            should not be taken too seriously!_"
        )
    else:
        st.write(
            "_The Parrot persona does not make use of [Cohere](https://cohere.com)'s large language models._"
        )


def draw_chatbot_config_form() -> None:
    """Adds widgets to edit the chatbot config."""
    config = st.session_state.snapshot_chatbot_config
    max_context_examples = st.slider(
        label="max_context_examples",
        min_value=0,
        max_value=20,
        value=config["max_context_examples"],
    )
    st.session_state.bot.configure_chatbot(
        {"max_context_examples": max_context_examples}
    )


def draw_client_config_form() -> None:
    """Adds widgets to edit the client config."""
    config = st.session_state.snapshot_client_config
    model_options = ["", "small", "medium", "large", "xlarge"]
    model = st.selectbox(
        label="model",
        options=model_options,
        index=model_options.index(config["model"])
        if config["model"] in model_options
        else 0,
    )
    model_id_override = st.text_input(
        label="model ID override",
        value=model if model else config["model"],
    )
    if model != model_id_override:
        st.warning(
            "WARNING: This demo does not validate that the model ID used for override is valid.",
        )
    max_tokens = st.slider(
        label="max_tokens", min_value=50, max_value=250, value=config["max_tokens"]
    )
    temperature = st.slider(
        label="temperature", min_value=0.0, max_value=5.0, value=config["temperature"]
    )
    st.session_state.bot.configure_client(
        {
            "model": model_id_override,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
    )


def draw_prompt_form(disabled: bool = False) -> None:
    """Adds a form for configuring the prompt through its fields.

    The form is rendered as disabled when we only need to show the non-editable values
    of a prompt. This is used when the JSON editor is active.

    Args:
        disabled (bool): Whether or not the form should be rendered as disabled.
    """
    # Batches elements together as a form with a common submit button.
    with st.form("prompt_form"):
        # When the form is disabled, each time it is rendered its values need to be
        # taken from the current prompt config. Otherwise, its values should be taken
        # from the snapshot of the prompt config whenever it is first rendered.
        config = (
            defaultdict(str, st.session_state.bot.prompt.to_dict())
            if disabled
            else defaultdict(str, st.session_state.snapshot_prompt_config)
        )
        # We need to be careful about indexing into the dictionaries here
        # because when editing the prompt JSON, keys can end up malformed.
        default_preamble = config["preamble"]
        default_example_separator = config["example_separator"]
        default_user_name = (
            config["headers"]["user"] if "user" in config["headers"] else ""
        )
        default_bot_name = (
            config["headers"]["bot"] if "bot" in config["headers"] else ""
        )
        # This is where we create the text areas for the form.
        preamble = st.text_area(
            label="preamble",
            disabled=disabled,
            value=default_preamble,
        )
        example_separator = st.text_input(
            label="example_separator",
            disabled=disabled,
            value=default_example_separator,
        )
        user_name = st.text_input(
            label="user",
            disabled=disabled,
            value=default_user_name,
        )
        bot_name = st.text_input(label="bot", disabled=disabled, value=default_bot_name)
        # Because prompt examples have a more complex structure, it is not very user
        # friendly to render them as form input fields.
        st.text_input(
            label="examples",
            placeholder="Please edit examples with the JSON editor.",
            disabled=True,
        )
        # Upon submitting the form, we will save the form values in to the current
        # prompt config, then update the bot. Any errors should be saved.
        submitted = st.form_submit_button("Update")
        if submitted:
            try:
                # print(repr(example_separator))
                current_config = st.session_state.bot.prompt.to_dict()
                current_config["preamble"] = preamble.encode(
                    "raw_unicode_escape"
                ).decode("unicode_escape")
                current_config["example_separator"] = example_separator.encode(
                    "raw_unicode_escape"
                ).decode("unicode_escape")
                current_config["headers"]["user"] = user_name
                current_config["headers"]["bot"] = bot_name
                st.session_state.bot.prompt.update(current_config)
                st.session_state.error = ""
            except Exception as e:
                st.session_state.error = e


def draw_prompt_json_editor(max_height: int) -> None:
    """Renders an streamlit-ace editor into the app.

    streamlit-ace is a custom Streamlitcomponent for an Ace editor.
    Reference: https://github.com/okld/streamlit-ace

    Args:
        max_height (int): Desired height of the UI element expressed in pixels.
            If set to None, height will auto adjust to editor's content.
            None by default.
    """
    st.write(f"**Prompt (JSON):**")
    st_ace(
        value=f"{st.session_state.bot.prompt.to_json_string()}",
        placeholder="Enter a JSON representation of a prompt.",
        height=max_height,
        language="json",
        wrap=True,
        auto_update=True,
        key="json_editor_input",
        theme="monokai",
    )


def draw_prompt_view(json: bool = False) -> None:
    """Adds a representation of the prompt in JSON or as a string.

    Args:
        json (bool): Whether to render the prompt as a JSON object.
    """
    if json:
        st.write(f"**Prompt (JSON):**")
        st.json(st.session_state.bot.prompt.to_dict())
    else:
        st.write(
            f"**{st.session_state.bot.prompt.bot_name} responds to you using the prompt below:**"
        )
        # If the current JSON string is malformed, show the error to the user to help
        # with debugging.
        if "error" in st.session_state and st.session_state.error:
            st.exception(st.session_state.error)
        else:
            st.code(
                st.session_state.bot.get_current_prompt("{Your message here}"),
                language="markdown",
            )
            if len(st.session_state.bot.chat_history) > 0:
                st.write(f"_(includes the current chat history)_")
