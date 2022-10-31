# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.

import logging
from dataclasses import field
from typing import List

from pydantic.dataclasses import dataclass

from conversant.prompts.prompt import Prompt


@dataclass
class StartPrompt(Prompt):
    """A start prompt given to a Chatbot.

    Required fields:
        user: An entity speaking to the bot.
        bot: The Chatbot itself.

    Constants:
        REQUIRED_FIELDS (List[str]): The list of required fields for the prompt. (default: `["user", "bot"]`)
        MIN_PREAMBLE_LENGTH (int): The minimum length of the preamble. (default: `1`)
        MIN_NUM_EXAMPLES (int): The minimum number of examples that should be passed in. (default: `1`)
    """

    REQUIRED_FIELDS: List[str] = field(default_factory=lambda: ["user", "bot"])
    MIN_PREAMBLE_LENGTH: int = 10
    MIN_NUM_EXAMPLES: int = 0

    def __post_init__(self) -> None:
        """Validators for the start prompt.

        Validates that the prompt follows the requirements of the validators listed below.
        Minimally, the StartPrompt needs to follow the requirements of its parent class.
        """
        super().__post_init__()
        self._validate_dialogue()

    @property
    def user_name(self):
        """
        Returns:
            str: The name of the user that interacts with the chatbot who uses this
                StartPrompt. Typically this should be set to `'User'`.
        """
        return self.headers["user"]

    @property
    def bot_name(self):
        """
        Returns:
            str: The name of the chatbot who uses this StartPrompt.
        """
        return self.headers["bot"]

    @property
    def stop_sequences(self) -> List[str]:
        """A (partial) list of stop sequences upon which the chatbot will cut off
        generation.

        The chatbot will stop generation when it encounters a newline followed by
        a user or bot's name.

        Returns:
            List[str]: A list of stop sequences corresponding to the headers of the prompt.
        """
        return [f"\n{self.headers[speaker]}:" for speaker in self.headers]

    def create_example_string(self, *args, **kwargs) -> str:
        """Creates a string representation of conversation interaction from positional
        and keyword arguments.

        Examples should look like the following:

            {example_separator}
            {user_name}: {utterance}\n
            {bot_name}: {utterance}\n
            {example_separator}
            {user_name}: {utterance}\n
            {bot_name}: {utterance}\n

        Note the colon and space separating the speaker name from the respective
        utterance.

        Args:
            args: Positional arguments for the new example.
            kwargs: Keyword arguments for the new example.

        Returns:
            str: String representation of an example.
        """
        example = self.create_example(*args, **kwargs) if len(args) > 0 else kwargs
        return f"{self.example_separator}" + "".join(
            f"{self.headers[field]}: {example[field]}\n" for field in example.keys()
        )


    def _validate_dialogue(self) -> None:
        """Validates that the examples conform to a 2-person dialogue.


        There should only be 2 speakers in the examples, and each speaker's utterance
        should not be prefixed with their name.

        Raises:
            ValueError: If the above requirement is not met.
        """
        # Only 2 speakers should be in each conversation interaction
        if not all([len(example) == 2 for example in self.examples]):
            raise ValueError("Conversation interactions must be pairs of utterances.")

        # Only check the examples for name-prefixed utterances if there is at least
        # one example
        if self.examples:
            user_turns = [example["user"] for example in self.examples]
            bot_turns = [example["bot"] for example in self.examples]
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
                raise ValueError(
                    "Conversation interactions should not be prefixed with user/bot names!"
                )
