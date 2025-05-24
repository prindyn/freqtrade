<template>
    <div class="dashboard">
        <!-- Dashboard Header -->
        <div class="dashboard-header">
            <h1 class="dashboard-title">Trading Dashboard</h1>
            <p class="dashboard-subtitle">Monitor your trading performance and manage your bots</p>
        </div>

        <!-- Bot Comparison Section -->
        <div class="dashboard-section">
            <div class="section-header">
                <h2 class="section-title">
                    <i class="pi pi-android"></i>
                    Bot Comparison
                </h2>
                <button class="refresh-btn" @click="refreshData">
                    <i class="pi pi-refresh" :class="{ 'spinning': isRefreshing }"></i>
                </button>
            </div>
            <div class="bot-comparison-grid">
                <div v-for="bot in bots" :key="bot.id" class="bot-card">
                    <div class="bot-card-header">
                        <div class="bot-name">{{ bot.name }}</div>
                        <div class="bot-status" :class="bot.status">{{ bot.status }}</div>
                    </div>
                    <div class="bot-metrics">
                        <div class="metric">
                            <span class="metric-value">{{ bot.profit }}%</span>
                            <span class="metric-label">Profit</span>
                        </div>
                        <div class="metric">
                            <span class="metric-value">{{ bot.trades }}</span>
                            <span class="metric-label">Trades</span>
                        </div>
                        <div class="metric">
                            <span class="metric-value">{{ bot.winRate }}%</span>
                            <span class="metric-label">Win Rate</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Charts Grid -->
        <div class="charts-grid">
            <!-- Profit Over Time Chart -->
            <div class="chart-container">
                <div class="chart-header">
                    <h3 class="chart-title">
                        <i class="pi pi-chart-line"></i>
                        Profit Over Time
                    </h3>
                    <div class="chart-controls">
                        <select v-model="profitTimeframe" @change="updateProfitChart" class="timeframe-select">
                            <option value="24h">24H</option>
                            <option value="7d">7D</option>
                            <option value="30d">30D</option>
                            <option value="90d">90D</option>
                        </select>
                    </div>
                </div>
                <div class="chart-content">
                    <canvas ref="profitChart" class="chart-canvas"></canvas>
                </div>
            </div>

            <!-- Cumulative Profit Chart -->
            <div class="chart-container">
                <div class="chart-header">
                    <h3 class="chart-title">
                        <i class="pi pi-trending-up"></i>
                        Cumulative Profit
                    </h3>
                </div>
                <div class="chart-content">
                    <canvas ref="cumulativeProfitChart" class="chart-canvas"></canvas>
                </div>
            </div>

            <!-- Profit Distribution Chart -->
            <div class="chart-container">
                <div class="chart-header">
                    <h3 class="chart-title">
                        <i class="pi pi-chart-pie"></i>
                        Profit Distribution
                    </h3>
                </div>
                <div class="chart-content">
                    <canvas ref="profitDistributionChart" class="chart-canvas"></canvas>
                </div>
            </div>

            <!-- Trades Log Chart -->
            <div class="chart-container">
                <div class="chart-header">
                    <h3 class="chart-title">
                        <i class="pi pi-history"></i>
                        Trades Volume
                    </h3>
                </div>
                <div class="chart-content">
                    <canvas ref="tradesLogChart" class="chart-canvas"></canvas>
                </div>
            </div>
        </div>

        <!-- Trading Tables Grid -->
        <div class="tables-grid">
            <!-- Open Trades -->
            <div class="table-container">
                <div class="table-header">
                    <h3 class="table-title">
                        <i class="pi pi-clock"></i>
                        Open Trades
                        <span class="trade-count">{{ openTrades.length }}</span>
                    </h3>
                </div>
                <div class="table-content">
                    <div v-if="openTrades.length === 0" class="empty-state">
                        <i class="pi pi-info-circle"></i>
                        <p>No open trades</p>
                    </div>
                    <div v-else class="trades-table">
                        <div class="table-header-row">
                            <div class="table-cell">Pair</div>
                            <div class="table-cell">Side</div>
                            <div class="table-cell">Entry</div>
                            <div class="table-cell">Current</div>
                            <div class="table-cell">P&L</div>
                            <div class="table-cell">Time</div>
                        </div>
                        <div v-for="trade in openTrades" :key="trade.id" class="table-row">
                            <div class="table-cell font-semibold">{{ trade.pair }}</div>
                            <div class="table-cell">
                                <span class="side-badge" :class="trade.side">{{ trade.side }}</span>
                            </div>
                            <div class="table-cell">${{ trade.entryPrice }}</div>
                            <div class="table-cell">${{ trade.currentPrice }}</div>
                            <div class="table-cell">
                                <span class="pnl" :class="trade.pnl > 0 ? 'positive' : 'negative'">
                                    {{ trade.pnl > 0 ? '+' : '' }}{{ trade.pnl }}%
                                </span>
                            </div>
                            <div class="table-cell text-gray">{{ formatTime(trade.openTime) }}</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Closed Trades -->
            <div class="table-container">
                <div class="table-header">
                    <h3 class="table-title">
                        <i class="pi pi-check-circle"></i>
                        Recent Closed Trades
                        <span class="trade-count">{{ closedTrades.length }}</span>
                    </h3>
                </div>
                <div class="table-content">
                    <div v-if="closedTrades.length === 0" class="empty-state">
                        <i class="pi pi-info-circle"></i>
                        <p>No closed trades</p>
                    </div>
                    <div v-else class="trades-table">
                        <div class="table-header-row">
                            <div class="table-cell">Pair</div>
                            <div class="table-cell">Side</div>
                            <div class="table-cell">Entry</div>
                            <div class="table-cell">Exit</div>
                            <div class="table-cell">P&L</div>
                            <div class="table-cell">Duration</div>
                        </div>
                        <div v-for="trade in closedTrades.slice(0, 10)" :key="trade.id" class="table-row">
                            <div class="table-cell font-semibold">{{ trade.pair }}</div>
                            <div class="table-cell">
                                <span class="side-badge" :class="trade.side">{{ trade.side }}</span>
                            </div>
                            <div class="table-cell">${{ trade.entryPrice }}</div>
                            <div class="table-cell">${{ trade.exitPrice }}</div>
                            <div class="table-cell">
                                <span class="pnl" :class="trade.profit > 0 ? 'positive' : 'negative'">
                                    {{ trade.profit > 0 ? '+' : '' }}{{ trade.profit }}%
                                </span>
                            </div>
                            <div class="table-cell text-gray">{{ trade.duration }}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'DashboardView',
    data() {
        return {
            isRefreshing: false,
            profitTimeframe: '7d',
            bots: [
                {
                    id: 1,
                    name: 'BTC Scalper',
                    status: 'running',
                    profit: 12.5,
                    trades: 45,
                    winRate: 78
                },
                {
                    id: 2,
                    name: 'ETH DCA',
                    status: 'running',
                    profit: 8.2,
                    trades: 23,
                    winRate: 65
                },
                {
                    id: 3,
                    name: 'Alt Momentum',
                    status: 'stopped',
                    profit: -2.1,
                    trades: 12,
                    winRate: 42
                }
            ],
            openTrades: [
                {
                    id: 1,
                    pair: 'BTC/USDT',
                    side: 'long',
                    entryPrice: 42150,
                    currentPrice: 42890,
                    pnl: 1.75,
                    openTime: new Date(Date.now() - 2 * 60 * 60 * 1000)
                },
                {
                    id: 2,
                    pair: 'ETH/USDT',
                    side: 'long',
                    entryPrice: 2580,
                    currentPrice: 2545,
                    pnl: -1.36,
                    openTime: new Date(Date.now() - 4 * 60 * 60 * 1000)
                },
                {
                    id: 3,
                    pair: 'ADA/USDT',
                    side: 'short',
                    entryPrice: 0.485,
                    currentPrice: 0.472,
                    pnl: 2.68,
                    openTime: new Date(Date.now() - 6 * 60 * 60 * 1000)
                }
            ],
            closedTrades: [
                {
                    id: 1,
                    pair: 'BTC/USDT',
                    side: 'long',
                    entryPrice: 41200,
                    exitPrice: 42150,
                    profit: 2.31,
                    duration: '3h 24m'
                },
                {
                    id: 2,
                    pair: 'ETH/USDT',
                    side: 'short',
                    entryPrice: 2620,
                    exitPrice: 2580,
                    profit: 1.53,
                    duration: '1h 45m'
                },
                {
                    id: 3,
                    pair: 'SOL/USDT',
                    side: 'long',
                    entryPrice: 85.2,
                    exitPrice: 83.1,
                    profit: -2.46,
                    duration: '45m'
                }
            ]
        }
    },
    mounted() {
        this.initializeCharts();
    },
    methods: {
        async refreshData() {
            this.isRefreshing = true;
            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 1000));
            this.isRefreshing = false;
        },
        initializeCharts() {
            // Initialize profit over time chart
            this.initProfitChart();
            // Initialize cumulative profit chart
            this.initCumulativeProfitChart();
            // Initialize profit distribution chart
            this.initProfitDistributionChart();
            // Initialize trades log chart
            this.initTradesLogChart();
        },
        initProfitChart() {
            // Mock implementation - in real app, use Chart.js or similar
            const canvas = this.$refs.profitChart;
            if (canvas) {
                const ctx = canvas.getContext('2d');
                this.drawMockLineChart(ctx, canvas, 'Profit Over Time');
            }
        },
        initCumulativeProfitChart() {
            const canvas = this.$refs.cumulativeProfitChart;
            if (canvas) {
                const ctx = canvas.getContext('2d');
                this.drawMockAreaChart(ctx, canvas, 'Cumulative Profit');
            }
        },
        initProfitDistributionChart() {
            const canvas = this.$refs.profitDistributionChart;
            if (canvas) {
                const ctx = canvas.getContext('2d');
                this.drawMockPieChart(ctx, canvas);
            }
        },
        initTradesLogChart() {
            const canvas = this.$refs.tradesLogChart;
            if (canvas) {
                const ctx = canvas.getContext('2d');
                this.drawMockBarChart(ctx, canvas, 'Trades Volume');
            }
        },
        drawMockLineChart(ctx, canvas, title) {
            const width = canvas.width = canvas.offsetWidth * 2;
            const height = canvas.height = canvas.offsetHeight * 2;
            ctx.scale(2, 2);
            
            ctx.fillStyle = '#f8fafc';
            ctx.fillRect(0, 0, width/2, height/2);
            
            ctx.strokeStyle = '#3b82f6';
            ctx.lineWidth = 2;
            ctx.beginPath();
            
            const points = [
                [50, height/2 - 20], [100, height/2 - 40], [150, height/2 - 30],
                [200, height/2 - 60], [250, height/2 - 45], [300, height/2 - 70]
            ];
            
            ctx.moveTo(points[0][0], points[0][1]);
            points.forEach(point => ctx.lineTo(point[0], point[1]));
            ctx.stroke();
            
            // Add gradient fill
            ctx.fillStyle = 'rgba(59, 130, 246, 0.1)';
            ctx.beginPath();
            ctx.moveTo(points[0][0], points[0][1]);
            points.forEach(point => ctx.lineTo(point[0], point[1]));
            ctx.lineTo(300, height/2);
            ctx.lineTo(50, height/2);
            ctx.closePath();
            ctx.fill();
        },
        drawMockAreaChart(ctx, canvas, title) {
            const width = canvas.width = canvas.offsetWidth * 2;
            const height = canvas.height = canvas.offsetHeight * 2;
            ctx.scale(2, 2);
            
            ctx.fillStyle = '#f8fafc';
            ctx.fillRect(0, 0, width/2, height/2);
            
            const gradient = ctx.createLinearGradient(0, 0, 0, height/2);
            gradient.addColorStop(0, 'rgba(34, 197, 94, 0.3)');
            gradient.addColorStop(1, 'rgba(34, 197, 94, 0.05)');
            
            ctx.fillStyle = gradient;
            ctx.beginPath();
            ctx.moveTo(50, height/2 - 10);
            ctx.lineTo(100, height/2 - 25);
            ctx.lineTo(150, height/2 - 35);
            ctx.lineTo(200, height/2 - 50);
            ctx.lineTo(250, height/2 - 45);
            ctx.lineTo(300, height/2 - 60);
            ctx.lineTo(300, height/2);
            ctx.lineTo(50, height/2);
            ctx.closePath();
            ctx.fill();
        },
        drawMockPieChart(ctx, canvas) {
            const width = canvas.width = canvas.offsetWidth * 2;
            const height = canvas.height = canvas.offsetHeight * 2;
            ctx.scale(2, 2);
            
            ctx.fillStyle = '#f8fafc';
            ctx.fillRect(0, 0, width/2, height/2);
            
            const centerX = width/4;
            const centerY = height/4;
            const radius = 60;
            
            const data = [
                { value: 45, color: '#22c55e' },
                { value: 30, color: '#3b82f6' },
                { value: 15, color: '#f59e0b' },
                { value: 10, color: '#ef4444' }
            ];
            
            let currentAngle = 0;
            data.forEach(segment => {
                const sliceAngle = (segment.value / 100) * 2 * Math.PI;
                
                ctx.fillStyle = segment.color;
                ctx.beginPath();
                ctx.moveTo(centerX, centerY);
                ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
                ctx.closePath();
                ctx.fill();
                
                currentAngle += sliceAngle;
            });
        },
        drawMockBarChart(ctx, canvas, title) {
            const width = canvas.width = canvas.offsetWidth * 2;
            const height = canvas.height = canvas.offsetHeight * 2;
            ctx.scale(2, 2);
            
            ctx.fillStyle = '#f8fafc';
            ctx.fillRect(0, 0, width/2, height/2);
            
            const barWidth = 30;
            const barSpacing = 20;
            const data = [45, 60, 38, 72, 55, 48, 65];
            
            data.forEach((value, index) => {
                const x = 50 + index * (barWidth + barSpacing);
                const barHeight = (value / 80) * (height/2 - 80);
                const y = height/2 - 40 - barHeight;
                
                ctx.fillStyle = '#3b82f6';
                ctx.fillRect(x, y, barWidth, barHeight);
            });
        },
        updateProfitChart() {
            // Reinitialize chart with new timeframe
            this.initProfitChart();
        },
        formatTime(date) {
            const now = new Date();
            const diff = now - date;
            const hours = Math.floor(diff / (1000 * 60 * 60));
            const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
            
            if (hours > 0) {
                return `${hours}h ${minutes}m ago`;
            }
            return `${minutes}m ago`;
        }
    }
}
</script>

