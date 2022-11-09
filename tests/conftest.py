# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.

import json
import os
from typing import Any, Dict, Optional

import cohere
import pytest
from cohere.embeddings import Embeddings
from cohere.generation import Generations
from cohere.tokenize import Tokens

from conversant.prompt_chatbot import PERSONA_MODEL_DIRECTORY, PromptChatbot
from conversant.prompts.chat_prompt import ChatPrompt
from conversant.prompts.prompt import Prompt
from conversant.prompts.rewrite_prompt import RewritePrompt
from conversant.search.document import Document
from conversant.search.local_searcher import LocalSearcher
from conversant.search.searcher import Searcher


class MockCo:
    def generate(*args, **kwargs) -> Generations:
        return Generations(
            response={"generations": [dict(text="Hello!", likelihood=1.0)]},
            return_likelihoods="NONE",
        )

    def embed(*args, **kwargs) -> Embeddings:
        if "texts" in kwargs:
            embeddings = [[1.0, 1.0]] * len(kwargs["texts"])
            return Embeddings(embeddings=embeddings)

        return Embeddings(embeddings=[[1.0, 1.0]])

    def tokenize(*args, **kwargs) -> Tokens:
        token_strings = args[1].split()
        tokens = [x for x in range(len(token_strings))]

        return Tokens(tokens, token_strings)


@pytest.fixture
def mock_co() -> object:
    """Mock of Cohere client.

    Returns:
        object: A simple mock of Cohere's API client.
    """
    return MockCo()


@pytest.fixture
def mock_prompt_config() -> Dict[str, Any]:
    """A Prompt config fixture for tests.

    Returns:
        Dict[str, Any]: Dictionary that can be used to construct to instantiate a
            Prompt.
    """
    return {
        "preamble": "This is a prompt.",
        "example_separator": "<example>\n",
        "headers": {
            "query": "<query>",
            "context": "<context>",
            "generation": "<generation>",
        },
        "examples": [
            {
                "query": "This is a query.",
                "context": "This is a context.",
                "generation": "This is a generation.",
            },
            {
                "query": "This is a second query.",
                "context": "This is a second context.",
                "generation": "This is a second generation.",
            },
        ],
        "REQUIRED_KEYS": ["query", "context", "generation"],
    }


@pytest.fixture
def mock_prompt(mock_prompt_config: Dict[str, Any]) -> Prompt:
    """Instantiates a Prompt fixture for tests.

    Args:
        mock_prompt_config (Dict[str, Any]): A config used to instantiate a Prompt
            fixture.

    Returns:
        Prompt: A mock Prompt object fixture for tests.
    """
    return Prompt(**mock_prompt_config)


@pytest.fixture
def mock_chat_prompt_config() -> Dict[str, Any]:
    """A ChatPrompt config fixture for tests.

    Returns:
        Dict[str, Any]: Dictionary that can be used to construct to instantiate a
            ChatPrompt.
    """
    return {
        "preamble": "This is a chat prompt.",
        "example_separator": "\n",
        "headers": {"user": "User", "bot": "Mock Chatbot"},
        "examples": [
            [
                {"user": "This is a user utterance", "bot": "This is a bot utterance"},
                {
                    "user": "This is second user utterance",
                    "bot": "This is second bot utterance",
                },
            ],
            [
                {
                    "user": "This is a user utterance in the second example.",
                    "bot": "This is a bot utterance in the second example.",
                },
                {
                    "user": "This is second user utterance in the second example.",
                    "bot": "This is second bot utterance in the second example.",
                },
            ],
        ],
    }


@pytest.fixture
def mock_chat_prompt(mock_chat_prompt_config: Dict[str, Any]) -> ChatPrompt:
    """A ChatPrompt config fixture for tests.

    Args:
        mock_chat_prompt_config (Dict[str, Any]): A config used to instantiate a
            ChatPrompt fixture.

    Returns:
        ChatPrompt: A mock ChatPrompt object fixture for tests.
    """
    return ChatPrompt(**mock_chat_prompt_config)


@pytest.fixture
def mock_rewrite_prompt_config() -> Dict[str, Any]:
    """A RewritePrompt config fixture for tests.

    Returns:
        Dict[str, Any]: Dictionary that can be used to construct to instantiate a
            RewritePrompt.
    """
    return {
        "preamble": "This is a rewrite prompt.",
        "example_separator": "\n",
        "headers": {
            "conversation": "<<CONVERSATION>>",
            "fact": "<<FACTUAL_PARAGRAPH>>",
            "rewrite": "<<REWRITE BASED ON THE ABOVE>>",
        },
        "examples": [
            {
                "conversation": "This is a wrong message.",
                "fact": "This is a fact.",
                "rewrite": "This is a message based on fact.",
            },
            {
                "conversation": "This is a second wrong message.",
                "fact": "This is a second fact.",
                "rewrite": "This is a second message based on fact.",
            },
        ],
    }


@pytest.fixture
def mock_rewrite_prompt(mock_rewrite_prompt_config: Dict[str, Any]) -> RewritePrompt:
    """A RewritePrompt config fixture for tests.

    Args:
        mock_rewrite_prompt_config (Dict[str, Any]): A config used to instantiate a
            RewritePrompt fixture.

    Returns:
        RewritePrompt: A mock RewritePrompt fixture for tests.
    """
    return RewritePrompt(**mock_rewrite_prompt_config)


@pytest.fixture
def mock_prompt_chatbot(mock_co: object, mock_chat_prompt: ChatPrompt) -> PromptChatbot:
    """Instantiates a single bot fixture for tests.

    Args:
        mock_co (object): A mock Cohere client.
        mock_chat_prompt (ChatPrompt): A mock ChatPrompt.

    Returns:
        PromptChatbot: A simple mock of a chatbot that works through prompts.
    """
    return PromptChatbot(
        client=mock_co,
        prompt=mock_chat_prompt,
    )


@pytest.fixture
def mock_persona() -> Dict[str, Any]:
    """Instantiates a persona dict fixture for tests.

    Returns:
        Dict[str, Any]: A mock dictionary used to initialize a PromptChatbot.
    """
    persona_name = "watch-sales-agent"
    persona_path = os.path.join(PERSONA_MODEL_DIRECTORY, persona_name, "config.json")
    with open(persona_path) as f:
        persona = json.load(f)
    return persona


@pytest.fixture()
def mock_searcher(mock_co: cohere.Client) -> Searcher:
    """Mock fixture subclass to test abstract class methods.

    Args:
        mock_co (cohere.Client): Cohere API client.

    Returns:
        Searcher: Mock Searcher object.
    """

    class MockSearcher(Searcher):
        def search(self, query: str) -> Optional[Document]:
            return super().search(query)

    return MockSearcher(
        client=mock_co,
        documents=[
            Document(
                source_link="http://url",
                doc_id="123",
                content="test content",
            )
        ],
    )


@pytest.fixture()
def mock_local_searcher(mock_co: cohere.Client) -> LocalSearcher:
    """Mock fixture subclass to test class methods.

    Args:
        mock_co (cohere.Client): Cohere API client.

    Returns:
        LocalSearcher: Mock Searcher object.
    """

    return LocalSearcher(
        client=mock_co,
        documents=[
            Document(
                source_link="http://url",
                doc_id="123",
                content="test content",
                embedding=[1.0, -1.0],
            ),
            Document(
                source_link="http://url",
                doc_id="123",
                content="test content",
                embedding=[1.0, 1.0],
            ),
        ],
    )
