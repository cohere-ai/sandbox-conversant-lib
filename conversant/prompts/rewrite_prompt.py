# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.


from dataclasses import dataclass
from typing import Any, Dict, List

import jsonschema

REWRITE_PROMPT_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "example_separator": {"type": "string"},
        "fact_header": {"type": "string"},
        "conversation_header": {"type": "string"},
        "rewrite_header": {"type": "string"},
        "preamble": {"type": "string"},
        "examples": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "fact": {"type": "string"},
                    "conversation": {"type": "string"},
                    "rewrite": {"type": "string"},
                },
            },
        },
    },
}


@dataclass
class RewritePrompt:
    """A prompt given to a chatbot to rewrite a message based on a factual paragraph.

    Splits the rewrite prompt to a preamble describing this grounded rewriting
    functionaltiy, the separators and header used to demarcate an example,
    a fact, a conversation message, and a rewrite. Also includes a series
    of examples to help show this functionality, and some validation methods
    that trigger on__post__init().
    """

    example_separator: str
    fact_header: str
    conversation_header: str
    rewrite_header: str
    preamble: str
    examples: List[Dict[str, str]]

    MIN_NUM_EXAMPLES: int = 1

    def __post_init__(self) -> None:
        self._validate_examples()

    @classmethod
    def from_dict(cls, config: Dict[str, Any]):
        """Initializes a RewritePrompt using a dictionary.

        The dictionary should be of the form
        {
            "example_separator": str
            "fact_header": str
            "conversation_header": str
            "rewrite_header": str
            "preamble": str
            "examples: [
                {
                    "fact": str
                    "conversation": str
                    "rewrite": str
                },
                ...
            ]
        }

        Args:
            config (Dict[str, Any]): Dictionary containing the variables for
            a RewritePrompt
        """
        # Validate that theprompt follows our predefined schema
        cls._validate_config(config)

        return cls(**config)

    def _validate_examples(self) -> None:
        """Checks at least MIN_NUM_EXAMPLES examples are given.

        Raises:
            ValueError: Error if there are insufficient examples given.
        """
        if len(self.examples) < self.MIN_NUM_EXAMPLES:
            raise ValueError(
                f"At least {self.MIN_NUM_EXAMPLES} example must be given for {self.__class__.__name__}"
            )

    @staticmethod
    def _validate_config(config: Dict[str, Any]) -> None:
        """Validates formatting of a prompt defined as a dictionary.

        Args:
            persona (Dict[str, Any]): A dictionary containing the prompt information.
        """
        try:
            jsonschema.validate(instance=config, schema=REWRITE_PROMPT_JSON_SCHEMA)
        except jsonschema.exceptions.ValidationError as e:
            raise jsonschema.exceptions.ValidationError(
                f"Type of values in given dictionary do not match schema': {e}"
            )
        except KeyError as e:
            raise KeyError(f"Invalid key in given dictionary': {e}")
        except Exception as e:
            raise Exception(f"Failed to validate prompt in given dictionary: {e}")
