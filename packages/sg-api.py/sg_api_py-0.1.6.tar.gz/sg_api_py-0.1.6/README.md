# sg_api.py
An API wrapper for the Squid Game API.

A simple way to extract JSON content from [the Squid Game API](https://github.com/stainlesteel/squid-game-api).

You can either get character content or episode content, and filter out specific key:value pairs.

## Warning

Some JSON files you fetch may have invalid headers leading to an error.
If this occurs, open an issue on the GitHub.

## Usage
```python
import sg_api_py
from sg_api_py import characters, episodes
# This package uses return statements instead of print
print(characters(1, 218, "title"))
# Cho Sang-woo
print(episodes(1, 4, "title"))
# Stick to the Team
```

For more info, read the [documentation.](docs/usage.md)
## Installation
You can easily install via PIP.
```bash
pip install sg_api_py
```
## Other Information

Licensed under the MIT License.
### Credits:

BeautifulSoup: for easy HTML extraction

Squid Game Fandom: for providing information about Squid Game
