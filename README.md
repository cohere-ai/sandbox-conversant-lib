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
# conversant
A framework for building conversational agents on top of the [Cohere API](https://docs.cohere.ai/). 

## Installation
`conversant` is tested on Python 3.8+ and Cohere 2.4.2+.

```
pip install conversant
```

We recommend installing `conversant` in a virtual environment.

## Running a Streamlit Demo
The fastest way to see what `conversant` can do for you is to start talking to a chatbot! 
You will first need a `COHERE_API_KEY`. 
You can generate one by visiting [dashboard.cohere.ai](https://dashboard.cohere.ai). 

Add the key to `.streamlit/secrets.toml`:
```
COHERE_API_KEY = "YOUR_KEY_HERE"
```

Start a streamlit demo using `app/streamlit_example.py`:
```
streamlit run app/streamlit_example.py
```

## Contributing Guidelines
If you would like to contribute to this project, please read [`CONTRIBUTORS.md`](CONTRIBUTORS.md)
in this repository, and sign the Contributor License Agreement before submitting
any pull requests. A link to sign the Cohere CLA will be generated the first time 
you make a pull request to a Cohere repository.

## Maintainers
**Maintainer Team:** [Cohere ConvAI Team](mailto:convai@cohere.com) \
**Project maintained until at least (YYYY-MM-DD):** 2023-03-01

## License
`conversant` has an [MIT License](LICENSE).