<template>
    <div class="create-bot-view p-d-flex p-jc-center p-ai-center">
        <Card style="width: 30em; margin-top: 2em; margin-bottom: 2em;">
            <template #title>
                <div class="p-text-center">Create New Freqtrade Bot</div>
            </template>
            <template #content>
                <form @submit.prevent="handleSubmit" class="p-fluid">
                    <!-- Removed Tenant ID input field -->
                    <div class="p-field">
                        <label for="exchange_name">Exchange Name</label>
                        <InputText id="exchange_name" type="text" v-model="formData.exchange_name"
                            placeholder="e.g., binance, kraken" required />
                    </div>
                    <div class="p-field">
                        <label for="api_key">API Key</label>
                        <InputText id="api_key" type="text" v-model="formData.api_key" required />
                    </div>
                    <div class="p-field">
                        <label for="api_secret">API Secret</label>
                        <Password id="api_secret" v-model="formData.api_secret" :feedback="false" :toggleMask="true"
                            required />
                    </div>
                    <div class="p-field-checkbox">
                        <Checkbox id="dry_run" v-model="formData.dry_run" :binary="true" />
                        <label for="dry_run" class="p-ml-2">Dry Run</label>
                    </div>
                    <div class="p-field">
                        <label for="stake_currency">Stake Currency</label>
                        <InputText id="stake_currency" type="text" v-model="formData.stake_currency"
                            placeholder="e.g., USDT, BTC" required />
                    </div>
                    <div class="p-field">
                        <label for="stake_amount">Stake Amount</label>
                        <InputNumber id="stake_amount" v-model="formData.stake_amount" mode="decimal"
                            :minFractionDigits="2" :maxFractionDigits="8" required />
                    </div>
                    <div class="p-field">
                        <label for="strategy">Strategy Name (optional)</label>
                        <InputText id="strategy" v-model="formData.strategy"
                            placeholder="Defaults to SampleStrategy if empty" />
                    </div>
                    <div class="p-field">
                        <label for="pair_whitelist">Pair Whitelist (comma-separated)</label>
                        <Textarea id="pair_whitelist" v-model="pair_whitelist_str" rows="3"
                            placeholder="e.g., BTC/USDT,ETH/USDT" required />
                    </div>
                    <div class="p-field">
                        <label for="max_open_trades">Max Open Trades (optional)</label>
                        <InputNumber id="max_open_trades" v-model="formData.max_open_trades" :min="0" placeholder="3" />
                    </div>
                    <div class="p-field-checkbox">
                        <Checkbox id="telegram_enabled" v-model="formData.telegram_enabled" :binary="true" />
                        <label for="telegram_enabled" class="p-ml-2">Enable Telegram</label>
                    </div>
                    <div v-if="formData.telegram_enabled">
                        <div class="p-field">
                            <label for="telegram_token">Telegram Token</label>
                            <InputText id="telegram_token" v-model="formData.telegram_token" />
                        </div>
                        <div class="p-field">
                            <label for="telegram_chat_id">Telegram Chat ID</label>
                            <InputText id="telegram_chat_id" v-model="formData.telegram_chat_id" />
                        </div>
                    </div>

                    <Button type="submit" label="Create Bot" icon="pi pi-save" :loading="isLoading" class="p-mt-3" />

                    <Message v-if="successMessage" severity="success" :closable="true" @close="successMessage = null"
                        class="p-mt-3">{{ successMessage }}</Message>
                    <Message v-if="error" severity="error" :closable="true" @close="error = null" class="p-mt-3">
                        <div v-if="typeof error === 'string'">{{ error }}</div>
                        <div v-else>
                            <p><strong>Error:</strong> {{ error.message || 'Failed to create bot.' }}</p>
                            <p v-if="error.detail" style="font-size: 0.9em; white-space: pre-wrap;">Detail: {{
                                error.detail }}</p>
                        </div>
                    </Message>
                </form>
            </template>
        </Card>
    </div>
</template>

