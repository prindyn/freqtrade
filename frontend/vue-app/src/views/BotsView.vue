<template>
    <div class="bots-view p-p-3"> <!-- Added PrimeVue padding class -->
        <h1>Manage Your Bots</h1>
        <div class="controls p-d-flex p-jc-between p-mb-3"> <!-- PrimeFlex for layout -->
            <div class="p-d-flex p-jc-start">
                <Button @click="fetchBots" :loading="isLoading" class="p-button-info p-mr-2" icon="pi pi-refresh"
                    label="Refresh Bots" />
                <Button @click="goToCreateBot" class="p-button-success p-mr-2" icon="pi pi-plus" label="Create New Bot" />
            </div>
            <div class="p-d-flex p-jc-end">
                <Button @click="goToConnectBot" class="p-button-secondary p-mr-2" icon="pi pi-link" label="Connect Bot" />
                <Button @click="goToMarketplace" class="p-button-primary" icon="pi pi-shopping-cart" label="Marketplace" />
            </div>
        </div>

        <Message v-if="error" severity="error" :closable="true" @close="error = null" class="p-mb-3">
            Error fetching bots: {{ error.message || error }}
            <div v-if="error.response && error.response.data && error.response.data.detail" class="p-mt-1">
                <small>Detail: {{ error.response.data.detail }}</small>
            </div>
        </Message>

        <DataTable :value="bots" :loading="isLoading" responsiveLayout="scroll" v-if="bots.length > 0 || isLoading"
            class="p-datatable-customers">
            <template #header>
                <div class="table-header">
                    Your Bots
                </div>
            </template>
            <template #empty v-if="!isLoading && bots.length === 0">
                No bots found for your account.
            </template>
            <Column field="name" header="Bot Name" :sortable="true" style="min-width:12rem">
                <template #body="slotProps">
                    <div class="p-d-flex p-ai-center">
                        <span class="p-mr-2">{{ slotProps.data.name || slotProps.data.bot_id }}</span>
                        <Tag v-if="slotProps.data.bot_type === 'external'" value="External" severity="info" class="p-tag-sm" />
                        <Tag v-else-if="slotProps.data.bot_type === 'shared'" value="Shared" severity="success" class="p-tag-sm" />
                        <Tag v-else value="Platform" severity="warning" class="p-tag-sm" />
                    </div>
                </template>
            </Column>
            <Column field="status" header="Status" :sortable="true" style="min-width:8rem">
                <template #body="slotProps">
                    <Tag :value="slotProps.data.status" :severity="getStatusSeverity(slotProps.data.status)" />
                </template>
            </Column>
            <Column field="source" header="Source" style="min-width:10rem">
                <template #body="slotProps">
                    <div v-if="slotProps.data.bot_type === 'external'">
                        <i class="pi pi-link p-mr-1"></i>
                        {{ slotProps.data.api_url || 'External API' }}
                    </div>
                    <div v-else-if="slotProps.data.bot_type === 'shared'">
                        <i class="pi pi-cloud p-mr-1"></i>
                        {{ slotProps.data.config_template || 'Platform Managed' }}
                    </div>
                    <div v-else>
                        <i class="pi pi-server p-mr-1"></i>
                        {{ slotProps.data.details?.host_port || 'N/A' }}
                    </div>
                </template>
            </Column>
            <Column field="details.created_at" header="Created At" :sortable="true" style="min-width:12rem">
                <template #body="slotProps">
                    {{ slotProps.data.details && slotProps.data.details.created_at ?
                        formatDate(slotProps.data.details.created_at) : 'N/A' }}
                </template>
            </Column>
            <Column header="Actions" style="min-width:18rem; text-align:center;">
                <template #body="slotProps">
                    <Button v-if="canStartBot(slotProps.data)" icon="pi pi-play" class="p-button-success p-button-sm p-mr-1"
                        @click="startBot(slotProps.data)" v-tooltip.top="'Start Bot'" :loading="slotProps.data._starting" />
                    <Button v-if="canStopBot(slotProps.data)" icon="pi pi-stop" class="p-button-warning p-button-sm p-mr-1"
                        @click="stopBot(slotProps.data)" v-tooltip.top="'Stop Bot'" :loading="slotProps.data._stopping" />
                    <Button icon="pi pi-align-justify" class="p-button-info p-button-sm p-mr-1"
                        @click="openLogsModal(slotProps.data)" v-tooltip.top="'View Logs'" />
                    <Button icon="pi pi-trash" class="p-button-danger p-button-sm"
                        @click="confirmDeleteBot(slotProps.data)" v-tooltip.top="'Delete Bot'" />
                </template>
            </Column>
        </DataTable>
        <Message v-if="!isLoading && !error && bots.length === 0" severity="info" :closable="false">No bots found for
            your
            account.</Message>


        <!-- Logs Modal -->
        <Dialog header="Bot Logs" v-model:visible="showLogsModal" :style="{ width: '75vw', 'max-height': '90vh' }"
            :modal="true" :dismissableMask="true" class="p-dialog-maximized">
            <template #header>
                <div class="p-d-flex p-ai-center">
                    <i class="pi pi-align-justify p-mr-2" style="font-size: 1.5rem"></i>
                    <span class="p-dialog-title">Logs for Bot: {{ selectedBotIdForLogs }}</span>
                </div>
            </template>
            <div v-if="isLoadingLogs" class="p-text-center p-p-3">
                <ProgressSpinner style="width:50px;height:50px" strokeWidth="8" animationDuration=".5s" />
                <p>Loading logs...</p>
            </div>
            <pre v-else-if="currentBotLogs" class="logs-pre">{{ currentBotLogs }}</pre>
            <Message v-else severity="info">No logs available or an error occurred.</Message>
            <template #footer>
                <Button label="Close" icon="pi pi-times" @click="closeLogsModal" class="p-button-text" />
            </template>
        </Dialog>
    </div>
