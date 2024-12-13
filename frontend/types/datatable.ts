import { ReactNode } from 'react';

export interface Column<T> {
    key: keyof T;
    label: string;
    sortable?: boolean;
    render?: (item: T) => ReactNode;
}

export interface DataTableProps<T> {
    columns: Column<T>[];
    data: T[];
    totalItems: number;
    currentPage: number;
    totalPages: number;
    onPageChange: (page: number) => void;
    onSearch?: (query: string) => void;
    onSort?: (field: string) => void;
    currentSort?: {
        field: string;
        order: 'asc' | 'desc';
    };
    isLoading?: boolean;
    emptyMessage?: string;
} 