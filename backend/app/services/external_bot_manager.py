import requests
import asyncio
import time
from typing import Dict, List, Optional, Union
from datetime import datetime
import json

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
    
    def test_bot_connection(self, api_url: str, api_token: str) -> Dict:
        """
        Test connection to an external trading bot
        
        Args:
            api_url: Bot's API URL (e.g., "http://192.168.1.100:8080")
            api_token: Bot's API authentication token
            
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
            headers = {
                'Authorization': f'Bearer {api_token}',
                'Content-Type': 'application/json'
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
    
    def get_bot_status(self, api_url: str, api_token: str) -> Dict:
        """Get current status of an external bot"""
        try:
            api_url = api_url.rstrip('/')
            headers = {'Authorization': f'Bearer {api_token}'}
            
            response = self.session.get(
                f"{api_url}/api/v1/status",
                headers=headers
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
    
    def get_bot_performance(self, api_url: str, api_token: str) -> Dict:
        """Get performance metrics from external bot"""
        try:
            api_url = api_url.rstrip('/')
            headers = {'Authorization': f'Bearer {api_token}'}
            
            # Get performance data
            response = self.session.get(
                f"{api_url}/api/v1/performance",
                headers=headers
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
    
    def get_bot_trades(self, api_url: str, api_token: str, limit: int = 50) -> Dict:
        """Get trade history from external bot"""
        try:
            api_url = api_url.rstrip('/')
            headers = {'Authorization': f'Bearer {api_token}'}
            
            response = self.session.get(
                f"{api_url}/api/v1/trades",
                headers=headers,
                params={'limit': limit}
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
    
    def start_bot(self, api_url: str, api_token: str) -> Dict:
        """Start an external bot"""
        try:
            api_url = api_url.rstrip('/')
            headers = {'Authorization': f'Bearer {api_token}'}
            
            response = self.session.post(
                f"{api_url}/api/v1/start",
                headers=headers
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
    
    def stop_bot(self, api_url: str, api_token: str) -> Dict:
        """Stop an external bot"""
        try:
            api_url = api_url.rstrip('/')
            headers = {'Authorization': f'Bearer {api_token}'}
            
            response = self.session.post(
                f"{api_url}/api/v1/stop",
                headers=headers
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
    
    def get_bot_logs(self, api_url: str, api_token: str, lines: int = 100) -> Dict:
        """Get logs from external bot"""
        try:
            api_url = api_url.rstrip('/')
            headers = {'Authorization': f'Bearer {api_token}'}
            
            response = self.session.get(
                f"{api_url}/api/v1/logs",
                headers=headers,
                params={'lines': lines}
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
    
    async def ping_bot(self, api_url: str, api_token: str) -> Dict:
        """Async ping to check bot health"""
        try:
            api_url = api_url.rstrip('/')
            headers = {'Authorization': f'Bearer {api_token}'}
            
            # Use asyncio to make this non-blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.session.get(f"{api_url}/api/v1/ping", headers=headers)
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