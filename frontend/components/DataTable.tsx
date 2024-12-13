import { ReactNode, useState } from 'react';
import Pagination from './Pagination';
import SearchInput from './SearchInput';
import SortButton from './SortButton';

interface Column<T> {
    key: keyof T;
    label: string;
    sortable?: boolean;
    render?: (item: T) => ReactNode;
}

interface DataTableProps<T> {
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

export default function DataTable<T>({
    columns,
    data,
    totalItems,
    currentPage,
    totalPages,
    onPageChange,
    onSearch,
    onSort,
    currentSort,
    isLoading = false,
    emptyMessage = 'داده‌ای یافت نشد'
}: DataTableProps<T>) {
    return (
        <div className="space-y-4">
            {/* Search */}
            {onSearch && (
                <div className="flex justify-end">
                    <SearchInput
                        onSearch={onSearch}
                        className="w-64"
                    />
                </div>
            )}

            {/* Table */}
            <div className="bg-white rounded-lg shadow overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                {columns.map((column) => (
                                    <th
                                        key={String(column.key)}
                                        scope="col"
                                        className="px-6 py-3 text-right text-xs font-medium text-gray-500"
                                    >
                                        {column.sortable && onSort ? (
                                            <SortButton
                                                label={column.label}
                                                field={String(column.key)}
                                                currentSort={currentSort || { field: '', order: 'asc' }}
                                                onSort={onSort}
                                            />
                                        ) : (
                                            column.label
                                        )}
                                    </th>
                                ))}
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {isLoading ? (
                                <tr>
                                    <td
                                        colSpan={columns.length}
                                        className="px-6 py-4 text-center text-sm text-gray-500"
                                    >
                                        <div className="flex justify-center">
                                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                                        </div>
                                    </td>
                                </tr>
                            ) : data.length === 0 ? (
                                <tr>
                                    <td
                                        colSpan={columns.length}
                                        className="px-6 py-4 text-center text-sm text-gray-500"
                                    >
                                        {emptyMessage}
                                    </td>
                                </tr>
                            ) : (
                                data.map((item, index) => (
                                    <tr key={index} className="hover:bg-gray-50">
                                        {columns.map((column) => (
                                            <td
                                                key={String(column.key)}
                                                className="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                                            >
                                                {column.render
                                                    ? column.render(item)
                                                    : String(item[column.key])}
                                            </td>
                                        ))}
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>

                {/* Pagination */}
                {totalPages > 1 && (
                    <Pagination
                        currentPage={currentPage}
                        totalPages={totalPages}
                        onPageChange={onPageChange}
                    />
                )}
            </div>

            {/* Total Items */}
            <div className="text-sm text-gray-600 text-left">
                تعداد کل: {totalItems}
            </div>
        </div>
    );
} 