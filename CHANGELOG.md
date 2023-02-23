# Changelog
## 0.2.3 (2023-02-23)

### Added
- N/A
### Changed
- Updated streamlit to 1.18.1.
- Fixed a bug that was causing the last utterance to be repeated in the Streamlit demo.

### Removed
- N/A

## 0.2.2 (2023-02-17)

### Added
- Simulated token streaming support for Streamlit demo app
- Method in `PromptChatbot` to chain `co.generate` calls (`partial_reply`) for one response

### Changed
- N/A

### Removed
- N/A

## 0.2.1 (2023-01-20)

### Added
- N/A

### Changed
- Fixed a bug in Streamlit demo by casting `max_tokens` to `int`

### Removed
- N/A

## 0.2.0 (2023-01-20)

### Added
- N/A

### Changed
- Update dependency on `cohere` to `^3.0`

### Removed
- N/A

## 0.1.7 (2023-01-16)

### Added
- N/A

### Changed
- Changed `client_config` form in Streamlit demo to allow any number of `max_tokens`

### Removed
- N/A

## 0.1.6 (2023-01-13)

### Added
- N/A

### Changed
- Fixed `PromptChatbot.to_dict()`. Previously, this threw an error as the Cohere client cannot be pickled.
- Fixed Streamlit demo to save stop sequences correctly when swapping personas.

### Removed
- N/A

## 0.1.5 (2023-01-10)

### Added
- N/A

### Changed
- Bug fix of twemoji MaxCDN outage

### Removed
- N/A

## 0.1.4 (2022-12-16)

### Added
- N/A

### Changed
- Converted relative links in README to absolute links for PyPI compatibility
- Bug fix related to custom persona injection in streamlit

### Removed
- N/A

## 0.1.3 (2022-12-02)

### Added
- N/A

### Changed
- Updated README content to clarify secrets management
- Streamline custom persona injection in streamlit

### Removed
- N/A

## 0.1.2 (2022-11-14)

### Added
- Added Streamlit demo app to `conversant`

### Changed
- Updated README content
- Updated default persona directory 

### Removed
- N/A

## 0.1.1 (2022-11-02)

### Added
- Added metadata for PyPI homepage
- Updated README content
- Updated `__init__.py` files for cleaner imports

### Changed
- N/A

### Removed
- N/A
## 0.1.0 (2022-11-02)

### Added
- Initial release of repo
- Streamlit demo alongside repo
- Upload to PyPI

### Changed
- N/A

### Removed
- N/A