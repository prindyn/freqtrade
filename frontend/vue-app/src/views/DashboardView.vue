<template>
    <div class="dashboard-container p-4">
        <!-- Dashboard Header -->
        <div class="flex justify-content-between align-items-center mb-4">
            <div>
                <h1 class="text-3xl font-bold text-900 mb-2">FreqTrade Dashboard</h1>
                <p class="text-600">Manage and monitor your trading bots</p>
            </div>
            <div class="flex gap-2">
                <Button 
                    icon="pi pi-link" 
                    label="Connect Bot" 
                    class="p-button-outlined"
                    @click="$router.push('/connect-bot')"
                />
                <Button 
                    icon="pi pi-shopping-cart" 
                    label="Marketplace" 
                    class="p-button-outlined"
                    @click="$router.push('/marketplace')"
                />
                <Button 
                    icon="pi pi-plus" 
                    label="Create Bot" 
                    class="p-button-primary"
                    @click="showCreateBotDialog = true"
                />
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
                    <Button 
                        icon="pi pi-refresh" 
                        class="p-button-text"
                        @click="refreshBots"
                        :loading="loading"
                    />
                </div>
            </div>
            
            <DataTable 
                :value="bots" 
                :loading="loading"
                responsiveLayout="scroll"
                class="bot-table"
                :paginator="true"
                :rows="10"
            >
                <Column field="name" header="Bot Name" :sortable="true">
                    <template #body="slotProps">
                        <div class="flex align-items-center gap-2">
                            <Tag 
                                :value="slotProps.data.bot_type === 'external' ? 'External' : 'Shared'" 
                                :severity="slotProps.data.bot_type === 'external' ? 'info' : 'success'"
                                class="text-xs"
                            />
                            <div class="font-medium text-900">{{ slotProps.data.name || slotProps.data.bot_id }}</div>
                        </div>
                    </template>
                </Column>
                
                <Column field="status" header="Status" :sortable="true">
                    <template #body="slotProps">
                        <Tag 
                            :value="slotProps.data.status" 
                            :severity="getStatusSeverity(slotProps.data.status)"
                            class="font-medium"
                        />
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
                
                <Column header="Actions">
                    <template #body="slotProps">
                        <div class="flex gap-2">
                            <Button 
                                icon="pi pi-play" 
                                class="p-button-rounded p-button-text p-button-success"
                                v-tooltip="'Start Bot'"
                                @click="startBot(slotProps.data.bot_id)"
                                :disabled="slotProps.data.status === 'running'"
                            />
                            <Button 
                                icon="pi pi-stop" 
                                class="p-button-rounded p-button-text p-button-warning"
                                v-tooltip="'Stop Bot'"
                                @click="stopBot(slotProps.data.bot_id)"
                                :disabled="slotProps.data.status === 'stopped'"
                            />
                            <Button 
                                icon="pi pi-chart-line" 
                                class="p-button-rounded p-button-text p-button-info"
                                v-tooltip="'View Performance'"
                                @click="viewBotPerformance(slotProps.data.bot_id)"
                            />
                            <Button 
                                icon="pi pi-trash" 
                                class="p-button-rounded p-button-text p-button-danger"
                                v-tooltip="'Delete Bot'"
                                @click="deleteBot(slotProps.data.bot_id)"
                            />
                        </div>
                    </template>
                </Column>
            </DataTable>
        </div>

        <!-- Create Bot Dialog -->
        <Dialog v-model:visible="showCreateBotDialog" modal header="Create New Bot" class="w-full max-w-4xl">
            <CreateBotView @bot-created="onBotCreated" @cancel="showCreateBotDialog = false" />
        </Dialog>
    </div>
</template>

<script>
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Tag from 'primevue/tag';
import Dialog from 'primevue/dialog';
import api from '@/services/api';
import CreateBotView from './CreateBotView.vue';

export default {
    name: 'DashboardView',
    components: {
        DataTable,
        Column,
        Button,
        Tag,
        Dialog,
        CreateBotView
    },
    data() {
        return {
            bots: [],
            loading: false,
            showCreateBotDialog: false,
            stats: {
                totalBots: 0,
                runningBots: 0,
                totalProfit: 0,
                activeTrades: 0
            },
            websocket: null
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
                // Load both legacy bots and new types
                const [botsResponse, sharedBotsResponse] = await Promise.all([
                    api.getBots().catch(() => ({ data: [] })),
                    api.getMySharedBotSubscriptions().catch(() => ({ data: [] }))
                ]);
                
                // Combine both types, ensuring data is always an array
                this.bots = [
                    ...(botsResponse.data || []),
                    ...(sharedBotsResponse.data || [])
                ];
                
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
        
        async startBot(botId) {
            try {
                await api.startBot(botId);
                this.$toast.add({
                    severity: 'success',
                    summary: 'Success',
                    detail: `Bot ${botId} start command sent`,
                    life: 3000
                });
                await this.loadBots();
            } catch (error) {
                console.error('Error starting bot:', error);
                this.$toast.add({
                    severity: 'error',
                    summary: 'Error',
                    detail: 'Failed to start bot',
                    life: 3000
                });
            }
        },
        
        async stopBot(botId) {
            try {
                await api.stopBot(botId);
                this.$toast.add({
                    severity: 'success',
                    summary: 'Success',
                    detail: `Bot ${botId} stop command sent`,
                    life: 3000
                });
                await this.loadBots();
            } catch (error) {
                console.error('Error stopping bot:', error);
                this.$toast.add({
                    severity: 'error',
                    summary: 'Error',
                    detail: 'Failed to stop bot',
                    life: 3000
                });
            }
        },
        
        async deleteBot(botId) {
            if (confirm(`Are you sure you want to delete bot ${botId}?`)) {
                try {
                    await api.deleteBot(botId);
                    this.$toast.add({
                        severity: 'success',
                        summary: 'Success',
                        detail: `Bot ${botId} deleted successfully`,
                        life: 3000
                    });
                    await this.loadBots();
                } catch (error) {
                    console.error('Error deleting bot:', error);
                    this.$toast.add({
                        severity: 'error',
                        summary: 'Error',
                        detail: 'Failed to delete bot',
                        life: 3000
                    });
                }
            }
        },
        
        viewBotPerformance(botId) {
            // TODO: Navigate to bot performance view
            this.$router.push(`/bots/${botId}/performance`);
        },
        
        onBotCreated() {
            this.showCreateBotDialog = false;
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
</style>