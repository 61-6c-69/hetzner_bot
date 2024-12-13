import { useEffect, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import DashboardLayout from '@/components/DashboardLayout';
import ServerCard from '@/components/ServerCard';
import LoadingSpinner from '@/components/LoadingSpinner';
import { endpoints } from '@/services/api';
import { Server, DashboardStats } from '@/types';
import { toast } from 'react-toastify';
import Link from 'next/link';

export default function Dashboard() {
    const { user } = useAuth();
    const [servers, setServers] = useState<Server[]>([]);
    const [balance, setBalance] = useState(0);
    const [stats, setStats] = useState<DashboardStats>({
        total_servers: 0,
        active_servers: 0,
        total_spent: 0
    });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            setLoading(true);
            const [serversRes, balanceRes, statsRes] = await Promise.all([
                endpoints.servers.list(),
                endpoints.transactions.getBalance(),
                endpoints.servers.stats(0) // 0 means get overall stats
            ]);

            setServers(serversRes.data);
            setBalance(balanceRes.data.balance);
            setStats(statsRes.data);
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'خطا در دریافت اطلاعات');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <DashboardLayout>
                <div className="flex justify-center items-center h-96">
                    <LoadingSpinner />
                </div>
            </DashboardLayout>
        );
    }

    return (
        <DashboardLayout>
            <div className="p-6">
                {/* Header */}
                <div className="flex justify-between items-center mb-8">
                    <h1 className="text-2xl font-bold">داشبورد</h1>
                    <Link
                        href="/dashboard/servers/create"
                        className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
                    >
                        سرور جدید
                    </Link>
                </div>

                {/* Stats Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                    <div className="bg-white rounded-lg shadow p-6">
                        <h3 className="text-gray-500 text-sm">موجودی</h3>
                        <p className="text-2xl font-bold mt-2">{balance.toLocaleString()} تومان</p>
                        <Link
                            href="/dashboard/transactions"
                            className="text-blue-600 text-sm hover:text-blue-700 mt-2 inline-block"
                        >
                            مشاهده تراکنش‌ها
                        </Link>
                    </div>
                    <div className="bg-white rounded-lg shadow p-6">
                        <h3 className="text-gray-500 text-sm">تعداد کل سرورها</h3>
                        <p className="text-2xl font-bold mt-2">{stats.total_servers}</p>
                    </div>
                    <div className="bg-white rounded-lg shadow p-6">
                        <h3 className="text-gray-500 text-sm">سرورهای فعال</h3>
                        <p className="text-2xl font-bold mt-2">{stats.active_servers}</p>
                    </div>
                    <div className="bg-white rounded-lg shadow p-6">
                        <h3 className="text-gray-500 text-sm">هزینه کل</h3>
                        <p className="text-2xl font-bold mt-2">{stats.total_spent.toLocaleString()} تومان</p>
                    </div>
                </div>

                {/* Servers List */}
                <div className="mb-8">
                    <h2 className="text-xl font-bold mb-4">سرورهای شما</h2>
                    {servers.length > 0 ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {servers.map(server => (
                                <ServerCard key={server.id} server={server} onUpdate={fetchData} />
                            ))}
                        </div>
                    ) : (
                        <div className="bg-white rounded-lg shadow p-8 text-center">
                            <p className="text-gray-500 mb-4">شما هنوز هیچ سروری ندارید</p>
                            <Link
                                href="/dashboard/servers/create"
                                className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 inline-block"
                            >
                                ایجاد اولین سرور
                            </Link>
                        </div>
                    )}
                </div>

                {/* Quick Actions */}
                <div className="bg-white rounded-lg shadow p-6">
                    <h2 className="text-xl font-bold mb-4">دسترسی سریع</h2>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <Link
                            href="/dashboard/support"
                            className="p-4 border rounded-lg text-center hover:bg-gray-50"
                        >
                            پشتیبانی
                        </Link>
                        <Link
                            href="/dashboard/profile"
                            className="p-4 border rounded-lg text-center hover:bg-gray-50"
                        >
                            تنظیمات حساب
                        </Link>
                        <Link
                            href="/dashboard/notifications"
                            className="p-4 border rounded-lg text-center hover:bg-gray-50"
                        >
                            تنظیمات اعلان‌ها
                        </Link>
                        <Link
                            href="/dashboard/transactions"
                            className="p-4 border rounded-lg text-center hover:bg-gray-50"
                        >
                            تراکنش‌ها
                        </Link>
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
} 