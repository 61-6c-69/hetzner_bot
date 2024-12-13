export interface User {
    id: number;
    username: string;
    email: string;
    first_name: string;
    last_name?: string;
    phone: string;
    role: string;
    balance: number;
    is_active: boolean;
    is_blocked: boolean;
    name?: string;
    created_at: string;
    telegram_id?: number;
}

export interface Server {
    id: number;
    user_id: number;
    name: string;
    status: string;
    ip: string;
    datacenter: string;
    server_type: string;
    hourly_price: number;
    monthly_price: number;
    last_charge_at: string;
    created_at: string;
    specifications: {
        cores: number;
        memory: number;
        disk: number;
        disk_type: string;
    };
}

export interface Transaction {
    id: number;
    user_id: number;
    amount: number;
    type: 'deposit' | 'withdrawal' | 'server_charge' | 'ip_change';
    status: 'pending' | 'completed' | 'failed' | 'refunded';
    payment_id?: string;
    description?: string;
    created_at: string;
}

export interface Ticket {
    id: number;
    user_id: number;
    subject: string;
    message: string;
    file_path?: string;
    status: string;
    priority: string;
    created_at: string;
    updated_at: string;
}

export interface TicketMessage {
    id: number;
    ticket_id: number;
    user_id: number;
    message: string;
    file_path?: string;
    created_at: string;
}

export interface NotificationSettings {
    id: number;
    user_id: number;
    server_notifications: boolean;
    payment_notifications: boolean;
    ticket_notifications: boolean;
    low_balance_threshold: number;
}

export interface Price {
    id: number;
    type: string;
    name: string;
    specs: {
        cpu: number;
        memory: number;
        disk: number;
        bandwidth: number;
    };
    hourly_price: number;
    monthly_price: number;
    location: string;
    available: boolean;
}

export interface ServerStats {
    cpu: Array<{
        timestamp: string;
        value: number;
    }>;
    memory: Array<{
        timestamp: string;
        value: number;
    }>;
    disk: Array<{
        timestamp: string;
        value: number;
    }>;
    network: Array<{
        timestamp: string;
        in: number;
        out: number;
    }>;
}

export interface ServerAction {
    action: 'start' | 'stop' | 'restart';
}

export interface UserSettingsUpdate {
    first_name?: string;
    last_name?: string;
    email?: string;
    phone?: string;
    telegram_id?: number;
    notification_settings?: {
        server_notifications?: boolean;
        payment_notifications?: boolean;
        ticket_notifications?: boolean;
        low_balance_threshold?: number;
    };
}

export interface TelegramConnect {
    code: string;
}

export interface ServerType {
    id: string;
    name: string;
    cpu: number;
    memory: number;
    disk: number;
    price: number;
}

export interface Location {
    id: string;
    name: string;
    country: string;
}

export interface DashboardStats {
    total_servers: number;
    active_servers: number;
    total_spent: number;
} 