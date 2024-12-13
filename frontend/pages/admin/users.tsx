import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { toast } from 'react-toastify';
import { User } from '@/types';
import { useAuth } from '@/contexts/AuthContext';
import { endpoints } from '@/services/api';
import AdminLayout from '@/components/AdminLayout';
import DataTable from '@/components/DataTable';
import type { Column } from '@/types/datatable';

export default function AdminUsers() {
    const [users, setUsers] = useState<User[]>([]);
    const [loading, setLoading] = useState(true);
    const [totalItems, setTotalItems] = useState(0);
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [search, setSearch] = useState('');
    const [sort, setSort] = useState({ field: 'created_at', order: 'desc' as 'asc' | 'desc' });
    
    const { user } = useAuth();
    const router = useRouter();

    // Redirect if not admin
    if (user && user.role !== 'admin') {
        router.push('/dashboard');
        return null;
    }

    const fetchUsers = async () => {
        try {
            setLoading(true);
            const response = await endpoints.admin.users.list({
                page: currentPage,
                per_page: 10,
                search,
                sort_by: sort.field,
                sort_order: sort.order
            });
            
            setUsers(response.data.items);
            setTotalItems(response.data.total);
            setTotalPages(response.data.total_pages);
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'خطا در دریافت لیست کاربرا��');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchUsers();
    }, [currentPage, search, sort]);

    const handleBlock = async (userId: number) => {
        try {
            await endpoints.admin.users.block(userId);
            toast.success('کاربر با موفقیت مسدود شد');
            fetchUsers();
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'خطا در مسدود کردن کاربر');
        }
    };

    const handleUnblock = async (userId: number) => {
        try {
            await endpoints.admin.users.unblock(userId);
            toast.success('کاربر با موفقیت آزاد شد');
            fetchUsers();
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'خطا در آزاد کردن کاربر');
        }
    };

    const columns: Column<User>[] = [
        { key: 'id', label: 'شناسه', sortable: true },
        { key: 'username', label: 'نام کاربری', sortable: true },
        { key: 'email', label: 'ایمیل', sortable: true },
        { key: 'phone', label: 'شماره موبایل', sortable: true },
        {
            key: 'balance',
            label: 'موجودی',
            sortable: true,
            render: (user: User) => `${user.balance.toLocaleString()} تومان`
        },
        {
            key: 'is_active',
            label: 'وضعیت',
            render: (user: User) => (
                <span
                    className={`px-2 py-1 rounded-full text-xs ${
                        user.is_active
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                    }`}
                >
                    {user.is_active ? 'فعال' : 'غیرفعال'}
                </span>
            )
        },
        {
            key: 'created_at',
            label: 'تاریخ عضویت',
            sortable: true,
            render: (user: User) => new Date(user.created_at).toLocaleDateString('fa-IR')
        },
        {
            key: 'actions',
            label: 'عملیات',
            render: (user: User) => (
                <div className="flex space-x-2 space-x-reverse">
                    <button
                        onClick={() => user.is_blocked ? handleUnblock(user.id) : handleBlock(user.id)}
                        className={`px-3 py-1 rounded-md text-sm ${
                            user.is_blocked
                                ? 'bg-green-600 hover:bg-green-700 text-white'
                                : 'bg-red-600 hover:bg-red-700 text-white'
                        }`}
                    >
                        {user.is_blocked ? 'آزادسازی' : 'مسدود'}
                    </button>
                </div>
            )
        }
    ];

    return (
        <AdminLayout>
            <div className="space-y-6">
                <h1 className="text-2xl font-bold text-gray-800">مدیریت کاربران</h1>

                <DataTable
                    columns={columns}
                    data={users}
                    totalItems={totalItems}
                    currentPage={currentPage}
                    totalPages={totalPages}
                    onPageChange={setCurrentPage}
                    onSearch={setSearch}
                    onSort={(field) => {
                        setSort(prev => ({
                            field,
                            order: prev.field === field && prev.order === 'asc' ? 'desc' : 'asc'
                        }));
                    }}
                    currentSort={sort}
                    isLoading={loading}
                />
            </div>
        </AdminLayout>
    );
}