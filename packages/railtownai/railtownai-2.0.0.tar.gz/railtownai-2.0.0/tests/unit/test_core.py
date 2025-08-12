#   ---------------------------------------------------------------------------------
#   Copyright (c) Railtown AI. All rights reserved.
#   Licensed under the MIT License. See LICENSE in project root for information.
#   ---------------------------------------------------------------------------------
"""Tests for the core module."""

from __future__ import annotations

import logging

import pytest

from railtownai.config import clear_config, get_api_key
from railtownai.core import get_railtown_handler, init
from railtownai.handler import RailtownHandler


class TestCoreFunctions:
    """Test core functionality."""

    def setup_method(self):
        """Set up test environment."""
        # Clear any existing configuration
        clear_config()

        # Remove any existing Railtown handlers from root logger
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            if isinstance(handler, RailtownHandler):
                root_logger.removeHandler(handler)

    def teardown_method(self):
        """Clean up after each test."""
        # Clear configuration
        clear_config()

        # Remove any Railtown handlers from root logger
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            if isinstance(handler, RailtownHandler):
                root_logger.removeHandler(handler)

    def test_init_function(self):
        """Test the init function."""
        test_token = "test_api_key"

        # Initialize Railtown
        init(test_token)

        # Verify API key was set
        assert get_api_key() == test_token

        # Verify handler was added to root logger
        root_logger = logging.getLogger()
        railtown_handlers = [handler for handler in root_logger.handlers if isinstance(handler, RailtownHandler)]
        assert len(railtown_handlers) == 1

        # Verify handler level is set to INFO
        handler = railtown_handlers[0]
        assert handler.level == logging.INFO

    def test_init_function_replaces_existing_handler(self):
        """Test that init function replaces existing Railtown handlers."""
        test_token1 = "test_api_key_1"
        test_token2 = "test_api_key_2"

        # Initialize with first token
        init(test_token1)

        # Get the first handler
        root_logger = logging.getLogger()
        handlers_before = [handler for handler in root_logger.handlers if isinstance(handler, RailtownHandler)]
        assert len(handlers_before) == 1
        first_handler = handlers_before[0]

        # Initialize with second token
        init(test_token2)

        # Verify API key was updated
        assert get_api_key() == test_token2

        # Verify handler was replaced (should still be only one)
        handlers_after = [handler for handler in root_logger.handlers if isinstance(handler, RailtownHandler)]
        assert len(handlers_after) == 1

        # Verify it's a different handler object
        second_handler = handlers_after[0]
        assert first_handler is not second_handler

    def test_init_function_sets_root_logger_level(self):
        """Test that init function sets root logger level appropriately."""
        # Set root logger to a high level
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.CRITICAL)

        test_token = "test_api_key"
        init(test_token)

        # Should set root logger to INFO if it was higher
        assert root_logger.level == logging.INFO

    def test_init_function_preserves_root_logger_level(self):
        """Test that init function preserves root logger level if already low enough."""
        # Set root logger to DEBUG (lower than INFO)
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)

        test_token = "test_api_key"
        init(test_token)

        # Should preserve the DEBUG level
        assert root_logger.level == logging.DEBUG

    def test_init_function_with_valid_api_key(self):
        """Test init function with a valid API key."""
        # Valid base64 encoded JWT
        valid_key = "eyJ1IjoidGVzdC1ob3N0LmNvbSIsIm8iOiJ0ZXN0LW9yZyIsInAiOiJ0ZXN0LXByb2oiLCJoIjoidGVzdC1zZWNyZXQiLCJlIjoidGVzdC1lbnYifQ=="  # noqa: E501

        init(valid_key)

        # Verify API key was set
        assert get_api_key() == valid_key

        # Verify handler was added
        root_logger = logging.getLogger()
        railtown_handlers = [handler for handler in root_logger.handlers if isinstance(handler, RailtownHandler)]
        assert len(railtown_handlers) == 1

    def test_init_function_with_empty_token(self):
        """Test init function with empty token."""
        init("")

        # Should still set the empty token
        assert get_api_key() == ""

        # Should still add handler (validation happens later)
        root_logger = logging.getLogger()
        railtown_handlers = [handler for handler in root_logger.handlers if isinstance(handler, RailtownHandler)]
        assert len(railtown_handlers) == 1

    def test_init_function_multiple_calls(self):
        """Test multiple calls to init function."""
        test_token1 = "test_api_key_1"
        test_token2 = "test_api_key_2"
        test_token3 = "test_api_key_3"

        # Multiple init calls
        init(test_token1)
        init(test_token2)
        init(test_token3)

        # Should use the last token
        assert get_api_key() == test_token3

        # Should have only one handler
        root_logger = logging.getLogger()
        railtown_handlers = [handler for handler in root_logger.handlers if isinstance(handler, RailtownHandler)]
        assert len(railtown_handlers) == 1

    def test_get_railtown_handler_with_handler_present(self):
        """Test get_railtown_handler when a RailtownHandler is present."""
        # Initialize Railtown to add a handler
        test_token = "test_api_key"
        init(test_token)

        # Get the handler using our helper function
        handler = get_railtown_handler()

        # Should return a RailtownHandler instance
        assert handler is not None
        assert isinstance(handler, RailtownHandler)
        assert handler.level == logging.INFO

    def test_get_railtown_handler_without_handler(self):
        """Test get_railtown_handler when no RailtownHandler is present."""
        # Ensure no Railtown handlers exist
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            if isinstance(handler, RailtownHandler):
                root_logger.removeHandler(handler)

        # Get the handler using our helper function
        handler = get_railtown_handler()

        # Should return None when no handler is present
        assert handler is None

    def test_get_railtown_handler_with_multiple_handlers(self):
        """Test get_railtown_handler when multiple handlers exist but only one is RailtownHandler."""
        # Add a non-Railtown handler first
        root_logger = logging.getLogger()
        console_handler = logging.StreamHandler()
        root_logger.addHandler(console_handler)

        # Initialize Railtown to add a RailtownHandler
        test_token = "test_api_key"
        init(test_token)

        # Get the handler using our helper function
        handler = get_railtown_handler()

        # Should return the RailtownHandler instance
        assert handler is not None
        assert isinstance(handler, RailtownHandler)

        # Verify other handlers are still present
        all_handlers = root_logger.handlers
        assert len(all_handlers) >= 2  # At least console handler + railtown handler

        # Clean up
        root_logger.removeHandler(console_handler)

    def test_get_railtown_handler_returns_first_handler(self):
        """Test that get_railtown_handler returns the first RailtownHandler found."""
        # Initialize Railtown to add a handler
        test_token = "test_api_key"
        init(test_token)

        # Get the handler using our helper function
        handler = get_railtown_handler()

        # Should return the same handler that was added by init
        root_logger = logging.getLogger()
        railtown_handlers = [h for h in root_logger.handlers if isinstance(h, RailtownHandler)]
        assert len(railtown_handlers) == 1
        assert handler is railtown_handlers[0]

    def test_get_railtown_handler_after_handler_removal(self):
        """Test get_railtown_handler after the handler has been removed."""
        # Initialize Railtown to add a handler
        test_token = "test_api_key"
        init(test_token)

        # Verify handler is present
        handler = get_railtown_handler()
        assert handler is not None

        # Remove the handler manually
        root_logger = logging.getLogger()
        root_logger.removeHandler(handler)

        # Verify handler is no longer found
        handler_after_removal = get_railtown_handler()
        assert handler_after_removal is None

    def test_get_railtown_handler_after_reinitialization(self):
        """Test get_railtown_handler after reinitializing with a new token."""
        # Initialize with first token
        test_token1 = "test_api_key_1"
        init(test_token1)

        # Get the first handler
        handler1 = get_railtown_handler()
        assert handler1 is not None

        # Initialize with second token (should replace handler)
        test_token2 = "test_api_key_2"
        init(test_token2)

        # Get the new handler
        handler2 = get_railtown_handler()
        assert handler2 is not None

        # Should be different handler objects
        assert handler1 is not handler2

        # Both should be RailtownHandler instances
        assert isinstance(handler1, RailtownHandler)
        assert isinstance(handler2, RailtownHandler)

    def test_get_railtown_handler_with_multiple_railtown_handlers(self):
        """Test get_railtown_handler raises RuntimeError when multiple RailtownHandler instances exist."""
        # Initialize Railtown to add a handler
        test_token = "test_api_key"
        init(test_token)

        # Manually add another RailtownHandler (this shouldn't happen in normal usage)
        root_logger = logging.getLogger()
        second_handler = RailtownHandler()
        root_logger.addHandler(second_handler)

        # Verify we now have multiple RailtownHandler instances
        railtown_handlers = [h for h in root_logger.handlers if isinstance(h, RailtownHandler)]
        assert len(railtown_handlers) == 2

        # Should raise RuntimeError when multiple handlers exist
        with pytest.raises(RuntimeError) as exc_info:
            get_railtown_handler()

        # Verify the error message
        assert "Multiple RailtownHandler instances found" in str(exc_info.value)
        assert "2" in str(exc_info.value)  # Should mention the count
        assert "Only one handler should exist" in str(exc_info.value)

        # Clean up the extra handler
        root_logger.removeHandler(second_handler)
