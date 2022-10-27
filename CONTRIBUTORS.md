## High-level Guidelines

Thank you for your interest in contributing to this repository. To help maintain
the quality of the codebase and ensure a quick review of your pull request, you
should:

1. Write clear, clean code and format it in line with the style used in the 
repository.
2. Leave comments, and use docstrings where appropriate.
3. Add unit tests for any new functionality you introduce, if a set of test cases
are already set up in the repository.
4. Use git commit messages to leave an informative trace of what additions and
changes were made.
5. Write an informative high level description of the pull request, changes made,
and the reason for these changes before submitting the pull request.

If you have not signed our Contributor License Agreement, you will be asked to
sign one by our automated system when you submit your first pull request to
a Cohere repository.

## Pro-tips
- Set up a new `git branch` for any additional work and make a PR back to `main`. :)
- Tests should be added using `pytest` alongside feature development. PRs require good test coverage before they are approved.
- Aim to include a single change in each commit. Commit messages should be descriptive and start with action verbs.
- Try to keep PRs as small as possible, ideally with one feature per PR. This makes PRs easier to review and faster to merge. 
- Use the `typing` module to define typing signatures for all functions you define.
- Write Google-style docstrings for all functions created, explaining its description, the arguments, and return value.
- Use expressive and descriptive variable and function names.

## Full Walkthrough

Obtain the `conversant` source code from Github:
```
git clone git@github.com:cohere-ai/sandbox-conversant.git
cd sandbox-conversant
```

We use `conda` as an environment manager, `pip` as the package installer, and `poetry` as a dependency manager. For more information, please read this [guide](https://ealizadeh.com/blog/guide-to-python-env-pkg-dependency-using-conda-poetry). 

Create the `conda` environment:
```
conda create -n conversant python=3.8.10
```

Activate the `conversant` environment:
```
conda activate conversant
```

Install `poetry`:
```
pip install poetry==1.2.0
```

Set `poetry` to use the Python installed in the `conversant` environment:
```
poetry env use $(which python)
```

Install all dependencies specified in `pyproject.toml`, including dev dependencies:
```
poetry install
```

Once the `conversant` poetry environment is setup, each command needs to be prefixed with `poetry run` so it can run in that poetry environment. The following command can be run to spawn a [shell](https://python-poetry.org/docs/cli/#shell) so that commands can be run without this prefix:
```
poetry shell
```

Commands from hereon assume that `poetry shell` has been run. We use git `pre-commit` hooks, such that a commit will fail if any of the checks defined in `.pre-commit-config.yaml` fail. We also use `black` as the formatter, and `pytest` for testing:
```
pre-commit install
black .
pytest
```

Documents can be built using `pdoc` as follows:
```
pdoc conversant -o docs/ --docformat google
```

## `conversant` schematic

### Key components
- *Persona:* Defines a specific chatbot personality, which consists of a bot description and a dialogue sample, as well as a bot name, a user name, a maximum number of context lines
- *Chatlog:* Maintained over time to track the history of the conversation, contains user queries and bot replies
    - *User queries:* Submitted at each turn, and are added to the prompt before passing it into `co.generate()`
    - *Bot replies:* Generated responses from the chatbot

### Conversation stages
*Note: This contains implementation details that are specific to the streamlit app, particularly around how the conversation is initiated in Steps 1-3.*

1. The conversation begins with a call to `co.generate()`. The prompt is constructed from the bot description, example turns, and the user hypothetically saying hello.
    
    ```
    In this chat, a helpful and informative bot answers questions from the user.
    User: Hi
    Bot: Hi, do you have any questions?
    User: Are African swallows migratory?
    Bot: No, African swallows are non-migratory.
    User: Great, that's all I wanted to know. Goodbye!
    Bot: Goodbye!
    User: Hello
    Bot:
    ```
    *This small example shows the structure of the starter prompt passed to co.generate(). The prompt starts with a description of the bot. The six lines that follow represent an example conversation. The penultimate line shows the user hypothetically saying “Hello”. In the last line, the label “Bot:” prompts co.generate() to produce an appropriate greeting to start the conversation.*

2. The generated output is returned to the user, such that the user sees the bot’s response (but not the hypothetical ‘Hello’ that was inserted at the end of the prompt).
3. The response from the bot is added to the chat log (technically, the hypothetical ‘Hello’ is as well, but it is immediately removed).
4. The user replies with a novel query.
5. The bot description, example turns, chat log, and user query are concatenated into a single prompt, and the chat log + user query are truncated based on max context lines.

    ```
    In this chat, a helpful and informative bot answers questions from the user.
    User: Hi
    Bot: Hi, do you have any questions?
    User: Are African swallows migratory?
    Bot: No, African swallows are non-migratory.
    User: Great, that's all I wanted to know. Goodbye!
    Bot: Goodbye!
    Bot: Hello, is there anything you'd like to ask me?
    User: Are coconuts tropical?
    Bot:
    ```
    *An example of a new prompt. Note that the hypothetical ‘Hello’ is no longer in the prompt, but all previous statements from the bot and user are included as part of the chat log.*

6. Prompt is given to `co.generate()` to produce the response from the bot.
7. The user query & response from the bot are added to the chat log.

![A diagram that shows how conversant constructs prompts before they are passed to co.generate() in order to craft a reply from the bot.](images/sandox-conversant%402x.png)

### A note about search & grounded question answering

Given the architecture described above, the chatbots are very likely to hallucinate facts in response to user questions. In some situations (e.g. the fantasy wizard demo) this may be desired behaviour, while in others it may not be. Eventually, we plan to incorporate grounded question answering, in order to ensure the bot’s responses are accurate when appropriate. 

This will involve a database of documents that will be embedded using `co.embed()`. The user query will be likewise embedded, and we will use cosine similarity to find the document that most closely corresponds to the user query. Following this, we will use another call to `co.generate()` for grounded rewriting of the initial bot reply. This section is intentionally left vague, as the implementation of the grounded question answering and search are not yet fully implemented.