<script>
import api from '@/services/api';
import Card from 'primevue/card';
import InputText from 'primevue/inputtext';
import Password from 'primevue/password';
import Checkbox from 'primevue/checkbox';
import InputNumber from 'primevue/inputnumber';
import Textarea from 'primevue/textarea';
import Button from 'primevue/button';
import Message from 'primevue/message';

const initialFormData = {
    exchange_name: '',
    api_key: '',
    api_secret: '',
    dry_run: true,
    stake_currency: 'USDT',
    stake_amount: 100,
    strategy: '',
    max_open_trades: 3,
    telegram_enabled: false,
    telegram_token: '',
    telegram_chat_id: '',
};

export default {
    name: 'CreateBotView',
    components: { Card, InputText, Password, Checkbox, InputNumber, Textarea, Button, Message },
    data() {
        return {
            // tenantId: 'default-tenant', // Removed
            formData: { ...initialFormData },
            pair_whitelist_str: 'BTC/USDT,ETH/USDT', // Default example
            isLoading: false,
            error: null,
            successMessage: null,
        };
    },
    methods: {
        async handleSubmit() {
            this.isLoading = true;
            this.error = null;
            this.successMessage = null;

            if (!this.formData.exchange_name || !this.formData.api_key || !this.formData.api_secret || !this.pair_whitelist_str || !this.formData.stake_currency || this.formData.stake_amount === null) {
                this.error = 'Please fill in all required fields: Exchange, API Key, API Secret, Stake Currency, Stake Amount, and Pair Whitelist.';
                this.isLoading = false;
                return;
            }
            if (this.formData.telegram_enabled && (!this.formData.telegram_token || !this.formData.telegram_chat_id)) {
                this.error = 'If Telegram is enabled, Token and Chat ID are required.';
                this.isLoading = false;
                return;
            }

            const payload = {
                ...this.formData,
                strategy: this.formData.strategy || undefined,
                pair_whitelist: this.pair_whitelist_str.split(',').map(p => p.trim()).filter(p => p),
            };

            if (payload.strategy === undefined) delete payload.strategy;
            if (payload.max_open_trades === null || payload.max_open_trades === '') delete payload.max_open_trades;
            if (!payload.telegram_enabled) { // Don't send telegram fields if not enabled
                delete payload.telegram_token;
                delete payload.telegram_chat_id;
            }


            try {
                // Changed: api.createBot no longer takes tenantId as first argument
                const response = await api.createBot(payload);
                this.successMessage = `Bot ${response.data.bot_id} created successfully! Redirecting to bot list...`;
                this.formData = { ...initialFormData };
                this.pair_whitelist_str = 'BTC/USDT,ETH/USDT';

                setTimeout(() => {
                    if (!this.error) {
                        this.$router.push({ name: 'bots' });
                    }
                }, 2500);
            } catch (err) {
                console.error('Error creating bot:', err);
                if (err.response && err.response.data) {
                    this.error = {
                        message: err.response.data.detail || err.response.data.message || 'Failed to create bot due to server error.',
                        detail: typeof err.response.data === 'string' ? err.response.data : JSON.stringify(err.response.data, null, 2)
                    };
                } else if (err.request) {
                    this.error = { message: 'No response from server. Is the backend running?' };
                } else {
                    this.error = { message: err.message || 'An unknown error occurred during bot creation.' };
                }
            } finally {
                this.isLoading = false;
            }
        },
    },
};
</script>

<style scoped>
.create-bot-view {
    min-height: calc(100vh - 100px);
    /* Adjust based on navbar height */
    display: flex;
    align-items: flex-start;
    /* Align card to top */
    justify-content: center;
    background-color: #f4f7f6;
    padding-top: 2em;
    /* Add some padding at the top */
}

.p-field,
.p-field-checkbox {
    margin-bottom: 1.25rem;
    /* Consistent spacing */
}

label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 600;
}

.p-ml-2 {
    /* PrimeVue margin left utility */
    margin-left: 0.5rem;
}
</style>
