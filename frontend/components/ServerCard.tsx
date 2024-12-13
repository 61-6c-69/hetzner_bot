import Link from 'next/link';
import type { ServerCardProps } from '@/types';
import { endpoints } from '@/services/api';
import { toast } from 'react-toastify';

export default function ServerCard({ server, onAction }: ServerCardProps) {
    const handlePowerAction = async (action: 'start' | 'stop' | 'restart') => {
        try {
            await endpoints.servers.action(server.id, action);
            toast.success('عملیات با موفقیت انجام شد');
            onAction?.(action);
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'خطا در انجام عملیات');
        }
    };

    const handleChangeIP = async () => {
        try {
            await endpoints.servers.changeIP(server.id);
            toast.success('IP با موفقیت تغییر کرد');
            onAction?.('change_ip');
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'خطا در تغییر IP');
        }
    };

    return (
        <div className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-start mb-4">
                <h3 className="text-xl font-semibold">{server.name}</h3>
                <span className={`px-2 py-1 rounded-full text-sm ${
                    server.status === 'running' 
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-800'
                }`}>
                    {server.status === 'running' ? 'فعال' : 'غیرفعال'}
                </span>
            </div>

            <div className="space-y-2 mb-4">
                <p className="text-gray-600">
                    <span className="font-medium">IP:</span> {server.ip}
                </p>
                <p className="text-gray-600">
                    <span className="font-medium">نوع:</span> {server.type}
                </p>
                <p className="text-gray-600">
                    <span className="font-medium">سیستم عامل:</span> {server.os}
                </p>
                <p className="text-gray-600">
                    <span className="font-medium">موقعیت:</span> {server.location}
                </p>
                <p className="text-gray-600">
                    <span className="font-medium">هزینه ساعتی:</span> {server.hourly_price.toLocaleString()} تومان
                </p>
            </div>

            <div className="flex flex-wrap gap-2">
                <button
                    onClick={() => handlePowerAction(server.status === 'running' ? 'stop' : 'start')}
                    className={`px-4 py-2 rounded-md text-white ${
                        server.status === 'running' 
                            ? 'bg-red-600 hover:bg-red-700' 
                            : 'bg-green-600 hover:bg-green-700'
                    }`}
                >
                    {server.status === 'running' ? 'خاموش کردن' : 'روشن کردن'}
                </button>

                <button
                    onClick={() => handlePowerAction('restart')}
                    className="px-4 py-2 bg-yellow-600 text-white rounded-md hover:bg-yellow-700"
                >
                    راه‌اندازی مجدد
                </button>

                <button
                    onClick={handleChangeIP}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                    تغییر IP
                </button>

                <Link
                    href={`/dashboard/servers/${server.id}/monitoring`}
                    className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700"
                >
                    مانیتورینگ
                </Link>
            </div>
        </div>
    );
} 