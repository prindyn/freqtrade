<template>
    <div class="terminal-page">
        <!-- Terminal Header -->
        <div class="terminal-header">
            <div class="header-left">
                <h1 class="terminal-title">
                    <i class="pi pi-desktop"></i>
                    Bot Terminal
                </h1>
                <p class="terminal-subtitle">Direct command-line interface to your trading bots</p>
            </div>
            <div class="header-controls">
                <!-- Bot Selector -->
                <div class="bot-selector">
                    <label for="botSelect" class="selector-label">Select Bot:</label>
                    <select id="botSelect" v-model="selectedBot" @change="switchBot" class="bot-select">
                        <option value="">Choose a bot...</option>
                        <option v-for="bot in availableBots" :key="bot.id" :value="bot.id">
                            {{ bot.name }} ({{ bot.status }})
                        </option>
                    </select>
                </div>
                <!-- Connection Status -->
                <div class="connection-status" :class="connectionStatus">
                    <i class="pi" :class="statusIcon"></i>
                    <span>{{ statusText }}</span>
                </div>
            </div>
        </div>

        <!-- Terminal Container -->
        <div class="terminal-container">
            <!-- Terminal Output -->
            <div ref="terminalOutput" class="terminal-output" @click="focusInput">
                <!-- Welcome Message -->
                <div v-if="terminalHistory.length === 0" class="welcome-message">
                    <div class="ascii-art">
                        ╔════════════════════════════════════════╗
                        ║ TradeWise Terminal ║
                        ║ Bot Command Interface ║
                        ╚════════════════════════════════════════╝
                    </div>
                    <div class="welcome-text">
                        <p>Welcome to the TradeWise Bot Terminal!</p>
                        <p>Type <span class="command-highlight">help</span> to see available commands.</p>
                        <p>Select a bot from the dropdown above to get started.</p>
                    </div>
                </div>

                <!-- Terminal History -->
                <div v-for="(entry, index) in terminalHistory" :key="index" class="terminal-entry">
                    <div v-if="entry.type === 'command'" class="command-line">
                        <span class="prompt">{{ currentPrompt }}</span>
                        <span class="command-text">{{ entry.content }}</span>
                    </div>
                    <div v-else-if="entry.type === 'output'" class="output-line" :class="entry.level">
                        <pre>{{ entry.content }}</pre>
                    </div>
                    <div v-else-if="entry.type === 'error'" class="error-line">
                        <i class="pi pi-exclamation-triangle"></i>
                        <span>{{ entry.content }}</span>
                    </div>
                    <div v-else-if="entry.type === 'info'" class="info-line">
                        <i class="pi pi-info-circle"></i>
                        <span>{{ entry.content }}</span>
                    </div>
                    <div v-else-if="entry.type === 'success'" class="success-line">
                        <i class="pi pi-check-circle"></i>
                        <span>{{ entry.content }}</span>
                    </div>
                </div>

                <!-- Current Input Line -->
                <div v-if="selectedBot" class="input-line">
                    <span class="prompt">{{ currentPrompt }}</span>
                    <input ref="terminalInput" v-model="currentCommand" @keydown="handleKeyDown" @keyup="handleKeyUp"
                        class="command-input" :disabled="isExecuting" autocomplete="off" spellcheck="false" />
                    <span v-if="isExecuting" class="executing-indicator">
                        <i class="pi pi-spin pi-spinner"></i>
                    </span>
                </div>

                <!-- No Bot Selected Message -->
                <div v-else class="no-bot-message">
                    <i class="pi pi-exclamation-triangle"></i>
                    <span>Please select a bot to start using the terminal</span>
                </div>
            </div>

            <!-- Terminal Footer -->
            <div class="terminal-footer">
                <div class="footer-left">
                    <div class="terminal-info">
                        <span class="info-item">
                            <i class="pi pi-clock"></i>
                            Connected: {{ connectionTime }}
                        </span>
                        <span class="info-item">
                            <i class="pi pi-chart-line"></i>
                            Commands: {{ commandCount }}
                        </span>
                    </div>
                </div>
                <div class="footer-right">
                    <button @click="clearTerminal" class="footer-btn" title="Clear Terminal">
                        <i class="pi pi-trash"></i>
                        Clear
                    </button>
                    <button @click="exportLogs" class="footer-btn" title="Export Logs">
                        <i class="pi pi-download"></i>
                        Export
                    </button>
                    <button @click="toggleFullscreen" class="footer-btn" title="Toggle Fullscreen">
                        <i class="pi" :class="isFullscreen ? 'pi-compress' : 'pi-expand'"></i>
                        {{ isFullscreen ? 'Exit' : 'Fullscreen' }}
                    </button>
                </div>
            </div>
        </div>

        <!-- Command Suggestions -->
        <div v-if="showSuggestions && filteredSuggestions.length > 0" class="command-suggestions">
            <div v-for="(suggestion, index) in filteredSuggestions" :key="index" @click="selectSuggestion(suggestion)"
                class="suggestion-item" :class="{ active: selectedSuggestionIndex === index }">
                <span class="suggestion-command">{{ suggestion.command }}</span>
                <span class="suggestion-description">{{ suggestion.description }}</span>
            </div>
        </div>
    </div>