<style scoped>
.dashboard {
    max-width: 1400px;
    margin: 0 auto;
    padding: 2rem;
    background: #f8fafc;
    min-height: 100vh;
}

/* Dashboard Header */
.dashboard-header {
    margin-bottom: 2rem;
}

.dashboard-title {
    font-size: 2.5rem;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 0.5rem;
}

.dashboard-subtitle {
    font-size: 1.125rem;
    color: #64748b;
}

/* Section Styling */
.dashboard-section {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 2rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}

.section-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: #1e293b;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.refresh-btn {
    background: #3b82f6;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.5rem;
    cursor: pointer;
    transition: all 0.2s ease;
}

.refresh-btn:hover {
    background: #2563eb;
}

.spinning {
    animation: spin 1s linear infinite;
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

/* Bot Comparison */
.bot-comparison-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1rem;
}

.bot-card {
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.5rem;
    transition: transform 0.2s ease;
}

.bot-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.bot-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}

.bot-name {
    font-weight: 600;
    font-size: 1.125rem;
    color: #1e293b;
}

.bot-status {
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.875rem;
    font-weight: 500;
    text-transform: capitalize;
}

.bot-status.running {
    background: #dcfce7;
    color: #16a34a;
}

.bot-status.stopped {
    background: #fee2e2;
    color: #dc2626;
}

