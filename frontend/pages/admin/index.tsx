import { useEffect, useState } from 'react';
import { FiUsers, FiServer, FiDollarSign, FiMessageSquare } from 'react-icons/fi';
import { endpoints } from '@/services/api';
import AdminLayout from '@/components/AdminLayout';

interface Stats {
    total_users: number;
    active_servers: number;
    monthly_revenue: number;
    open_tickets: number;
}

const AdminDashboard = () => {
    const [stats, setStats] = useState<Stats | null>(null);
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
            value: stats?.total_users || 0,
            icon: FiUsers,
            color: 'bg-blue-500',
        },
        {
            title: 'سرورهای فعال',
            value: stats?.active_servers || 0,
            icon: FiServer,
            color: 'bg-green-500',
        },
        {
            title: 'درآمد ماهانه',
            value: `$${stats?.monthly_revenue || 0}`,
            icon: FiDollarSign,
            color: 'bg-yellow-500',
        },
        {
            title: 'تیکت‌های باز',
            value: stats?.open_tickets || 0,
            icon: FiMessageSquare,
            color: 'bg-red-500',
        },
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
                                </div>
                            </div>
                        );
                    })}
                </div>

                {/* Recent Activity */}
                <div className="bg-white rounded-lg shadow p-6">
                    <h2 className="text-xl font-semibold text-gray-800 mb-4">فعالیت‌های اخیر</h2>
                    {/* Add recent activity list here */}
                </div>
            </div>
        </AdminLayout>
    );
};

export default AdminDashboard;