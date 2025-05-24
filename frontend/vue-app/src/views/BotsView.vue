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
                            <!-- Primary Control Buttons -->
                            <div class="primary-controls">
                                <Button icon="pi pi-play" class="control-btn success" v-tooltip="'Start Bot'"
                                    @click="startBot(slotProps.data)"
                                    :disabled="slotProps.data.status === 'running' || isExecuting(slotProps.data.bot_id)"
                                    :loading="isExecuting(slotProps.data.bot_id) && lastAction === 'start'" />

                                <Button icon="pi pi-stop" class="control-btn danger" v-tooltip="'Stop Bot'"
                                    @click="stopBot(slotProps.data)"
                                    :disabled="slotProps.data.status === 'stopped' || isExecuting(slotProps.data.bot_id)"
                                    :loading="isExecuting(slotProps.data.bot_id) && lastAction === 'stop'" />

                                <!-- More Actions Dropdown -->
                                <SplitButton icon="pi pi-cog" class="control-btn secondary" v-tooltip="'More Actions'"
                                    :model="getMoreActionsMenu(slotProps.data)" @click="openBotSettings(slotProps.data)"
                                    menuButtonIcon="pi pi-chevron-down" />
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
import SplitButton from 'primevue/splitbutton';
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
        SplitButton,
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
            realTimeData: {}, // Store real-time bot data
            commandInputs: {}, // Store command inputs for each bot
            commandHistory: {}, // Store command history for each bot
            showCommandHistory: {} // Toggle command history display for each bot
        };
    },
    async mounted() {
        // Ensure auth header is set
        const token = localStorage.getItem('authToken');
        if (token) {
            console.log('Setting auth header with token:', token.substring(0, 10) + '...');
            api.setAuthHeader(token);
        } else {
            console.warn('No auth token found in localStorage');
        }

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
                console.log('Loading bots...');

                // Load external bots (primary) and shared bots
                const [externalBotsResponse, sharedBotsResponse] = await Promise.all([
                    api.getExternalBots().catch(err => {
                        console.error('Error loading external bots:', err);
                        return { data: [] };
                    }),
                    api.getMySharedBotSubscriptions().catch(err => {
                        console.error('Error loading shared bots:', err);
                        return { data: [] };
                    })
                ]);

                console.log('External bots response:', externalBotsResponse);
                console.log('Shared bots response:', sharedBotsResponse);

                // Process external bots data
                const externalBots = (externalBotsResponse.data || []).map(bot => {
                    console.log('Processing external bot:', bot);
                    return {
                        ...bot,
                        bot_type: 'external',
                        bot_id: bot.bot_id || bot.id,
                        name: bot.name || bot.api_url || `Bot ${bot.bot_id || bot.id}`,
                        status: bot.status || 'unknown',
                        details: {
                            created_at: bot.created_at,
                            host_port: bot.api_url ? (function () {
                                try {
                                    return new URL(bot.api_url).port || new URL(bot.api_url).hostname;
                                } catch (e) {
                                    return bot.api_url;
                                }
                            })() : 'N/A',
                            api_url: bot.api_url
                        }
                    };
                });

                // Process shared bots data
                const sharedBots = (sharedBotsResponse.data || []).map(bot => {
                    console.log('Processing shared bot:', bot);
                    return {
                        ...bot,
                        bot_type: 'shared',
                        bot_id: bot.bot_id || bot.id,
                        name: bot.name || `Shared Bot ${bot.bot_id || bot.id}`,
                        status: bot.status || 'unknown',
                        details: {
                            created_at: bot.created_at,
                            host_port: 'N/A'
                        }
                    };
                });

                // Combine both types
                this.bots = [...externalBots, ...sharedBots];
                console.log('Combined bots:', this.bots);

                // Initialize command data for each bot
                this.bots.forEach(bot => {
                    this.initializeBotCommandData(bot.bot_id);
                });

                // Load real-time data for external bots
                if (externalBots.length > 0) {
                    await this.loadRealTimeData();
                }

                this.updateStats();

                // Show success message if bots were loaded
                if (this.bots.length > 0) {
                    console.log(`Successfully loaded ${this.bots.length} bots`);
                } else {
                    console.log('No bots found');
                    this.$toast.add({
                        severity: 'info',
                        summary: 'No Bots',
                        detail: 'No connected bots found. Connect a bot to get started.',
                        life: 5000
                    });
                }

            } catch (error) {
                console.error('Error loading bots:', error);
                this.$toast.add({
                    severity: 'error',
                    summary: 'Error',
                    detail: `Failed to load bots: ${error.message}`,
                    life: 5000
                });
            } finally {
                this.loading = false;
            }
        },

        async loadRealTimeData() {
            // Load real-time data for each external bot
            const externalBots = this.bots.filter(bot => bot.bot_type === 'external');
            console.log(`Loading real-time data for ${externalBots.length} external bots...`);

            for (const bot of externalBots) {
                try {
                    console.log(`Loading data for bot ${bot.bot_id} (${bot.name})...`);

                    const [statusResponse, performanceResponse] = await Promise.all([
                        api.getExternalBotStatus(bot.bot_id).catch(err => {
                            console.warn(`Failed to get status for bot ${bot.bot_id}:`, err);
                            return null;
                        }),
                        api.getExternalBotPerformance(bot.bot_id).catch(err => {
                            console.warn(`Failed to get performance for bot ${bot.bot_id}:`, err);
                            return null;
                        })
                    ]);

                    console.log(`Bot ${bot.bot_id} status response:`, statusResponse);
                    console.log(`Bot ${bot.bot_id} performance response:`, performanceResponse);

                    this.realTimeData[bot.bot_id] = {
                        status: statusResponse?.data || {},
                        performance: performanceResponse?.data || {}
                    };

                    // Update bot status with real data
                    if (statusResponse?.data?.status) {
                        console.log(`Updating bot ${bot.bot_id} status from '${bot.status}' to '${statusResponse.data.status}'`);
                        bot.status = statusResponse.data.status;
                    }

                } catch (error) {
                    console.error(`Error loading data for bot ${bot.bot_id}:`, error);
                }
            }

            console.log('Real-time data loading complete. Updated bots:', this.bots);
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

        formatTime(timestamp) {
            return new Date(timestamp).toLocaleTimeString();
        },

        // Initialize command data for a bot if it doesn't exist
        initializeBotCommandData(botId) {
            if (!this.commandInputs[botId]) {
                this.commandInputs[botId] = { command: null };
            }
            if (!this.commandHistory[botId]) {
                this.commandHistory[botId] = [];
            }
            if (!this.showCommandHistory[botId]) {
                this.showCommandHistory[botId] = false;
            }
        },

        // Get more actions menu for each bot
        getMoreActionsMenu(bot) {
            return [
                {
                    label: 'Restart',
                    icon: 'pi pi-refresh',
                    command: () => this.restartBot(bot),
                    disabled: this.isExecuting(bot.bot_id)
                },
                {
                    label: 'Pause',
                    icon: 'pi pi-pause',
                    command: () => this.pauseBot(bot),
                    disabled: bot.status !== 'running' || this.isExecuting(bot.bot_id)
                },
                { separator: true },
                {
                    label: 'Terminal',
                    icon: 'pi pi-desktop',
                    command: () => this.openTerminal(bot)
                },
                {
                    label: 'Performance',
                    icon: 'pi pi-chart-line',
                    command: () => this.viewBotPerformance(bot)
                },
                { separator: true },
                {
                    label: 'Delete',
                    icon: 'pi pi-trash',
                    command: () => this.deleteBot(bot),
                    class: 'p-menuitem-danger'
                }
            ];
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

            this.executingBots.add(bot.bot_id);
            this.lastAction = 'start';

            try {
                // Send start command to the external bot
                await api.startExternalBot(bot.bot_id);

                this.$toast.add({
                    severity: 'success',
                    summary: 'Success',
                    detail: `Bot "${bot.name}" start command sent successfully`,
                    life: 3000
                });

                // Update local status immediately
                bot.status = 'starting';

                // Refresh data after a delay to get updated status
                setTimeout(async () => {
                    await this.loadRealTimeData();
                }, 3000);

            } catch (error) {
                console.error('Error starting bot:', error);
                this.$toast.add({
                    severity: 'error',
                    summary: 'Error',
                    detail: error.response?.data?.detail || 'Failed to start bot',
                    life: 3000
                });
            } finally {
                this.executingBots.delete(bot.bot_id);
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

            this.executingBots.add(bot.bot_id);
            this.lastAction = 'pause';

            try {
                // For now, use stop command since pause is not implemented
                await api.stopExternalBot(bot.bot_id);

                this.$toast.add({
                    severity: 'info',
                    summary: 'Success',
                    detail: `Bot "${bot.name}" pause command sent successfully`,
                    life: 3000
                });

                // Update local status
                bot.status = 'paused';

                // Refresh data after a delay
                setTimeout(async () => {
                    await this.loadRealTimeData();
                }, 3000);

            } catch (error) {
                console.error('Error pausing bot:', error);
                this.$toast.add({
                    severity: 'error',
                    summary: 'Error',
                    detail: error.response?.data?.detail || 'Failed to pause bot',
                    life: 3000
                });
            } finally {
                this.executingBots.delete(bot.bot_id);
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

            this.executingBots.add(bot.bot_id);
            this.lastAction = 'stop';

            try {
                // Send stop command to the external bot
                await api.stopExternalBot(bot.bot_id);

                this.$toast.add({
                    severity: 'success',
                    summary: 'Success',
                    detail: `Bot "${bot.name}" stop command sent successfully`,
                    life: 3000
                });

                // Update local status immediately
                bot.status = 'stopping';

                // Refresh data after a delay to get updated status
                setTimeout(async () => {
                    await this.loadRealTimeData();
                }, 3000);

            } catch (error) {
                console.error('Error stopping bot:', error);
                this.$toast.add({
                    severity: 'error',
                    summary: 'Error',
                    detail: error.response?.data?.detail || 'Failed to stop bot',
                    life: 3000
                });
            } finally {
                this.executingBots.delete(bot.bot_id);
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

            this.executingBots.add(bot.bot_id);
            this.lastAction = 'restart';

            try {
                // Send stop command first
                await api.stopExternalBot(bot.bot_id);
                bot.status = 'stopping';

                // Wait a moment, then send start command
                setTimeout(async () => {
                    try {
                        await api.startExternalBot(bot.bot_id);
                        bot.status = 'starting';

                        this.$toast.add({
                            severity: 'success',
                            summary: 'Success',
                            detail: `Bot "${bot.name}" restart command sent successfully`,
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
                        this.executingBots.delete(bot.bot_id);
                    }
                }, 3000);

            } catch (error) {
                console.error('Error restarting bot (stop phase):', error);
                this.$toast.add({
                    severity: 'error',
                    summary: 'Error',
                    detail: error.response?.data?.detail || 'Failed to restart bot (stop phase)',
                    life: 3000
                });
                this.executingBots.delete(bot.bot_id);
            }
        },

        async deleteBot(bot) {
            const confirmMessage = `Are you sure you want to delete bot "${bot.name}"? This action cannot be undone.`;

            if (confirm(confirmMessage)) {
                try {
                    if (bot.bot_type === 'external') {
                        await api.deleteExternalBot(bot.bot_id);
                    } else {
                        await api.unsubscribeFromSharedBot(bot.bot_id);
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
                query: { bot: bot.bot_id }
            });
        },

        viewBotPerformance(bot) {
            // Navigate to bot performance view or show modal
            this.$router.push(`/bots/${bot.bot_id}/performance`);
        },

        openBotSettings() {
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
    gap: 0.5rem;
    min-width: 200px;
    align-items: center;
}

.primary-controls {
    display: flex;
    gap: 0.25rem;
    justify-content: flex-start;
}

.control-btn {
    border-radius: 6px !important;
    padding: 0.5rem !important;
    font-size: 0.875rem !important;
    min-width: 2.5rem;
    height: 2.5rem;
    transition: all 0.2s ease;
}

.control-btn.success {
    background: #22c55e !important;
    border-color: #22c55e !important;
    color: white !important;
}

.control-btn.success:hover:not(:disabled) {
    background: #16a34a !important;
    border-color: #16a34a !important;
    transform: translateY(-1px);
}

.control-btn.danger {
    background: #ef4444 !important;
    border-color: #ef4444 !important;
    color: white !important;
}

.control-btn.danger:hover:not(:disabled) {
    background: #dc2626 !important;
    border-color: #dc2626 !important;
    transform: translateY(-1px);
}

.control-btn.info {
    background: #3b82f6 !important;
    border-color: #3b82f6 !important;
    color: white !important;
}

.control-btn.info:hover:not(:disabled) {
    background: #2563eb !important;
    border-color: #2563eb !important;
    transform: translateY(-1px);
}

.control-btn.secondary {
    background: #6b7280 !important;
    border-color: #6b7280 !important;
    color: white !important;
}

.control-btn.secondary:hover:not(:disabled) {
    background: #4b5563 !important;
    border-color: #4b5563 !important;
    transform: translateY(-1px);
}

.control-btn:disabled {
    opacity: 0.5 !important;
    cursor: not-allowed !important;
    transform: none !important;
}

.actions-column {
    min-width: 200px;
}

/* SplitButton Styling */
:deep(.p-splitbutton) {
    height: 2.5rem;
}

:deep(.p-splitbutton .p-button) {
    min-width: 2.5rem !important;
    border-radius: 6px !important;
    padding: 0.5rem !important;
    font-size: 0.875rem !important;
    transition: all 0.2s ease !important;
}

:deep(.p-splitbutton .p-button:first-child) {
    border-top-right-radius: 0 !important;
    border-bottom-right-radius: 0 !important;
}

:deep(.p-splitbutton .p-button:last-child) {
    border-top-left-radius: 0 !important;
    border-bottom-left-radius: 0 !important;
    border-left: 1px solid rgba(255, 255, 255, 0.3) !important;
    min-width: 1.5rem !important;
    padding: 0.5rem 0.375rem !important;
}

:deep(.p-splitbutton.control-btn.secondary .p-button) {
    background: #6b7280 !important;
    border-color: #6b7280 !important;
    color: white !important;
}

:deep(.p-splitbutton.control-btn.secondary .p-button:hover:not(:disabled)) {
    background: #4b5563 !important;
    border-color: #4b5563 !important;
    transform: translateY(-1px);
}

:deep(.p-splitbutton.control-btn.secondary .p-button:disabled) {
    opacity: 0.5 !important;
    cursor: not-allowed !important;
    transform: none !important;
}

/* Menu item danger styling */
:deep(.p-menuitem-danger .p-menuitem-link) {
    color: #ef4444 !important;
}

:deep(.p-menuitem-danger .p-menuitem-link:hover) {
    background: #fef2f2 !important;
    color: #dc2626 !important;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .bot-actions {
        min-width: 160px;
    }

    .primary-controls {
        flex-wrap: wrap;
    }

    .control-btn {
        min-width: 2rem;
        height: 2rem;
        padding: 0.25rem !important;
    }

    .actions-column {
        min-width: 180px;
    }
}
</style>