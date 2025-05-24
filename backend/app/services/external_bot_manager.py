import requests
import asyncio
import time
from typing import Dict, Optional
from datetime import datetime
import base64

from app.core.logging import get_logger, log_external_api_call

logger = get_logger("external_bot_manager")


class ExternalBotManager:
    """
    Manages connections to external trading bot instances via their REST APIs
    """
    
    def __init__(self):
        self.session = requests.Session()
        # Set both connect and read timeouts
        self.timeout = (5, 10)  # (connect_timeout, read_timeout)
    
    def _get_auth_args(self, auth_method: str, api_token: Optional[str] = None, username: Optional[str] = None, password: Optional[str] = None) -> Dict:
        """Helper method to prepare authentication arguments for method calls"""
        return {
            "auth_method": auth_method,
            "api_token": api_token,
            "username": username,
            "password": password
        }
    
    def test_bot_connection(self, api_url: str, auth_method: str = "token", api_token: Optional[str] = None, username: Optional[str] = None, password: Optional[str] = None) -> Dict:
        """
        Test connection to an external trading bot
        
        Args:
            api_url: Bot's API URL (e.g., "http://192.168.1.100:8080")
            auth_method: Authentication method ('token' or 'basic')
            api_token: Bot's API authentication token (for token auth)
            username: Username (for basic auth)
            password: Password (for basic auth)
            
        Returns:
            Dict with connection status and bot info
        """
        start_time = time.time()
        normalized_url = api_url.rstrip('/')
        
        logger.info(
            "Testing connection to external trading bot",
            extra={
                "api_url": normalized_url,
                "event_type": "bot_connection_test_start"
            }
        )
        
        try:
            headers = {'Content-Type': 'application/json'}
            
            # Set authentication headers based on method
            if auth_method == "token":
                headers['Authorization'] = f'Bearer {api_token}'
            elif auth_method == "basic":
                credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
                headers['Authorization'] = f'Basic {credentials}'
            else:
                return {
                    "success": False,
                    "status": "error",
                    "error": f"Unsupported auth method: {auth_method}",
                    "message": "Invalid authentication method"
                }
            
            # Test basic connectivity with /api/v1/ping
            ping_start = time.time()
            response = self.session.get(
                f"{normalized_url}/api/v1/ping",
                headers=headers,
                timeout=self.timeout
            )
            ping_duration = (time.time() - ping_start) * 1000
            
            log_external_api_call(
                service="trading_bot",
                endpoint="/api/v1/ping",
                method="GET",
                status_code=response.status_code,
                duration_ms=ping_duration,
                api_url=normalized_url
            )
            
            if response.status_code == 200:
                # Get bot status and info
                status_start = time.time()
                status_response = self.session.get(
                    f"{normalized_url}/api/v1/status",
                    headers=headers,
                    timeout=self.timeout
                )
                status_duration = (time.time() - status_start) * 1000
                
                log_external_api_call(
                    service="trading_bot",
                    endpoint="/api/v1/status",
                    method="GET",
                    status_code=status_response.status_code,
                    duration_ms=status_duration,
                    api_url=normalized_url
                )
                
                if status_response.status_code == 200:
                    bot_info = status_response.json()
                    total_duration = (time.time() - start_time) * 1000
                    
                    logger.info(
                        "Bot connection test successful",
                        extra={
                            "api_url": normalized_url,
                            "event_type": "bot_connection_test_success",
                            "total_duration_ms": total_duration,
                            "bot_info": bot_info
                        }
                    )
                    
                    return {
                        "success": True,
                        "status": "connected",
                        "bot_info": bot_info,
                        "message": "Successfully connected to trading bot"
                    }
                else:
                    logger.warning(
                        "Bot ping successful but status failed",
                        extra={
                            "api_url": normalized_url,
                            "event_type": "bot_connection_test_partial_failure",
                            "ping_status": response.status_code,
                            "status_status": status_response.status_code
                        }
                    )
                    
                    return {
                        "success": False,
                        "status": "error",
                        "error": f"Failed to get bot status: {status_response.status_code}",
                        "message": "Bot ping successful but status failed"
                    }
            else:
                logger.warning(
                    "Failed to connect to trading bot",
                    extra={
                        "api_url": normalized_url,
                        "event_type": "bot_connection_test_failure",
                        "status_code": response.status_code
                    }
                )
                
                return {
                    "success": False,
                    "status": "error", 
                    "error": f"Connection failed: {response.status_code}",
                    "message": "Failed to connect to trading bot"
                }
                
        except requests.exceptions.ConnectTimeout:
            logger.warning(
                "Bot connection test timed out",
                extra={
                    "api_url": normalized_url,
                    "event_type": "bot_connection_test_timeout",
                    "timeout_seconds": self.timeout[0]
                }
            )
            
            return {
                "success": False,
                "status": "error",
                "error": "Connection timeout",
                "message": "Bot did not respond within timeout period"
            }
        except requests.exceptions.ConnectionError as e:
            logger.warning(
                "Bot connection test failed with connection error",
                extra={
                    "api_url": normalized_url,
                    "event_type": "bot_connection_test_connection_error",
                    "error": str(e)
                }
            )
            
            return {
                "success": False,
                "status": "error",
                "error": "Connection error",
                "message": "Could not connect to bot - check URL and network"
            }
        except Exception as e:
            logger.error(
                "Bot connection test failed with unexpected error",
                extra={
                    "api_url": normalized_url,
                    "event_type": "bot_connection_test_error",
                    "error": str(e)
                },
                exc_info=True
            )
            
            return {
                "success": False,
                "status": "error",
                "error": str(e),
                "message": "Unexpected error during connection test"
            }
    
    def get_bot_status(self, api_url: str, auth_method: str = "token", api_token: Optional[str] = None, username: Optional[str] = None, password: Optional[str] = None) -> Dict:
        """Get current status of an external bot"""
        try:
            api_url = api_url.rstrip('/')
            headers = {}
            
            # Set authentication headers
            if auth_method == "token":
                headers['Authorization'] = f'Bearer {api_token}'
            elif auth_method == "basic":
                credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
                headers['Authorization'] = f'Basic {credentials}'
            
            response = self.session.get(
                f"{api_url}/api/v1/status",
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json(),
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "message": "Failed to get bot status"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Error getting bot status"
            }
    
    def get_bot_performance(self, api_url: str, auth_method: str = "token", api_token: Optional[str] = None, username: Optional[str] = None, password: Optional[str] = None) -> Dict:
        """Get performance metrics from external bot"""
        try:
            api_url = api_url.rstrip('/')
            headers = {}
            
            # Set authentication headers
            if auth_method == "token":
                headers['Authorization'] = f'Bearer {api_token}'
            elif auth_method == "basic":
                credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
                headers['Authorization'] = f'Basic {credentials}'
            
            # Get performance data
            response = self.session.get(
                f"{api_url}/api/v1/performance",
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json(),
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "message": "Failed to get performance data"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Error getting performance data"
            }
    
    def get_bot_trades(self, api_url: str, auth_method: str = "token", api_token: Optional[str] = None, username: Optional[str] = None, password: Optional[str] = None, limit: int = 50) -> Dict:
        """Get trade history from external bot"""
        try:
            api_url = api_url.rstrip('/')
            headers = {}
            
            # Set authentication headers
            if auth_method == "token":
                headers['Authorization'] = f'Bearer {api_token}'
            elif auth_method == "basic":
                credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
                headers['Authorization'] = f'Basic {credentials}'
            
            response = self.session.get(
                f"{api_url}/api/v1/trades",
                headers=headers,
                params={'limit': limit},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json(),
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "message": "Failed to get trades"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Error getting trades"
            }
    
    def start_bot(self, api_url: str, auth_method: str = "token", api_token: Optional[str] = None, username: Optional[str] = None, password: Optional[str] = None) -> Dict:
        """Start an external bot"""
        try:
            api_url = api_url.rstrip('/')
            headers = {}
            
            # Set authentication headers
            if auth_method == "token":
                headers['Authorization'] = f'Bearer {api_token}'
            elif auth_method == "basic":
                credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
                headers['Authorization'] = f'Basic {credentials}'
            
            response = self.session.post(
                f"{api_url}/api/v1/start",
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "Bot start command sent successfully",
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "message": "Failed to start bot"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Error starting bot"
            }
    
    def stop_bot(self, api_url: str, auth_method: str = "token", api_token: Optional[str] = None, username: Optional[str] = None, password: Optional[str] = None) -> Dict:
        """Stop an external bot"""
        try:
            api_url = api_url.rstrip('/')
            headers = {}
            
            # Set authentication headers
            if auth_method == "token":
                headers['Authorization'] = f'Bearer {api_token}'
            elif auth_method == "basic":
                credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
                headers['Authorization'] = f'Basic {credentials}'
            
            response = self.session.post(
                f"{api_url}/api/v1/stop",
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "Bot stop command sent successfully",
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "message": "Failed to stop bot"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Error stopping bot"
            }
    
    def get_bot_logs(self, api_url: str, auth_method: str = "token", api_token: Optional[str] = None, username: Optional[str] = None, password: Optional[str] = None, lines: int = 100) -> Dict:
        """Get logs from external bot"""
        try:
            api_url = api_url.rstrip('/')
            headers = {}
            
            # Set authentication headers
            if auth_method == "token":
                headers['Authorization'] = f'Bearer {api_token}'
            elif auth_method == "basic":
                credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
                headers['Authorization'] = f'Basic {credentials}'
            
            response = self.session.get(
                f"{api_url}/api/v1/logs",
                headers=headers,
                params={'lines': lines},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json(),
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}", 
                    "message": "Failed to get logs"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Error getting logs"
            }
    
    async def ping_bot(self, api_url: str, auth_method: str = "token", api_token: Optional[str] = None, username: Optional[str] = None, password: Optional[str] = None) -> Dict:
        """Async ping to check bot health"""
        try:
            api_url = api_url.rstrip('/')
            headers = {}
            
            # Set authentication headers
            if auth_method == "token":
                headers['Authorization'] = f'Bearer {api_token}'
            elif auth_method == "basic":
                credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
                headers['Authorization'] = f'Basic {credentials}'
            
            # Use asyncio to make this non-blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.session.get(f"{api_url}/api/v1/ping", headers=headers, timeout=self.timeout)
            )
            
            return {
                "success": response.status_code == 200,
                "timestamp": datetime.utcnow().isoformat(),
                "response_time": response.elapsed.total_seconds() if hasattr(response, 'elapsed') else None
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }