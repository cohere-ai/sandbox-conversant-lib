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

    Required keys:
        conversation: The possibly ungrounded message to be rewritten.
        fact: A reference paragraph containing a fact to ground the message.
        rewrite: A rewritten grounded message based on the reference fact.

    Constants;
        REQUIRED_KEYS (List[str]): The list of required keys for the prompt. (default:
            `["conversation", "rewrite", "fact"]`)
        MIN_PREAMBLE_LENGTH (int): The minimum length of the preamble. (default: `10`)
        MIN_NUM_EXAMPLES (int): The minimum number of examples that should be passed in.
            (default: `1`)
    """

    REQUIRED_KEYS: List[str] = field(
        default_factory=lambda: ["conversation", "rewrite", "fact"]
    )
    MIN_PREAMBLE_LENGTH: int = 10
    MIN_NUM_EXAMPLES: int = 1

    def __post_init__(self) -> None:
        """Validators for the rewrite prompt.

        Validates that the prompt follows the requirements of the validators listed
        below. Minimally, the RewritePrompt needs to follow the requirements of its
        parent class.
        """
        super().__post_init__()

    def create_interaction_string(self, *args, **kwargs) -> str:
        """Creates a string representation of a grounded rewriting interaction.

        Interactions will look like the following:

            {conversation_header}\n
            {conversation}\n
            {fact_header}\n
            {fact}\n
            {rewrite_header}\n
            {rewrite}\n

        Args:
            args: Positional arguments for the new interaction.
            kwargs: Keyword arguments for the new interaction.

        Returns:
            str: String representation of an interaction.
        """
        interaction = self.create_interaction(*args, **kwargs) if args else kwargs
        return "".join(
            f"{self.headers[key]}\n{interaction[key]}\n" for key in interaction.keys()
        )
