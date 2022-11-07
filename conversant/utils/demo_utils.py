# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.

import codecs
import os
import pickle
import sys
from typing import Type

import cohere
from streamlit.web import cli as stcli

import conversant
from conversant.chatbot import Chatbot


def encode_chatbot(chatbot: Type[Chatbot]) -> str:
    """Serialize and encode a Chatbot object to a base-64 string encoding.

    Args:
        chatbot (object): a chatbot of class inherited from Chatbot

    Returns:
        str: Chatbot object as a base-64 string
    """
    chatbot.co = None
    return codecs.encode(pickle.dumps(chatbot), "base64").decode()


def decode_chatbot(chatbot_string: str, client: cohere.Client) -> Type[Chatbot]:
    """Decode and deserialize a Chatbot object.

    Args:
        obj_string (str): a base-64 string encoding

    Returns:
        Type[Chatbot]: a chatbot of class inherited rom Chatbot
    """
    chatbot = pickle.loads(codecs.decode(chatbot_string.encode(), "base64"))
    chatbot.co = client
    return chatbot


def launch_streamlit(chatbot: Type[Chatbot]) -> None:
    """Launches a demo of a chatbot using Streamlit.

    The bot will be a persona available for chatting using the interface
    defined in conversant/demo/streamlit_example.py.

    Args:
        bot (Type[Chatbot]): a chatbot of class inherited from Chatbot
    """
    path = os.path.dirname(conversant.__file__)
    sys.argv = f"streamlit run {path}/demo/streamlit_example.py --".split(" ")
    sys.argv.append(encode_chatbot(chatbot))
    sys.exit(stcli.main())
