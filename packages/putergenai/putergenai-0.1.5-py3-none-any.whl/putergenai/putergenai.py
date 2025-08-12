import json
import logging
import re
import time
from typing import Any, Dict, Generator, List, Optional, Union
from urllib.parse import urlparse

import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def sanitize_string(s, allow_empty=False, allow_path=False):
    """
    Sanitize user input for usernames, passwords, and file paths only.
    For chat and prompt text, allow natural language (no sanitization).
    """
    if not isinstance(s, str):
        raise ValueError("Input must be a string.")
    s = s.strip()
    if not allow_empty and not s:
        raise ValueError("Input cannot be empty.")
    if allow_path:
        pattern = r'^[\w\-\.\/]+$'
        if not re.match(pattern, s):
            raise ValueError("Input contains invalid characters for path.")
    return s


def sanitize_url(url):
    # Improved URL validation
    if not isinstance(url, str):
        raise ValueError("Invalid URL: not a string.")
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError("Invalid URL.")
    return url


class PuterClient:
    def __init__(self, token: Optional[str] = None):
        self.token = token
        self.api_base = "https://api.puter.com"
        self.login_url = "https://puter.com/login"
        self.headers = {
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Origin": "https://puter.com",
            "Referer": "https://puter.com/",
            "User-Agent": (
                "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36"
            ),
        }
        # Model to driver mapping for all models from puter.js documentation
        self.model_to_driver = {
            "gpt-4o-mini": "openai-completion",
            "gpt-4o": "openai-completion",
            "o1": "openai-completion",
            "o1-mini": "openai-completion",
            "o1-pro": "openai-completion",
            "o3": "openai-completion",
            "o3-mini": "openai-completion",
            "o4-mini": "openai-completion",
            "gpt-5-2025-08-07": "openai-completion",
            "gpt-5-mini-2025-08-07": "openai-completion",
            "gpt-5-nano-2025-08-07": "openai-completion",
            "gpt-5-chat-latest": "openai-completion",
            "gpt-4.1": "openai-completion",
            "gpt-4.1-mini": "openai-completion",
            "gpt-4.1-nano": "openai-completion",
            "claude-sonnet-4": "claude",
            "claude-opus-4-1-20250805": "claude",
            "claude-opus-4-latest": "claude",
            "claude-3-7-sonnet-latest": "claude",
            "claude-3-5-sonnet-latest": "claude",
            "deepseek-chat": "deepseek",
            "deepseek-reasoner": "deepseek",
        }
        self.fallback_models = [
            "gpt-4.1-nano",
            "gpt-4o-mini",
            "claude-3-5-sonnet",
            "deepseek-chat",
        ]
        self.max_retries = 3

    def login(self, username: str, password: str) -> str:
        username = sanitize_string(username)
        password = sanitize_string(password)
        payload = {"username": username, "password": password}
        try:
            response = requests.post(
                self.login_url, headers=self.headers, json=payload
            )
            response.raise_for_status()
            data = response.json()
            if data.get("proceed"):
                self.token = data["token"]
                logger.info("Login successful, token acquired")
                return self.token
            else:
                logger.warning("Login failed: Invalid credentials")
                raise ValueError("Login failed. Please check your credentials.")
        except requests.RequestException as e:
            logger.warning(f"Login error: {e}")
            raise ValueError(f"Login error: {e}")

    def _get_auth_headers(self) -> Dict[str, str]:
        if not self.token:
            logger.error("Authentication error: No token available")
            raise ValueError("Not authenticated. Please login first.")
        return {
            **self.headers,
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def fs_write(
        self, path: str, content: Union[str, bytes, Any]
    ) -> Dict[str, Any]:
        """
        Write content to a file in Puter FS.
        If content is str or bytes, send directly. If file-like, read it.
        Returns the file info.
        """
        path = sanitize_string(path, allow_path=True)
        headers = self._get_auth_headers()
        headers.pop("Content-Type")
        if isinstance(content, str):
            content = content.encode("utf-8")
        if not isinstance(content, bytes):
            if hasattr(content, "read"):
                content = content.read()
            else:
                logger.warning("Invalid content type for fs_write")
                raise ValueError(
                    "Content must be str, bytes, or file-like object."
                )
        try:
            response = requests.post(
                f"{self.api_base}/write",
                params={"path": path},
                data=content,
                headers=headers,
            )
            response.raise_for_status()
            logger.info(f"File written successfully at {path}")
            return response.json()
        except requests.RequestException as e:
            logger.warning(f"fs_write error: {e}")
            raise

    def fs_read(self, path: str) -> bytes:
        """
        Read file content from Puter FS.
        """
        path = sanitize_string(path, allow_path=True)
        headers = self._get_auth_headers()
        try:
            response = requests.get(
                f"{self.api_base}/read",
                params={"path": path},
                headers=headers,
            )
            response.raise_for_status()
            logger.info(f"File read successfully from {path}")
            return response.content
        except requests.RequestException as e:
            logger.warning(f"fs_read error: {e}")
            raise

    def fs_delete(self, path: str) -> None:
        """
        Delete a file or directory in Puter FS.
        """
        path = sanitize_string(path, allow_path=True)
        headers = self._get_auth_headers()
        try:
            response = requests.post(
                f"{self.api_base}/delete",
                params={"path": path},
                headers=headers,
            )
            response.raise_for_status()
            logger.info(f"File deleted successfully at {path}")
        except requests.RequestException as e:
            logger.warning(f"fs_delete error: {e}")
            raise

    def ai_chat(
        self,
        prompt: Optional[Union[str, List[Dict[str, Any]]]] = None,
        options: Optional[Dict[str, Any]] = None,
        test_mode: bool = False,
        image_url: Optional[Union[str, List[str]]] = None,
        messages: Optional[List[Dict[str, Any]]] = None,
        retry_count: int = 0,
        strict_model: bool = False,
    ) -> Union[Dict[str, Any], Generator[tuple[str, str], None, None]]:
        """
        AI chat completion, supporting multiple models with fallback and retries.
        Returns: For stream, a generator of (content, used_model) tuples; for non-stream, a dict with response and used_model.
        """
        if options is None:
            options = {}
        model = options.get("model", self.fallback_models[0])
        driver = self.model_to_driver.get(model, "openai-completion")
        stream = options.get("stream", False)
        temperature = options.get("temperature", 0.7)
        max_tokens = options.get("max_tokens", 1000)

        if messages is None:
            messages = []
            if prompt:
                content = prompt
                if image_url:
                    if not isinstance(image_url, list):
                        image_url = [image_url]
                    content_parts = (
                        [{"type": "text", "text": content}]
                        if isinstance(content, str)
                        else content
                    )
                    for url in image_url:
                        safe_url = sanitize_url(url)
                        content_parts.append(
                            {"type": "image_url", "image_url": {"url": safe_url}}
                        )
                    content = content_parts
                messages.append({"role": "user", "content": content})

        args = {
            "messages": messages,
            "model": model,
            "stream": stream,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "tools": options.get("tools"),
        }
        payload = {
            "interface": "puter-chat-completion",
            "driver": driver,
            "method": "complete",
            "args": args,
            "stream": stream,
            "testMode": test_mode,
        }

        headers = self._get_auth_headers()
        try:
            logger.info(
                f"Sending ai_chat request with model {model}, "
                f"driver {driver}, stream={stream}, "
                f"test_mode={test_mode}, retry={retry_count}"
            )
            logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
            response = requests.post(
                f"{self.api_base}/drivers/call",
                json=payload,
                headers=headers,
                stream=stream,
            )
            response.raise_for_status()

            def check_used_model(
                data: Dict[str, Any], requested_model: str, strict: bool
            ) -> str:
                """Extract used model from response metadata and validate."""
                used_model = None
                if (
                    "result" in data
                    and "usage" in data["result"]
                    and data["result"]["usage"]
                ):
                    used_model = data["result"]["usage"][0].get("model", "unknown")
                elif "metadata" in data and "service_used" in data["metadata"]:
                    used_model = data["metadata"].get("service_used", "unknown")
                if used_model and used_model != requested_model:
                    msg = (
                        f"Requested model {requested_model}, "
                        f"but server used {used_model}"
                    )
                    if strict:
                        raise ValueError(msg)
                    else:
                        logger.warning(msg)
                return used_model or requested_model

            def process_line(
                line: bytes, requested_model: str, strict: bool
            ) -> Optional[tuple[str, str]]:
                if not line:
                    return None
                logger.debug(f"Raw stream line: {line}")
                try:
                    data = json.loads(line)
                    if not data.get("success", True):
                        error_data = data.get("error", {})
                        error_code = error_data.get("code")
                        error_msg = error_data.get("message", "Unknown error")
                        raise ValueError(
                            f"API error: {error_msg} (code: {error_code})"
                        )
                    used_model = check_used_model(data, requested_model, strict)
                    # Handle custom text response format
                    if "type" in data and data["type"] == "text" and "text" in data:
                        content = data["text"]
                        if content:
                            logger.info("Processed custom text JSON streaming response")
                            return content, used_model
                    # Handle Claude-style response
                    if "result" in data and "message" in data["result"]:
                        message_content = data["result"]["message"].get(
                            "content", ""
                        )
                        if isinstance(message_content, str):
                            logger.info(
                                "Processed string content JSON streaming response"
                            )
                            return message_content, used_model
                        elif isinstance(message_content, list):
                            content = message_content[0].get("text", "")
                            if content:
                                logger.info(
                                    "Processed list content JSON streaming response"
                                )
                                return content, used_model
                            else:
                                logger.warning(
                                    f"No text in list content: {message_content}"
                                )
                        else:
                            logger.warning(
                                f"Unexpected content type: {type(message_content)}"
                            )
                    # Handle OpenAI-style response
                    if "choices" in data:
                        content = (
                            data.get("choices", [{}])[0]
                            .get("delta", {})
                            .get("content", "")
                        )
                        if content:
                            logger.info("Processed OpenAI-style JSON streaming response")
                            return content, used_model
                        else:
                            logger.warning(f"No content in OpenAI-style response: {data}")
                    logger.warning(f"Unexpected JSON response format: {data}")
                except json.JSONDecodeError:
                    # Handle SSE format
                    if line.startswith(b"data: "):
                        try:
                            data = json.loads(line[6:])
                            if not data.get("success", True):
                                error_data = data.get("error", {})
                                error_code = error_data.get("code")
                                error_msg = data.get("message", "Unknown error")
                                raise ValueError(
                                    f"API error: {error_msg} (code: {error_code})"
                                )
                            used_model = check_used_model(data, requested_model, strict)
                            content = data.get("text", "")
                            if content:
                                logger.info("Processed SSE streaming response")
                                return content, used_model
                            else:
                                logger.warning(f"No text in SSE data: {data}")
                        except json.JSONDecodeError:
                            logger.warning(f"Invalid SSE data: {line}")
                    else:
                        # Treat as plain text
                        decoded_line = line.decode("utf-8", errors="ignore")
                        if decoded_line.strip():
                            logger.info("Processed plain text streaming response")
                            return decoded_line, requested_model
                        else:
                            logger.warning(f"Empty or invalid stream line: {line}")
                return None

            if stream:
                line_iter = response.iter_lines()
                # Peek at the first line to check for errors
                first_line = next(line_iter, None)
                if first_line:
                    try:
                        # Process first line to check for error
                        processed = process_line(first_line, model, strict_model)
                        if processed is None:
                            # If no content, but no raise, continue
                            pass
                    except ValueError as e:
                        error_msg = str(e)
                        if "API error" in error_msg:
                            # Extract code if possible
                            if "(code: " in error_msg:
                                error_code = error_msg.split("(code: ")[1][:-1]
                            else:
                                error_code = None
                            if error_code in (
                                "no_implementation_available",
                                "forbidden",
                            ) and retry_count < self.max_retries:
                                if strict_model:
                                    raise ValueError(
                                        f"Model {model} not available due to "
                                        "permission issues or implementation. "
                                        "Since strict_model is True, no fallback."
                                    )
                                else:
                                    if not test_mode:
                                        logger.warning(
                                            f"Model {model} not available, "
                                            f"retrying with test_mode=True, "
                                            f"attempt {retry_count + 1}"
                                        )
                                        return self.ai_chat(
                                            prompt=prompt,
                                            options=options,
                                            test_mode=True,
                                            image_url=image_url,
                                            messages=messages,
                                            retry_count=retry_count + 1,
                                            strict_model=strict_model,
                                        )
                                    # Fallback to another model
                                    current_model_index = (
                                        self.fallback_models.index(model)
                                        if model in self.fallback_models
                                        else -1
                                    )
                                    next_model_index = (
                                        current_model_index + 1
                                        if current_model_index >= 0
                                        else 0
                                    )
                                    if next_model_index < len(self.fallback_models):
                                        next_model = self.fallback_models[
                                            next_model_index
                                        ]
                                        logger.warning(
                                            f"Model {model} (driver {driver}) "
                                            f"not available, retrying with "
                                            f"model {next_model}, "
                                            f"attempt {retry_count + 1}"
                                        )
                                        options["model"] = next_model
                                        time.sleep(1)
                                        return self.ai_chat(
                                            prompt=prompt,
                                            options=options,
                                            test_mode=test_mode,
                                            image_url=image_url,
                                            messages=messages,
                                            retry_count=retry_count + 1,
                                            strict_model=strict_model,
                                        )
                                    else:
                                        logger.error(
                                            f"No more fallback models available "
                                            f"after {model}."
                                        )
                                        raise
                            else:
                                raise
                        else:
                            raise
                # If no error, create generator that yields processed first and then others
                def generator():
                    if first_line:
                        processed = process_line(first_line, model, strict_model)
                        if processed:
                            yield processed
                    for line in line_iter:
                        processed = process_line(line, model, strict_model)
                        if processed:
                            yield processed

                logger.info("ai_chat stream request initiated")
                return generator()
            else:
                result = response.json()
                if not result.get("success", True):
                    error_data = result.get("error", {})
                    error_code = error_data.get("code")
                    error_msg = error_data.get("message", "Unknown error")
                    if error_code in (
                        "no_implementation_available",
                        "forbidden",
                    ) and retry_count < self.max_retries:
                        if strict_model:
                            raise ValueError(
                                f"Model {model} not available due to "
                                "permission issues or implementation. "
                                "Since strict_model is True, no fallback."
                            )
                        else:
                            if not test_mode:
                                logger.warning(
                                    f"Model {model} not available, "
                                    f"retrying with test_mode=True, "
                                    f"attempt {retry_count + 1}"
                                )
                                return self.ai_chat(
                                    prompt=prompt,
                                    options=options,
                                    test_mode=True,
                                    image_url=image_url,
                                    messages=messages,
                                    retry_count=retry_count + 1,
                                    strict_model=strict_model,
                                )
                            # Fallback to another model
                            current_model_index = (
                                self.fallback_models.index(model)
                                if model in self.fallback_models
                                else -1
                            )
                            next_model_index = (
                                current_model_index + 1
                                if current_model_index >= 0
                                else 0
                            )
                            if next_model_index < len(self.fallback_models):
                                next_model = self.fallback_models[next_model_index]
                                logger.warning(
                                    f"Model {model} (driver {driver}) "
                                    f"not available, retrying with "
                                    f"model {next_model}, "
                                    f"attempt {retry_count + 1}"
                                )
                                options["model"] = next_model
                                time.sleep(1)
                                return self.ai_chat(
                                    prompt=prompt,
                                    options=options,
                                    test_mode=test_mode,
                                    image_url=image_url,
                                    messages=messages,
                                    retry_count=retry_count + 1,
                                    strict_model=strict_model,
                                )
                            else:
                                logger.error(
                                    f"No more fallback models available "
                                    f"after {model}."
                                )
                                raise ValueError(
                                    f"No implementation available for "
                                    f"model {model}: {error_msg}"
                                )
                    else:
                        logger.error(f"AI chat error: {error_msg}")
                        raise ValueError(f"AI chat error: {error_msg}")
                used_model = check_used_model(result, model, strict_model)
                logger.info(f"ai_chat request successful, used model: {used_model}")
                return {"response": result, "used_model": used_model}

        except requests.RequestException as e:
            logger.error(f"ai_chat request failed: {e}")
            raise

    def ai_img2txt(self, image: Union[str, Any], test_mode: bool = False) -> str:
        """
        Image to text (OCR).
        image: URL or file-like.
        """
        headers = self._get_auth_headers()
        try:
            if isinstance(image, str):
                safe_url = sanitize_url(image)
                payload = {"image_url": safe_url, "testMode": test_mode}
                response = requests.post(
                    f"{self.api_base}/ai/img2txt",
                    json=payload,
                    headers=headers,
                )
            else:
                files = {"image": image}
                response = requests.post(
                    f"{self.api_base}/ai/img2txt",
                    files=files,
                    data={"testMode": test_mode},
                    headers=headers,
                )
            response.raise_for_status()
            logger.info("ai_img2txt request successful")
            return response.json().get("text")
        except requests.RequestException as e:
            logger.warning(f"ai_img2txt error: {e}")
            raise

    def ai_txt2img(self, prompt: str, model: str = "pollinations-image", test_mode: bool = False) -> str:
        """
        Text to image using Puter's driver API.
        Returns image URL.
        """
        payload = {
            "interface": "puter-image-generation",
            "driver": model,  # or other supported image model in puter.js docs
            "method": "generate",
            "args": {
                "prompt": prompt
            },
            "testMode": test_mode
        }

        headers = self._get_auth_headers()
        try:
            response = requests.post(f"{self.api_base}/drivers/call", json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            if "result" in data and "image_url" in data["result"]:
                return data["result"]["image_url"]
            elif "result" in data and isinstance(data["result"], dict):
                # Some models might return base64 or direct data URL
                return data["result"].get("url") or data["result"].get("data")
            else:
                raise ValueError(f"Unexpected response format: {data}")
        except requests.RequestException as e:
            logger.warning(f"ai_txt2img error: {e}")
            raise

    def ai_txt2speech(
        self, text: str, options: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """
        Text to speech.
        Returns MP3 bytes.
        """
        if options is None:
            options = {}
        # Allow natural language text
        payload = {"text": text, "testMode": options.get("testMode", False)}
        headers = self._get_auth_headers()
        try:
            response = requests.post(
                f"{self.api_base}/ai/txt2speech",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            logger.info("ai_txt2speech request successful")
            return response.content
        except requests.RequestException as e:
            logger.warning(f"ai_txt2speech error: {e}")
            raise