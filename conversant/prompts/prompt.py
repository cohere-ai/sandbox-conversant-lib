# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.

from dataclasses import field
from typing import Any, Dict, List

from pydantic.dataclasses import dataclass


@dataclass
class Prompt:
    """Base class for all prompts.

    Args:
        preamble (str): A preamble to direct the model to behave in certain ways.
        example_separator (str): A separator for each example.
        fields (List[str]): Fields for each example.
        headers (Dict[str, str]): Headers to demarcate each field within examples.
        examples (List[Dict[str, str]]): A list of examples with fields to illustrate the intended behaviour.

    Constants:
        REQUIRED_FIELDS (List[str]): The list of required fields for the prompt. (default: `[]`)
        MIN_PREAMBLE_LENGTH (int): The minimum length of the preamble. (default: `1`)
        MIN_NUM_EXAMPLES (int): The minimum number of examples that should be passed in. (default: `1`)
    """

    preamble: str
    fields: List[str]
    example_separator: str
    headers: Dict[str, str]
    examples: List[Dict[str, str]]

    REQUIRED_FIELDS: List[str] = field(default_factory=lambda: [])
    MIN_PREAMBLE_LENGTH: int = 1
    MIN_NUM_EXAMPLES: int = 1

    def __post_init__(self) -> None:
        """Validators for each prompt.

        Each subclass that inherits from Prompt should call this using
        `super().__post_init__()` so that their prompt structure is also validated.
        Stricter validation can be implemented in subclasses by overriding these methods,
        defining custom validators, or adjusting the constants of Prompt.
        """
        self._validate_preamble()
        self._validate_fields()
        self._validate_example_separator()
        self._validate_headers()
        self._validate_examples()

    def __repr__(self) -> str:
        return self.to_string()

    def __str__(self) -> str:
        return self.to_string()

    @property
    def stop_sequences(self) -> List[str]:
        """A (partial) list of stop sequences on which the model will stop generation.

        By default, models should cut off generation when encountering
        any header already defined in the prompt. More stop sequences can be added
        external to Prompt, before passing them as an argument to a generation client.

        Returns:
            List[str]: A list of stop sequences corresponding to the headers of the prompt.
        """
        return list(self.headers.keys())

    def create_example(self, *args, **kwargs) -> Dict[str, str]:
        """Creates a new dictionary representation of an example from positional
        and keyword arguments.

        The order of args here should correspond to the order of the `fields`. The i-th
        positional argument passed in corresponds to the i-th field, up to `len(fields)`.
        If fewer than `len(fields)` arguments are passed in, the remaining fields default
        to `""`. If more than `len(fields)` arguments are passed in, they are ignored.

        Any subsequent keyword arguments overrides the values defined by the positional
        arguments.

        Args:
            args: Positional arguments for the new example.
            kwargs: Keyword arguments for the new example.

        Returns:
            Dict[str, str]: Dictionary representation of an example.
        """
        new_example = {
            field: args[i] if i < len(args) else ""
            for i, field in enumerate(self.fields)
        }
        new_example.update(kwargs)
        return new_example

    def create_example_string(self, *args, **kwargs) -> str:
        """Creates a string representation of an example from positional and
        keyword arguments.

        The order of args here should correspond to the order of the `fields`. The i-th
        positional argument passed in corresponds to the i-th field, up to `len(fields)`.
        If fewer than `len(fields)` arguments are passed in, the remaining fields default
        to `""`. If more than `len(fields)` arguments are passed in, they are ignored.

        Any subsequent keyword arguments overrides the values defined by the positional
        arguments.

        Each prompt can have their own way of stitching together headers and field
        values within examples. Generally, each field should follow its corresponding
        header. The class Prompt does not enforce a specific ordering of the `fields`
        until this method. The default ordering defined here follows the order of `fields`.

        Examples will look like the following:

            {example_separator}
            {field}{value}\n
            {field}{value}\n
            ...
            {example_separator}
            {field}{value}\n
            {field}{value}\n

        Any custom logic should be defined in a subclass method that
        overrides this method.

        Args:
            args: Positional arguments for the new example.
            kwargs: Keyword arguments for the new example.

        Returns:
            str: String representation of an example.
        """
        example = self.create_example(*args, **kwargs)
        assert all(key in self.fields for key in example.keys())
        return f"{self.example_separator}" + "".join(
            f"{self.headers[field]}{example[field]}\n" for field in self.fields
        )

    def to_string(self) -> str:
        """Creates a string representation of the prompt.

        The string representation is assembled from the preamble and examples.
        Each example is created from a `create_example_string` method and is demarcated
        by an `example_separator`.

        Returns:
            str: String representation of the prompt.
        """
        lines = [f"{self.preamble}\n"]
        for example in self.examples:
            lines.append(self.create_example_string(**example))
        return "".join(lines).strip()

    def update(self, config: Dict[str, Any]) -> None:
        """Updates attributes of this class with attributes from `config`.

        Args:
            config (Dict[str, Any]): Dictionary of attributes that should be updated for this class.
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

    def _validate_preamble(self) -> None:
        """Validates that the preamble meets the following requirements:

        - At least `MIN_PREAMBLE_LENGTH` in length.

        Raises:
            ValueError: If the length of the preamble is less than `MIN_PREAMBLE_LENGTH`.
        """
        if len(self.preamble) < self.MIN_PREAMBLE_LENGTH:
            raise ValueError(
                f"Preamble must be at least {self.MIN_PREAMBLE_LENGTH} characters."
            )

    def _validate_fields(self) -> None:
        """Validates that `fields` meets the following requirements:

        - Contains all fields in `REQUIRED_FIELDS`.

        Raises:
            ValueError: If any field in `REQUIRED_FIELDS` is missing from the prompt's
                fields.
        """
        if any(field not in self.fields for field in self.REQUIRED_FIELDS):
            raise ValueError(
                f"Missing required field.\nPrompt's fields: {self.fields}.\nRequired: {self.REQUIRED_FIELDS}."
            )

    def _validate_example_separator(self) -> None:
        """Validates that the `example_separator` meets the following requirements:

        - Is a str.

        Raises:
            TypeError: If the `example_separator` is not a `str`.
        """
        if not isinstance(self.example_separator, str):
            raise ValueError(
                f"example_separator must be a string. Current type: {type(self.example_separator)}"
            )

    def _validate_headers(self) -> None:
        """Validates that the `headers` meet the following requirements:

        - All fields have a corresponding header in `headers`.

        Raises:
            ValueError: If any field is missing from `headers`.
        """
        if any(field not in self.headers for field in self.fields):
            raise ValueError(
                f"All fields must have a corresponding header.\nHeaders: {self.headers}\nFields: {self.fields}"
            )

    def _validate_examples(self) -> None:
        """Validates that the `examples` meet the following requirements:

        - All fields are used in every example of `examples`.
        - At least `MIN_NUM_EXAMPLES` examples are given.

        Raises:
            ValueError: If any of the above requirements is not met.
        """
        # All fields are used in every example of `examples`.
        for example in self.examples:
            if any(field not in example for field in self.fields):
                raise ValueError(
                    f"All fields must be used in each example.\nExample: {example}\nFields found: {example.keys()}"
                )

        # At least `MIN_NUM_EXAMPLES` examples are given.
        if len(self.examples) < self.MIN_NUM_EXAMPLES:
            raise ValueError(
                f"At least {self.MIN_NUM_EXAMPLES} example must be given for {self.__class__.__name__}"
            )
