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
from typing import Any, Dict, List, Tuple

import cohere
import jsonschema
from streamlit.web import cli as stcli


from conversant.chatbot import Chatbot
from conversant.prompts.start_prompt import StartPrompt

MAX_PROMPT_SIZE = 2048
PERSONA_MODEL_DIRECTORY = "conversant/personas"
PERSONA_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "user_name": {"type": "string"},
        "bot_name": {"type": "string"},
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
            },
        },
        "start_prompt_config": {
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
        start_prompt: StartPrompt,
        user_name: str = "User",
        bot_name: str = "PromptChatbot",
        persona_name: str = "",
        chatbot_config: Dict[str, Any] = {},
        client_config: Dict[str, Any] = {},
    ):
        """Enriches init by adding a start prompt and user/bot names.

        Args:
            client (cohere.Client): Cohere client for API
            start_prompt (StartPrompt): Starter prompt object for dialogue shaping.
            user_name (str, optional): User's chat handle. Defaults to "User".
            bot_name (str, optional): Bot's chat handle. Defaults to "PromptChatbot".
            persona_name (str, optional): Bot's persona name. Defaults to empty string.
            client_config (Dict, optional): Bot's client config. Defaults to empty dict.
        """

        super().__init__(client)

        self.user_name = user_name
        self.bot_name = bot_name
        self.persona_name = persona_name

        self.start_prompt = start_prompt
        self._validate_start_dialogue()

        self.configure_chatbot(chatbot_config)
        self.configure_client(client_config)

        self.max_prompt_size = MAX_PROMPT_SIZE - self.client_config["max_tokens"]
        self.check_prompt_size()

    def check_and_adjust_prompt_size(self, prompt: str, formatted_query: str) -> Tuple[dict,str]:
        """Check if the prompt size is smaller than the max prompt size.
            
        If not, try to adjust max_context_lines until a possible prompt size.
            
        if this is not possible, just send an error message.

        Args:
            prompt (str): Prompt that will be send to .generate
            formatted_query (str): Last message from user in the correct format

        Returns:
            Tuple[dict,str]: A dict containing the status of the response, the output message, and a new prompt if changed 
        """    

        response = {}
        response['status'] = 'Success'

        curr_size = self.co.tokenize(prompt).length

        # Store original values
        original_size = curr_size
        original_max_context_lines = self.chatbot_config['max_context_lines']

        # Reduce max_context_lines until the size of the prompt is less than maximum or reaches 1
        while (curr_size > self.max_prompt_size) and (self.chatbot_config['max_context_lines'] > 1):
            
            # if the size of chat is less than the max_context_lines start from there
            self.chatbot_config["max_context_lines"] = min(self.chatbot_config["max_context_lines"]-1,len(self.chatlog))
            prompt = self._assemble_prompt(
                                [f"{turn['speaker_name']}: {turn['utterance']}" for turn in self.chatlog]
                                + [f"{formatted_query['speaker_name']}: {formatted_query['utterance']}"])
            
            curr_size = self.co.tokenize(prompt).length

            # Change status and set a output message
            response["status"] = "Warning"
            response["output_message"] = f"The parameter max_context_lines was reduced from {original_max_context_lines} to {self.chatbot_config['max_context_lines']} so that the total amount of tokens does not exceed 2048."

        # If even reducing the max_context_lines to 1, the number of tokens of the prompt is bigger then max
        # an error message should appear and the input ignored
        if curr_size > self.max_prompt_size:
            response["status"] = "Error"
            self.chatbot_config["max_context_lines"] = original_max_context_lines
            response["output_message"] = f"The total number of tokens (prompt and prediction) cannot exceed 2048. Try using a shorter start prompt, sending smaller text messages in the chat, or setting a smaller value for the parameter max_tokens. More details: \n - Start Prompt: {self.start_prompt_size} tokens \n - Messages sent in chat: {original_size - self.start_prompt_size} tokens \n - Parameter max_tokens: {self.client_config['max_tokens']} tokens"

        return response, prompt             



    def reply(self, query: str) -> Dict:
        """Replies to a user's query given a chatlog.

        The reply is then generated directly from a call to a LLM.

        Args:
            query (str): Last message from user

        Returns:
            Dict: Response containing the status, the reply generated by .generate 
            and output message if the status is not success
        """    

        formatted_query = {
            "speaker_name": self.user_name,
            "utterance": query,
        }

        prompt = self._assemble_prompt(
            [f"{turn['speaker_name']}: {turn['utterance']}" for turn in self.chatlog]
            + [f"{formatted_query['speaker_name']}: {formatted_query['utterance']}"]
        )

        final_response,prompt = self.check_and_adjust_prompt_size(prompt,formatted_query)

        if final_response["status"] == "Error":
            return final_response
        
        generated_object = self.co.generate(
            model=self.client_config["model"],
            prompt=prompt,
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
                
        formatted_response = {
            "speaker_name": self.bot_name,
            "utterance": response,
        }

        final_response["data"] = formatted_response
        
        self.chatlog.append(formatted_query)
        self.chatlog.append(formatted_response)

        return final_response


    def configure_chatbot(self, chatbot_config: Dict = {}) -> None:
        """Configures chatbot options.

        Args:
            chatbot_config (Dict, optional): Updates self.chatbot_config. Defaults to {}.
        """
        # We initialize the chatbot to these default config values.
        if not hasattr(self, "chatbot_config"):
            self.chatbot_config = {
                "max_context_lines": 20,
            }
        # Override default config values with the config passed in by the user.
        if isinstance(chatbot_config, Dict):
            self.chatbot_config.update(chatbot_config)
        else:
            raise TypeError(
                f"chatbot_config must be of type Dict, but was passed in as {type(chatbot_config)}"
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
                "stop_seq": [f"\n"],
            }
        # Override default config values with the config passed in by the user.
        if isinstance(client_config, Dict):
            self.client_config.update(client_config)
        else:
            raise TypeError(
                f"client_config must be of type Dict, but was passed in as {type(client_config)}"
            )

    @classmethod
    def from_persona(cls, persona_name: str, client: cohere.Client):
        """Initializes a PromptChatbot using a persona.

        Args:
            persona (str): Name of persona, corresponding to a .json file.
            client (cohere.Client): Cohere client for API
        """
        # Load the persona from a local directory
        persona_path = os.path.join(
            PERSONA_MODEL_DIRECTORY, persona_name, f"config.json"
        )
        if os.path.isfile(persona_path):
            logging.info(f"loading persona from {persona_path}")
        else:
            raise FileNotFoundError(
                f"{persona_name}.json cannot be found in {PERSONA_MODEL_DIRECTORY}/{persona_name}"
            )
        with open(persona_path) as f:
            persona = json.load(f)

        # Validate that the persona follows our predefined schema
        cls._validate_persona_dict(persona, persona_path)

        return cls(
            client=client,
            start_prompt=StartPrompt.from_dict(persona["start_prompt_config"]),
            user_name=persona["user_name"],
            bot_name=persona["bot_name"],
            client_config=persona["client_config"],
            persona_name=persona_name,
        )

    def _assemble_prompt(self, new_lines: List[str]) -> str:
        """Stitches the starter prompt with a trailing window of the chat.

        Args:
            new_lines (List[str]): New lines to append
        """

        trimmed_lines = new_lines[-self.chatbot_config["max_context_lines"] :]
        context_prompt = "\n".join(trimmed_lines)

        stripped_desc = self.start_prompt.bot_desc.strip()

        prepended_turns = [
            (
                f"{self.user_name}: {user_query.strip()}",
                f"{self.bot_name}: {bot_reply.strip()}",
            )
            for (user_query, bot_reply) in self.start_prompt.example_turns
        ]

        stitched_turns = "\n".join(
            ["\n".join([user, bot]) for (user, bot) in prepended_turns]
        )

        description_header = "<<DESCRIPTION>>"
        conversation_header = "<<CONVERSATION>>"

        joined_start_prompt = (
            f"Below is a series of chats between {self.bot_name} and {self.user_name}."
            + f"{self.bot_name} responds to {self.user_name} based on the {description_header}.\n"
            + f"{description_header}\n"
            + f"{stripped_desc}\n"
            + f"{conversation_header}\n"
            + f"{stitched_turns}\n"
            + f"{conversation_header}"
        )

        return f"{joined_start_prompt}\n{context_prompt}\n{self.bot_name}:"

    def _validate_start_dialogue(self) -> None:
        """Validates formatting of starter dialogue."""

        user_turns = [turn[0] for turn in self.start_prompt.example_turns]
        bot_turns = [turn[1] for turn in self.start_prompt.example_turns]
        all_turns = user_turns + bot_turns

        colon_prefixed = all(":" in turn for turn in all_turns)
        hyphen_prefixed = all("-" in turn for turn in all_turns)

        if colon_prefixed or hyphen_prefixed:
            # This might false-positive, so we only log a warning
            logging.warning(
                "Did you mistakenly prefix the example dialogue turns with user/bot names?"
            )

        user_prefixed = all(
            turn.lstrip().startswith(self.user_name) for turn in user_turns
        )

        bot_prefixed = all(
            turn.lstrip().startswith(self.bot_name) for turn in bot_turns
        )

        if user_prefixed and bot_prefixed:
            # It's hard to think of any genuine case where all utterances start with self-names.
            raise ValueError("Start turns should not be prefixed with user/bot names!")

    def check_prompt_size(self) -> None:
        
        self.start_prompt_size = len(self.co.tokenize(self._assemble_prompt([])))
        if self.start_prompt_size > self.max_prompt_size:
            raise ValueError(f"The start prompt config has too many tokens. The total number of tokens cannot exceed 2048 - received {self.start_prompt_size + self.client_config['max_tokens']}. Try using a smaller description or texts in the example turns.")

    @staticmethod
    def _validate_persona_dict(persona: Dict[str, Any], persona_path: str) -> None:
        """Validates formatting of a persona defined as a dictionary.

        Args:
            persona (Dict[str, Any]): A dictionary containing the persona.
            persona_path: The path from which the persona was loaded.
        """
        
        # Checks if the parameter does not exceed MAX_PROMPT_SIZE
        if persona['client_config']['max_tokens'] >= MAX_PROMPT_SIZE:
            raise ValueError("The parameter max_tokens cannot exceed 2048. Try using a smaller value.")
        
        try:
            jsonschema.validate(instance=persona, schema=PERSONA_JSON_SCHEMA)
        except jsonschema.exceptions.ValidationError as e:
            raise jsonschema.exceptions.ValidationError(
                f"Type of values in given dictionary (persona from {persona_path}) do not match schema': {e}"
            )
        except KeyError as e:
            raise KeyError(
                f"Invalid key in given dictionary (persona from {persona_path})': {e}"
            )
        except Exception as e:
            raise Exception(
                f"Failed to validate persona in given dictionary (persona from {persona_path}): {e}"
            )

    
