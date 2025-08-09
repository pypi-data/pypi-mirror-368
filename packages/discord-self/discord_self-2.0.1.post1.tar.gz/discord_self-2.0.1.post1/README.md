# discord_self

A vendorized version of discord.py-self that avoids namespace conflicts with the regular discord.py library.

## Installation

```bash
pip install discord_self
```

## Usage

Simply replace your discord.py-self imports:

```python
# Instead of:
# import discord

# Use:
import discord_self as discord

# The API is identical to discord.py-self
client = discord.Client()
```

## Features

- **Namespace isolation**: No conflicts with regular discord.py
- **Automatic updates**: GitHub Actions keeps the vendored package up-to-date
- **Zero API changes**: Drop-in replacement for discord.py-self

## Development

This package uses automated vendorization to bundle discord.py-self. The vendorization process:

1. Monitors PyPI for new discord.py-self releases
2. Downloads and vendors the package to `_vendor/discord/`
3. Creates wrapper imports in `discord_self/`
4. Automatically creates PRs for updates

### Manual Update

```bash
python scripts/vendorize.py
```

### Testing

```bash
pytest tests/
```

## License

This package follows the same license as discord.py-self. The vendorization scripts are MIT licensed.
