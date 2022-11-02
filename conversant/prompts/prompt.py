# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.

import json
from dataclasses import field
from typing import Any, Dict, List

from pydantic.dataclasses import dataclass

from conversant.chatbot import Interaction


@dataclass
class Prompt:
    """Base class for all structured zero-shot or few-shot prompts.

    Args:
        preamble (str): A string that directs the model to behave in certain ways by
            describing its function (e.g. a description of a bot's persona).
        example_separator (str): A separator for each example.
        headers (Dict[str, str]): A dictionary mapping from keys in examples to the
            values that will substitute them.
        examples (List[Interaction]): A list of examples to illustrate the intended
            behaviour.

    Constants:
        REQUIRED_HEADER_KEYS (List[str]): The list of required keys in headers for the
            prompt. (default: `[]`)
        MIN_PREAMBLE_LENGTH (int): The minimum length of the preamble. (default: `1`)
        MIN_NUM_EXAMPLES (int): The minimum number of examples that should be passed in.
            (default: `1`)
    """

    preamble: str
    example_separator: str
    headers: Dict[str, str]
    examples: List[Interaction]

    REQUIRED_KEYS: List[str] = field(default_factory=lambda: [])
    MIN_PREAMBLE_LENGTH: int = 1
    MIN_NUM_EXAMPLES: int = 1

    def __post_init__(self) -> None:
        """Validators for each prompt.

        Each subclass that inherits from Prompt should call this using
        `super().__post_init__()` so that their prompt structure is also validated.
        Stricter validation can be implemented in subclasses by overriding these
        methods, defining custom validators, or adjusting the constants of Prompt.
        """
        self._validate_preamble()
        self._validate_example_separator()
        self._validate_headers()
        self._validate_examples()

    def __repr__(self) -> str:
        return self.to_string()

    def __str__(self) -> str:
        return self.to_string()

    def create_interaction(self, *args, **kwargs) -> Interaction:
        """Creates a new dictionary representation of an interaction.

        The order of args here should correspond to the order of the keys in `headers`.
        The i-th positional argument passed in corresponds to the i-th key, up to
        `len(headers)`. If fewer than `len(headers)` arguments are passed in, the
        remaining entries default to `""`. If more than `len(headers)` arguments are
        passed in, they are ignored.

        Any subsequent keyword arguments override the values defined by the positional
        arguments.

        Args:
            args: Positional arguments for the new interaction.
            kwargs: Keyword arguments for the new interaction.

        Returns:
            Interaction: Dictionary representation of an interaction.
        """
        new_interaction = {
            key: args[i] if i < len(args) else ""
            for i, key in enumerate(self.headers.keys())
        }
        new_interaction.update(kwargs)
        return new_interaction

    def create_interaction_string(self, *args, **kwargs) -> str:
        """Creates a string representation of an interaction.

        The order of args here should correspond to the order of the keys in `headers`.
        The i-th positional argument passed in corresponds to the i-th key, up to
        `len(headers)`. If fewer than `len(headers)` arguments are passed in, the
        remaining entries default to `""`. If more than `len(headers)` arguments are
        passed in, they are ignored.

        Any subsequent keyword arguments override the values defined by the positional
        arguments.

        Each prompt can have their own way of stitching together headers and values
        within examples. Generally, each header should follow its corresponding example
        value. If there are no positional arguments passed in, then the ordering of the
        variables in examples follows the order of the keyword arguments. Otherwise, a
        new example dictionary is created from the positional arguments and the ordering
        is dependent on the order of the `headers`.

        Interactions will look like the following:

            {header}{value}\n
            {header}{value}\n

        Any custom logic should be defined in a subclass method that
        overrides this method.

        Args:
            args: Positional arguments for the new interaction.
            kwargs: Keyword arguments for the new interaction.

        Returns:
            str: String representation of an interaction.
        """
        interaction = self.create_interaction(*args, **kwargs) if args else kwargs
        return "".join(
            f"{self.headers[key]}{interaction[key]}\n" for key in interaction.keys()
        )

    def to_string(self) -> str:
        """Creates a string representation of the prompt.

        The string representation is assembled from the preamble and examples.
        Each example is created from a `create_interaction_string` method and is
        demarcated by an `example_separator`.

        Examples will look like the following:

            {preamble}\n
            {example_separator}
            {field}{value}\n
            {field}{value}\n
            {example_separator}
            {field}{value}\n
            {field}{value}\n
            ...

        Returns:
            str: String representation of the prompt.
        """
        lines = [f"{self.preamble}\n"]
        lines += self.example_separator + f"{self.example_separator}".join(
            self.create_interaction_string(**example) for example in self.examples
        )
        return "".join(lines).strip()

    def update(self, config: Dict[str, Any]) -> None:
        """Updates attributes of this class with attributes from `config`.

        Args:
            config (Dict[str, Any]): Dictionary of attributes that should be updated for
                this class.
        """
        for key, value in config.items():
            if hasattr(self, key):
                setattr(self, key, value)

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> "Prompt":
        """Instantiates a `Prompt` from a dictionary.

        Args:
            config (Dict[str, Any]: Dictionary used to instantiate a prompt object.
            The dictionary should have the following required keys: `preamble`,
            `headers`, `examples`, example_separator`

        Returns:
            Prompt: The prompt object instantiated from the `config`.
        """
        return cls(**config)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes this instance into a Python dictionary.

        Returns:
            Dict[str, Any]: Dictionary of attributes that defines this instance of a
                Prompt.
        """
        return {
            "preamble": self.preamble,
            "example_separator": self.example_separator,
            "headers": self.headers,
            "examples": self.examples,
        }

    def to_json_string(self) -> str:
        """Serializes this instance into a JSON string.

        Returns:
            str: JSON string representation of this instance of a Prompt.
        """
        prompt_dict = self.to_dict()
        return json.dumps(prompt_dict, indent=4) + "\n"

    def _validate_preamble(self) -> None:
        """Validates that the preamble meets the following requirements:

        - At least `MIN_PREAMBLE_LENGTH` in length.

        Raises:
            ValueError: If the length of the preamble is less than
                `MIN_PREAMBLE_LENGTH`.
        """
        if len(self.preamble) < self.MIN_PREAMBLE_LENGTH:
            raise ValueError(
                f"Preamble must be at least {self.MIN_PREAMBLE_LENGTH} characters."
            )

    def _validate_headers(self) -> None:
        """Validates that `headers` meets the following requirements:

        - Contains all keys in `REQUIRED_KEYS`.

        Raises:
            ValueError: If any keys in `REQUIRED_KEYS` is missing from the prompt's
                `headers`.
        """
        if any(key not in self.headers.keys() for key in self.REQUIRED_KEYS):
            raise ValueError(
                f"Missing required key.\nHeader keys: {self.headers.keys()}.\n"
                f"Required: {self.REQUIRED_KEYS}."
            )

    def _validate_example_separator(self) -> None:
        """Validates that the `example_separator` meets the following requirements:

        - Is a str.

        Raises:
            TypeError: If the `example_separator` is not a `str`.
        """
        if not isinstance(self.example_separator, str):
            raise ValueError(
                "example_separator must be a string. Current type: "
                f"{type(self.example_separator)}"
            )

    def _validate_examples(self) -> None:
        """Validates that the `examples` meet the following requirements:

        - All keys are used in every example of `examples`.
        - At least `MIN_NUM_EXAMPLES` examples are given.

        Raises:
            ValueError: If any of the above requirements is not met.
        """
        # All required keys are used in every example of `examples`.
        for example in self.examples:
            if any(key not in example for key in self.REQUIRED_KEYS):
                raise ValueError(
                    f"Missing required key.\nHeader keys: {self.headers.keys()}.\n"
                    f"Required: {self.REQUIRED_KEYS}."
                )

        # At least `MIN_NUM_EXAMPLES` examples are given.
        if len(self.examples) < self.MIN_NUM_EXAMPLES:
            raise ValueError(
                f"At least {self.MIN_NUM_EXAMPLES} example must be given for "
                f"{self.__class__.__name__}"
            )
