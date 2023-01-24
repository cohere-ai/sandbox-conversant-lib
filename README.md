```
################################################################################
#    ____      _                     ____                  _ _                 #
#   / ___|___ | |__   ___ _ __ ___  / ___|  __ _ _ __   __| | |__   _____  __  #
#  | |   / _ \| '_ \ / _ \ '__/ _ \ \___ \ / _` | '_ \ / _` | '_ \ / _ \ \/ /  #
#  | |__| (_) | | | |  __/ | |  __/  ___) | (_| | | | | (_| | |_) | (_) >  <   #
#   \____\___/|_| |_|\___|_|  \___| |____/ \__,_|_| |_|\__,_|_.__/ \___/_/\_\  #
#                                                                              #
# This project is part of Cohere Sandbox, Cohere's Experimental Open Source    #
# offering. This project provides a library, tooling, or demo making use of    #
# the Cohere Platform. You should expect (self-)documented, high quality code  #
# but be warned that this is EXPERIMENTAL. Therefore, also expect rough edges, #
# non-backwards compatible changes, or potential changes in functionality as   #
# the library, tool, or demo evolves. Please consider referencing a specific   #
# git commit or version if depending upon the project in any mission-critical  #
# code as part of your own projects.                                           #
#                                                                              #
# Please don't hesitate to raise issues or submit pull requests, and thanks    #
# for checking out this project!                                               #
#                                                                              #
################################################################################
```

**Maintainer:** [Cohere ConvAI Team](mailto:convai@cohere.com) \
**Project maintained until at least (YYYY-MM-DD):** 2023-03-01

# Conversant
[![tests](https://github.com/cohere-ai/sandbox-conversant-lib/actions/workflows/run_tests.yaml/badge.svg)](https://github.com/cohere-ai/sandbox-conversant-lib/actions/workflows/run_tests.yaml/badge.svg)
[![PyPI](https://img.shields.io/pypi/v/conversant.svg)](https://img.shields.io/pypi/v/conversant.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

Build conversational AI on top of [Cohere](https://cohere.ai/)'s [large language models](https://docs.cohere.ai/generate-reference/)
- 🗣 Use large language models quickly with Cohere's [API](https://docs.cohere.ai/api-reference/)
- 😃 Customize personas
- 💁 Leave management of chat history up to `conversant`
- 🪨 Ground conversations in your provided facts (soon!)
- 🐍 Install `conversant` with pip

`conversant` is a work-in-progress framework for building customizable dialogue agents (aka chatbots) that can answer questions and converse with users with a variety of different chatbot personas. `conversant` aims
to be modular, flexible and extensible so you can create any kind of chatbots you want!

We provide several custom personas for you, including 🧑‍💼 a client support agent, ⌚️ a watch sales agent, 🧑‍🏫 a math teacher, and 🧙 a fantasy wizard. Create your own persona with just a description and some example conversations!

Read more about how `conversant` is part of the Cohere Sandbox on our [launch blog post](https://txt.cohere.ai/introducing-sandbox-coheres-experimental-open-source-initiative/).

Try `conversant` on our Streamlit demo [here](https://conversant.streamlit.app/)! 🎉

## Table of Contents
1. [Installation and Usage](#installation-and-usage)
   1. [Installation](#installation)
   2. [Streamlit Demo](#streamlit-demo)
   3. [Running Your Own Streamlit Demo](#running-your-own-streamlit-demo)
   4. [Creating a Custom Persona](#creating-a-custom-persona)
   5. [Editing a Persona on the Demo](#editing-a-persona-on-the-demo)
   6. [Usage](#usage)
2. [How Conversant Works](#how-conversant-works)
3. [Documentation](#documentation)
4. [Get Support](#get-support)
5. [Contributing Guidelines](#contributing-guidelines)
6. [License](#license)

## Installation and Usage

### Installation

`conversant` is available [on PyPI](https://pypi.org/project/conversant/), and is tested on Python 3.8+ and [Cohere](https://pypi.org/project/cohere/) 2.8.0+.
```
pip install conversant
```
### Streamlit Demo

Want to see it in action first? You can use `conversant` on a [Streamlit](https://docs.streamlit.io/) app without installing anything [here](https://conversant.streamlit.app/)! 🎉

<p float="none">
  <img src="https://github.com/cohere-ai/sandbox-conversant-lib/raw/main/static/fortune-teller-setup.png" alt="Screenshot showing the available personas on the Streamlit demo, with the Fortune Teller persona selected by default.." height="550"/>
  <img src="https://github.com/cohere-ai/sandbox-conversant-lib/raw/main/static/fortune-teller-chat.png" alt="Screenshot showing an exchange between a Fortune Teller chatbot and a user." height="550"/>
</p>

### Running Your Own Streamlit Demo

Cohere uses Streamlit to create its demo applications. If you’re new to Streamlit, you can install it [here](https://docs.streamlit.io/library/get-started/installation) and read more about running Streamlit commands [here](https://docs.streamlit.io/library/get-started/main-concepts).

If you would like to modify this Streamlit demo locally, we strongly recommend forking this repository rather than installing it as a library from PyPI.

If you'd like to spin up your own instance of the Streamlit demo, you will first need a `COHERE_API_KEY`. 
You can generate one by visiting [dashboard.cohere.ai](https://dashboard.cohere.ai/welcome/register?utm_source=github&utm_medium=content&utm_campaign=sandbox&utm_content=conversant). 

#### Local Streamlit apps
If you plan to run the Streamlit app locally, you can add the key to `.streamlit/secrets.toml`:
```
COHERE_API_KEY = "YOUR_API_KEY_HERE"
```

When running locally, Streamlit will read the `secrets.toml` file and silently inject these values into the environment variables. Alternatively, you may directly set the API key as an environment variable by running the following command from the command line:
```
export COHERE_API_KEY = "YOUR_API_KEY_HERE"
```

Start the Streamlit app from the command line with the following command:
```
streamlit run conversant/demo/streamlit_example.py
```

#### Hosted Streamlit apps
If instead you would like to create a hosted Streamlit app, add your Cohere API key to Streamlit via [Secrets Management](https://docs.streamlit.io/streamlit-cloud/get-started/deploy-an-app/connect-to-data-sources/secrets-management). Add the following line as a Secret:
```
COHERE_API_KEY = "YOUR_API_KEY_HERE"
```

### Creating a Custom Persona
Once you have your own instance of the Streamlit app, you can begin experimenting with creating custom personas! Check out the `config.json` for each persona in [`conversant/personas`](https://github.com/cohere-ai/sandbox-conversant-lib/tree/main/conversant/personas) directory. You'll need to create a subfolder within this directory that corresponds to your new persona and add a `config.json` file. 

As a note, we strongly recommend forking the `sandbox-conversant-lib` repository rather than installing it as a library from PyPI. When you create a new persona, use the `personas` directory in the cloned repository. The directory structure should look like this:

```
conversant/personas
├── fortune-teller
│   └── config.json
└── your-persona-name # new
    └── config.json
