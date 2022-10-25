# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.

from abc import ABC, abstractmethod
from typing import Dict

import cohere


class Chatbot(ABC):
    """Defines bots that reply to users in a 1:1 text conversation"""

    def __init__(self, client: cohere.Client):
        """A Chatbot should be passed a Cohere Client for API calls.

        Args:
            client (cohere.Client): Provides access to Cohere API via the Python SDK
        """

        self.co = client

        # Holds the full, formatted chat history with type of
        # List[Dict[str, str]]. Each dict object represents a
        # conversation turn and has two keys: "speaker_name" and
        # "utterance".
        self.chatlog = []

    @abstractmethod
    def reply(self, query: str) -> Dict[str, str]:
        """Replies to a user given some input and context.

        Args:
            query (str): Most recent message from the user.

        Returns:
            Dict[str, str]: A reply from a Chatbot with "speaker_name" and
            "utterance" keys
        """
