import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000', // Your backend API URL
  headers: {
    'Content-Type': 'application/json',
  },
});

export default {
  // Bot Management (Legacy - for backward compatibility)
  getBots() {
    return apiClient.get('/api/v1/bots');
  },
  createBot(botConfig) {
    return apiClient.post('/api/v1/bots', botConfig);
  },
  getBot(botId) {
    return apiClient.get(`/api/v1/bots/${botId}`);
  },
  deleteBot(botId) {
    return apiClient.delete(`/api/v1/bots/${botId}`);
  },

  // External Bot Management
  testBotConnection(connectionData) {
    return apiClient.post('/api/v1/external-bots/test-connection', connectionData);
  },
  connectExternalBot(botData) {
    return apiClient.post('/api/v1/external-bots/connect', botData);
  },
  getExternalBotStatus(botId) {
    return apiClient.get(`/api/v1/external-bots/${botId}/status`);
  },
  startExternalBot(botId) {
    return apiClient.post(`/api/v1/external-bots/${botId}/start`);
  },
  stopExternalBot(botId) {
    return apiClient.post(`/api/v1/external-bots/${botId}/stop`);
  },
  getExternalBotPerformance(botId) {
    return apiClient.get(`/api/v1/external-bots/${botId}/performance`);
  },
  getExternalBotTrades(botId, limit = 50) {
    return apiClient.get(`/api/v1/external-bots/${botId}/trades`, { params: { limit } });
  },
  disconnectExternalBot(botId) {
    return apiClient.delete(`/api/v1/external-bots/${botId}`);
  },
  getExternalBots() {
    return apiClient.get('/api/v1/external-bots');
  },
  deleteExternalBot(botId) {
    return apiClient.delete(`/api/v1/external-bots/${botId}`);
  },
  getExternalBotLogs(botId, tail = 100) {
    return apiClient.get(`/api/v1/external-bots/${botId}/logs`, { params: { tail } });
  },

  // Shared Bot Marketplace
  getSharedBotsMarketplace() {
    return apiClient.get('/api/v1/shared-bots/marketplace');
  },
  subscribeToSharedBot(subscriptionData) {
    return apiClient.post('/api/v1/shared-bots/subscribe', subscriptionData);
  },
  unsubscribeFromSharedBot(botId) {
    return apiClient.delete(`/api/v1/shared-bots/unsubscribe/${botId}`);
  },
  getMySharedBotSubscriptions() {
    return apiClient.get('/api/v1/shared-bots/my-subscriptions');
  },
  getSharedBotPerformance(botId) {
    return apiClient.get(`/api/v1/shared-bots/${botId}/performance`);
  },
  
  // Bot Control
  startBot(botId) {
    return apiClient.post(`/api/v1/bots/${botId}/start`);
  },
  stopBot(botId) {
    return apiClient.post(`/api/v1/bots/${botId}/stop`);
  },
  restartBot(botId) {
    return apiClient.post(`/api/v1/bots/${botId}/restart`);
  },
  
  // Bot Monitoring
  getBotLogs(botId, tail = 100) {
    return apiClient.get(`/api/v1/bots/${botId}/logs`, { params: { tail } });
  },
  getBotPerformance(botId) {
    return apiClient.get(`/api/v1/bots/${botId}/performance`);
  },
  getBotTrades(botId, limit = 50) {
    return apiClient.get(`/api/v1/bots/${botId}/trades`, { params: { limit } });
  },
  
  // Bot Configuration
  updateBotConfig(botId, config) {
    return apiClient.put(`/api/v1/bots/${botId}/config`, config);
  },
  
  // Authentication
  login(credentials) { // credentials: { username: email, password: password }
    // FastAPI's OAuth2PasswordRequestForm expects form data
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    return apiClient.post('/api/v1/auth/token', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
  },
  register(userData) { // userData: { email, password, full_name }
    return apiClient.post('/api/v1/auth/register', userData);
  },
  
  // Terminal/Bot Commands
  executeTerminalCommand(botId, command, args = []) {
    return apiClient.post(`/api/v1/external-bots/${botId}/terminal/command`, {
      command,
      args
    });
  },
  getBotStatus(botId) {
    return apiClient.get(`/api/v1/external-bots/${botId}/status`);
  },
  getBotBalance(botId) {
    return apiClient.get(`/api/v1/external-bots/${botId}/balance`);
  },
  getBotPositions(botId) {
    return apiClient.get(`/api/v1/external-bots/${botId}/positions`);
  },
  getBotConfig(botId) {
    return apiClient.get(`/api/v1/external-bots/${botId}/config`);
  },
  getBotProfit(botId) {
    return apiClient.get(`/api/v1/external-bots/${botId}/profit`);
  },
  pingBot(botId) {
    return apiClient.get(`/api/v1/external-bots/${botId}/ping`);
  },
  getBotVersion(botId) {
    return apiClient.get(`/api/v1/external-bots/${botId}/version`);
  },
  reloadBotConfig(botId) {
    return apiClient.post(`/api/v1/external-bots/${botId}/reload`);
  },

  // WebSocket for real-time terminal updates
  createTerminalWebSocket(botId, onMessage, onError, onClose) {
    const token = localStorage.getItem('authToken');
    const wsUrl = `ws://localhost:8000/api/v1/ws/bot/${botId}/${token}`;
    
    const ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
      console.log('Terminal WebSocket connected');
    };
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
        onError(error);
      }
    };
    
    ws.onerror = (error) => {
      console.error('Terminal WebSocket error:', error);
      onError(error);
    };
    
    ws.onclose = (event) => {
      console.log('Terminal WebSocket closed:', event.code, event.reason);
      onClose(event);
    };
    
    return ws;
  },

  // Utility
  setAuthHeader(token) {
    if (token) {
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      delete apiClient.defaults.headers.common['Authorization'];
    }
  }
};
