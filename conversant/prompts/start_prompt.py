# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import jsonschema

START_PROMPT_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "bot_desc": {"type": "string"},
        "example_turns": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "user": {"type": "string"},
                    "bot": {"type": "string"},
                },
            },
        },
    },
}


@dataclass
class StartPrompt:
    """A starting prompt given to a Chatbot.

    Splits a start prompt into a description with a min length
    requirement, and a series of example turns that help to shape
    the dialogue during the "real" chat with a user. Also includes
    some validation methods that trigger on __post_init__().
    """

    bot_desc: str
    example_turns: List[Tuple[str, str]]

    MIN_DESC_LEN: int = 10

    def __post_init__(self) -> None:
        self._validate_bot_desc()
        self._validate_example_turns()

    @classmethod
    def from_dict(cls, config: Dict[str, Any]):
        """Initializes a StartPrompt using a dictionary.

        The dictionary should be of the form
        {
            "bot_desc": str
            "example_turns": [
                {
                    "user": str
                    "bot": str
                },
                ...
            ]
        }

        Args:
            config (Dict[str, Any]): Dictionary containing the variables for
            a StartPrompt.
        """

        # Validate that the prompt follows our predefined schema
        cls._validate_config(config)

        # Parse the example turns in the dictionary.
        example_turns = [
            (turn["user"], turn["bot"]) for turn in config["example_turns"]
        ]

        return cls(bot_desc=config["bot_desc"], example_turns=example_turns)

    def _validate_example_turns(self) -> None:
        """Checks starter turn dialogue formatting.

        Raises:
            ValueError: Errors if formatting of turns isn't a 1-1 convo.
        """

        if not all(isinstance(pair, tuple) for pair in self.example_turns):
            raise ValueError("Start turns must be a list of tuples.")

        if not all([len(pair) == 2 for pair in self.example_turns]):
            raise ValueError("Start turns must be pairs of (user, bot) utterances.")

    def _validate_bot_desc(self) -> None:
        """Checks the description isn't trivially short.

        Raises:
            ValueError: Errors if a description of a bot is trivially short.
        """

        if len(self.bot_desc) < self.MIN_DESC_LEN:
            raise ValueError(
                f"Bot description must be more than {self.MIN_DESC_LEN} characters and \
                    ideally should be a paragraph long."
            )

    @staticmethod
    def _validate_config(config: Dict[str, Any]) -> None:
        """Validates formatting of a prompt defined as a dictionary.

        Args:
            persona (Dict[str, Any]): A dictionary containing the prompt information.
        """
        try:
            jsonschema.validate(instance=config, schema=START_PROMPT_JSON_SCHEMA)
        except jsonschema.exceptions.ValidationError as e:
            raise jsonschema.exceptions.ValidationError(
                f"Type of values in given dictionary do not match schema': {e}"
            )
        except KeyError as e:
            raise KeyError(f"Invalid key in given dictionary': {e}")
        except Exception as e:
            raise Exception(f"Failed to validate prompt in given dictionary: {e}")
