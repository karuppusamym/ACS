const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = {
    // Admin endpoints
    admin: {
        createLLMConfig: async (config: any) => {
            const res = await fetch(`${API_BASE_URL}/api/v1/admin/llm-config`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config),
            });
            return res.json();
        },
        getLLMConfigs: async () => {
            const res = await fetch(`${API_BASE_URL}/api/v1/admin/llm-config`);
            return res.json();
        },
        updateStorageConfig: async (config: any) => {
            const res = await fetch(`${API_BASE_URL}/api/v1/admin/storage-config`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config),
            });
            return res.json();
        },
    },

    // Connection endpoints
    connection: {
        create: async (config: any) => {
            const res = await fetch(`${API_BASE_URL}/api/v1/connection/connect`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config),
            });
            return res.json();
        },
        getAll: async () => {
            const res = await fetch(`${API_BASE_URL}/api/v1/connection/connections`);
            return res.json();
        },
        getMetadata: async (connectionName: string) => {
            const res = await fetch(`${API_BASE_URL}/api/v1/connection/metadata/${connectionName}`);
            return res.json();
        },
    },

    // Semantic layer endpoints
    semantic: {
        createModel: async (model: any) => {
            const res = await fetch(`${API_BASE_URL}/api/v1/semantic/model`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(model),
            });
            return res.json();
        },
        getModels: async (connectionName: string) => {
            const res = await fetch(`${API_BASE_URL}/api/v1/semantic/model/${connectionName}`);
            return res.json();
        },
    },

    // Agent endpoints
    agent: {
        chat: async (query: string, context: any = {}) => {
            const res = await fetch(`${API_BASE_URL}/api/v1/agent/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query, context }),
            });
            return res.json();
        },
    },
};
