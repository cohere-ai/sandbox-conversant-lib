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
from typing import Any, Dict, Tuple

import cohere
import jsonschema


from conversant.chatbot import Chatbot
from conversant.prompts.prompt import Prompt
from conversant.prompts.start_prompt import StartPrompt

MAX_PROMPT_SIZE = 2048
PERSONA_MODEL_DIRECTORY = "conversant/personas"
PERSONA_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "chatbot_config": {
            "type": "object",
            "properties": {
                "max_context_examples": {"type": "integer"},
            },
        },
        "client_config": {
            "type": "object",
            "properties": {
                "model": {"type": "string"},
                "max_tokens": {"type": "integer"},
                "temperature": {"type": "number"},
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

        # For the generation models, the maximum token length is 2048
        # (prompt and generation). So the prompt sent to .generate should be
        # MAX_PROMPT_SIZE minus max tokens generated
        self.max_prompt_size = MAX_PROMPT_SIZE - self.client_config["max_tokens"]
        self.check_prompt_size()

    def __repr__(self) -> Dict[str, Any]:
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

    def check_and_adjust_prompt_size(self, prompt: str, query: str) -> Tuple[dict, str]:
        """Check if the prompt size is smaller than the max prompt size.

        If not, try to adjust max_context_examples until a possible prompt size.

        if this is not possible, just send an error message.

        Args:
            prompt (str): Prompt that will be send to .generate
            formatted_query (str): Last message from user in the correct format

        Returns:
            Tuple[dict, str]: A tuple containing a dict mapping from "status" and
            "output_message" keys to their respective values, and a prompt that
            has been adjusted if necessary
        """

        response = {}
        response["status"] = "Success"

        curr_size = self.co.tokenize(prompt).length

        # Store original values
        original_size = curr_size
        original_max_context_examples = self.chatbot_config["max_context_examples"]

        # Reduce max_context_examples until the number of token of the prompt
        # is less than maximum or reaches 1
        while (curr_size > self.max_prompt_size) and (
            self.chatbot_config["max_context_examples"] > 1
        ):

            # if the size of chat is less than the max_context_examples start from there
            self.chatbot_config["max_context_examples"] = min(
                self.chatbot_config["max_context_examples"] - 1, len(self.chat_history)
            )
            prompt = self.get_current_prompt(query)
            curr_size = self.co.tokenize(prompt).length

            # Change status and set a output message
            response["status"] = "Warning"
            response["output_message"] = (
                "The parameter max_context_lines was reduced"
                f"from {original_max_context_examples} to"
                f"{self.chatbot_config['max_context_lines']}"
                f"so that the total amount of tokens does not exceed {MAX_PROMPT_SIZE}."
            )

        # If even reducing the max_context_examples to 1, the number of tokens of the
        # prompt is bigger then max an error message should appear and the input ignored
        if curr_size > self.max_prompt_size:
            response["status"] = "Error"
            self.chatbot_config["max_context_examples"] = original_max_context_examples
            response["output_message"] = (
                "The total number of tokens (prompt and prediction) cannot exceed"
                f"{MAX_PROMPT_SIZE}.Try using a shorter start prompt, sending "
                "smaller text messages in the chat, or setting a smaller value "
                "for the parameter max_tokens. More details: \n"
                f" - Start Prompt: {self.start_prompt_size} tokens \n"
                f" - Messages sent in chat: {original_size - self.start_prompt_size} "
                f" tokens \n - Parameter max_tokens: {self.client_config['max_tokens']}"
                "tokens"
            )

        return response, prompt

    def reply(self, query: str) -> Dict:
        """Replies to a query given a chat history.

        The reply is then generated directly from a call to a LLM.

        Args:
            query (str): A query passed to the prompt chatbot.

        Returns:
            Dict: Response containing the status, the reply generated by .generate
            and output message if the status is not success
        """
        # The current prompt is assembled from the initial prompt,
        # from the chat history with a maximum of max_context_examples,
        # and from the current query
        current_prompt = self.get_current_prompt(query)
        # The current prompt is assembled from the initial prompt,
        # from the chat history with a maximum of max_context_examples,
        # and from the current query
        current_prompt = self.get_current_prompt(query)
        final_response, current_prompt = self.check_and_adjust_prompt_size(
            current_prompt, query
        )

        if final_response["status"] == "Error":
            return final_response

        # Make a call to Cohere's co.generate API

        generated_object = self.co.generate(
            model=self.client_config["model"],
            prompt=current_prompt,
            max_tokens=self.client_config["max_tokens"],
            temperature=self.client_config["temperature"],
            stop_sequences=self.client_config["stop_seq"],
        )
        # If response was cut off by .generate() finding a stop sequence,
        # remove that sequence from the response.
        response = generated_object.generations[0].text
        for stop_seq in self.client_config["stop_seq"]:
            if response.endswith(stop_seq):
                response = response[: -len(stop_seq)]
        response = response.lstrip()

        final_response["data"] = response

        # We need to remember the current response in the chat history for future
        # responses.
        self.chat_history.append(self.prompt.create_example(query, response))
        self.prompt_history.append(current_prompt)

        return final_response

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
            context_prompt_lines.append(self.prompt.create_example_string(**turn))
        context_prompt = "".join(context_prompt_lines)

        # get query prompt
        query_prompt = self.prompt.create_example_string(query)

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
                "stop_seq": self.prompt.stop_sequences,
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
            Dict[str, Any]: Dictionary of attributes that defines this
            instance of a PromptChatbot.
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

    def check_prompt_size(self) -> None:

        self.start_prompt_size = self.co.tokenize(self.get_current_prompt([])).length
        if self.start_prompt_size > self.max_prompt_size:
            raise ValueError(
                "The prompt given to PromptChatbot has too many tokens. The total "
                "number of tokens "
                f"({self.start_prompt_size + self.client_config['max_tokens']}) cannot "
                f"exceed {MAX_PROMPT_SIZE}. Try using a shorter preamble or less "
                "examples."
            )

    @staticmethod
    def _validate_persona_dict(persona: Dict[str, Any], persona_path: str) -> None:
        """Validates formatting of a persona defined as a dictionary.

        Args:
            persona (Dict[str, Any]): A dictionary containing the persona.
            persona_path: The path from which the persona was loaded.
        """

        # Checks if the parameter does not exceed MAX_PROMPT_SIZE
        if persona["client_config"]["max_tokens"] >= MAX_PROMPT_SIZE:
            raise ValueError(
                f"The parameter max_tokens cannot exceed {MAX_PROMPT_SIZE}."
                " Try using a smaller value."
            )
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