</template>

<script>
import api from '@/services/api';

export default {
    name: 'TerminalView',
    data() {
        return {
            selectedBot: '',
            currentCommand: '',
            terminalHistory: [],
            commandHistory: [],
            commandHistoryIndex: -1,
            isExecuting: false,
            connectionStatus: 'disconnected', // connected, connecting, disconnected, error
            connectionTime: '--:--',
            commandCount: 0,
            isFullscreen: false,
            showSuggestions: false,
            selectedSuggestionIndex: 0,
            availableBots: [],
            websocket: null,
            connectionStartTime: null,
            commandSuggestions: [
                { command: 'help', description: 'Show available commands' },
                { command: 'status', description: 'Show bot status information' },
                { command: 'start', description: 'Start the trading bot' },
                { command: 'stop', description: 'Stop the trading bot' },
                { command: 'restart', description: 'Restart the trading bot' },
                { command: 'balance', description: 'Show account balance' },
                { command: 'positions', description: 'Show open positions' },
                { command: 'trades', description: 'Show recent trades' },
                { command: 'profit', description: 'Show profit summary' },
                { command: 'config', description: 'Show bot configuration' },
                { command: 'logs', description: 'Show recent log entries' },
                { command: 'reload', description: 'Reload bot configuration' },
                { command: 'version', description: 'Show bot version information' },
                { command: 'ping', description: 'Test connection to bot' },
                { command: 'clear', description: 'Clear terminal output' },
                { command: 'exit', description: 'Disconnect from current bot' }
            ]
        }
    },
    computed: {
        currentPrompt() {
            if (!this.selectedBot) return '';
            const botName = this.availableBots.find(b => b.id === this.selectedBot)?.name || 'bot';
            return `${botName.toLowerCase().replace(/\s+/g, '-')}@tradewise:~$ `;
        },
        statusIcon() {
            switch (this.connectionStatus) {
                case 'connected': return 'pi-check-circle';
                case 'connecting': return 'pi-spin pi-spinner';
                case 'error': return 'pi-exclamation-triangle';
                default: return 'pi-times-circle';
            }
        },
        statusText() {
            switch (this.connectionStatus) {
                case 'connected': return 'Connected';
                case 'connecting': return 'Connecting...';
                case 'error': return 'Connection Error';
                default: return 'Disconnected';
            }
        },
        filteredSuggestions() {
            if (!this.currentCommand.trim()) return [];
            return this.commandSuggestions.filter(suggestion =>
                suggestion.command.toLowerCase().startsWith(this.currentCommand.toLowerCase())
            ).slice(0, 5);
        }
    },
    async mounted() {
        this.focusInput();
        this.updateConnectionTime();
        setInterval(this.updateConnectionTime, 1000);

        // Handle fullscreen events
        document.addEventListener('fullscreenchange', this.handleFullscreenChange);
        document.addEventListener('webkitfullscreenchange', this.handleFullscreenChange);

        // Load available bots from server
        await this.loadAvailableBots();
        
        // Check if bot is pre-selected via query parameter
        if (this.$route.query.bot) {
            this.selectedBot = this.$route.query.bot;
            await this.switchBot();
        }
    },
    beforeUnmount() {
        document.removeEventListener('fullscreenchange', this.handleFullscreenChange);
        document.removeEventListener('webkitfullscreenchange', this.handleFullscreenChange);

        // Close WebSocket connection
        if (this.websocket) {
            this.websocket.close();
        }
    },
    methods: {
        focusInput() {
            this.$nextTick(() => {
                if (this.$refs.terminalInput) {
                    this.$refs.terminalInput.focus();
                }
            });
        },
        handleKeyDown(event) {
            switch (event.key) {
                case 'Enter':
                    event.preventDefault();
                    this.executeCommand();
                    break;
                case 'ArrowUp':
                    event.preventDefault();
                    this.navigateHistory('up');
                    break;
                case 'ArrowDown':
                    event.preventDefault();
                    this.navigateHistory('down');
                    break;
                case 'Tab':
                    event.preventDefault();
                    this.handleTabCompletion();
                    break;
                case 'Escape':
                    this.hideSuggestions();
                    break;
            }
        },
        handleKeyUp(event) {
            if (event.key === 'ArrowUp' || event.key === 'ArrowDown') return;

            if (this.currentCommand.trim()) {
                this.showSuggestions = true;
                this.selectedSuggestionIndex = 0;
            } else {
                this.hideSuggestions();
            }
        },
        navigateHistory(direction) {
            if (this.commandHistory.length === 0) return;

            if (direction === 'up') {
                if (this.commandHistoryIndex < this.commandHistory.length - 1) {
                    this.commandHistoryIndex++;
                }
            } else {
                if (this.commandHistoryIndex > -1) {
                    this.commandHistoryIndex--;
                }
            }

            if (this.commandHistoryIndex === -1) {
                this.currentCommand = '';
            } else {
                this.currentCommand = this.commandHistory[this.commandHistory.length - 1 - this.commandHistoryIndex];
            }
        },
        handleTabCompletion() {
            if (this.filteredSuggestions.length > 0) {
                this.selectSuggestion(this.filteredSuggestions[0]);
            }
        },
        selectSuggestion(suggestion) {
            this.currentCommand = suggestion.command;
            this.hideSuggestions();
            this.focusInput();
        },
        hideSuggestions() {
            this.showSuggestions = false;
            this.selectedSuggestionIndex = 0;
        },
        async executeCommand() {
            if (!this.currentCommand.trim() || this.isExecuting) return;

            const command = this.currentCommand.trim();

            // Add command to history
            this.terminalHistory.push({
                type: 'command',
                content: command,
                timestamp: new Date()
            });

            this.commandHistory.unshift(command);
            this.commandHistoryIndex = -1;
            this.commandCount++;

            // Clear input
            this.currentCommand = '';
            this.hideSuggestions();

            // Execute command
            this.isExecuting = true;
            await this.processCommand(command);
            this.isExecuting = false;

            // Scroll to bottom
            this.$nextTick(() => {
                this.scrollToBottom();
                this.focusInput();
            });
        },
        async processCommand(command) {
            const [cmd, ...args] = command.split(' ');

            try {
                switch (cmd.toLowerCase()) {
                    case 'help':
                        this.showHelp();
                        break;
                    case 'clear':
                        this.clearTerminal();
                        break;
                    case 'status':
                        await this.getBotStatusReal();
                        break;
                    case 'start':
                        await this.startBotReal();
                        break;
                    case 'stop':
                        await this.stopBotReal();
                        break;
                    case 'restart':
                        await this.restartBotReal();
                        break;
                    case 'balance':
                        await this.getBalanceReal();
                        break;
                    case 'positions':
                        await this.getPositionsReal();
                        break;
                    case 'trades':
                        await this.getTradesReal(args[0]);
                        break;
                    case 'profit':
                        await this.getProfitReal();
                        break;
                    case 'config':
                        await this.getConfigReal();
                        break;
                    case 'logs':
                        await this.getLogsReal(args[0]);
                        break;
                    case 'ping':
                        await this.pingBotReal();
                        break;
                    case 'version':
                        await this.getVersionReal();
                        break;
                    case 'reload':
                        await this.reloadBotConfig();
                        break;
                    case 'exit':
                        this.disconnectFromBot();
                        break;
                    default:
                        // Try to execute as a generic command
                        await this.executeGenericCommand(cmd, args);
                }
            } catch (error) {
                this.addError(`Error executing command: ${error.response?.data?.detail || error.message}`);
            }
        },
        showHelp() {
            const helpText = `
Available Commands:
──────────────────

System Commands:
  help              Show this help message
  clear             Clear terminal output
  ping              Test connection to bot
  version           Show bot version information
  exit              Disconnect from current bot

Bot Control:
  status            Show bot status and information
  start             Start the trading bot
  stop              Stop the trading bot
  restart           Restart the trading bot
  config            Show bot configuration
  reload            Reload bot configuration

Trading Information:
  balance           Show account balance
  positions         Show open positions
  trades [limit]    Show recent trades (default: 10)
  profit            Show profit summary
  logs [level]      Show recent log entries

Real-time Features:
  • Live bot status updates via WebSocket
  • Real-time trade notifications
  • Instant log streaming
  • Connection status monitoring

Navigation:
  ↑/↓               Navigate command history
  Tab               Auto-complete commands
  Ctrl+L            Clear terminal

Note: Commands are executed directly on the selected bot server.
            `;
            this.addOutput(helpText);
        },
        // Real server communication methods
        async loadAvailableBots() {
            try {
                const response = await api.getExternalBots();
                this.availableBots = response.data.map(bot => ({
                    id: bot.id,
                    name: bot.name,
                    status: bot.status
                }));
            } catch (error) {
                console.error('Failed to load bots:', error);
                this.addError('Failed to load available bots from server');
            }
        },

        async executeGenericCommand(command, args) {
            try {
                const response = await api.executeTerminalCommand(this.selectedBot, command, args);
                this.addOutput(response.data.output || response.data.message || 'Command executed successfully');
            } catch (error) {
                throw error;
            }
        },

        async getBotStatusReal() {
            try {
                const response = await api.getBotStatus(this.selectedBot);
                const status = response.data;

                const statusInfo = `
Bot Status Information:
─────────────────────

Name:           ${status.name || 'Unknown'}
Status:         ${status.status?.toUpperCase() || 'UNKNOWN'}
Uptime:         ${status.uptime || 'Unknown'}
Strategy:       ${status.strategy || 'Unknown'}
Pair:           ${status.pair || 'Unknown'}
Balance:        ${status.balance || 'Unknown'}
Open Trades:    ${status.open_trades || 0}
Total Trades:   ${status.total_trades || 0}
Win Rate:       ${status.win_rate || 0}%
Last Update:    ${new Date().toLocaleString()}
                `;
                this.addOutput(statusInfo);
            } catch (error) {
                throw error;
            }
        },

        async startBotReal() {
            try {
                this.addInfo('Starting trading bot...');
                const response = await api.startExternalBot(this.selectedBot);
                this.addSuccess(response.data.message || 'Bot started successfully');

                // Update local bot status
                const bot = this.availableBots.find(b => b.id === this.selectedBot);
                if (bot) bot.status = 'running';
            } catch (error) {
                throw error;
            }
        },

        async stopBotReal() {
            try {
                this.addInfo('Stopping trading bot...');
                const response = await api.stopExternalBot(this.selectedBot);
                this.addSuccess(response.data.message || 'Bot stopped successfully');

                // Update local bot status
                const bot = this.availableBots.find(b => b.id === this.selectedBot);
                if (bot) bot.status = 'stopped';
            } catch (error) {
                throw error;
            }
        },

        async restartBotReal() {
            try {
                this.addInfo('Restarting trading bot...');
                await api.stopExternalBot(this.selectedBot);
                await new Promise(resolve => setTimeout(resolve, 1000));
                await api.startExternalBot(this.selectedBot);
                this.addSuccess('Bot restarted successfully');
            } catch (error) {
                throw error;
            }
        },

        async getBalanceReal() {
            try {
                const response = await api.getBotBalance(this.selectedBot);
                const balance = response.data;

                let balanceInfo = `
Account Balance:
───────────────

Total Balance:    ${balance.total || 'Unknown'}
Available:        ${balance.available || 'Unknown'}
In Orders:        ${balance.in_orders || 'Unknown'}
Unrealized P&L:   ${balance.unrealized_pnl || 'Unknown'}
                `;

                if (balance.assets && balance.assets.length > 0) {
                    balanceInfo += '\nAsset Breakdown:\n';
                    balance.assets.forEach(asset => {
                        balanceInfo += `${asset.currency}:${' '.repeat(15 - asset.currency.length)}${asset.amount} ${asset.currency}  (${asset.value || 'Unknown'})\n`;
                    });
                }

                this.addOutput(balanceInfo);
            } catch (error) {
                throw error;
            }
        },

        async getPositionsReal() {
            try {
                const response = await api.getBotPositions(this.selectedBot);
                const positions = response.data;

                if (!positions || positions.length === 0) {
                    this.addOutput('No open positions');
                    return;
                }

                let positionsInfo = `
Open Positions:
──────────────

`;
                let totalPnl = 0;

                positions.forEach(pos => {
                    const pnlPercent = pos.unrealized_pnl_percent || 0;
                    totalPnl += parseFloat(pos.unrealized_pnl || 0);

                    positionsInfo += `${pos.pair}  ${pos.side?.toUpperCase()}   ${pos.amount}    $${pos.entry_price}   $${pos.current_price}   ${pnlPercent > 0 ? '+' : ''}${pnlPercent}%   ${pos.duration || 'Unknown'}\n`;
                });

                positionsInfo += `\nTotal Unrealized P&L: ${totalPnl > 0 ? '+' : ''}$${totalPnl.toFixed(2)}`;

                this.addOutput(positionsInfo);
            } catch (error) {
                throw error;
            }
        },

        async getTradesReal(limit = '10') {
            try {
                const response = await api.getBotTrades(this.selectedBot, parseInt(limit));
                const trades = response.data;

                if (!trades || trades.length === 0) {
                    this.addOutput('No recent trades');
                    return;
                }

                let tradesInfo = `
Recent Trades (Last ${limit}):
─────────────────────────

`;
                let totalProfit = 0;

                trades.forEach(trade => {
                    const profit = parseFloat(trade.profit_percent || 0);
                    totalProfit += profit;

                    tradesInfo += `${trade.pair}  ${trade.side?.toUpperCase()}  ${trade.amount}  $${trade.price}  ${profit > 0 ? '+' : ''}${profit.toFixed(2)}%   ${trade.duration || 'Unknown'}\n`;
                });

                tradesInfo += `\nTotal Profit: ${totalProfit > 0 ? '+' : ''}$${totalProfit.toFixed(2)}`;

                this.addOutput(tradesInfo);
            } catch (error) {
                throw error;
            }
        },

        async getProfitReal() {
            try {
                const response = await api.getBotProfit(this.selectedBot);
                const profit = response.data;

                const profitInfo = `
Profit Summary:
──────────────

Today:           ${profit.today || 'Unknown'}
This Week:       ${profit.this_week || 'Unknown'}
This Month:      ${profit.this_month || 'Unknown'}
All Time:        ${profit.all_time || 'Unknown'}

Best Trade:      ${profit.best_trade || 'Unknown'}
Worst Trade:     ${profit.worst_trade || 'Unknown'}
Win Rate:        ${profit.win_rate || 0}%
Average Trade:   ${profit.avg_trade || 'Unknown'}
                `;
                this.addOutput(profitInfo);
            } catch (error) {
                throw error;
            }
        },

        async getConfigReal() {
            try {
                const response = await api.getBotConfig(this.selectedBot);
                const config = response.data;

                let configInfo = `
Bot Configuration:
─────────────────

`;
                Object.entries(config).forEach(([key, value]) => {
                    const formattedKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                    configInfo += `${formattedKey}:${' '.repeat(20 - formattedKey.length)}${value}\n`;
                });

                this.addOutput(configInfo);
            } catch (error) {
                throw error;
            }
        },

        async getLogsReal(level = 'info') {
            try {
                const response = await api.getExternalBotLogs(this.selectedBot, 20);
                const logs = response.data;

                if (!logs || logs.length === 0) {
                    this.addOutput('No recent log entries');
                    return;
                }

                let logsInfo = `
Recent Log Entries (${level}):
─────────────────────────────

`;
                logs.forEach(log => {
                    logsInfo += `[${log.timestamp}] ${log.level}: ${log.message}\n`;
                });

                this.addOutput(logsInfo);
            } catch (error) {
                throw error;
            }
        },

        async pingBotReal() {
            try {
                const startTime = Date.now();
                await api.pingBot(this.selectedBot);
                const latency = Date.now() - startTime;
                this.addSuccess(`PONG - Bot is responding (latency: ${latency}ms)`);
            } catch (error) {
                throw error;
            }
        },

        async getVersionReal() {
            try {
                const response = await api.getBotVersion(this.selectedBot);
                const version = response.data;

                let versionInfo = `
Version Information:
───────────────────

`;
                Object.entries(version).forEach(([key, value]) => {
                    const formattedKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                    versionInfo += `${formattedKey}:${' '.repeat(20 - formattedKey.length)}${value}\n`;
                });

                this.addOutput(versionInfo);
            } catch (error) {
                throw error;
            }
        },

        async reloadBotConfig() {
            try {
                this.addInfo('Reloading bot configuration...');
                const response = await api.reloadBotConfig(this.selectedBot);
                this.addSuccess(response.data.message || 'Configuration reloaded successfully');
            } catch (error) {
                throw error;
            }
        },
        async switchBot() {
            // Close existing WebSocket if any
            if (this.websocket) {
                this.websocket.close();
                this.websocket = null;
            }

            if (!this.selectedBot) {
                this.connectionStatus = 'disconnected';
                this.connectionStartTime = null;
                return;
            }

            this.connectionStatus = 'connecting';
            const botName = this.availableBots.find(b => b.id === this.selectedBot)?.name;
            this.addInfo(`Connecting to ${botName}...`);

            try {
                // Test connection first
                await api.pingBot(this.selectedBot);

                // Establish WebSocket connection for real-time updates
                this.websocket = api.createTerminalWebSocket(
                    this.selectedBot,
                    this.handleWebSocketMessage,
                    this.handleWebSocketError,
                    this.handleWebSocketClose
                );

                this.connectionStatus = 'connected';
                this.connectionStartTime = new Date();
                this.addSuccess('Connected successfully');
                this.focusInput();

            } catch (error) {
                this.connectionStatus = 'error';
                this.addError(`Failed to connect: ${error.response?.data?.detail || error.message}`);
            }
        },

        handleWebSocketMessage(data) {
            // Handle real-time messages from the bot
            switch (data.type) {
                case 'log':
                    this.addOutput(`[${data.timestamp}] ${data.level}: ${data.message}`);
                    break;
                case 'status_update':
                    this.addInfo(`Bot status changed to: ${data.status}`);
                    // Update local bot status
                    const bot = this.availableBots.find(b => b.id === this.selectedBot);
                    if (bot) bot.status = data.status;
                    break;
                case 'trade_update':
                    this.addSuccess(`Trade executed: ${data.side} ${data.amount} ${data.pair} at $${data.price}`);
                    break;
                case 'error':
                    this.addError(`Bot error: ${data.message}`);
                    break;
                default:
                    this.addOutput(data.message || JSON.stringify(data));
            }

            // Auto-scroll to bottom
            this.$nextTick(() => {
                this.scrollToBottom();
            });
        },

        handleWebSocketError(error) {
            console.error('WebSocket error:', error);
            this.connectionStatus = 'error';
            this.addError('WebSocket connection error');
        },

        handleWebSocketClose(event) {
            if (event.code !== 1000) { // Not a normal closure
                this.connectionStatus = 'disconnected';
                this.addError('WebSocket connection lost');
            }
        },

        disconnectFromBot() {
            if (this.websocket) {
                this.websocket.close();
                this.websocket = null;
            }
            this.selectedBot = '';
            this.connectionStatus = 'disconnected';
            this.connectionStartTime = null;
            this.addInfo('Disconnected from bot');
        },
        clearTerminal() {
            this.terminalHistory = [];
            this.commandCount = 0;
        },
        exportLogs() {
            const logs = this.terminalHistory.map(entry => {
                const timestamp = entry.timestamp ? entry.timestamp.toISOString() : new Date().toISOString();
                return `[${timestamp}] ${entry.type.toUpperCase()}: ${entry.content}`;
            }).join('\n');

            const blob = new Blob([logs], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `terminal-logs-${new Date().toISOString().split('T')[0]}.txt`;
            a.click();
            URL.revokeObjectURL(url);

            this.addSuccess('Logs exported successfully');
        },
        toggleFullscreen() {
            if (!this.isFullscreen) {
                const element = this.$el;
                if (element.requestFullscreen) {
                    element.requestFullscreen();
                } else if (element.webkitRequestFullscreen) {
                    element.webkitRequestFullscreen();
                }
            } else {
                if (document.exitFullscreen) {
                    document.exitFullscreen();
                } else if (document.webkitExitFullscreen) {
                    document.webkitExitFullscreen();
                }
            }
        },
        handleFullscreenChange() {
            this.isFullscreen = !!(document.fullscreenElement || document.webkitFullscreenElement);
        },
        updateConnectionTime() {
            if (this.connectionStatus === 'connected' && this.connectionStartTime) {
                const now = new Date();
                const diff = Math.floor((now - this.connectionStartTime) / 1000);
                const hours = Math.floor(diff / 3600);
                const minutes = Math.floor((diff % 3600) / 60);
                const seconds = diff % 60;

                if (hours > 0) {
                    this.connectionTime = `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
                } else {
                    this.connectionTime = `${minutes}:${seconds.toString().padStart(2, '0')}`;
                }
            } else {
                this.connectionTime = '--:--';
            }
        },
        scrollToBottom() {
            const output = this.$refs.terminalOutput;
            if (output) {
                output.scrollTop = output.scrollHeight;
            }
        },
        addOutput(content, level = 'info') {
            this.terminalHistory.push({
                type: 'output',
                content,
                level,
                timestamp: new Date()
            });
        },
        addError(content) {
            this.terminalHistory.push({
                type: 'error',
                content,
                timestamp: new Date()
            });
        },
        addInfo(content) {
            this.terminalHistory.push({
                type: 'info',
                content,
                timestamp: new Date()
            });
        },
        addSuccess(content) {
            this.terminalHistory.push({
                type: 'success',
                content,
                timestamp: new Date()
            });
        }
    }
}
</script>

<style scoped>
.terminal-page {
    height: 100vh;
    display: flex;
    flex-direction: column;
    background: #0a0a0a;
    color: #e2e8f0;
    font-family: 'Fira Code', 'Monaco', 'Consolas', monospace;
    font-size: 14px;
    line-height: 1.4;
    overflow: hidden;
}

/* Header */
.terminal-header {
    background: #1a1a1a;
    border-bottom: 1px solid #333;
    padding: 1rem 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-shrink: 0;
}

.header-left {
    display: flex;
    flex-direction: column;
}

.terminal-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: #00d4aa;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.terminal-subtitle {
    color: #64748b;
    margin: 0.25rem 0 0 0;
    font-size: 0.875rem;
}

.header-controls {
    display: flex;
    align-items: center;
    gap: 1.5rem;
}

.bot-selector {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.selector-label {
    color: #94a3b8;
    font-size: 0.875rem;
}

.bot-select {
    background: #2a2a2a;
    border: 1px solid #404040;
    border-radius: 6px;
    color: #e2e8f0;
    padding: 0.5rem;
    min-width: 200px;
}

.bot-select:focus {
    outline: none;
    border-color: #00d4aa;
}

.connection-status {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    font-size: 0.875rem;
    font-weight: 500;
}

.connection-status.connected {
    background: rgba(34, 197, 94, 0.1);
    color: #22c55e;
}

.connection-status.connecting {
    background: rgba(251, 191, 36, 0.1);
    color: #fbbf24;
}

.connection-status.disconnected {
    background: rgba(107, 114, 128, 0.1);
    color: #6b7280;
}

.connection-status.error {
    background: rgba(239, 68, 68, 0.1);
    color: #ef4444;
}

/* Terminal Container */
.terminal-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.terminal-output {
    flex: 1;
    padding: 1rem;
    overflow-y: auto;
    background: #0a0a0a;
    cursor: text;
}

.terminal-output::-webkit-scrollbar {
    width: 8px;
}

.terminal-output::-webkit-scrollbar-track {
    background: #1a1a1a;
}

.terminal-output::-webkit-scrollbar-thumb {
    background: #404040;
    border-radius: 4px;
}

.terminal-output::-webkit-scrollbar-thumb:hover {
    background: #4a4a4a;
}

/* Welcome Message */
.welcome-message {
    text-align: center;
    padding: 2rem;
    color: #64748b;
}

.ascii-art {
    font-family: monospace;
    color: #00d4aa;
    margin-bottom: 1rem;
    white-space: pre;
    line-height: 1.2;
}

.welcome-text p {
    margin: 0.5rem 0;
}

.command-highlight {
    color: #00d4aa;
    background: rgba(0, 212, 170, 0.1);
    padding: 0.125rem 0.25rem;
    border-radius: 3px;
    font-weight: 600;
}

/* Terminal Entries */
.terminal-entry {
    margin-bottom: 0.25rem;
}

.command-line {
    display: flex;
    align-items: center;
    margin-bottom: 0.5rem;
}

.prompt {
    color: #00d4aa;
    font-weight: 600;
    margin-right: 0.5rem;
}

.command-text {
    color: #e2e8f0;
}

.output-line {
    color: #94a3b8;
    margin-left: 1rem;
    white-space: pre-wrap;
}

.error-line {
    color: #ef4444;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-left: 1rem;
}

.info-line {
    color: #3b82f6;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-left: 1rem;
}

.success-line {
    color: #22c55e;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-left: 1rem;
}

/* Input Line */
.input-line {
    display: flex;
    align-items: center;
    position: relative;
}

.command-input {
    background: transparent;
    border: none;
    color: #e2e8f0;
    font-family: inherit;
    font-size: inherit;
    flex: 1;
    outline: none;
    padding: 0;
    margin-left: 0.5rem;
}

.command-input:disabled {
    opacity: 0.5;
}

.executing-indicator {
    color: #fbbf24;
    margin-left: 0.5rem;
}

.no-bot-message {
    color: #f59e0b;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 1rem;
    background: rgba(251, 191, 36, 0.1);
    border-radius: 6px;
    margin: 1rem 0;
}

/* Command Suggestions */
.command-suggestions {
    position: absolute;
    bottom: 60px;
    left: 1rem;
    right: 1rem;
    background: #1a1a1a;
    border: 1px solid #404040;
    border-radius: 6px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    z-index: 1000;
    max-height: 200px;
    overflow-y: auto;
}

.suggestion-item {
    padding: 0.75rem 1rem;
    cursor: pointer;
    border-bottom: 1px solid #2a2a2a;
    transition: background-color 0.2s ease;
}

.suggestion-item:hover,
.suggestion-item.active {
    background: #2a2a2a;
}

.suggestion-command {
    color: #00d4aa;
    font-weight: 600;
    margin-right: 1rem;
}

.suggestion-description {
    color: #64748b;
    font-size: 0.875rem;
}

/* Terminal Footer */
.terminal-footer {
    background: #1a1a1a;
    border-top: 1px solid #333;
    padding: 0.75rem 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-shrink: 0;
}

.footer-left {
    display: flex;
    align-items: center;
}

.terminal-info {
    display: flex;
    gap: 1.5rem;
}

.info-item {
    color: #64748b;
    font-size: 0.875rem;
    display: flex;
    align-items: center;
    gap: 0.25rem;
}

.footer-right {
    display: flex;
    gap: 0.5rem;
}

.footer-btn {
    background: #2a2a2a;
    border: 1px solid #404040;
    color: #e2e8f0;
    padding: 0.5rem 0.75rem;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    gap: 0.25rem;
    font-size: 0.875rem;
}

.footer-btn:hover {
    background: #404040;
    border-color: #525252;
}

/* Fullscreen styles */
.terminal-page:-webkit-full-screen {
    width: 100vw;
    height: 100vh;
}

.terminal-page:fullscreen {
    width: 100vw;
    height: 100vh;
}

/* Responsive Design */
@media (max-width: 768px) {
    .terminal-header {
        flex-direction: column;
        gap: 1rem;
        align-items: stretch;
    }

    .header-controls {
        flex-direction: column;
        gap: 1rem;
    }

    .bot-selector {
        flex-direction: column;
        align-items: stretch;
        gap: 0.25rem;
    }

    .bot-select {
        min-width: auto;
    }

    .terminal-info {
        flex-direction: column;
        gap: 0.5rem;
    }

    .footer-right {
        flex-wrap: wrap;
    }

    .command-suggestions {
        left: 0.5rem;
        right: 0.5rem;
    }
}
</style>