```

The config file should contain the following:
- `chatbot_config`: 
  -  `max_context_examples`: The length of the chat history for the chatbot to use in reply.
  -  `avatar`: Optional emoji shortcode or URL to image as the chatbot's avatar. Defaults to 🤖.
-  `client_config`: Parameters for [`co.generate()`](https://docs.cohere.ai/generate-reference)
-  `chat_prompt_config`: 
   - `preamble`: Description of the persona.
   - `example_separator`: A string that separates each example conversation.
   - `headers`: A name for the `bot` and the `user`.
   - `examples`: A few conversation examples (few-shot), or empty (zero-shot).

`conversant` will take care of the rest! As an example, check out [`fortune-teller/config.json`](https://github.com/cohere-ai/sandbox-conversant-lib/blob/main/conversant/personas/fortune-teller/config.json). When you launch the Streamlit app, the new persona will appear in the drop down menu.

#### Running the app with a subset of custom personas

If you would like to run the app with a subset of custom personas, it's possible to create a new directory that contains only the desired ones. This is analogous to the `conversant/personas` directory, and needs to have the same structure:
```
custom-personas
├── your-first-persona
│   └── config.json
└── your-second-persona
    └── config.json
```  

After creating this directory, you'll need to tell the app where to look for it. In the demo Streamlit app (`streamlit_example.py`), one of the 
first lines reads `CUSTOM_PERSONA_DIRECTORY = None`. Change this to specify the desired 
persona directory, e.g. `CUSTOM_PERSONA_DIRECTORY = "/Users/yourname/custom-personas"`.

If this is unchanged, the app will default to using the directory that contains the 
`conversant` demo personas.

#### Troubleshooting missing personas

If you do not see the new persona in the drop down menu, you may need to specify a 
custom persona directory. Follow [the instructions above](#running-the-app-with-a-subset-of-custom-personas) to tell the app where to look for the personas.

### Editing a Persona on the Demo
You can also edit a persona on the Streamlit app!
<img src="https://github.com/cohere-ai/sandbox-conversant-lib/raw/main/static/fortune-teller-edit.png" alt="Screenshot showing the interface for editing a persona on the Streamlit app."/>

### Usage

With `conversant`, you can create a chatbot powered by [Cohere](https://cohere.ai/)'s large language models with just the following code snippet.
```python
import cohere
import conversant

