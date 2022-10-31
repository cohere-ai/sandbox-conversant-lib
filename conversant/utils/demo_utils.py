# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.

import codecs
import pickle
import sys
from typing import Type

from streamlit.web import cli as stcli

from conversant.chatbot import Chatbot


def encode_object(obj: object) -> str:
    """Serialize and encode an object to a base-64 string encoding.

    Args:
        obj (object): a Python object
    """
    return codecs.encode(pickle.dumps(obj), "base64").decode()


def decode_object(obj_string: str) -> object:
    """Decode and deserialize an object,

    Args:
        obj_string: a base-64 string encoding
    """
    return pickle.loads(codecs.decode(obj_string.encode(), "base64"))


def launch_streamlit(bot: Type[Chatbot]) -> None:
    """Launches a demo of a chatbot using Streamlit.

    The bot will be a persona available for chatting using the interface
    defined in app/streamlit_example.py.

    Args:
        bot (Type[Chatbot]): a chatbot of class inherited from Chatbot
    """
    sys.argv = "streamlit run app/streamlit_example.py --".split(" ")
    sys.argv.append(encode_object(bot))
    sys.exit(stcli.main())
