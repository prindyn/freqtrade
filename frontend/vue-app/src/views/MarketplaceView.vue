<template>
    <div class="marketplace-container p-4">
        <!-- Header -->
        <div class="flex justify-content-between align-items-center mb-4">
            <div>
                <h1 class="text-3xl font-bold text-900 mb-2">Bot Marketplace</h1>
                <p class="text-600">Discover and subscribe to proven trading strategies</p>
            </div>
            <Button 
                icon="pi pi-plus" 
                label="Connect Your Bot" 
                class="p-button-outlined"
                @click="$router.push('/connect-bot')"
            />
        </div>

        <!-- Marketplace Stats -->
        <div class="grid mb-4">
            <div class="col-12 md:col-4">
                <div class="stat-card p-4 border-round-lg shadow-2 text-center">
                    <div class="text-2xl font-bold text-blue-600 mb-2">{{ marketplaceStats.totalStrategies }}</div>
                    <div class="text-600">Available Strategies</div>
                </div>
            </div>
            <div class="col-12 md:col-4">
                <div class="stat-card p-4 border-round-lg shadow-2 text-center">
                    <div class="text-2xl font-bold text-green-600 mb-2">{{ marketplaceStats.totalSubscribers }}</div>
                    <div class="text-600">Active Subscribers</div>
                </div>
            </div>
            <div class="col-12 md:col-4">
                <div class="stat-card p-4 border-round-lg shadow-2 text-center">
                    <div class="text-2xl font-bold text-purple-600 mb-2">{{ marketplaceStats.avgPerformance }}%</div>
                    <div class="text-600">Avg. 30-Day Return</div>
                </div>
            </div>
        </div>

        <!-- Strategy Cards -->
        <div class="strategy-grid">
            <div 
                v-for="strategy in sharedBots" 
                :key="strategy.bot_id"
                class="strategy-card p-4 border-round-lg shadow-3 mb-4"
            >
                <div class="flex justify-content-between align-items-start mb-3">
                    <div>
                        <h3 class="text-xl font-semibold text-900 mb-2">{{ strategy.name }}</h3>
                        <p class="text-600 mb-2">{{ strategy.description }}</p>
                        <div class="flex gap-2 mb-2">
                            <Tag :value="strategy.risk_level" :severity="getRiskSeverity(strategy.risk_level)" />
                            <Tag :value="strategy.strategy_type" severity="info" />
                        </div>
                    </div>
                    <div class="text-right">
                        <div class="text-2xl font-bold text-green-600 mb-1">
                            +{{ strategy.performance_30d || 0 }}%
                        </div>
                        <div class="text-600">30-day return</div>
                    </div>
                </div>
                
                <div class="flex justify-content-between align-items-center mt-3">
                    <div class="flex align-items-center text-600">
                        <i class="pi pi-users mr-2"></i>
                        <span>{{ strategy.subscribers_count }} subscribers</span>
                    </div>
                    <div class="flex gap-2">
                        <Button 
                            label="View Details" 
                            icon="pi pi-eye"
                            class="p-button-text"
                            @click="viewStrategyDetails(strategy)"
                        />
                        <Button 
                            label="Subscribe" 
                            icon="pi pi-plus"
                            :disabled="isSubscribed(strategy.bot_id)"
                            @click="subscribeToStrategy(strategy)"
                        />
                    </div>
                </div>
            </div>
        </div>

        <!-- No strategies message -->
        <div v-if="!loading && sharedBots.length === 0" class="text-center py-8">
            <i class="pi pi-shopping-cart text-6xl text-400 mb-4"></i>
            <h3 class="text-xl text-600 mb-2">No strategies available yet</h3>
            <p class="text-500">Check back later for new trading strategies</p>
        </div>

        <!-- Loading -->
        <div v-if="loading" class="text-center py-8">
            <ProgressSpinner />
            <p class="text-600 mt-3">Loading marketplace...</p>
        </div>

        <!-- Subscription Dialog -->
        <Dialog v-model:visible="showSubscriptionDialog" modal header="Subscribe to Strategy" class="w-full max-w-md">
            <div v-if="selectedStrategy" class="flex flex-column gap-4">
                <div>
                    <h4 class="text-lg font-medium mb-2">{{ selectedStrategy.name }}</h4>
                    <p class="text-600">{{ selectedStrategy.description }}</p>
                </div>
                
                <div class="flex flex-column gap-2">
                    <label for="allocation" class="font-medium">Allocation Amount (USDT)</label>
                    <InputNumber 
                        id="allocation"
                        v-model="allocationAmount"
                        :min="100"
                        :max="10000"
                        placeholder="500"
                        class="w-full"
                    />
                    <small class="text-600">Minimum allocation: 100 USDT</small>
                </div>
                
                <div class="flex justify-content-end gap-2 mt-4">
                    <Button label="Cancel" class="p-button-text" @click="showSubscriptionDialog = false" />
                    <Button 
                        label="Subscribe" 
                        :loading="subscribing"
                        @click="confirmSubscription"
                    />
                </div>
            </div>
        </Dialog>
    </div>
