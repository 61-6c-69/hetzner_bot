import { useEffect, useState } from 'react';
import { FiPower, FiRefreshCw, FiTrash2, FiMonitor } from 'react-icons/fi';
import { endpoints } from '@/services/api';
import { Server } from '@/types';
import AdminLayout from '@/components/AdminLayout';
import { toast } from 'react-toastify';
import Link from 'next/link';

export default function AdminServers() {
    const [servers, setServers] = useState<Server[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchServers();
    }, []);

    const fetchServers = async () => {
        try {
            const { data } = await endpoints.admin.listServers();
            setServers(data);
        } catch (error) {
            console.error('Error fetching servers:', error);
            toast.error('خطا در دریافت لیست سرورها');
        } finally {
            setLoading(false);
        }
    };

    const handleServerAction = async (serverId: number, action: string) => {
        try {
            await endpoints.admin.serverAction(serverId, action);
            toast.success('عملیات با موفقیت انجام شد');
            await fetchServers();
        } catch (error) {
            console.error(`Error performing server action ${action}:`, error);
            toast.error('خطا در انجام عملیات');
        }
    };

    const handleDeleteServer = async (serverId: number) => {
        if (!confirm('آیا از حذف این سرور اطمینان دارید؟')) return;
        
        try {
            await endpoints.admin.deleteServer(serverId);
            toast.success('سرور با موفقیت حذف شد');
            await fetchServers();
        } catch (error) {
            console.error('Error deleting server:', error);
            toast.error('خطا در حذف سرور');
        }
    };

    if (loading) {
        return (
            <AdminLayout>
                <div className="flex justify-center items-center h-full">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                </div>
            </AdminLayout>
        );
    }

    return (
        <AdminLayout>
            <div className="space-y-6">
                <div className="flex justify-between items-center">
                    <h1 className="text-2xl font-bold text-gray-800">مدیریت سرورها</h1>
                    <div className="text-sm text-gray-600">
                        تعداد کل: {servers.length}
                    </div>
                </div>

                <div className="bg-white rounded-lg shadow overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                                        نام سرور
                                    </th>
                                    <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                                        نوع
                                    </th>
                                    <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                                        IP
                                    </th>
                                    <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                                        وضعیت
                                    </th>
                                    <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                                        کاربر
                                    </th>
                                    <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                                        عملیات
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {servers.map((server) => (
                                    <tr key={server.id} className="hover:bg-gray-50">
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="text-sm font-medium text-gray-900">
                                                {server.name}
                                            </div>
                                            <div className="text-sm text-gray-500">
                                                {new Date(server.created_at).toLocaleDateString('fa-IR')}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="text-sm text-gray-900">{server.type}</div>
                                            <div className="text-sm text-gray-500">{server.location}</div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="text-sm font-mono text-gray-900">{server.ip}</div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                                                server.status === 'running'
                                                    ? 'bg-green-100 text-green-800'
                                                    : server.status === 'stopped'
                                                    ? 'bg-red-100 text-red-800'
                                                    : 'bg-yellow-100 text-yellow-800'
                                            }`}>
                                                {server.status}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="text-sm text-gray-900">ID: {server.user_id}</div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                            <div className="flex items-center space-x-3 space-x-reverse">
                                                <button
                                                    onClick={() => handleServerAction(server.id, server.status === 'running' ? 'stop' : 'start')}
                                                    className={`${
                                                        server.status === 'running' ? 'text-red-600 hover:text-red-900' : 'text-green-600 hover:text-green-900'
                                                    }`}
                                                    title={server.status === 'running' ? 'خاموش کردن' : 'روشن کردن'}
                                                >
                                                    <FiPower className="w-5 h-5" />
                                                </button>
                                                <button
                                                    onClick={() => handleServerAction(server.id, 'restart')}
                                                    className="text-yellow-600 hover:text-yellow-900"
                                                    title="راه‌اندازی مجدد"
                                                >
                                                    <FiRefreshCw className="w-5 h-5" />
                                                </button>
                                                <Link
                                                    href={`/admin/servers/${server.id}/monitoring`}
                                                    className="text-blue-600 hover:text-blue-900"
                                                    title="مانیتورینگ"
                                                >
                                                    <FiMonitor className="w-5 h-5" />
                                                </Link>
                                                <button
                                                    onClick={() => handleDeleteServer(server.id)}
                                                    className="text-red-600 hover:text-red-900"
                                                    title="حذف سرور"
                                                >
                                                    <FiTrash2 className="w-5 h-5" />
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </AdminLayout>
    );
}