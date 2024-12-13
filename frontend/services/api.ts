import axios from 'axios';
import Cookies from 'js-cookie';

const api = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL,
    headers: {
        'Content-Type': 'application/json'
    }
});

// Add token to requests
api.interceptors.request.use((config) => {
    const token = Cookies.get('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// API endpoints
export const endpoints = {
    // Auth
    auth: {
        requestOTP: (phone: string) => api.post('/auth/request-otp', { phone }),
        verifyOTP: (phone: string, code: string) => api.post('/auth/verify-otp', { phone, code }),
    },

    // User
    user: {
        me: () => api.get('/users/me'),
        updateSettings: (settings: any) => api.patch('/users/me/settings', settings),
        getNotificationSettings: () => api.get('/users/me/notifications'),
        connectTelegram: (code: string) => api.post('/users/telegram-connect', { code }),
    },

    // Servers
    servers: {
        list: () => api.get('/servers'),
        create: (data: any) => api.post('/servers', data),
        get: (id: number) => api.get(`/servers/${id}`),
        delete: (id: number) => api.delete(`/servers/${id}`),
        stats: (id: number) => api.get(`/servers/${id}/stats`),
        action: (id: number, action: string) => api.post(`/servers/${id}/action`, { action }),
        changeIP: (id: number) => api.post(`/servers/${id}/ip`),
    },

    // Transactions
    transactions: {
        list: () => api.get('/transactions'),
        getBalance: () => api.get('/transactions/balance'),
        createDeposit: (amount: number, description?: string) => 
            api.post('/transactions/deposit', { amount, description }),
        verify: (authority: string, status: string) => 
            api.get(`/transactions/verify?authority=${authority}&status=${status}`),
    },

    // Tickets
    tickets: {
        list: () => api.get('/tickets'),
        get: (id: number) => api.get(`/tickets/${id}`),
        create: (data: FormData) => api.post('/tickets', data),
        reply: (id: number, data: FormData) => api.post(`/tickets/${id}/reply`, data),
        getMessages: (id: number) => api.get(`/tickets/${id}/messages`),
    },

    // Prices
    prices: {
        list: () => api.get('/prices'),
        getServerPrice: (type: string) => api.get(`/prices/server/${type}`),
        getServerCost: (id: number) => api.get(`/prices/server/${id}/cost`),
    },

    // Admin
    admin: {
        // Users
        users: {
            list: (params: { page?: number; per_page?: number; search?: string; sort_by?: string; sort_order?: 'asc' | 'desc' }) => 
                api.get('/admin/users', { params }),
            block: (id: number) => api.post(`/admin/users/${id}/ban`),
            unblock: (id: number) => api.post(`/admin/users/${id}/unban`),
            delete: (id: number) => api.delete(`/admin/users/${id}`),
        },

        // Servers
        listServers: () => api.get('/admin/servers'),
        serverAction: (id: number, action: string) => 
            api.post(`/admin/servers/${id}/action`, { action }),
        deleteServer: (id: number) => api.delete(`/admin/servers/${id}`),

        // Tickets
        listTickets: () => api.get('/admin/tickets'),
        replyTicket: (id: number, response: string) => 
            api.post(`/admin/tickets/${id}/reply`, { response }),

        // Notifications
        sendNotification: (message: string) => 
            api.post('/admin/notifications', { message }),

        // Stats
        getStats: () => api.get('/admin/stats'),
        getServerStats: (id: number) => api.get(`/admin/servers/${id}/stats`),

        // Transactions
        listTransactions: () => api.get('/admin/transactions'),
        approveTransaction: (id: number) => 
            api.post(`/admin/transactions/${id}/approve`),
        rejectTransaction: (id: number) => 
            api.post(`/admin/transactions/${id}/reject`),
    }
};

export default api; 