.bot-metrics {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
}

.metric {
    text-align: center;
}

.metric-value {
    display: block;
    font-size: 1.5rem;
    font-weight: 700;
    color: #1e293b;
}

.metric-label {
    display: block;
    font-size: 0.875rem;
    color: #64748b;
    margin-top: 0.25rem;
}

/* Charts Grid */
.charts-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
    gap: 2rem;
    margin-bottom: 2rem;
}

.chart-container {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.chart-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}

.chart-title {
    font-size: 1.125rem;
    font-weight: 600;
    color: #1e293b;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.chart-controls {
    display: flex;
    gap: 0.5rem;
}

.timeframe-select {
    border: 1px solid #d1d5db;
    border-radius: 6px;
    padding: 0.5rem;
    font-size: 0.875rem;
    background: white;
}

.chart-content {
    height: 300px;
    position: relative;
}

.chart-canvas {
    width: 100%;
    height: 100%;
    border-radius: 8px;
}

/* Tables Grid */
.tables-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
    gap: 2rem;
}

.table-container {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.table-header {
    margin-bottom: 1rem;
}

.table-title {
    font-size: 1.125rem;
    font-weight: 600;
    color: #1e293b;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.trade-count {
    background: #3b82f6;
    color: white;
    padding: 0.125rem 0.5rem;
    border-radius: 12px;
    font-size: 0.75rem;
    margin-left: 0.5rem;
}

.table-content {
    max-height: 400px;
    overflow-y: auto;
}

.empty-state {
    text-align: center;
    color: #64748b;
    padding: 2rem;
}

.empty-state i {
    font-size: 2rem;
    margin-bottom: 0.5rem;
    opacity: 0.5;
}

.trades-table {
    width: 100%;
}

.table-header-row {
    display: grid;
    grid-template-columns: 1fr 0.8fr 1fr 1fr 0.8fr 1fr;
    gap: 1rem;
    padding: 0.75rem;
    background: #f8fafc;
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.875rem;
    color: #475569;
    margin-bottom: 0.5rem;
}

.table-row {
    display: grid;
    grid-template-columns: 1fr 0.8fr 1fr 1fr 0.8fr 1fr;
    gap: 1rem;
    padding: 0.75rem;
    border-bottom: 1px solid #f1f5f9;
    transition: background-color 0.2s ease;
}

.table-row:hover {
    background: #f8fafc;
}

.table-cell {
    display: flex;
    align-items: center;
    font-size: 0.875rem;
    color: #1e293b;
}

.side-badge {
    padding: 0.125rem 0.5rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 500;
    text-transform: uppercase;
}

.side-badge.long {
    background: #dcfce7;
    color: #16a34a;
}

.side-badge.short {
    background: #fee2e2;
    color: #dc2626;
}

.pnl {
    font-weight: 600;
}

.pnl.positive {
    color: #16a34a;
}

.pnl.negative {
    color: #dc2626;
}

.font-semibold {
    font-weight: 600;
}

.text-gray {
    color: #64748b;
}

/* Responsive Design */
@media (max-width: 1200px) {
    .charts-grid {
        grid-template-columns: 1fr;
    }
    
    .tables-grid {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 768px) {
    .dashboard {
        padding: 1rem;
    }
    
    .dashboard-title {
        font-size: 2rem;
    }
    
    .bot-comparison-grid {
        grid-template-columns: 1fr;
    }
    
    .table-header-row,
    .table-row {
        grid-template-columns: 1fr 0.6fr 0.8fr 0.8fr 0.6fr 0.8fr;
        gap: 0.5rem;
        font-size: 0.75rem;
    }
    
    .chart-content {
        height: 250px;
    }
}
</style>