"""ODIN HTTP client for service endpoints."""

import asyncio
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .errors import (
    AuthError,
    NetworkError,
    OdinError,
    RateLimitError,
    ServerError,
)


class OdinClient:
    """HTTP client for ODIN service endpoints."""

    def __init__(
        self,
        base_url: str = "https://api.odin.ai",
        api_key: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_backoff: float = 1.0,
    ):
        """
        Initialize ODIN client.
        
        Args:
            base_url: Base URL for ODIN service
            api_key: API key for authentication
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            retry_backoff: Exponential backoff factor for retries
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff
        
        # HTTP client configuration
        headers = {
            "User-Agent": "odin-protocol-python/0.1.0",
            "Content-Type": "application/json",
        }
        
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
            
        self.client = httpx.Client(
            timeout=timeout,
            headers=headers,
            follow_redirects=True,
        )
        
        self.async_client = httpx.AsyncClient(
            timeout=timeout,
            headers=headers,
            follow_redirects=True,
        )

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.aclose()

    def close(self):
        """Close the HTTP client."""
        self.client.close()

    async def aclose(self):
        """Close the async HTTP client."""
        await self.async_client.aclose()

    def _make_retry_decorator(self):
        """Create retry decorator with configured settings."""
        return retry(
            retry=retry_if_exception_type((NetworkError, ServerError)),
            stop=stop_after_attempt(self.max_retries),
            wait=wait_exponential(multiplier=self.retry_backoff),
        )

    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """
        Handle HTTP response and convert errors.
        
        Args:
            response: HTTP response object
            
        Returns:
            Response data as dictionary
            
        Raises:
            OdinError subclasses based on status code
        """
        try:
            # Check for HTTP errors
            if response.status_code == 401:
                raise AuthError("Authentication failed")
            elif response.status_code == 403:
                raise AuthError("Access forbidden")
            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            elif 400 <= response.status_code < 500:
                try:
                    error_data = response.json()
                    message = error_data.get('error', f"Client error: {response.status_code}")
                except Exception:
                    message = f"Client error: {response.status_code}"
                raise OdinError(message)
            elif 500 <= response.status_code < 600:
                raise ServerError(f"Server error: {response.status_code}")
            
            # Raise for other HTTP errors
            response.raise_for_status()
            
            # Parse JSON response
            return response.json()
            
        except httpx.HTTPStatusError as e:
            raise ServerError(f"HTTP error: {e}")
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}")
        except Exception as e:
            if isinstance(e, OdinError):
                raise
            raise OdinError(f"Unexpected error: {e}")

    @retry(
        retry=retry_if_exception_type((NetworkError,)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1.0),
    )
    def _request(
        self,
        method: str,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic.
        
        Args:
            method: HTTP method
            endpoint: API endpoint path
            json: JSON payload
            params: Query parameters
            files: File uploads
            
        Returns:
            Response data
        """
        url = urljoin(self.base_url, endpoint)
        
        try:
            response = self.client.request(
                method=method,
                url=url,
                json=json,
                params=params,
                files=files,
            )
            return self._handle_response(response)
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}")

    @retry(
        retry=retry_if_exception_type((NetworkError,)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1.0),
    )
    async def _arequest(
        self,
        method: str,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make async HTTP request with retry logic.
        
        Args:
            method: HTTP method
            endpoint: API endpoint path
            json: JSON payload
            params: Query parameters
            files: File uploads
            
        Returns:
            Response data
        """
        url = urljoin(self.base_url, endpoint)
        
        try:
            response = await self.async_client.request(
                method=method,
                url=url,
                json=json,
                params=params,
                files=files,
            )
            return self._handle_response(response)
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}")

    # Mediator endpoints
    def mediator_submit(
        self,
        odin_files: List[bytes],
        chain_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Submit ODIN files to mediator for processing.
        
        Args:
            odin_files: List of ODIN file binary data
            chain_data: Optional chain context
            metadata: Optional request metadata
            
        Returns:
            Mediator response
        """
        files = {}
        for i, file_data in enumerate(odin_files):
            files[f"odin_{i}"] = ("file.odin", file_data, "application/octet-stream")
        
        data = {}
        if chain_data:
            data["chain"] = chain_data
        if metadata:
            data["metadata"] = metadata
        
        return self._request("POST", "/mediator", files=files, json=data if data else None)

    async def amediator_submit(
        self,
        odin_files: List[bytes],
        chain_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Async version of mediator_submit."""
        files = {}
        for i, file_data in enumerate(odin_files):
            files[f"odin_{i}"] = ("file.odin", file_data, "application/octet-stream")
        
        data = {}
        if chain_data:
            data["chain"] = chain_data
        if metadata:
            data["metadata"] = metadata
        
        return await self._arequest("POST", "/mediator", files=files, json=data if data else None)

    # Rules endpoints
    def rules_evaluate(
        self,
        rule_id: str,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate a rule against input data.
        
        Args:
            rule_id: Rule identifier
            input_data: Input data for rule evaluation
            context: Optional evaluation context
            
        Returns:
            Rule evaluation result
        """
        payload = {
            "rule_id": rule_id,
            "input": input_data,
        }
        if context:
            payload["context"] = context
        
        return self._request("POST", "/rules/evaluate", json=payload)

    async def arules_evaluate(
        self,
        rule_id: str,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Async version of rules_evaluate."""
        payload = {
            "rule_id": rule_id,
            "input": input_data,
        }
        if context:
            payload["context"] = context
        
        return await self._arequest("POST", "/rules/evaluate", json=payload)

    # ODIN file operations
    def odin_repair(
        self,
        odin_data: bytes,
        repair_type: str = "checksum",
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Repair corrupted ODIN file.
        
        Args:
            odin_data: ODIN file binary data
            repair_type: Type of repair to perform
            options: Repair options
            
        Returns:
            Repair result with fixed file data
        """
        files = {"odin_file": ("file.odin", odin_data, "application/octet-stream")}
        data = {"repair_type": repair_type}
        if options:
            data["options"] = options
        
        return self._request("POST", "/odin/repair", files=files, json=data)

    async def aodin_repair(
        self,
        odin_data: bytes,
        repair_type: str = "checksum",
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Async version of odin_repair."""
        files = {"odin_file": ("file.odin", odin_data, "application/octet-stream")}
        data = {"repair_type": repair_type}
        if options:
            data["options"] = options
        
        return await self._arequest("POST", "/odin/repair", files=files, json=data)

    def odin_translate(
        self,
        odin_data: bytes,
        target_format: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Translate ODIN file to different format.
        
        Args:
            odin_data: ODIN file binary data
            target_format: Target format (json, yaml, etc.)
            options: Translation options
            
        Returns:
            Translation result
        """
        files = {"odin_file": ("file.odin", odin_data, "application/octet-stream")}
        data = {"target_format": target_format}
        if options:
            data["options"] = options
        
        return self._request("POST", "/odin/translate", files=files, json=data)

    async def aodin_translate(
        self,
        odin_data: bytes,
        target_format: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Async version of odin_translate."""
        files = {"odin_file": ("file.odin", odin_data, "application/octet-stream")}
        data = {"target_format": target_format}
        if options:
            data["options"] = options
        
        return await self._arequest("POST", "/odin/translate", files=files, json=data)

    # Registry endpoints
    def registry_put(
        self,
        key: str,
        odin_data: bytes,
        metadata: Optional[Dict[str, Any]] = None,
        ttl: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Store ODIN file in registry.
        
        Args:
            key: Registry key
            odin_data: ODIN file binary data
            metadata: Optional metadata
            ttl: Time to live in seconds
            
        Returns:
            Storage result
        """
        files = {"odin_file": ("file.odin", odin_data, "application/octet-stream")}
        data = {"key": key}
        if metadata:
            data["metadata"] = metadata
        if ttl:
            data["ttl"] = ttl
        
        return self._request("POST", "/registry/put", files=files, json=data)

    async def aregistry_put(
        self,
        key: str,
        odin_data: bytes,
        metadata: Optional[Dict[str, Any]] = None,
        ttl: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Async version of registry_put."""
        files = {"odin_file": ("file.odin", odin_data, "application/octet-stream")}
        data = {"key": key}
        if metadata:
            data["metadata"] = metadata
        if ttl:
            data["ttl"] = ttl
        
        return await self._arequest("POST", "/registry/put", files=files, json=data)

    def registry_get(self, key: str) -> Dict[str, Any]:
        """
        Retrieve ODIN file from registry.
        
        Args:
            key: Registry key
            
        Returns:
            ODIN file data and metadata
        """
        return self._request("GET", f"/registry/get/{key}")

    async def aregistry_get(self, key: str) -> Dict[str, Any]:
        """Async version of registry_get."""
        return await self._arequest("GET", f"/registry/get/{key}")

    def registry_index(
        self,
        prefix: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        List registry entries.
        
        Args:
            prefix: Key prefix filter
            limit: Maximum number of entries
            offset: Pagination offset
            
        Returns:
            Registry index
        """
        params = {"limit": limit, "offset": offset}
        if prefix:
            params["prefix"] = prefix
        
        return self._request("GET", "/registry/index", params=params)

    async def aregistry_index(
        self,
        prefix: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Async version of registry_index."""
        params = {"limit": limit, "offset": offset}
        if prefix:
            params["prefix"] = prefix
        
        return await self._arequest("GET", "/registry/index", params=params)

    # Billing endpoints
    def billing_credits(self) -> Dict[str, Any]:
        """
        Get billing credits information.
        
        Returns:
            Credits balance and usage
        """
        return self._request("GET", "/billing/credits")

    async def abilling_credits(self) -> Dict[str, Any]:
        """Async version of billing_credits."""
        return await self._arequest("GET", "/billing/credits")

    def billing_usage(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get billing usage information.
        
        Args:
            start_date: Start date (ISO 8601)
            end_date: End date (ISO 8601)
            
        Returns:
            Usage statistics
        """
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        
        return self._request("GET", "/billing/usage", params=params if params else None)

    async def abilling_usage(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Async version of billing_usage."""
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        
        return await self._arequest("GET", "/billing/usage", params=params if params else None)
