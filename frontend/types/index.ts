import { ReactNode } from 'react';

// User and Auth Types
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

export interface JWTPayload {
  sub: string
  role: string
  exp: number
  iat: number
}

export interface AuthContextType {
    user: User | null;
    loading: boolean;
    error: string | null;
    login: (token: string) => void;
    logout: () => void;
    isAdmin: () => boolean;
    refreshUser: () => Promise<void>;
}

// Server and Resources Types
export interface ServerResources {
  ram: number;
  cpu: number;
  disk: number;
}

export interface PlanPricing {
  hourly: number;
  daily: number;
}

export interface ServerPlan extends PlanPricing {
  name: string;
  resources: ServerResources;
}

export interface PriceProps {
  basic: ServerPlan;
  pro: ServerPlan;
  enterprise: ServerPlan;
}

export interface Server {
    id: number;
    user_id: number;
    name: string;
    type: string;
    location: string;
    os: string;
    ip: string;
    status: string;
    datacenter: string;
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

export interface ServerAction {
    action: 'start' | 'stop' | 'restart';
}

export interface ServerType {
    id: string;
    name: string;
    cpu: number;
    memory: number;
    disk: number;
    price: number;
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

// Transaction and Payment Types
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

// Support and Tickets Types
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

// Settings and Notifications Types
export interface NotificationSettings {
    id: number;
    user_id: number;
    server_notifications: boolean;
    payment_notifications: boolean;
    ticket_notifications: boolean;
    low_balance_threshold: number;
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

// Location and Price Types
export interface Location {
    id: string;
    name: string;
    country: string;
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

// Component Props Types
export interface ErrorMessageProps {
    message: string;
}

export interface AdminLayoutProps {
    children: ReactNode;
}

export interface ServerCardProps {
    server: Server;
    onAction?: (action: string) => void;
}

export interface PaginationProps {
    currentPage: number;
    totalPages: number;
    onPageChange: (page: number) => void;
}

export interface SearchInputProps {
    onSearch: (query: string) => void;
    className?: string;
}

export interface SortButtonProps {
    label: string;
    field: string;
    currentSort: {
        field: string;
        order: 'asc' | 'desc';
    };
    onSort: (field: string) => void;
    className?: string;
}

// Stats Types
export interface DashboardStats {
    total_servers: number;
    active_servers: number;
    total_spent: number;
}

export interface AdminStats {
    users: {
        total: number;
        active: number;
    };
    servers: {
        total: number;
        active: number;
    };
    transactions: {
        total: number;
        pending: number;
        volume: number;
    };
}

// Other Types
export interface TelegramConnect {
    code: string;
} 