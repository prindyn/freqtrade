import requests
import logging
import asyncio
from typing import Dict, List, Optional, Union
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class ExternalBotManager:
    """
    Manages connections to external FreqTrade bot instances via their REST APIs
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = 10  # 10 second timeout for API calls
    
    def test_bot_connection(self, api_url: str, api_token: str) -> Dict:
        """
        Test connection to an external FreqTrade bot
        
        Args:
            api_url: Bot's API URL (e.g., "http://192.168.1.100:8080")
            api_token: Bot's API authentication token
            
        Returns:
            Dict with connection status and bot info
        """
        try:
            # Normalize URL
            api_url = api_url.rstrip('/')
            
            headers = {
                'Authorization': f'Bearer {api_token}',
                'Content-Type': 'application/json'
            }
            
            # Test basic connectivity with /api/v1/ping
            response = self.session.get(
                f"{api_url}/api/v1/ping",
                headers=headers
            )
            
            if response.status_code == 200:
                # Get bot status and info
                status_response = self.session.get(
                    f"{api_url}/api/v1/status",
                    headers=headers
                )
                
                if status_response.status_code == 200:
                    bot_info = status_response.json()
                    return {
                        "success": True,
                        "status": "connected",
                        "bot_info": bot_info,
                        "message": "Successfully connected to FreqTrade bot"
                    }
                else:
                    return {
                        "success": False,
                        "status": "error",
                        "error": f"Failed to get bot status: {status_response.status_code}",
                        "message": "Bot ping successful but status failed"
                    }
            else:
                return {
                    "success": False,
                    "status": "error", 
                    "error": f"Connection failed: {response.status_code}",
                    "message": "Failed to connect to FreqTrade bot"
                }
                
        except requests.exceptions.ConnectTimeout:
            return {
                "success": False,
                "status": "error",
                "error": "Connection timeout",
                "message": "Bot did not respond within timeout period"
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "status": "error",
                "error": "Connection error",
                "message": "Could not connect to bot - check URL and network"
            }
        except Exception as e:
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