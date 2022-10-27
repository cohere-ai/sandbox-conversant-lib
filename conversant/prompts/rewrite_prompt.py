# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.


from dataclasses import field
from typing import List

from pydantic.dataclasses import dataclass

from conversant.prompts.prompt import Prompt


@dataclass
class RewritePrompt(Prompt):
    """A rewrite prompt given to a Chatbot.

    Required fields:
        conversation: The possibly ungrounded message to be rewritten.
        fact: A reference paragraph containing a fact to ground the message.
        rewrite: A rewritten grounded message based on the reference fact.

    Constants;
        REQUIRED_FIELDS (List[str]): The list of required fields for the prompt. (default: `["conversation", "rewrite", "fact"]`)
        MIN_PREAMBLE_LENGTH (int): The minimum length of the preamble. (default: `10`)
        MIN_NUM_EXAMPLES (int): The minimum number of examples that should be passed in. (default: `1`)
    """

    REQUIRED_FIELDS: List[str] = field(
        default_factory=lambda: ["conversation", "rewrite", "fact"]
    )
    MIN_PREAMBLE_LENGTH: int = 10
    MIN_NUM_EXAMPLES: int = 1

    def __post_init__(self) -> None:
        """Validators for the rewrite prompt.

        Validates that the prompt follows the requirements of the validators listed below.
        Minimally, the RewritePrompt needs to follow the requirements of its parent class.
        """
        super().__post_init__()

    def create_example_string(self, *args, **kwargs) -> str:
        """Creates a string representation of a grounded rewriting example from positional
        and keyword arguments.

        Examples should look like the following:

            {example_seprator}
            {conversation_header}\n
            {conversation}\n
            {fact_header}\n
            {fact}\n
            {rewrite_header}\n
            {rewrite}\n
            {example_seprator}
            {convesation_header}\n
            {conversation}\n
            {fact_header}\n
            {fact}\n
            {rewrite_header}\n
            {rewrite}

        Args:
            args: Positional arguments for the new example.
            kwargs: Keyword arguments for the new example.

        Returns:
            str: String representation of an example.
        """
        example = self.create_example(*args, **kwargs) if len(args) > 0 else kwargs
        return f"{self.example_separator}" + "".join(
            f"{self.headers[field]}\n{example[field]}\n" for field in example.keys()
        )
