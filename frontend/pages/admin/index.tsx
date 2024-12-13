import { useState, useEffect } from 'react';
import { endpoints } from '@/services/api';
import AdminLayout from '@/components/AdminLayout';
import type { AdminStats } from '@/types';
import { FiServer, FiDollarSign, FiUsers } from 'react-icons/fi';

export default function AdminDashboard() {
    const [stats, setStats] = useState<AdminStats | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const response = await endpoints.admin.getStats();
                setStats(response.data);
            } catch (error) {
                console.error('Error fetching stats:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchStats();
    }, []);

    if (loading) {
        return (
            <AdminLayout>
                <div className="flex justify-center items-center h-full">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                </div>
            </AdminLayout>
        );
    }

    const statCards = [
        {
            title: 'کاربران',
            value: stats?.users.total || 0,
            subValue: `${stats?.users.active || 0} کاربر فعال`,
            icon: FiUsers,
            color: 'bg-blue-500',
        },
        {
            title: 'سرورها',
            value: stats?.servers.total || 0,
            subValue: `${stats?.servers.active || 0} سرور فعال`,
            icon: FiServer,
            color: 'bg-green-500',
        },
        {
            title: 'تراکنش‌ها',
            value: stats?.transactions.total || 0,
            subValue: `${stats?.transactions.pending || 0} تراکنش در انتظار`,
            icon: FiDollarSign,
            color: 'bg-yellow-500',
        },
        {
            title: 'گردش مالی',
            value: (stats?.transactions.volume || 0).toLocaleString(),
            subValue: 'تومان',
            icon: FiDollarSign,
            color: 'bg-purple-500',
        }
    ];

    return (
        <AdminLayout>
            <div className="space-y-6">
                <h1 className="text-2xl font-bold text-gray-800">داشبورد مدیریت</h1>
                
                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {statCards.map((stat, index) => {
                        const Icon = stat.icon;
                        return (
                            <div
                                key={index}
                                className="bg-white rounded-lg shadow p-6 flex items-center"
                            >
                                <div className={`${stat.color} p-4 rounded-lg ml-4`}>
                                    <Icon className="w-6 h-6 text-white" />
                                </div>
                                <div>
                                    <p className="text-sm text-gray-600">{stat.title}</p>
                                    <p className="text-2xl font-bold text-gray-800">{stat.value}</p>
                                    {stat.subValue && (
                                        <p className="text-sm text-gray-500">{stat.subValue}</p>
                                    )}
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>
        </AdminLayout>
    );
}