<template>
    <div class="dashboard-container p-4">
        <!-- Dashboard Header -->
        <div class="flex justify-content-between align-items-center mb-4">
            <div>
                <h1 class="text-3xl font-bold text-900 mb-2">FreqTrade Dashboard</h1>
                <p class="text-600">Manage and monitor your trading bots</p>
            </div>
            <div class="flex gap-2">
                <Button icon="pi pi-shopping-cart" label="Marketplace" class="p-button-outlined"
                    @click="$router.push('/marketplace')" />
                <Button icon="pi pi-link" label="Connect Bot" class="p-button-primary" @click="showConnectBotModal" />
            </div>
        </div>

        <!-- Stats Cards -->
        <div class="grid mb-4">
            <div class="col-12 md:col-6 lg:col-3">
                <div class="stat-card p-4 border-round-lg shadow-2">
                    <div class="flex align-items-center">
                        <div class="stat-icon bg-blue-100 text-blue-600 border-round mr-3">
                            <i class="pi pi-cog text-2xl"></i>
                        </div>
                        <div>
                            <div class="text-2xl font-bold text-900">{{ stats.totalBots }}</div>
                            <div class="text-600">Total Bots</div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="col-12 md:col-6 lg:col-3">
                <div class="stat-card p-4 border-round-lg shadow-2">
                    <div class="flex align-items-center">
                        <div class="stat-icon bg-green-100 text-green-600 border-round mr-3">
                            <i class="pi pi-play text-2xl"></i>
                        </div>
                        <div>
                            <div class="text-2xl font-bold text-900">{{ stats.runningBots }}</div>
                            <div class="text-600">Running</div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="col-12 md:col-6 lg:col-3">
                <div class="stat-card p-4 border-round-lg shadow-2">
                    <div class="flex align-items-center">
                        <div class="stat-icon bg-orange-100 text-orange-600 border-round mr-3">
                            <i class="pi pi-dollar text-2xl"></i>
                        </div>
                        <div>
                            <div class="text-2xl font-bold text-900">${{ stats.totalProfit.toFixed(2) }}</div>
                            <div class="text-600">Total Profit</div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="col-12 md:col-6 lg:col-3">
                <div class="stat-card p-4 border-round-lg shadow-2">
                    <div class="flex align-items-center">
                        <div class="stat-icon bg-purple-100 text-purple-600 border-round mr-3">
                            <i class="pi pi-chart-line text-2xl"></i>
                        </div>
                        <div>
                            <div class="text-2xl font-bold text-900">{{ stats.activeTrades }}</div>
                            <div class="text-600">Active Trades</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Bots Table -->
        <div class="bot-table-container">
            <div class="flex justify-content-between align-items-center mb-3">
                <h2 class="text-xl font-semibold text-900">Your Bots</h2>
                <div class="flex gap-2">
                    <Button icon="pi pi-refresh" class="p-button-text" @click="refreshBots" :loading="loading" />
                </div>
            </div>

            <DataTable :value="bots" :loading="loading" responsiveLayout="scroll" class="bot-table" :paginator="true"
                :rows="10">
                <Column field="name" header="Bot Name" :sortable="true">
                    <template #body="slotProps">
                        <div class="flex align-items-center gap-2">
                            <Tag :value="slotProps.data.bot_type === 'external' ? 'External' : 'Shared'"
                                :severity="slotProps.data.bot_type === 'external' ? 'info' : 'success'"
                                class="text-xs" />
                            <div class="font-medium text-900">{{ slotProps.data.name || slotProps.data.bot_id }}</div>
                        </div>
                    </template>
                </Column>

                <Column field="status" header="Status" :sortable="true">
                    <template #body="slotProps">
                        <Tag :value="slotProps.data.status" :severity="getStatusSeverity(slotProps.data.status)"
                            class="font-medium" />
                    </template>
                </Column>

                <Column field="created_at" header="Created" :sortable="true">
                    <template #body="slotProps">
                        <div class="text-600">{{ formatDate(slotProps.data.details?.created_at) }}</div>
                    </template>
                </Column>

                <Column field="host_port" header="Port" :sortable="true">
                    <template #body="slotProps">
                        <div class="text-600">{{ slotProps.data.details?.host_port || 'N/A' }}</div>
                    </template>
                </Column>

                <Column header="Actions" class="actions-column">
                    <template #body="slotProps">
                        <div class="bot-actions">
                            <!-- Control Buttons -->
                            <div class="control-buttons">
                                <Button 
                                    icon="pi pi-play" 
                                    class="action-btn success"
                                    v-tooltip="'Start Bot'" 
                                    @click="startBot(slotProps.data)"
                                    :disabled="slotProps.data.status === 'running' || isExecuting(slotProps.data.id)"
                                    :loading="isExecuting(slotProps.data.id) && lastAction === 'start'" />
                                
                                <Button 
                                    icon="pi pi-pause" 
                                    class="action-btn warning"
                                    v-tooltip="'Pause Bot'" 
                                    @click="pauseBot(slotProps.data)"
                                    :disabled="slotProps.data.status !== 'running' || isExecuting(slotProps.data.id)"
                                    :loading="isExecuting(slotProps.data.id) && lastAction === 'pause'" />
                                
                                <Button 
                                    icon="pi pi-stop" 
                                    class="action-btn danger"
                                    v-tooltip="'Stop Bot'" 
                                    @click="stopBot(slotProps.data)"
                                    :disabled="slotProps.data.status === 'stopped' || isExecuting(slotProps.data.id)"
                                    :loading="isExecuting(slotProps.data.id) && lastAction === 'stop'" />
                                
                                <Button 
                                    icon="pi pi-refresh" 
                                    class="action-btn info"
                                    v-tooltip="'Restart Bot'" 
                                    @click="restartBot(slotProps.data)"
                                    :disabled="isExecuting(slotProps.data.id)"
                                    :loading="isExecuting(slotProps.data.id) && lastAction === 'restart'" />
                            </div>
                            
                            <!-- Additional Actions -->
                            <div class="additional-actions">
                                <Button 
                                    icon="pi pi-desktop" 
                                    class="action-btn secondary"
                                    v-tooltip="'Open Terminal'" 
                                    @click="openTerminal(slotProps.data)" />
                                
                                <Button 
                                    icon="pi pi-chart-line" 
                                    class="action-btn info"
                                    v-tooltip="'View Performance'" 
                                    @click="viewBotPerformance(slotProps.data)" />
                                
                                <Button 
                                    icon="pi pi-cog" 
                                    class="action-btn secondary"
                                    v-tooltip="'Bot Settings'" 
                                    @click="openBotSettings(slotProps.data)" />
                                
                                <Button 
                                    icon="pi pi-trash" 
                                    class="action-btn danger-outline"
                                    v-tooltip="'Delete Bot'" 
                                    @click="deleteBot(slotProps.data)" />
                            </div>
                        </div>
                    </template>
                </Column>
            </DataTable>
        </div>

        <!-- Connect Bot Modal -->
        <ConnectBotModal v-model:visible="connectBotModalVisible" @bot-connected="onBotConnected" />
    </div>
