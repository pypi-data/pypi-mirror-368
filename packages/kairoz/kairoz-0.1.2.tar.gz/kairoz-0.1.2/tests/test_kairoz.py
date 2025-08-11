import pytest
import os
from unittest.mock import patch, MagicMock
from kairoz import Kairoz, Prompt


# Test client initialization
def test_client_init():
    # Test with explicit API key
    client = Kairoz(api_key="test-key")
    assert client.api_key == "test-key"
    assert client.base_url == "https://api.kairozai.com"
    assert client.max_retries == 2  # valor por defecto

    # Test with environment variable
    with patch.dict(os.environ, {"KAIROZ_API_KEY": "env-key"}):
        client = Kairoz()
        assert client.api_key == "env-key"

    # Test with custom configuration
    client = Kairoz(
        api_key="test-key", base_url="https://custom.api.kairozai.com", max_retries=3
    )
    assert client.api_key == "test-key"
    assert client.base_url == "https://custom.api.kairozai.com"
    assert client.max_retries == 3


# Test prompt creation and validation
def test_prompt_validation():
    # Test valid text prompt
    text_prompt = Prompt(
        name="test-prompt",
        type="text",
        prompt="Hello {{name}}!",
        config={"temperature": 0.7},
        labels=["test"],
        version="1.0.0",
    )
    assert text_prompt.validate() is True

    # Test valid chat prompt
    chat_prompt = Prompt(
        name="test-chat",
        type="chat",
        prompt=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Hello {{name}}!"},
            {"role": "assistant", "content": "Hi! How can I help you?"},
        ],
        version="2.0.0",
    )
    assert chat_prompt.validate() is True

    # Test invalid prompt type
    with pytest.raises(ValueError):
        Prompt(name="invalid", type="invalid", prompt="test").validate()

    # Test invalid config
    with pytest.raises(ValueError):
        Prompt(
            name="invalid", type="text", prompt="test", config={"invalid": object()}
        ).validate()

    # Test invalid labels
    with pytest.raises(ValueError):
        Prompt(name="invalid", type="text", prompt="test", labels=[1]).validate()

    # Test invalid chat message format
    with pytest.raises(
        ValueError, match="Message role must be either 'system', 'user' or 'assistant'"
    ):
        Prompt(
            name="invalid-chat",
            type="chat",
            prompt=[{"role": "invalid", "content": "test"}],
        ).validate()


# Test prompt formatting
def test_prompt_formatting():
    # Test text prompt formatting
    text_prompt = Prompt(
        name="greeting",
        type="text",
        prompt="Hello {{name}}! Welcome to {{service}}.",
        config={"temperature": 0.7},
        labels=["test"],
        version="1.0.0",
    )
    formatted_prompt = text_prompt.format(name="John", service="Kairoz")

    assert isinstance(formatted_prompt, Prompt)
    assert formatted_prompt.name == "greeting"
    assert formatted_prompt.type == "text"
    assert formatted_prompt.prompt == "Hello John! Welcome to Kairoz."
    assert formatted_prompt.config == {"temperature": 0.7}
    assert formatted_prompt.labels == ["test"]
    assert formatted_prompt.version == "1.0.0"

    # Test chat prompt formatting
    chat_prompt = Prompt(
        name="chat-greeting",
        type="chat",
        prompt=[
            {"role": "system", "content": "You are {{assistant_type}}"},
            {"role": "user", "content": "Hi {{name}}!"},
            {"role": "assistant", "content": "Hello! I'm {{assistant_name}}"},
        ],
        version="2.0.0",
    )
    formatted_prompt = chat_prompt.format(
        assistant_type="helpful", name="John", assistant_name="Kairoz"
    )

    assert isinstance(formatted_prompt, Prompt)
    assert formatted_prompt.name == "chat-greeting"
    assert formatted_prompt.type == "chat"
    assert formatted_prompt.prompt == [
        {"role": "system", "content": "You are helpful"},
        {"role": "user", "content": "Hi John!"},
        {"role": "assistant", "content": "Hello! I'm Kairoz"},
    ]
    assert formatted_prompt.version == "2.0.0"

    # Test missing variables
    missing_var_prompt = Prompt(
        name="missing-var",
        type="text",
        prompt="Hello {{name}}! Welcome to {{service}}.",
        config={},
        labels=[],
    )
    with pytest.raises(ValueError, match="Variable 'name' not found"):
        missing_var_prompt.format(service="Kairoz")


# Test API interactions with mocking
@patch("requests.Session")
def test_get_prompt(mock_session):
    # Mock the API response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "prompt": {
            "id": "123",
            "name": "test-prompt",
            "type": "text",
            "messages": [{"role": "user", "content": "Hello {{name}}!"}],
            "config": {},
            "labels": ["test"],
            "version": "1",
        }
    }
    mock_response.raise_for_status.return_value = None
    mock_session.return_value.request.return_value = mock_response

    # Test get_prompt
    client = Kairoz(api_key="test-key")
    prompt = client.get_prompt("test-prompt")

    assert prompt.name == "test-prompt"
    assert prompt.type == "text"
    assert prompt.prompt == "Hello {{name}}!"
    assert prompt.version == "1"
    assert prompt.id == "123"

    # Test get_prompt with label
    prompt = client.get_prompt("test-prompt", label="test")
    assert prompt.labels == ["test"]

    # Test get_prompt with version
    prompt = client.get_prompt("test-prompt", version="1")
    assert prompt.version == "1"

    # Test error when using both label and version
    with pytest.raises(
        ValueError, match="Cannot filter by both label and version simultaneously"
    ):
        client.get_prompt("test-prompt", label="test", version="1")


@patch("requests.Session")
def test_create_prompt(mock_session):
    # Mock the API response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "prompt": {
            "id": "123",
            "name": "new-prompt",
            "type": "text",
            "messages": [{"role": "user", "content": "Test prompt"}],
            "config": {"temperature": 0.7},
            "labels": ["test"],
            "version": "1.0.0",
        }
    }
    mock_response.raise_for_status.return_value = None
    mock_session.return_value.request.return_value = mock_response

    # Test create_prompt
    client = Kairoz(api_key="test-key")
    prompt = client.create_prompt(
        name="new-prompt",
        type="text",
        prompt="Test prompt",
        config={"temperature": 0.7},
        labels=["test"],
    )

    assert prompt.name == "new-prompt"
    assert prompt.type == "text"
    assert prompt.prompt == "Test prompt"
    assert prompt.config == {"temperature": 0.7}
    assert prompt.labels == ["test"]
    assert prompt.version == "1.0.0"
    assert prompt.id == "123"

    # Test create chat prompt
    mock_response.json.return_value = {
        "prompt": {
            "id": "124",
            "name": "chat-prompt",
            "type": "chat",
            "messages": [
                {"role": "system", "content": "You are helpful"},
                {"role": "user", "content": "Hello!"},
            ],
            "config": {},
            "labels": [],
            "version": "1.0.0",
        }
    }

    prompt = client.create_prompt(
        name="chat-prompt",
        type="chat",
        prompt=[
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hello!"},
        ],
    )

    assert prompt.name == "chat-prompt"
    assert prompt.type == "chat"
    assert prompt.prompt == [
        {"role": "system", "content": "You are helpful"},
        {"role": "user", "content": "Hello!"},
    ]
    assert prompt.version == "1.0.0"
    assert prompt.id == "124"
