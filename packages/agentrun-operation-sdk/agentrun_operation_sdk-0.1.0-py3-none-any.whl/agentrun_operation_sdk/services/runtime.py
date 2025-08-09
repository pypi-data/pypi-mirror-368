import uuid
import json
import logging
import requests
from typing import Any, Dict
from rich.console import Console

logger = logging.getLogger(__name__)
console = Console()

def generate_session_id() -> str:
    """Generate session ID."""
    return str(uuid.uuid4())

def _handle_http_response(response) -> dict:
    response.raise_for_status()
    if "text/event-stream" in response.headers.get("content-type", ""):
        return _handle_streaming_response(response)
    else:
        # Check if response has content
        if not response.content:
            raise ValueError("Empty response from agent endpoint")

        return {"response": response.text}

def get_data_plane_endpoint(region: str) -> str:
    """Get the data plane endpoint URL for AgentRun services.

    Args:
        region: HW Cloud region to use.

    Returns:
        The data plane endpoint URL, either from environment override or constructed URL.
    """
    return f"https://agentrun.{region}.huaweicloud.com"

def _handle_streaming_response(response) -> Dict[str, Any]:
    complete_text = ""
    for line in response.iter_lines(chunk_size=1):
        if line:
            line = line.decode("utf-8")
            if line.startswith("data: "):
                json_chunk = line[6:]
                try:
                    parsed_chunk = json.loads(json_chunk)
                    if isinstance(parsed_chunk, str):
                        text_chunk = parsed_chunk
                    else:
                        text_chunk = json.dumps(parsed_chunk, ensure_ascii=False)
                        text_chunk += "\n"
                    console.print(text_chunk, end="", style="bold cyan")
                    complete_text += text_chunk
                except json.JSONDecodeError:
                    console.print(json_chunk, style="bold cyan")
                    continue
    console.print()
    return {}

class AgentRunClient:
    def __init__(self, region: str):
        """Initialize AgentRunClient.

        Args:
            region: HW Cloud region for the client
        """
        self.region = region
        self.dp_endpoint = get_data_plane_endpoint(region)
        self.logger = logging.getLogger(f"agentrun.http_runtime.{region}")

        self.logger.debug("Initializing HTTP AgentRun client for region: %s", region)
        self.logger.debug("Data plane: %s", self.dp_endpoint)

    def invoke_endpoint(
        self,
        agent_id,
        payload,
        session_id: str,
        endpoint_name: str = "DEFAULT",
        stream: bool = True,
    ) -> Dict:
        """Invoke agent endpoint using HTTP request.

        Args:
            agent_id: id of the agent
            payload: Payload to send (dict or string)
            session_id: Session ID for the request
            endpoint_name: Endpoint name, defaults to "DEFAULT"
            stream: Whether to stream the response, defaults to True

        Returns:
            Response from the agent endpoint
        """
        url = f"{self.dp_endpoint}/runtimes/invocations"
        # Headers
        headers = {
            "Content-Type": "application/json",
            "AgentRun-Runtime-Session-Id": session_id,
        }
        try:
            body = json.loads(payload) if isinstance(payload, str) else payload
        except json.JSONDecodeError:
            # Fallback for non-JSON strings - wrap in payload object
            self.logger.warning("Failed to parse payload as JSON, wrapping in payload object")
            body = {"payload": payload}
        try:
            # Make request with timeout
            response = requests.post(
                url,
                params={"qualifier": endpoint_name},
                headers=headers,
                json=body,
                timeout=900,
                stream=stream,
            )
            return _handle_http_response(response, stream)
        except requests.exceptions.RequestException as e:
            self.logger.error("Failed to invoke agent endpoint: %s", str(e))
            raise

class LocalAgentRunClient:
    """Local AgentRun client for invoking endpoints."""

    def __init__(self, endpoint: str):
        """Initialize the local client with the given endpoint."""
        self.endpoint = endpoint
        self.logger = logging.getLogger("agentrun.http_local")

    def invoke_endpoint(self, session_id: str, payload: str, stream: bool):
        """Invoke the endpoint with the given parameters."""
        from agentrun_wrapper.runtime.models import SESSION_HEADER

        url = f"{self.endpoint}/invocations"

        headers = {
            "Content-Type": "application/json",
            SESSION_HEADER: session_id,
        }

        try:
            body = json.loads(payload) if isinstance(payload, str) else payload
        except json.JSONDecodeError:
            # Fallback for non-JSON strings - wrap in payload object
            self.logger.warning("Failed to parse payload as JSON, wrapping in payload object")
            body = {"payload": payload}

        try:
            # Make request with timeout
            response = requests.post(url, headers=headers, json=body, timeout=900, stream=stream)
            return _handle_http_response(response)
        except requests.exceptions.RequestException as e:
            self.logger.error("Failed to invoke agent endpoint: %s", str(e))
            raise