</template>

<script>
import api from '@/services/api';
import Button from 'primevue/button';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Tag from 'primevue/tag';
import Message from 'primevue/message';
import Dialog from 'primevue/dialog';
import ProgressSpinner from 'primevue/progressspinner';
// For Tooltip (optional, if you want to use v-tooltip directive)
// import Tooltip from 'primevue/tooltip'; // Not strictly needed if using global registration or if not using custom options

export default {
    name: 'BotsView',
    // directives: { // Register tooltip if needed locally
    //   'tooltip': Tooltip
    // },
    components: {
        Button,
        DataTable,
        Column,
        Tag,
        Message,
        Dialog,
        ProgressSpinner
    },
    data() {
        return {
            bots: [],
            isLoading: false,
            error: null,
            // tenantId: 'default-tenant', // Removed
            showLogsModal: false,
            currentBotLogs: '',
            selectedBotIdForLogs: null,
            isLoadingLogs: false,
        };
    },
    methods: {
        async fetchBots() {
            this.isLoading = true;
            this.error = null;
            try {
                // Fetch both platform bots and external bots
                const [platformBotsResponse, externalBotsResponse] = await Promise.all([
                    api.getBots().catch(() => ({ data: [] })),
                    api.getExternalBots().catch(() => ({ data: [] }))
                ]);
                
                // Combine and mark bot types
                const platformBots = (platformBotsResponse.data || []).map(bot => ({
                    ...bot,
                    bot_type: bot.bot_type || 'platform',
                    name: bot.name || bot.bot_id
                }));
                
                const externalBots = (externalBotsResponse.data || []).map(bot => ({
                    ...bot,
                    bot_type: 'external',
                    name: bot.name || bot.bot_id || 'External Bot'
                }));
                
                this.bots = [...platformBots, ...externalBots];
            } catch (err) {
                console.error('Error fetching bots:', err);
                if (err.response && err.response.status === 404) {
                    this.error = null;
                    this.bots = [];
                } else if (err.response) {
                    this.error = { message: `Server error (${err.response.status}) while fetching bots.`, response: err.response };
                } else if (err.request) {
                    this.error = { message: 'No response from server. Is the backend running?' };
                } else {
                    this.error = { message: err.message || 'An unknown error occurred.' };
                }
                if (this.error) this.bots = [];
            } finally {
                this.isLoading = false;
            }
        },
        goToCreateBot() {
            this.$router.push({ name: 'create-bot' });
        },
        goToConnectBot() {
            this.$router.push({ name: 'connect-bot' });
        },
        goToMarketplace() {
            this.$router.push({ name: 'marketplace' });
        },
        async openLogsModal(bot) {
            const botId = bot.bot_id || bot.id;
            this.selectedBotIdForLogs = botId;
            this.isLoadingLogs = true;
            this.showLogsModal = true;
            this.currentBotLogs = '';
            try {
                let response;
                if (bot.bot_type === 'external') {
                    response = await api.getExternalBotLogs(botId);
                } else {
                    response = await api.getBotLogs(botId);
                }
                
                if (response.data && response.data.logs) {
                    this.currentBotLogs = response.data.logs;
                } else if (response.data && response.data.message) {
                    this.currentBotLogs = response.data.message;
                } else {
                    this.currentBotLogs = 'No logs available or bot not running.';
                }
            } catch (err) {
                console.error(`Error fetching logs for ${botId}:`, err);
                this.currentBotLogs = `Failed to load logs: ${err.message || 'Unknown error'}`;
                if (err.response && err.response.data && err.response.data.detail) {
                    this.currentBotLogs += `\nDetail: ${err.response.data.detail}`;
                }
            } finally {
                this.isLoadingLogs = false;
            }
        },
        closeLogsModal() {
            this.showLogsModal = false;
            this.currentBotLogs = '';
            this.selectedBotIdForLogs = null;
        },
        confirmDeleteBot(bot) {
            const botName = bot.name || bot.bot_id;
            if (confirm(`Are you sure you want to delete bot "${botName}"? This action cannot be undone.`)) {
                this.deleteBot(bot);
            }
        },
        async deleteBot(bot) {
            const botId = bot.bot_id || bot.id;
            try {
                if (bot.bot_type === 'external') {
                    await api.deleteExternalBot(botId);
                } else {
                    await api.deleteBot(botId);
                }
                this.fetchBots(); // Refresh list
            } catch (err) {
                console.error('Error deleting bot:', err);
                this.error = { message: `Failed to delete bot: ${err.message || 'Unknown error'}` };
            }
        },
        canStartBot(bot) {
            const status = (bot.status || '').toLowerCase();
            return !status.includes('running') && !bot._starting;
        },
        canStopBot(bot) {
            const status = (bot.status || '').toLowerCase();
            return status.includes('running') && !bot._stopping;
        },
        async startBot(bot) {
            const botId = bot.bot_id || bot.id;
            this.$set(bot, '_starting', true);
            try {
                if (bot.bot_type === 'external') {
                    await api.startExternalBot(botId);
                } else {
                    await api.startBot(botId);
                }
                // Refresh the specific bot status
                setTimeout(() => this.fetchBots(), 1000);
            } catch (err) {
                console.error('Error starting bot:', err);
                this.error = { message: `Failed to start bot: ${err.message || 'Unknown error'}` };
            } finally {
                this.$set(bot, '_starting', false);
            }
        },
        async stopBot(bot) {
            const botId = bot.bot_id || bot.id;
            this.$set(bot, '_stopping', true);
            try {
                if (bot.bot_type === 'external') {
                    await api.stopExternalBot(botId);
                } else {
                    await api.stopBot(botId);
                }
                // Refresh the specific bot status
                setTimeout(() => this.fetchBots(), 1000);
            } catch (err) {
                console.error('Error stopping bot:', err);
                this.error = { message: `Failed to stop bot: ${err.message || 'Unknown error'}` };
            } finally {
                this.$set(bot, '_stopping', false);
            }
        },
        formatDate(dateString) {
            if (!dateString) return 'N/A';
            const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
            return new Date(dateString).toLocaleDateString(undefined, options);
        },
        getStatusSeverity(status) {
            if (!status) return 'info';
            status = status.toLowerCase();
            if (status.includes('running') || status.includes('created')) return 'success';
            if (status.includes('stopped') || status.includes('exited')) return 'warning';
            if (status.includes('error')) return 'danger';
            return 'info';
        }
    },
    created() {
        this.fetchBots();
    },
};
</script>

<style scoped>
.bots-view {
    /* padding: 20px; // Replaced by p-p-3 */
    background-color: #fff;
    border-radius: 8px;
    /* box-shadow: 0 2px 4px rgba(0,0,0,0.1); // PrimeVue components have their own shadow */
    /* max-width: 900px; // DataTable can be responsive */
    margin: auto;
}

/* .controls { // Replaced by PrimeFlex classes
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
  align-items: center;
} */

.table-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 1.25rem;
    font-weight: bold;
}

.logs-pre {
    white-space: pre-wrap;
    word-break: break-all;
    background-color: #2a2a2a;
    color: #f8f8f2;
    padding: 15px;
    border-radius: 4px;
    max-height: 60vh;
    /* Ensure this is less than Dialog's max-height to see effect */
    overflow-y: auto;
    font-family: 'Courier New', Courier, monospace;
    font-size: 0.9rem;
}

.p-message {
    /* Ensure PrimeVue Message component takes full width if error message is long */
    width: 100%;
    box-sizing: border-box;
}

/* PrimeVue DataTable custom styling if needed */
.p-datatable-customers .p-datatable-thead>tr>th {
    background-color: #e9ecef;
    color: #495057;
    border-color: #dee2e6;
}
</style>