</template>

<script>
import Button from 'primevue/button';
import Tag from 'primevue/tag';
import Dialog from 'primevue/dialog';
import InputNumber from 'primevue/inputnumber';
import ProgressSpinner from 'primevue/progressspinner';
import api from '@/services/api';

export default {
    name: 'MarketplaceView',
    components: {
        Button,
        Tag,
        Dialog,
        InputNumber,
        ProgressSpinner
    },
    data() {
        return {
            sharedBots: [],
            mySubscriptions: [],
            loading: false,
            subscribing: false,
            showSubscriptionDialog: false,
            selectedStrategy: null,
            allocationAmount: 500,
            marketplaceStats: {
                totalStrategies: 0,
                totalSubscribers: 0,
                avgPerformance: 0
            }
        };
    },
    async mounted() {
        await this.loadMarketplace();
        await this.loadMySubscriptions();
    },
    methods: {
        async loadMarketplace() {
            this.loading = true;
            try {
                const response = await api.getSharedBotsMarketplace();
                this.sharedBots = response.data;
                this.updateMarketplaceStats();
            } catch (error) {
                console.error('Error loading marketplace:', error);
                this.$toast.add({
                    severity: 'error',
                    summary: 'Error',
                    detail: 'Failed to load marketplace',
                    life: 3000
                });
            } finally {
                this.loading = false;
            }
        },
        
        async loadMySubscriptions() {
            try {
                const response = await api.getMySharedBotSubscriptions();
                this.mySubscriptions = response.data;
            } catch (error) {
                console.error('Error loading subscriptions:', error);
            }
        },
        
        updateMarketplaceStats() {
            this.marketplaceStats.totalStrategies = this.sharedBots.length;
            this.marketplaceStats.totalSubscribers = this.sharedBots.reduce(
                (sum, bot) => sum + bot.subscribers_count, 0
            );
            const validPerformances = this.sharedBots
                .map(bot => bot.performance_30d)
                .filter(perf => perf != null);
            
            this.marketplaceStats.avgPerformance = validPerformances.length > 0
                ? (validPerformances.reduce((sum, perf) => sum + perf, 0) / validPerformances.length).toFixed(1)
                : 0;
        },
        
        getRiskSeverity(riskLevel) {
            const severityMap = {
                'low': 'success',
                'medium': 'warning', 
                'high': 'danger'
            };
            return severityMap[riskLevel] || 'info';
        },
        
        isSubscribed(botId) {
            return this.mySubscriptions.some(sub => 
                sub.config_template === this.sharedBots.find(bot => bot.bot_id === botId)?.config_template
            );
        },
        
        viewStrategyDetails(strategy) {
            // TODO: Navigate to strategy details page
            this.$router.push(`/strategy/${strategy.bot_id}`);
        },
        
        subscribeToStrategy(strategy) {
            this.selectedStrategy = strategy;
            this.showSubscriptionDialog = true;
        },
        
        async confirmSubscription() {
            if (!this.selectedStrategy || !this.allocationAmount) {
                return;
            }
            
            this.subscribing = true;
            try {
                await api.subscribeToSharedBot({
                    shared_bot_id: this.selectedStrategy.bot_id,
                    allocation_amount: this.allocationAmount
                });
                
                this.$toast.add({
                    severity: 'success',
                    summary: 'Success',
                    detail: `Successfully subscribed to ${this.selectedStrategy.name}`,
                    life: 3000
                });
                
                this.showSubscriptionDialog = false;
                await this.loadMySubscriptions();
                
            } catch (error) {
                console.error('Subscription failed:', error);
                this.$toast.add({
                    severity: 'error',
                    summary: 'Error',
                    detail: error.response?.data?.detail || 'Subscription failed',
                    life: 3000
                });
            } finally {
                this.subscribing = false;
            }
        }
    }
};
</script>

<style scoped>
.marketplace-container {
    max-width: 1200px;
    margin: 0 auto;
}

.stat-card {
    background: white;
    transition: transform 0.2s ease-in-out;
}

.stat-card:hover {
    transform: translateY(-2px);
}

.strategy-card {
    background: white;
    border: 1px solid #e9ecef;
    transition: all 0.3s ease-in-out;
}

.strategy-card:hover {
    border-color: #2a5298;
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(42, 82, 152, 0.15);
}

.strategy-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
    gap: 1.5rem;
}

@media (max-width: 768px) {
    .strategy-grid {
        grid-template-columns: 1fr;
    }
}
</style>