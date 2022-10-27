# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.

import json
import logging
import os
from typing import Any, Dict

import cohere
import jsonschema

from conversant.chatbot import Chatbot, Interaction
from conversant.prompts.prompt import Prompt
from conversant.prompts.start_prompt import StartPrompt

PERSONA_MODEL_DIRECTORY = "conversant/personas"
PERSONA_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "chatbot_config": {
            "type": "object",
            "properties": {
                "max_context_lines": {"type": "integer"},
            },
        },
        "client_config": {
            "type": "object",
            "properties": {
                "model": {"type": "string"},
                "max_tokens": {"type": "integer"},
                "temperature": {"type": "number"},
                "frequency_penalty": {"type": "number"},
                "presence_penalty": {"type": "number"},
                "stop_sequences": {"type": "array"},
            },
        },
        "prompt_config": {
            "type": "object",
        },
    },
}


class PromptChatbot(Chatbot):
    """Use prompt templates and LLM generation to define a chatbot.

    This bot makes no use of external knowledge sources.
    """

    def __init__(
        self,
        client: cohere.Client,
        prompt: Prompt,
        persona_name: str = "",
        chatbot_config: Dict[str, Any] = {},
        client_config: Dict[str, Any] = {},
    ):
        """Enriches init by adding a prompt.

        Args:
            client (cohere.Client): Cohere client for API
            prompt (Prompt): Prompt object to direct behavior.
            persona_name (str, optional): Bot's persona name. Defaults to empty string.
            chatbot_config: (Dict[str, Any], optional): Bot's chat config. Defaults to
                empty dict.
            client_config (Dict[str, Any], optional): Bot's client config. Defaults to
                empty dict.
        """

        super().__init__(client)
        self.prompt = prompt
        self.persona_name = persona_name

        self.configure_chatbot(chatbot_config)
        self.configure_client(client_config)
        self.chat_history = []
        self.prompt_history = [self.prompt.to_string()]

    def __repr__(self) -> str:
        return json.dumps(self.to_dict(), indent=4, default=str)

    @property
    def user_name(self):
        """
        Returns:
            str: The name of the user, defined in the prompt. Defaults to "User".
        """
        if hasattr(self.prompt, "user_name"):
            return self.prompt.user_name
        else:
            return "User"

    @property
    def bot_name(self):
        """
        Returns:
            str: The name of the chatbot, defined in the prompt. Defaults to
                "PromptChatbot".
        """
        if hasattr(self.prompt, "bot_name"):
            return self.prompt.bot_name
        else:
            return "PromptChatbot"

    @property
    def latest_prompt(self) -> str:
        """Retrieves the latest prompt.

        Returns:
            str: The prompt most recently added to the prompt history.
        """
        return self.prompt_history[-1]

    def reply(self, query: str) -> Interaction:
        """Replies to a query given a chat history.

        The reply is then generated directly from a call to a LLM.

        Args:
            query (str): A query passed to the prompt chatbot.

        Returns:
            Interaction: Dictionary of query and generated LLM response
        """
        # The current prompt is assembled from the initial prompt,
        # from the chat history with a maximum of max_context_examples,
        # and from the current query
        current_prompt = self.get_current_prompt(query)

        # Make a call to Cohere's co.generate API
        generated_object = self.co.generate(
            model=self.client_config["model"],
            prompt=current_prompt,
            max_tokens=self.client_config["max_tokens"],
            temperature=self.client_config["temperature"],
            frequency_penalty=self.client_config["frequency_penalty"],
            presence_penalty=self.client_config["presence_penalty"],
            stop_sequences=self.client_config["stop_sequences"],
        )

        # If response was cut off by .generate() finding a stop sequence,
        # remove that sequence from the response.
        response = generated_object.generations[0].text
        for stop_seq in self.client_config["stop_sequences"]:
            if response.endswith(stop_seq):
                response = response[: -len(stop_seq)]
        response = response.lstrip()

        # We need to remember the current response in the chat history for future
        # responses.
        self.chat_history.append(self.prompt.create_interaction(query, response))
        self.prompt_history.append(current_prompt)

        return response

    def get_current_prompt(self, query) -> str:
        """Stitches the prompt with a trailing window of the chat.

        Args:
            query (str): The current user query.

        Returns:
            str: The current prompt given a query.
        """
        # get base prompt
        base_prompt = self.prompt.to_string() + "\n"

        # get context prompt
        context_prompt_lines = []
        trimmed_chat_history = (
            self.chat_history[-self.chatbot_config["max_context_examples"] :]
            if self.chatbot_config["max_context_examples"] > 0
            else []
        )
        # TODO when prompt is updated, the history is mutated
        # as it is recreated using the new prompt. A possible fix is to save the old
        # prompt in history and use it when recreating.
        for turn in trimmed_chat_history:
            context_prompt_lines.append(self.prompt.create_interaction_string(**turn))
        context_prompt = self.prompt.example_separator + "".join(context_prompt_lines)

        # get query prompt
        query_prompt = self.prompt.create_interaction_string(query)

        current_prompt = base_prompt + context_prompt + query_prompt
        return current_prompt.strip()

    def configure_chatbot(self, chatbot_config: Dict = {}) -> None:
        """Configures chatbot options.

        Args:
            chatbot_config (Dict, optional): Updates self.chatbot_config. Defaults
            to {}.
        """
        # We initialize the chatbot to these default config values.
        if not hasattr(self, "chatbot_config"):
            self.chatbot_config = {
                "max_context_examples": 10,
            }
        # Override default config values with the config passed in
        if isinstance(chatbot_config, Dict):
            self.chatbot_config.update(chatbot_config)
        else:
            raise TypeError(
                f"chatbot_config must be of type Dict, but was passed in as \
                    {type(chatbot_config)}"
            )

    def configure_client(self, client_config: Dict = {}) -> None:
        """Configures client options.

        Args:
            client_config (Dict, optional): Updates self.client_config. Defaults to {}.
        """
        # We initialize the client to these default config values.
        if not hasattr(self, "client_config"):
            self.client_config = {
                "model": "xlarge",
                "max_tokens": 100,
                "temperature": 0.75,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0,
                "stop_sequences": self.prompt.stop_sequences,
            }
        # Override default config values with the config passed in
        if isinstance(client_config, Dict):
            self.client_config.update(client_config)
        else:
            raise TypeError(
                f"client_config must be of type Dict, but was passed in as \
                    {type(client_config)}"
            )

    @classmethod
    def from_persona(
        cls,
        persona_name: str,
        client: cohere.Client,
        persona_dir: str = PERSONA_MODEL_DIRECTORY,
    ):
        """Initializes a PromptChatbot using a persona.

        Args:
            persona (str): Name of persona, corresponding to a .json file.
            client (cohere.Client): Cohere client for API
            persona_dir (str): Path to where pre-defined personas are.
        """
        # Load the persona from a local directory
        persona_path = os.path.join(persona_dir, persona_name, "config.json")
        if os.path.isfile(persona_path):
            logging.info(f"loading persona from {persona_path}")
        else:
            raise FileNotFoundError(f"{persona_path} cannot be found.")
        with open(persona_path) as f:
            persona = json.load(f)

        # Validate that the persona follows our predefined schema
        cls._validate_persona_dict(persona, persona_path)

        return cls(
            client=client,
            prompt=StartPrompt.from_dict(persona["start_prompt_config"]),
            persona_name=persona_name,
            chatbot_config=persona["chatbot_config"],
            client_config=persona["client_config"],
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serializes this instance into a Python dictionary.

        Returns:
            Dict[str, Any]: Dictionary of attributes that defines this instance of a
                PromptChatbot.
        """
        return {
            "co": self.co,
            "prompt": self.prompt.to_dict(),
            "persona_name": self.persona_name,
            "chatbot_config": self.chatbot_config,
            "client_config": self.client_config,
            "chat_history": self.chat_history,
            "prompt_history": self.prompt_history,
            "user_name": self.user_name,
            "bot_name": self.bot_name,
            "latest_prompt": self.latest_prompt,
        }

    @staticmethod
    def _validate_persona_dict(persona: Dict[str, Any], persona_path: str) -> None:
        """Validates formatting of a persona defined as a dictionary.

        Args:
            persona (Dict[str, Any]): A dictionary containing the persona.
            persona_path: The path from which the persona was loaded.
        """
        try:
            jsonschema.validate(instance=persona, schema=PERSONA_JSON_SCHEMA)
        except jsonschema.exceptions.ValidationError as e:
            raise jsonschema.exceptions.ValidationError(
                f"Type of values in given dictionary (persona from {persona_path}) \
                    do not match schema': {e}"
            )
        except KeyError as e:
            raise KeyError(
                f"Invalid key in given dictionary (persona from {persona_path})': {e}"
            )
        except Exception as e:
            raise Exception(
                f"Failed to validate persona in given dictionary \
                    (persona from {persona_path}): {e}"
            )
