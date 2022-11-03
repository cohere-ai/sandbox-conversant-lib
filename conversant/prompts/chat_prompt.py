# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.

import logging
from dataclasses import field
from typing import List, NewType

from pydantic.dataclasses import dataclass

from conversant.chatbot import Interaction
from conversant.prompts.prompt import Prompt

Conversation = NewType("Conversation", List[Interaction])


@dataclass
class ChatPrompt(Prompt):
    """A chat prompt given to a Chatbot.

    The examples in a `ChatPrompt` are a list of `Conversation`s themselves a list of
    `Interaction`s. This is one level of nesting further as compared to those in
    `Prompt`, which are a list of `Interaction`s.

    Required keys:
        user: An entity speaking to the bot.
        bot: The Chatbot itself.

    Constants:
        REQUIRED_KEYS (List[str]): The list of required keys for the chat prompt.
            (default: `["user", "bot"]`)
        MIN_PREAMBLE_LENGTH (int): The minimum length of the preamble. (default: `1`)
        MIN_NUM_EXAMPLES (int): The minimum number of examples that should be passed in.
            (default: `1`)
    """

    examples: List[Conversation]

    REQUIRED_KEYS: List[str] = field(default_factory=lambda: ["user", "bot"])
    MIN_PREAMBLE_LENGTH: int = 10
    MIN_NUM_EXAMPLES: int = 0

    def __post_init__(self) -> None:
        """Validators for the chat prompt.

        Validates that the prompt follows the requirements of the validators listed
        below. Minimally, the ChatPrompt needs to follow the requirements of its parent
        class.
        """
        super()._validate_preamble()
        super()._validate_example_separator()
        super()._validate_headers()
        self._validate_examples()
        self._validate_dialogue()

    @property
    def user_name(self):
        """
        Returns:
            str: The name of the user that interacts with the chatbot who uses this
                ChatPrompt. Typically this should be set to `'User'`.
        """
        return self.headers["user"]

    @property
    def bot_name(self):
        """
        Returns:
            str: The name of the chatbot who uses this ChatPrompt.
        """
        return self.headers["bot"]

    def create_interaction_string(self, *args, **kwargs) -> str:
        """Creates a string representation of an interaction.

        Interactions will look like the following:

            {user_name}: {utterance}\n
            {bot_name}: {utterance}\n

        Note the colon and space separating the speaker name from the respective
        utterance.

        Args:
            args: Positional arguments for the new interaction.
            kwargs: Keyword arguments for the new interaction.

        Returns:
            str: String representation of an interaction.
        """
        interaction = (
            self.create_interaction(*args, **kwargs) if len(args) > 0 else kwargs
        )
        return "".join(
            f"{self.headers[key]}: {interaction[key]}\n" for key in interaction.keys()
        )

    def create_conversation_string(self, conversation: Conversation) -> str:
        """Creates a string represenation of a conversation.

        Conversations will look like the following:

            {user_name}: {utterance}\n
            {bot_name}: {utterance}\n
            {user_name}: {utterance}\n
            {bot_name}: {utterance}\n

        Args:
            conversation (Conversation): List of interactions.
        """
        return "".join(
            self.create_interaction_string(**interaction)
            for interaction in conversation
        )

    def to_string(self) -> str:
        """Creates a string representation of the conversation prompt.

        The string representation is assembled from the preamble and examples.
        Each example is created from a `create_conversation_string` method and is
        demarcated by an `example_separator`.

        Examples will look like the following:

            {example_separator}
            {user_name}: {utterance}\n
            {bot_name}: {utterance}\n
            {user_name}: {utterance}\n
            {bot_name}: {utterance}\n
            {example_separator}
            {user_name}: {utterance}\n
            {bot_name}: {utterance}\n

        Returns:
            str: String representation of the conversation prompt.
        """
        lines = [f"{self.preamble}\n"]
        lines += self.example_separator + f"{self.example_separator}".join(
            self.create_conversation_string(example) for example in self.examples
        )
        return "".join(lines).strip()

    def _validate_examples(self) -> None:
        """Validates that the `examples` meet the following requirements:

        - All fields are used in every example of `examples`.
        - At least `MIN_NUM_EXAMPLES` examples are given.

        Raises:
            ValueError: If any of the above requirements is not met.
        """
        # All fields are used in every interaction in every example of `examples`.
        for example in self.examples:
            for interaction in example:
                if any(key not in interaction for key in self.REQUIRED_KEYS):
                    raise ValueError(
                        "Missing required key.\nInteraction's keys: "
                        f"{interaction.keys()}\nRequired: {self.REQUIRED_KEYS}"
                    )
        # At least `MIN_NUM_EXAMPLES` examples are given.
        if len(self.examples) < self.MIN_NUM_EXAMPLES:
            raise ValueError(
                f"At least {self.MIN_NUM_EXAMPLES} example(s) must be given for"
                f"{self.__class__.__name__}"
            )

    def _validate_dialogue(self) -> None:
        """Validates that the examples conform to a 2-person dialogue.


        There should only be 2 speakers in the examples, and each speaker's utterance
        should not be prefixed with their name.

        Raises:
            ValueError: If the above requirement is not met.
        """
        for example in self.examples:
            # Only 2 speakers should be in each conversation interaction
            if not all([len(interaction) == 2 for interaction in example]):
                raise ValueError(
                    "Conversation interactions must be pairs of utterances."
                )

            # Only check the examples for name-prefixed utterances if there is at least
            # one interaction
            if example:
                user_turns = [interaction["user"] for interaction in example]
                bot_turns = [interaction["bot"] for interaction in example]
                all_turns = user_turns + bot_turns

                colon_prefixed = all(":" in turn for turn in all_turns)
                hyphen_prefixed = all("-" in turn for turn in all_turns)

                if colon_prefixed or hyphen_prefixed:
                    # This might false-positive, so we only log a warning
                    logging.warning(
                        "Did you mistakenly prefix the example dialogue turns with"
                        "user/bot names?"
                    )

                user_prefixed = all(
                    turn.lstrip().startswith(self.user_name) for turn in user_turns
                )

                bot_prefixed = all(
                    turn.lstrip().startswith(self.bot_name) for turn in bot_turns
                )
                if user_prefixed and bot_prefixed:
                    # It's hard to think of any genuine case where all utterances begin
                    # with self-names.
                    raise ValueError(
                        "Conversation interactions should not be prefixed with user/bot"
                        "names!"
                    )
