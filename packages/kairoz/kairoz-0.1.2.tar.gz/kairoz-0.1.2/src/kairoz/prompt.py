from typing import Dict, List, Literal, Optional, Union, Any
import re


class Prompt:
    """
    Model class for Kairoz prompts with variable interpolation support
    """

    def __init__(
        self,
        name: str,
        type: Literal["text", "chat"],
        prompt: Union[str, List[Dict[str, str]]],
        config: Dict[str, Any] = None,
        labels: List[str] = None,
        version: Optional[str] = None,
        id: Optional[str] = None,
    ):
        """
        Initialize a prompt object

        Args:
            name: Name of the prompt
            type: Type of prompt - either "text" or "chat"
            prompt: The prompt content - either a string for text prompts or a list of messages for chat prompts
            config: Additional configuration for the prompt
            labels: Optional list of labels to associate with the prompt
            version: Optional version of the prompt
            id: Optional ID of the prompt (set automatically by API when retrieved)
        """
        self.id = id
        self.name = name
        self.type = type
        self.prompt = prompt
        self.config = config or {}
        self.labels = labels or []
        self.version = version

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Prompt":
        """
        Create a Prompt object from API response data

        Args:
            data: The prompt data from the API

        Returns:
            A Prompt object
        """
        # Handle different response formats
        prompt_type = data.get("type", "chat")
        messages = data.get("messages", [])

        # Format prompt content based on type
        if prompt_type == "text" and messages and len(messages) > 0:
            prompt_content = messages[0].get("content", "")
        else:
            prompt_content = messages

        return cls(
            id=data.get("id"),
            name=data.get("name"),
            type=prompt_type,
            prompt=prompt_content,
            config=data.get("config", {}),
            labels=data.get("labels", []),
            version=data.get("version"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the prompt to a dictionary for API requests

        Returns:
            A dictionary representation of the prompt
        """
        data = {
            "name": self.name,
            "type": self.type,
            "config": self.config,
        }

        if self.labels:
            data["labels"] = self.labels

        # Add messages in the correct format for the API
        if self.type == "text":
            if isinstance(self.prompt, str):
                data["messages"] = [{"role": "user", "content": self.prompt}]
            else:
                raise ValueError("Text prompts must have a string prompt")
        else:  # chat type
            if isinstance(self.prompt, list):
                data["messages"] = self.prompt
            else:
                raise ValueError("Chat prompts must have a list of messages")

        return data

    def format(self, **variables) -> "Prompt":
        """
        Insert variables into the prompt template and return a new Prompt instance

        Args:
            **variables: Key-value pairs to replace in the template

        Returns:
            A new Prompt instance with variables replaced in the prompt
        """
        if self.type == "text":
            if not isinstance(self.prompt, str):
                raise ValueError("Text prompts must have a string prompt")

            formatted_prompt = self._replace_variables(self.prompt, variables)
            return Prompt(
                name=self.name,
                type=self.type,
                prompt=formatted_prompt,
                config=self.config,
                labels=self.labels,
                version=self.version,
                id=self.id,
            )

        else:  # chat type
            if not isinstance(self.prompt, list):
                raise ValueError("Chat prompts must have a list of messages")

            compiled_messages = []
            for message in self.prompt:
                if (
                    not isinstance(message, dict)
                    or "role" not in message
                    or "content" not in message
                ):
                    raise ValueError(
                        "Chat messages must be dictionaries with 'role' and 'content' keys"
                    )

                compiled_content = self._replace_variables(
                    message["content"], variables
                )
                compiled_messages.append(
                    {"role": message["role"], "content": compiled_content}
                )

            return Prompt(
                name=self.name,
                type=self.type,
                prompt=compiled_messages,
                config=self.config,
                labels=self.labels,
                version=self.version,
                id=self.id,
            )

    def _replace_variables(self, text: str, variables: Dict[str, Any]) -> str:
        """
        Replace template variables in a string

        Args:
            text: The template string
            variables: Key-value pairs to replace in the template

        Returns:
            The string with variables replaced

        Raises:
            ValueError: If a required variable is not found in the variables dict
        """
        # Find all variables in the text
        pattern = r"\{\{([^}]+)\}\}"
        matches = re.finditer(pattern, text)

        # Check if all variables are provided
        for match in matches:
            var_name = match.group(1).strip()
            if var_name not in variables:
                raise ValueError(f"Variable '{var_name}' not found")

        # Replace all variables
        for key, value in variables.items():
            pattern = r"\{\{" + re.escape(key) + r"\}\}"
            text = re.sub(pattern, str(value), text)

        return text

    def validate(self):
        """
        Validate the prompt object

        Raises:
            ValueError: If any of the prompt properties are invalid
        """
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Name must be a non-empty string")

        if self.type not in ["text", "chat"]:
            raise ValueError("Type must be either 'text' or 'chat'")

        if self.type == "text" and not isinstance(self.prompt, str):
            raise ValueError("Text prompts must have a string prompt")

        if self.type == "chat" and not isinstance(self.prompt, list):
            raise ValueError("Chat prompts must have a list of messages")

        if self.type == "chat":
            if not self.prompt:  # Check if list is empty
                raise ValueError("At least one message is required")

            for message in self.prompt:
                if (
                    not isinstance(message, dict)
                    or "role" not in message
                    or "content" not in message
                ):
                    raise ValueError(
                        "Chat messages must be dictionaries with 'role' and 'content' keys"
                    )

                if message["role"] not in ["system", "user", "assistant"]:
                    raise ValueError(
                        "Message role must be either 'system', 'user' or 'assistant'"
                    )

                if not isinstance(message["content"], str):
                    raise ValueError("Message content must be a string")

        # Validate config is JSON serializable
        if not isinstance(self.config, dict):
            raise ValueError("Config must be a dictionary")
        try:
            import json

            json.dumps(self.config)
        except TypeError:
            raise ValueError("Config must be JSON serializable")

        # Validate labels is a list of strings
        if not isinstance(self.labels, list):
            raise ValueError("Labels must be a list")
        if not all(isinstance(label, str) for label in self.labels):
            raise ValueError("All labels must be strings")

        # If we've made it this far, the prompt is valid
        return True
