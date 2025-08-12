"""HTTP webhook system for Gira external integrations.

Provides reliable HTTP webhook delivery with retry logic, authentication,
and integration with the existing hook system.
"""

import base64
import hashlib
import hmac
import json
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

import urllib3

from gira.utils.config import load_config
from gira.utils.console import console


class WebhookDeliveryError(Exception):
    """Exception raised when webhook delivery fails."""
    pass


class WebhookClient:
    """HTTP client for webhook delivery with retry logic and authentication."""
    
    def __init__(self):
        self.http = urllib3.PoolManager(
            timeout=urllib3.Timeout(connect=5.0, read=30.0),
            retries=False  # We handle retries manually
        )
        self.config = load_config()
        self.delivery_stats = {}  # Track delivery statistics
    
    def is_enabled(self) -> bool:
        """Check if webhooks are globally enabled."""
        return self.config.get("extensibility", {}).get("webhooks", {}).get("enabled", True)
    
    def get_endpoints(self) -> List[Dict[str, Any]]:
        """Get configured webhook endpoints."""
        return self.config.get("extensibility", {}).get("webhooks", {}).get("endpoints", [])
    
    def get_global_timeout(self) -> int:
        """Get global webhook timeout in seconds."""
        return self.config.get("extensibility", {}).get("webhooks", {}).get("timeout", 30)
    
    def get_global_retry_attempts(self) -> int:
        """Get global retry attempts."""
        return self.config.get("extensibility", {}).get("webhooks", {}).get("retry_attempts", 3)
    
    def _prepare_headers(self, endpoint: Dict[str, Any], payload: str) -> Dict[str, str]:
        """Prepare HTTP headers including authentication and signing."""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Gira-Webhook/1.0"
        }
        
        # Add custom headers from endpoint config
        if "headers" in endpoint:
            headers.update(endpoint["headers"])
        
        # Add authentication
        auth = endpoint.get("auth", {})
        auth_type = auth.get("type", "").lower()
        
        if auth_type == "bearer" and "token" in auth:
            token = self._resolve_env_var(auth["token"])
            headers["Authorization"] = f"Bearer {token}"
        elif auth_type == "api_key" and "key" in auth and "value" in auth:
            key = auth["key"]
            value = self._resolve_env_var(auth["value"])
            headers[key] = value
        elif auth_type == "basic" and "username" in auth and "password" in auth:
            username = self._resolve_env_var(auth["username"])
            password = self._resolve_env_var(auth["password"])
            credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
            headers["Authorization"] = f"Basic {credentials}"
        
        # Add webhook signature if signing is enabled
        signing_secret = self.config.get("extensibility", {}).get("webhooks", {}).get("signing_secret")
        if signing_secret:
            signing_secret = self._resolve_env_var(signing_secret)
            timestamp = str(int(time.time()))
            signature_payload = f"{timestamp}.{payload}"
            signature = hmac.new(
                signing_secret.encode(),
                signature_payload.encode(),
                hashlib.sha256
            ).hexdigest()
            headers["X-Gira-Timestamp"] = timestamp
            headers["X-Gira-Signature-256"] = f"sha256={signature}"
        
        return headers
    
    def _resolve_env_var(self, value: str) -> str:
        """Resolve environment variables in configuration values."""
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            env_var = value[2:-1]
            return os.environ.get(env_var, value)
        return value
    
    def _calculate_backoff_delay(self, attempt: int, base_delay: float = 1.0) -> float:
        """Calculate exponential backoff delay."""
        return min(base_delay * (2 ** attempt), 60.0)  # Cap at 60 seconds
    
    def deliver_webhook(self, endpoint: Dict[str, Any], payload: Dict[str, Any], 
                       silent: bool = False) -> Tuple[bool, Optional[str]]:
        """Deliver webhook to a single endpoint with retry logic.
        
        Args:
            endpoint: Webhook endpoint configuration
            payload: JSON payload to send
            silent: Whether to suppress console output
            
        Returns:
            Tuple of (success, error_message)
        """
        if not endpoint.get("enabled", True):
            return True, None  # Skip disabled endpoints
        
        url = endpoint["url"]
        name = endpoint.get("name", url)
        timeout = endpoint.get("timeout", self.get_global_timeout())
        max_attempts = endpoint.get("retry_attempts", self.get_global_retry_attempts())
        
        payload_json = json.dumps(payload, indent=2)
        headers = self._prepare_headers(endpoint, payload_json)
        
        last_error = None
        
        for attempt in range(max_attempts):
            try:
                if not silent and attempt > 0:
                    console.print(f"[dim]Retrying webhook {name} (attempt {attempt + 1}/{max_attempts})[/dim]")
                
                response = self.http.request(
                    "POST",
                    url,
                    body=payload_json.encode('utf-8'),
                    headers=headers,
                    timeout=timeout
                )
                
                if 200 <= response.status < 300:
                    if not silent:
                        console.print(f"[dim]✓ Webhook delivered to {name} ({response.status})[/dim]")
                    self._record_delivery_success(name)
                    return True, None
                else:
                    error_msg = f"HTTP {response.status}: {response.data.decode('utf-8', errors='ignore')[:200]}"
                    last_error = error_msg
                    
                    if not silent:
                        console.print(f"[yellow]Webhook {name} failed: {error_msg}[/yellow]")
                    
                    # Don't retry on client errors (4xx)
                    if 400 <= response.status < 500:
                        break
                        
            except urllib3.exceptions.TimeoutError:
                last_error = f"Request timeout after {timeout}s"
                if not silent:
                    console.print(f"[yellow]Webhook {name} timed out[/yellow]")
            except Exception as e:
                last_error = str(e)
                if not silent:
                    console.print(f"[yellow]Webhook {name} error: {e}[/yellow]")
            
            # Apply exponential backoff before retry
            if attempt < max_attempts - 1:
                delay = self._calculate_backoff_delay(attempt)
                time.sleep(delay)
        
        self._record_delivery_failure(name, last_error)
        return False, last_error
    
    def deliver_to_all_endpoints(self, event_type: str, payload: Dict[str, Any], 
                                silent: bool = False) -> Dict[str, Tuple[bool, Optional[str]]]:
        """Deliver webhook to all matching endpoints.
        
        Args:
            event_type: Type of event (e.g., 'ticket_created')
            payload: Event payload to send
            silent: Whether to suppress console output
            
        Returns:
            Dictionary mapping endpoint names to (success, error) tuples
        """
        if not self.is_enabled():
            return {}
        
        results = {}
        matching_endpoints = self._filter_endpoints_for_event(event_type, payload)
        
        if not matching_endpoints:
            return {}
        
        if not silent:
            console.print(f"[dim]Delivering webhook for {event_type} to {len(matching_endpoints)} endpoint(s)[/dim]")
        
        for endpoint in matching_endpoints:
            name = endpoint.get("name", endpoint["url"])
            success, error = self.deliver_webhook(endpoint, payload, silent)
            results[name] = (success, error)
        
        return results
    
    def _filter_endpoints_for_event(self, event_type: str, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter endpoints that should receive this event."""
        from gira.utils.webhook_filters import WebhookFilterManager
        return WebhookFilterManager.filter_endpoints_for_event(
            self.get_endpoints(), event_type, payload
        )
    
    def test_endpoint(self, endpoint_name: str, event_type: str = "test") -> Tuple[bool, Optional[str]]:
        """Test a specific webhook endpoint with a sample payload.
        
        Args:
            endpoint_name: Name of the endpoint to test
            event_type: Event type for the test payload
            
        Returns:
            Tuple of (success, error_message)
        """
        endpoints = self.get_endpoints()
        endpoint = None
        
        for ep in endpoints:
            if ep.get("name") == endpoint_name:
                endpoint = ep
                break
        
        if not endpoint:
            return False, f"Endpoint '{endpoint_name}' not found"
        
        # Create test payload
        test_payload = {
            "event": event_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "gira",
            "project": "test",
            "data": {
                "ticket": {
                    "id": "TEST-123",
                    "title": "Test webhook delivery",
                    "status": "todo",
                    "type": "task",
                    "priority": "medium",
                    "created_at": datetime.utcnow().isoformat() + "Z"
                }
            }
        }
        
        return self.deliver_webhook(endpoint, test_payload, silent=False)
    
    def _record_delivery_success(self, endpoint_name: str) -> None:
        """Record successful webhook delivery."""
        if endpoint_name not in self.delivery_stats:
            self.delivery_stats[endpoint_name] = {
                "total_attempts": 0,
                "successful_deliveries": 0,
                "failed_deliveries": 0,
                "last_success": None,
                "last_failure": None,
                "last_error": None
            }
        
        stats = self.delivery_stats[endpoint_name]
        stats["total_attempts"] += 1
        stats["successful_deliveries"] += 1
        stats["last_success"] = datetime.utcnow().isoformat() + "Z"
    
    def _record_delivery_failure(self, endpoint_name: str, error: Optional[str]) -> None:
        """Record failed webhook delivery."""
        if endpoint_name not in self.delivery_stats:
            self.delivery_stats[endpoint_name] = {
                "total_attempts": 0,
                "successful_deliveries": 0,
                "failed_deliveries": 0,
                "last_success": None,
                "last_failure": None,
                "last_error": None
            }
        
        stats = self.delivery_stats[endpoint_name]
        stats["total_attempts"] += 1
        stats["failed_deliveries"] += 1
        stats["last_failure"] = datetime.utcnow().isoformat() + "Z"
        stats["last_error"] = error
    
    def get_delivery_stats(self, endpoint_name: Optional[str] = None) -> Dict[str, Any]:
        """Get delivery statistics for webhooks."""
        if endpoint_name:
            return self.delivery_stats.get(endpoint_name, {})
        return self.delivery_stats.copy()
    
    def check_endpoint_health(self, endpoint_name: str) -> Tuple[bool, Dict[str, Any]]:
        """Check the health of a specific webhook endpoint."""
        endpoints = self.get_endpoints()
        endpoint = None
        
        for ep in endpoints:
            if ep.get("name") == endpoint_name:
                endpoint = ep
                break
        
        if not endpoint:
            return False, {"error": f"Endpoint '{endpoint_name}' not found"}
        
        url = endpoint["url"]
        timeout = endpoint.get("timeout", self.get_global_timeout())
        
        health_info = {
            "endpoint_name": endpoint_name,
            "url": url,
            "enabled": endpoint.get("enabled", True),
            "reachable": False,
            "response_time": None,
            "status_code": None,
            "error": None
        }
        
        if not endpoint.get("enabled", True):
            health_info["error"] = "Endpoint is disabled"
            return False, health_info
        
        try:
            start_time = time.time()
            
            # Simple HEAD request to check if endpoint is reachable
            response = self.http.request(
                "HEAD",
                url,
                timeout=timeout
            )
            
            response_time = time.time() - start_time
            
            health_info["reachable"] = True
            health_info["response_time"] = round(response_time * 1000, 2)  # Convert to ms
            health_info["status_code"] = response.status
            
            # Consider 2xx, 4xx as healthy (endpoint is responding)
            is_healthy = 200 <= response.status < 500
            
            if not is_healthy:
                health_info["error"] = f"HTTP {response.status}"
            
            return is_healthy, health_info
            
        except Exception as e:
            health_info["error"] = str(e)
            return False, health_info


# Global webhook client instance
_webhook_client = None


def get_webhook_client() -> WebhookClient:
    """Get the global webhook client instance."""
    global _webhook_client
    if _webhook_client is None:
        _webhook_client = WebhookClient()
    return _webhook_client


def deliver_webhook(event_type: str, payload: Dict[str, Any], silent: bool = True) -> Dict[str, Tuple[bool, Optional[str]]]:
    """Convenience function to deliver webhooks.
    
    Args:
        event_type: Type of event (e.g., 'ticket_created')
        payload: Event payload to send
        silent: Whether to suppress console output
        
    Returns:
        Dictionary mapping endpoint names to (success, error) tuples
    """
    try:
        client = get_webhook_client()
        return client.deliver_to_all_endpoints(event_type, payload, silent)
    except Exception as e:
        if not silent:
            console.print(f"[red]Webhook delivery failed: {e}[/red]")
        return {}