co = cohere.Client("YOUR_API_KEY_HERE")
bot = conversant.PromptChatbot.from_persona("fantasy-wizard", client=co)
print(bot.reply("Hello!"))
>>> "Well met, fair traveller. What bringest thou to mine village?"
```

You can also define your own persona by passing in your own `ChatPrompt`. 
```python
from conversant.prompts import ChatPrompt

shakespeare_config = {
    "preamble": "Below is a conversation between Shakespeare and a Literature Student.",
    "example_separator": "<CONVERSATION>\n",
    "headers": {
        "user": "Literature Student",
        "bot": "William Shakespeare",
    },
    "examples": [
        [
            {
                "user": "Who are you?",
                "bot": "Mine own nameth is Shakespeare, and I speaketh in riddles.",
            },
        ]
    ],
}
shakespeare_bot = conversant.PromptChatbot(
    client=co, prompt=ChatPrompt.from_dict(shakespeare_config)
)
print(shakespeare_bot.reply("Hello!"))
>>> "Greeteth, and welcome. I am Shakespeare, the great poet, dramatist, and playwright."
```

<!-- From here, it's also possible to talk to your chatbot using the [Streamlit](https://docs.streamlit.io/) app! This will launch the demo with your chatbot persona pre-selected. For this to work, `COHERE_API_KEY` needs to be set as an environment variable.
```python
from conversant.utils import demo_utils
demo_utils.launch_streamlit(shakespeare_bot)
``` -->
## How Conversant Works
`conversant` uses prompt completion to define a chatbot persona with a description and a few examples. The prompt is sent as input to Cohere's [`co.generate()`](https://docs.cohere.ai/generate-reference/) endpoint for an autoregressive language model to generate text in a few-shot manner from the examples and the current dialogue context. 

Each user message and chatbot response is appended to a chat history so that future responses are conditioned on the dialogue context at that point in time.

In the future, we plan to add functionality for a chatbot to be factually grounded using text that is retrieved from a local document cache.

For more information, refer to [this section in `CONTRIBUTORS.md`](https://github.com/cohere-ai/sandbox-conversant-lib/blob/main/CONTRIBUTORS.md#conversant-schematic).

## Documentation
Full documentation can be found [here](https://cohere-ai.github.io/sandbox-conversant-lib/).

## Get Support

If you have any questions or comments, please file an issue or reach out to us on [Discord](https://discord.gg/co-mmunity).

## Contributing Guidelines
If you would like to contribute to this project, please read [`CONTRIBUTORS.md`](https://github.com/cohere-ai/sandbox-conversant-lib/blob/main/CONTRIBUTORS.md)
in this repository, and sign the Contributor License Agreement before submitting
any pull requests. A link to sign the Cohere CLA will be generated the first time 
you make a pull request to a Cohere repository.

In addition to guidelines around submitting code to this repository, [`CONTRIBUTORS.md`](https://github.com/cohere-ai/sandbox-conversant-lib/blob/main/CONTRIBUTORS.md) contains a walkthrough to help developers get started, as well as schematics that explain how `conversant` works under the hood. :wrench:

## License
`conversant` has an [MIT License](https://github.com/cohere-ai/sandbox-conversant-lib/blob/main/LICENSE).
