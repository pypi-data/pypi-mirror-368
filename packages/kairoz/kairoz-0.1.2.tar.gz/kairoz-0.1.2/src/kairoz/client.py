from typing import Optional, Union, Dict, List, Any, Literal
import os
import logging
import requests
from .prompt import Prompt

MAX_RETRIES = 2
class Kairoz:
    log = logging.getLogger("kairoz")

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, max_retries: Optional[int] = MAX_RETRIES):
        self.api_key = api_key or os.environ.get("KAIROZ_API_KEY")
        self.base_url = (
            base_url or os.environ.get("KAIROZ_API_URL") or "https://api.kairozai.com"
        )
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})

    def _request(
        self, method: str, endpoint: str, params: dict = None, data: dict = None
    ) -> dict:
        """Make an HTTP request to the API"""

        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(
                method=method, url=url, params=params, json=data
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            self.log.error(f"Error making request to {url}: {e}")
            raise e

    def get_prompt(
        self,
        name: str,
        label: Optional[str] = None,
        version: Optional[str] = None,
        max_retries: Optional[int] = None,
    ) -> Prompt:
        """
        Get a prompt by name with optional label OR version filters (mutually exclusive)

        Args:
            name: Name of the prompt
            label: Optional label to filter by (cannot be used with version)
            version: Optional version to filter by (cannot be used with label)
            type: Optional type hint ("text" or "chat") - only used for validation
            max_retries: Number of retries on fetching prompts from the server (default: 2)

        Returns:
            Prompt: The prompt object

        Raises:
            ValueError: If both label and version are provided
        """
        if label is not None and version is not None:
            raise ValueError(
                "Cannot filter by both label and version simultaneously. Choose one."
            )

        params = {}
        if label:
            params["label"] = label
        if version:
            params["version"] = version

        # Implement retries
        response = None
        retry_count = 0
        last_error = None
        max_retries = max_retries or self.max_retries

        while retry_count <= max_retries:
            try:
                response = self._request(
                    method="GET", endpoint=f"/api/prompt/{name}", params=params
                )
                break
            except Exception as e:
                last_error = e
                retry_count += 1
                if retry_count > max_retries:
                    raise e

        if response is None:
            raise last_error or ValueError(
                f"Failed to fetch prompt {name} after {max_retries} retries"
            )

        return Prompt.from_dict(response["prompt"])

    def create_prompt(
        self,
        name: str,
        type: Literal["text", "chat"],
        prompt: Union[str, List[Dict[str, str]]],
        config: Optional[Dict[str, Any]] = None,
        labels: Optional[List[str]] = None,
    ) -> Prompt:
        """
        Create a new prompt

        Args:
            name: Name of the prompt
            type: Type of prompt - either "text" or "chat"
            prompt: For text prompts: A string containing the prompt template
                    For chat prompts: A list of message objects with "role" and "content" keys
            config: Optional configuration for the prompt (model parameters, etc.)
            labels: Optional list of labels to apply to the prompt

        Returns:
            Prompt: The created prompt object

        Raises:
            ValueError: If required fields are missing or invalid
        """

        prompt_obj = Prompt(
            name=name,
            type=type,
            prompt=prompt,
            config=config,
            labels=labels,
        )

        prompt_obj.validate()

        api_prompt = {"prompt": prompt_obj.to_dict()}

        response = self._request(method="POST", endpoint="/api/prompt", data=api_prompt)

        return Prompt.from_dict(response["prompt"])
