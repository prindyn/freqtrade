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
                        ║           TradeWise Terminal           ║
                        ║        Bot Command Interface           ║
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
                    <input
                        ref="terminalInput"
                        v-model="currentCommand"
                        @keydown="handleKeyDown"
                        @keyup="handleKeyUp"
                        class="command-input"
                        :disabled="isExecuting"
                        autocomplete="off"
                        spellcheck="false"
                    />
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
            <div
                v-for="(suggestion, index) in filteredSuggestions"
                :key="index"
                @click="selectSuggestion(suggestion)"
                class="suggestion-item"
                :class="{ active: selectedSuggestionIndex === index }"
            >
                <span class="suggestion-command">{{ suggestion.command }}</span>
                <span class="suggestion-description">{{ suggestion.description }}</span>
            </div>
        </div>
    </div>
</template>

<script>
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
            availableBots: [
                { id: 'bot1', name: 'BTC Scalper', status: 'running' },
                { id: 'bot2', name: 'ETH DCA', status: 'running' },
                { id: 'bot3', name: 'Alt Momentum', status: 'stopped' }
            ],
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
                { command: 'clear', description: 'Clear terminal output' }
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
    mounted() {
        this.focusInput();
        this.updateConnectionTime();
        setInterval(this.updateConnectionTime, 1000);
        
        // Handle fullscreen events
        document.addEventListener('fullscreenchange', this.handleFullscreenChange);
        document.addEventListener('webkitfullscreenchange', this.handleFullscreenChange);
    },
    beforeUnmount() {
        document.removeEventListener('fullscreenchange', this.handleFullscreenChange);
        document.removeEventListener('webkitfullscreenchange', this.handleFullscreenChange);
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
                        await this.getBotStatus();
                        break;
                    case 'start':
                        await this.startBot();
                        break;
                    case 'stop':
                        await this.stopBot();
                        break;
                    case 'restart':
                        await this.restartBot();
                        break;
                    case 'balance':
                        await this.getBalance();
                        break;
                    case 'positions':
                        await this.getPositions();
                        break;
                    case 'trades':
                        await this.getTrades(args[0]);
                        break;
                    case 'profit':
                        await this.getProfit();
                        break;
                    case 'config':
                        await this.getConfig();
                        break;
                    case 'logs':
                        await this.getLogs(args[0]);
                        break;
                    case 'ping':
                        await this.pingBot();
                        break;
                    case 'version':
                        await this.getVersion();
                        break;
                    default:
                        this.addError(`Unknown command: ${cmd}. Type 'help' for available commands.`);
                }
            } catch (error) {
                this.addError(`Error executing command: ${error.message}`);
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

Navigation:
  ↑/↓               Navigate command history
  Tab               Auto-complete commands
  Ctrl+L            Clear terminal
            `;
            this.addOutput(helpText);
        },
        async getBotStatus() {
            await this.simulateDelay();
            const bot = this.availableBots.find(b => b.id === this.selectedBot);
            if (!bot) {
                this.addError('Bot not found');
                return;
            }
            
            const statusInfo = `
Bot Status Information:
─────────────────────

Name:           ${bot.name}
Status:         ${bot.status.toUpperCase()}
Uptime:         2 days, 14 hours, 32 minutes
Strategy:       DCA + Grid Trading
Pair:           BTC/USDT
Balance:        $5,247.83
Open Trades:    3
Total Trades:   127
Win Rate:       73.2%
Last Update:    ${new Date().toLocaleString()}
            `;
            this.addOutput(statusInfo);
        },
        async startBot() {
            await this.simulateDelay(1500);
            this.addInfo('Starting trading bot...');
            await this.simulateDelay(1000);
            this.addSuccess('Bot started successfully');
            
            // Update bot status
            const bot = this.availableBots.find(b => b.id === this.selectedBot);
            if (bot) bot.status = 'running';
        },
        async stopBot() {
            await this.simulateDelay(1000);
            this.addInfo('Stopping trading bot...');
            await this.simulateDelay(500);
            this.addSuccess('Bot stopped successfully');
            
            // Update bot status
            const bot = this.availableBots.find(b => b.id === this.selectedBot);
            if (bot) bot.status = 'stopped';
        },
        async restartBot() {
            await this.simulateDelay(1000);
            this.addInfo('Restarting trading bot...');
            await this.simulateDelay(2000);
            this.addSuccess('Bot restarted successfully');
        },
        async getBalance() {
            await this.simulateDelay();
            const balanceInfo = `
Account Balance:
───────────────

Total Balance:    $5,247.83
Available:        $3,891.22
In Orders:        $1,356.61
Unrealized P&L:   +$142.35 (+2.78%)

Asset Breakdown:
BTC:             0.08432 BTC  ($3,654.21)
USDT:            1,593.62 USDT
ETH:             0.6841 ETH   ($1,782.33)
            `;
            this.addOutput(balanceInfo);
        },
        async getPositions() {
            await this.simulateDelay();
            const positionsInfo = `
Open Positions:
──────────────

BTC/USDT  LONG   0.02 BTC    $43,250   $43,890   +1.48%   2h 15m
ETH/USDT  LONG   0.31 ETH    $2,580    $2,545    -1.36%   4h 23m
ADA/USDT  SHORT  1,250 ADA   $0.485    $0.472    +2.68%   6h 12m

Total Unrealized P&L: +$142.35 (+2.78%)
            `;
            this.addOutput(positionsInfo);
        },
        async getTrades(limit = '10') {
            await this.simulateDelay();
            const tradesInfo = `
Recent Trades (Last ${limit}):
─────────────────────────

BTC/USDT  SELL  0.015 BTC  $42,150  +2.31%   3h 24m ago
ETH/USDT  BUY   0.284 ETH  $2,620   +1.53%   5h 45m ago
SOL/USDT  SELL  12.5 SOL   $85.20   -2.46%   8h 12m ago
ADA/USDT  BUY   800 ADA    $0.491   +3.84%   12h 33m ago
MATIC/USDT SELL 450 MATIC  $0.865   +1.92%   1d 2h ago

Total Profit Today: +$87.23 (+1.89%)
            `;
            this.addOutput(tradesInfo);
        },
        async getProfit() {
            await this.simulateDelay();
            const profitInfo = `
Profit Summary:
──────────────

Today:           +$87.23  (+1.89%)
This Week:       +$324.56 (+7.12%)
This Month:      +$1,247.83 (+31.24%)
All Time:        +$2,891.47 (+122.45%)

Best Trade:      BTC/USDT +$156.78 (5.24%)
Worst Trade:     ETH/USDT -$67.43 (-2.89%)
Win Rate:        73.2% (93/127 trades)
Average Trade:   +$22.74
            `;
            this.addOutput(profitInfo);
        },
        async getConfig() {
            await this.simulateDelay();
            const configInfo = `
Bot Configuration:
─────────────────

Strategy:         DCA + Grid Trading
Max Position:     5% of balance
Stop Loss:        -3%
Take Profit:      +5%
Grid Levels:      10
Grid Spacing:     0.5%
Trading Pairs:    BTC/USDT, ETH/USDT, ADA/USDT
Timeframe:        5m
Dry Run:          false
            `;
            this.addOutput(configInfo);
        },
        async getLogs(level = 'info') {
            await this.simulateDelay();
            const logsInfo = `
Recent Log Entries (${level}):
─────────────────────────────

[2024-01-15 14:32:15] INFO: Bot started successfully
[2024-01-15 14:32:16] INFO: Loading strategy configuration
[2024-01-15 14:32:17] INFO: Connected to exchange
[2024-01-15 14:32:18] INFO: Starting trading loop
[2024-01-15 14:35:21] INFO: New order placed: BUY 0.02 BTC at $43,250
[2024-01-15 14:38:45] INFO: Order filled: BUY 0.02 BTC at $43,250
[2024-01-15 14:42:12] WARN: High volatility detected
[2024-01-15 14:45:33] INFO: Grid order placed at $43,500
            `;
            this.addOutput(logsInfo);
        },
        async pingBot() {
            await this.simulateDelay(500);
            this.addSuccess('PONG - Bot is responding (latency: 45ms)');
        },
        async getVersion() {
            await this.simulateDelay();
            const versionInfo = `
Version Information:
───────────────────

Bot Version:      v2.4.1
API Version:      v1.8.2
Python:           3.9.16
Exchange:         Binance v1.2.45
Strategy Engine:  v3.1.0
Last Update:      2024-01-10
            `;
            this.addOutput(versionInfo);
        },
        switchBot() {
            if (!this.selectedBot) {
                this.connectionStatus = 'disconnected';
                return;
            }
            
            this.connectionStatus = 'connecting';
            this.addInfo(`Connecting to ${this.availableBots.find(b => b.id === this.selectedBot)?.name}...`);
            
            setTimeout(() => {
                this.connectionStatus = 'connected';
                this.addSuccess('Connected successfully');
                this.focusInput();
            }, 1500);
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
            if (this.connectionStatus === 'connected') {
                const now = new Date();
                this.connectionTime = now.toLocaleTimeString();
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
        simulateDelay(ms = 800) {
            return new Promise(resolve => setTimeout(resolve, ms));
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