</template>

<script>
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Tag from 'primevue/tag';
import Dialog from 'primevue/dialog';
import api from '@/services/api';
import ConnectBotModal from '@/components/ConnectBotModal.vue';

export default {
    name: 'BotsView',
    components: {
        DataTable,
        Column,
        Button,
        Tag,
        Dialog,
        ConnectBotModal
    },
    data() {
        return {
            bots: [],
            loading: false,
            connectBotModalVisible: false,
            stats: {
                totalBots: 0,
                runningBots: 0,
                totalProfit: 0,
                activeTrades: 0
            },
            websocket: null,
            executingBots: new Set(), // Track which bots are currently executing commands
            lastAction: null, // Track the last action for loading states
            realTimeData: {} // Store real-time bot data
        };
    },
    async mounted() {
        await this.loadBots();
        this.initWebSocket();
    },
    beforeUnmount() {
        if (this.websocket) {
            this.websocket.close();
        }
    },
    methods: {
        async loadBots() {
            this.loading = true;
            try {
                // Load external bots (primary) and shared bots
                const [externalBotsResponse, sharedBotsResponse] = await Promise.all([
                    api.getExternalBots().catch(() => ({ data: [] })),
                    api.getMySharedBotSubscriptions().catch(() => ({ data: [] }))
                ]);

                // Process external bots data
                const externalBots = (externalBotsResponse.data || []).map(bot => ({
                    ...bot,
                    bot_type: 'external',
                    bot_id: bot.id,
                    name: bot.name || bot.api_url,
                    status: bot.status || 'unknown'
                }));

                // Process shared bots data
                const sharedBots = (sharedBotsResponse.data || []).map(bot => ({
                    ...bot,
                    bot_type: 'shared',
                    bot_id: bot.id,
                    status: bot.status || 'unknown'
                }));

                // Combine both types
                this.bots = [...externalBots, ...sharedBots];

                // Load real-time data for external bots
                await this.loadRealTimeData();
                
                this.updateStats();
            } catch (error) {
                console.error('Error loading bots:', error);
                this.$toast.add({
                    severity: 'error',
                    summary: 'Error',
                    detail: 'Failed to load bots',
                    life: 3000
                });
            } finally {
                this.loading = false;
            }
        },

        async loadRealTimeData() {
            // Load real-time data for each external bot
            const externalBots = this.bots.filter(bot => bot.bot_type === 'external');
            
            for (const bot of externalBots) {
                try {
                    const [statusResponse, performanceResponse] = await Promise.all([
                        api.getBotStatus(bot.id).catch(() => null),
                        api.getBotPerformance(bot.id).catch(() => null)
                    ]);
                    
                    this.realTimeData[bot.id] = {
                        status: statusResponse?.data || {},
                        performance: performanceResponse?.data || {}
                    };
                    
                    // Update bot status with real data
                    if (statusResponse?.data?.status) {
                        bot.status = statusResponse.data.status;
                    }
                    
                } catch (error) {
                    console.error(`Error loading data for bot ${bot.id}:`, error);
                }
            }
        },

        async refreshBots() {
            await this.loadBots();
        },

        updateStats() {
            this.stats.totalBots = this.bots.length;
            this.stats.runningBots = this.bots.filter(bot => bot.status === 'running').length;
            // TODO: Calculate actual profit and trades from bot data
            this.stats.totalProfit = 0;
            this.stats.activeTrades = 0;
        },

        getStatusSeverity(status) {
            const severityMap = {
                'running': 'success',
                'stopped': 'secondary',
                'error': 'danger',
                'starting': 'info',
                'stopping': 'warning'
            };
            return severityMap[status] || 'secondary';
        },

        formatDate(dateString) {
            if (!dateString) return 'N/A';
            return new Date(dateString).toLocaleDateString();
        },

        // Helper method to check if bot is executing a command
        isExecuting(botId) {
            return this.executingBots.has(botId);
        },

        // Bot control methods with real server communication
        async startBot(bot) {
            if (bot.bot_type !== 'external') {
                this.$toast.add({
                    severity: 'warn',
                    summary: 'Not Available',
                    detail: 'Start command is only available for external bots',
                    life: 3000
                });
                return;
            }

            this.executingBots.add(bot.id);
            this.lastAction = 'start';
            
            try {
                await api.startExternalBot(bot.id);
                this.$toast.add({
                    severity: 'success',
                    summary: 'Success',
                    detail: `Bot "${bot.name}" start command sent`,
                    life: 3000
                });
                
                // Update local status immediately
                bot.status = 'starting';
                
                // Refresh data after a delay
                setTimeout(async () => {
                    await this.loadRealTimeData();
                }, 2000);
                
            } catch (error) {
                console.error('Error starting bot:', error);
                this.$toast.add({
                    severity: 'error',
                    summary: 'Error',
                    detail: error.response?.data?.detail || 'Failed to start bot',
                    life: 3000
                });
            } finally {
                this.executingBots.delete(bot.id);
            }
        },

        async pauseBot(bot) {
            if (bot.bot_type !== 'external') {
                this.$toast.add({
                    severity: 'warn',
                    summary: 'Not Available',
                    detail: 'Pause command is only available for external bots',
                    life: 3000
                });
                return;
            }

            this.executingBots.add(bot.id);
            this.lastAction = 'pause';
            
            try {
                // Send pause command via terminal command
                await api.executeTerminalCommand(bot.id, 'pause', []);
                this.$toast.add({
                    severity: 'info',
                    summary: 'Success',
                    detail: `Bot "${bot.name}" pause command sent`,
                    life: 3000
                });
                
                // Update local status
                bot.status = 'paused';
                
            } catch (error) {
                console.error('Error pausing bot:', error);
                this.$toast.add({
                    severity: 'error',
                    summary: 'Error',
                    detail: error.response?.data?.detail || 'Failed to pause bot',
                    life: 3000
                });
            } finally {
                this.executingBots.delete(bot.id);
            }
        },

        async stopBot(bot) {
            if (bot.bot_type !== 'external') {
                this.$toast.add({
                    severity: 'warn',
                    summary: 'Not Available',
                    detail: 'Stop command is only available for external bots',
                    life: 3000
                });
                return;
            }

            this.executingBots.add(bot.id);
            this.lastAction = 'stop';
            
            try {
                await api.stopExternalBot(bot.id);
                this.$toast.add({
                    severity: 'success',
                    summary: 'Success',
                    detail: `Bot "${bot.name}" stop command sent`,
                    life: 3000
                });
                
                // Update local status immediately
                bot.status = 'stopping';
                
                // Refresh data after a delay
                setTimeout(async () => {
                    await this.loadRealTimeData();
                }, 2000);
                
            } catch (error) {
                console.error('Error stopping bot:', error);
                this.$toast.add({
                    severity: 'error',
                    summary: 'Error',
                    detail: error.response?.data?.detail || 'Failed to stop bot',
                    life: 3000
                });
            } finally {
                this.executingBots.delete(bot.id);
            }
        },

        async restartBot(bot) {
            if (bot.bot_type !== 'external') {
                this.$toast.add({
                    severity: 'warn',
                    summary: 'Not Available',
                    detail: 'Restart command is only available for external bots',
                    life: 3000
                });
                return;
            }

            this.executingBots.add(bot.id);
            this.lastAction = 'restart';
            
            try {
                // Stop first, then start
                await api.stopExternalBot(bot.id);
                bot.status = 'stopping';
                
                // Wait a moment, then start
                setTimeout(async () => {
                    try {
                        await api.startExternalBot(bot.id);
                        bot.status = 'starting';
                        
                        this.$toast.add({
                            severity: 'success',
                            summary: 'Success',
                            detail: `Bot "${bot.name}" restart command sent`,
                            life: 3000
                        });
                        
                        // Refresh data after restart
                        setTimeout(async () => {
                            await this.loadRealTimeData();
                        }, 3000);
                        
                    } catch (error) {
                        console.error('Error restarting bot (start phase):', error);
                        this.$toast.add({
                            severity: 'error',
                            summary: 'Error',
                            detail: 'Failed to restart bot (start phase)',
                            life: 3000
                        });
                    } finally {
                        this.executingBots.delete(bot.id);
                    }
                }, 2000);
                
            } catch (error) {
                console.error('Error restarting bot (stop phase):', error);
                this.$toast.add({
                    severity: 'error',
                    summary: 'Error',
                    detail: error.response?.data?.detail || 'Failed to restart bot (stop phase)',
                    life: 3000
                });
                this.executingBots.delete(bot.id);
            }
        },

        async deleteBot(bot) {
            const confirmMessage = `Are you sure you want to delete bot "${bot.name}"? This action cannot be undone.`;
            
            if (confirm(confirmMessage)) {
                try {
                    if (bot.bot_type === 'external') {
                        await api.deleteExternalBot(bot.id);
                    } else {
                        await api.unsubscribeFromSharedBot(bot.id);
                    }
                    
                    this.$toast.add({
                        severity: 'success',
                        summary: 'Success',
                        detail: `Bot "${bot.name}" deleted successfully`,
                        life: 3000
                    });
                    await this.loadBots();
                } catch (error) {
                    console.error('Error deleting bot:', error);
                    this.$toast.add({
                        severity: 'error',
                        summary: 'Error',
                        detail: error.response?.data?.detail || 'Failed to delete bot',
                        life: 3000
                    });
                }
            }
        },

        openTerminal(bot) {
            // Navigate to terminal with pre-selected bot
            this.$router.push({
                name: 'terminal',
                query: { bot: bot.id }
            });
        },

        viewBotPerformance(bot) {
            // Navigate to bot performance view or show modal
            this.$router.push(`/bots/${bot.id}/performance`);
        },

        openBotSettings(bot) {
            // TODO: Implement bot settings modal or page
            this.$toast.add({
                severity: 'info',
                summary: 'Coming Soon',
                detail: 'Bot settings feature is coming soon',
                life: 3000
            });
        },

        showConnectBotModal() {
            this.connectBotModalVisible = true;
        },

        onBotConnected(botData) {
            this.connectBotModalVisible = false;
            this.$toast.add({
                severity: 'success',
                summary: 'Bot Connected',
                detail: `Successfully connected ${botData.name}!`,
                life: 5000
            });
            // Refresh the bots list
            this.loadBots();
        },

        initWebSocket() {
            // TODO: Implement WebSocket connection for real-time updates
            // const token = localStorage.getItem('authToken');
            // this.websocket = new WebSocket(`ws://localhost:8000/api/v1/ws/${token}`);
            // this.websocket.onmessage = (event) => {
            //     const data = JSON.parse(event.data);
            //     this.handleWebSocketMessage(data);
            // };
        },

        handleWebSocketMessage(data) {
            if (data.type === 'bot_status_update') {
                // Update bot statuses in real-time
                this.loadBots();
            }
        }
    }
};
</script>

