<template>
    <div class="home">
        <!-- Hero Section -->
        <section class="hero">
            <div class="hero-content">
                <h1 class="hero-title">Welcome to TradeWise</h1>
                <p class="hero-subtitle">
                    Professional trading bot management platform for automated cryptocurrency trading
                </p>
                <div class="hero-actions" v-if="!isAuthenticated">
                    <router-link to="/register" class="btn btn-primary">Get Started</router-link>
                    <router-link to="/login" class="btn btn-secondary">Sign In</router-link>
                </div>
                <div class="hero-actions" v-else>
                    <router-link to="/bots" class="btn btn-primary">View Your Bots</router-link>
                    <router-link to="/marketplace" class="btn btn-secondary">Browse Marketplace</router-link>
                </div>
            </div>
        </section>

        <!-- Features Section -->
        <section class="features">
            <div class="container">
                <h2 class="section-title">Why Choose TradeWise?</h2>
                <div class="features-grid">
                    <div class="feature-card">
                        <div class="feature-icon">🤖</div>
                        <h3>Automated Trading</h3>
                        <p>Deploy and manage sophisticated trading bots with advanced strategies and risk management</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">📊</div>
                        <h3>Real-time Analytics</h3>
                        <p>Monitor your bot performance with comprehensive metrics and detailed trading insights</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🔒</div>
                        <h3>Secure & Reliable</h3>
                        <p>Enterprise-grade security with encrypted API connections and secure key management</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🌐</div>
                        <h3>Multi-Exchange</h3>
                        <p>Connect to multiple cryptocurrency exchanges and diversify your trading strategies</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">📱</div>
                        <h3>Mobile Ready</h3>
                        <p>Access your trading dashboard from anywhere with our responsive web interface</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🔄</div>
                        <h3>Strategy Sharing</h3>
                        <p>Share and discover trading strategies in our community marketplace</p>
                    </div>
                </div>
            </div>
        </section>

        <!-- Stats Section (only for authenticated users) -->
        <section class="stats" v-if="isAuthenticated">
            <div class="container">
                <h2 class="section-title">Your Trading Overview</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number">{{ stats.activeBots }}</div>
                        <div class="stat-label">Active Bots</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{{ stats.totalTrades }}</div>
                        <div class="stat-label">Total Trades</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{{ stats.profitLoss }}%</div>
                        <div class="stat-label">Total P&L</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{{ stats.uptime }}%</div>
                        <div class="stat-label">Uptime</div>
                    </div>
                </div>
            </div>
        </section>

        <!-- CTA Section -->
        <section class="cta" v-if="!isAuthenticated">
            <div class="container">
                <h2>Ready to Start Trading?</h2>
                <p>Join thousands of traders who trust TradeWise for their automated trading needs</p>
                <router-link to="/register" class="btn btn-primary btn-large">Create Your Account</router-link>
            </div>
        </section>
    </div>
</template>

<script>
import api from '@/services/api'

export default {
    name: 'HomeView',
    data() {
        return {
            isAuthenticated: false,
            stats: {
                activeBots: 0,
                totalTrades: 0,
                profitLoss: 0,
                uptime: 0
            }
        }
    },
    async created() {
        this.updateAuthStatus()
        if (this.isAuthenticated) {
            await this.loadStats()
        }
    },
    watch: {
        '$route'() {
            this.updateAuthStatus()
        }
    },
    methods: {
        updateAuthStatus() {
            this.isAuthenticated = !!localStorage.getItem('authToken')
            if (this.isAuthenticated) {
                this.loadStats()
            }
        },
        async loadStats() {
            try {
                // Load user statistics
                const [botsResponse] = await Promise.all([
                    api.getBots().catch(() => ({ data: [] }))
                ])
                
                const bots = botsResponse.data || []
                this.stats.activeBots = bots.filter(bot => bot.status === 'running').length
                
                // Mock additional stats for now
                this.stats.totalTrades = Math.floor(Math.random() * 1000) + 500
                this.stats.profitLoss = (Math.random() * 20 - 5).toFixed(2)
                this.stats.uptime = (95 + Math.random() * 5).toFixed(1)
            } catch (error) {
                console.error('Error loading stats:', error)
            }
        }
    }
}
</script>

<style scoped>
.home {
    min-height: 100vh;
}

/* Hero Section */
.hero {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 80px 0;
    text-align: center;
}

.hero-content {
    max-width: 800px;
    margin: 0 auto;
    padding: 0 20px;
}

.hero-title {
    font-size: 3.5rem;
    font-weight: 700;
    margin-bottom: 1rem;
    line-height: 1.2;
}

.hero-subtitle {
    font-size: 1.25rem;
    margin-bottom: 2rem;
    opacity: 0.9;
    line-height: 1.6;
}

.hero-actions {
    display: flex;
    gap: 1rem;
    justify-content: center;
    flex-wrap: wrap;
}

/* Button Styles */
.btn {
    display: inline-block;
    padding: 12px 30px;
    border-radius: 6px;
    text-decoration: none;
    font-weight: 600;
    transition: all 0.3s ease;
    border: 2px solid transparent;
}

.btn-primary {
    background-color: #28a745;
    color: white;
}

.btn-primary:hover {
    background-color: #218838;
    transform: translateY(-2px);
}

.btn-secondary {
    background-color: transparent;
    color: white;
    border-color: white;
}

.btn-secondary:hover {
    background-color: white;
    color: #667eea;
}

.btn-large {
    padding: 16px 40px;
    font-size: 1.1rem;
}

/* Features Section */
.features {
    padding: 80px 0;
    background-color: #f8f9fa;
}

.section-title {
    text-align: center;
    font-size: 2.5rem;
    margin-bottom: 3rem;
    color: #333;
}

.features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin-top: 3rem;
}

.feature-card {
    background: white;
    padding: 2rem;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease;
}

.feature-card:hover {
    transform: translateY(-5px);
}

.feature-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
}

.feature-card h3 {
    font-size: 1.5rem;
    margin-bottom: 1rem;
    color: #333;
}

.feature-card p {
    color: #666;
    line-height: 1.6;
}

/* Stats Section */
.stats {
    padding: 80px 0;
    background-color: white;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 2rem;
    margin-top: 3rem;
}

.stat-card {
    text-align: center;
    padding: 2rem;
    border-radius: 12px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

.stat-number {
    font-size: 3rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}

.stat-label {
    font-size: 1.1rem;
    opacity: 0.9;
}

/* CTA Section */
.cta {
    padding: 80px 0;
    background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    color: white;
    text-align: center;
}

.cta h2 {
    font-size: 2.5rem;
    margin-bottom: 1rem;
}

.cta p {
    font-size: 1.25rem;
    margin-bottom: 2rem;
    opacity: 0.9;
}

/* Responsive Design */
@media (max-width: 768px) {
    .hero-title {
        font-size: 2.5rem;
    }
    
    .hero-subtitle {
        font-size: 1.1rem;
    }
    
    .hero-actions {
        flex-direction: column;
        align-items: center;
    }
    
    .btn {
        width: 100%;
        max-width: 300px;
    }
    
    .features-grid {
        grid-template-columns: 1fr;
    }
    
    .stats-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 480px) {
    .stats-grid {
        grid-template-columns: 1fr;
    }
}
</style>
