"""
Basic tests for discord_self package.
"""

import pytest


def test_import():
    """Test that discord_self can be imported."""
    try:
        import discord_self

        assert hasattr(discord_self, "__version__")
    except ImportError:
        pytest.skip("discord_self not yet vendorized")


def test_discord_compatibility():
    """Test that basic discord.py-self functionality works."""
    try:
        import discord_self as discord

        # Test basic classes exist
        assert hasattr(discord, "Client")

        # Test can instantiate (without connecting)
        client = discord.Client()
        assert client is not None

    except ImportError:
        pytest.skip("discord_self not yet vendorized")


def test_namespace_isolation():
    """Test that discord_self doesn't conflict with regular discord.py."""
    try:
        # This should work even if regular discord.py is installed
        import discord_self

        # Try importing regular discord (if available)
        try:
            import discord as regular_discord

            # They should be different modules
            assert discord_self.__file__ != regular_discord.__file__
        except ImportError:
            # Regular discord.py not installed, which is fine
            pass

    except ImportError:
        pytest.skip("discord_self not yet vendorized")