<style scoped>
.dashboard-container {
    max-width: 1400px;
    margin: 0 auto;
}

.stat-card {
    background: white;
    transition: transform 0.2s ease-in-out;
}

.stat-card:hover {
    transform: translateY(-2px);
}

.stat-icon {
    width: 3rem;
    height: 3rem;
    display: flex;
    align-items: center;
    justify-content: center;
}

.bot-table-container {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

:deep(.bot-table .p-datatable-tbody > tr > td) {
    padding: 1rem;
    border-bottom: 1px solid #e9ecef;
}

:deep(.bot-table .p-datatable-thead > tr > th) {
    padding: 1rem;
    background: #f8f9fa;
    color: #495057;
    font-weight: 600;
}

/* Bot Actions Styling */
.bot-actions {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    min-width: 280px;
}

.control-buttons {
    display: flex;
    gap: 0.25rem;
    justify-content: flex-start;
}

.additional-actions {
    display: flex;
    gap: 0.25rem;
    justify-content: flex-start;
}

.action-btn {
    border-radius: 6px !important;
    padding: 0.5rem !important;
    font-size: 0.875rem !important;
    min-width: 2.5rem;
    height: 2.5rem;
    transition: all 0.2s ease;
}

.action-btn.success {
    background: #22c55e !important;
    border-color: #22c55e !important;
    color: white !important;
}

.action-btn.success:hover:not(:disabled) {
    background: #16a34a !important;
    border-color: #16a34a !important;
    transform: translateY(-1px);
}

.action-btn.warning {
    background: #f59e0b !important;
    border-color: #f59e0b !important;
    color: white !important;
}

.action-btn.warning:hover:not(:disabled) {
    background: #d97706 !important;
    border-color: #d97706 !important;
    transform: translateY(-1px);
}

.action-btn.danger {
    background: #ef4444 !important;
    border-color: #ef4444 !important;
    color: white !important;
}

.action-btn.danger:hover:not(:disabled) {
    background: #dc2626 !important;
    border-color: #dc2626 !important;
    transform: translateY(-1px);
}

.action-btn.info {
    background: #3b82f6 !important;
    border-color: #3b82f6 !important;
    color: white !important;
}

.action-btn.info:hover:not(:disabled) {
    background: #2563eb !important;
    border-color: #2563eb !important;
    transform: translateY(-1px);
}

.action-btn.secondary {
    background: #6b7280 !important;
    border-color: #6b7280 !important;
    color: white !important;
}

.action-btn.secondary:hover:not(:disabled) {
    background: #4b5563 !important;
    border-color: #4b5563 !important;
    transform: translateY(-1px);
}

.action-btn.danger-outline {
    background: transparent !important;
    border-color: #ef4444 !important;
    color: #ef4444 !important;
}

.action-btn.danger-outline:hover:not(:disabled) {
    background: #ef4444 !important;
    color: white !important;
    transform: translateY(-1px);
}

.action-btn:disabled {
    opacity: 0.5 !important;
    cursor: not-allowed !important;
    transform: none !important;
}

.actions-column {
    min-width: 300px;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .bot-actions {
        min-width: 200px;
    }
    
    .control-buttons,
    .additional-actions {
        flex-wrap: wrap;
    }
    
    .action-btn {
        min-width: 2rem;
        height: 2rem;
        padding: 0.25rem !important;
    }
}
</style>