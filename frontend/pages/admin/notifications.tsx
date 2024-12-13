import { useState } from 'react';
import AdminLayout from '@/components/AdminLayout';
import { useAuth } from '@/contexts/AuthContext';
import { endpoints } from '@/services/api';
import { toast } from 'react-toastify';
import { useRouter } from 'next/router';

export default function AdminNotifications() {
    const [message, setMessage] = useState('');
    const [loading, setLoading] = useState(false);
    const { user } = useAuth();
    const router = useRouter();

    // Redirect if not admin
    if (user && user.role !== 'admin') {
        router.push('/dashboard');
        return null;
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!message.trim()) return;

        setLoading(true);
        try {
            await endpoints.admin.sendNotification(message);
            toast.success('اعلان با موفقیت ارسال شد');
            setMessage('');
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'خطا در ارسال اعلان');
        } finally {
            setLoading(false);
        }
    };

    return (
        <AdminLayout>
            <div className="max-w-4xl mx-auto p-6">
                <h1 className="text-2xl font-bold mb-6">ارسال اعلان به کاربران</h1>

                <div className="bg-white rounded-lg shadow p-6">
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                متن اعلان
                            </label>
                            <textarea
                                value={message}
                                onChange={(e) => setMessage(e.target.value)}
                                rows={6}
                                placeholder="متن اعلان را وارد کنید..."
                                className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                required
                            />
                            <p className="mt-2 text-sm text-gray-500">
                                این پیام به تمام کاربرانی که تلگرام خود را متصل کرده‌اند ارسال خواهد شد.
                            </p>
                        </div>

                        <button
                            type="submit"
                            disabled={loading || !message.trim()}
                            className="w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                        >
                            {loading ? 'در حال ارسال...' : 'ارسال اعلان'}
                        </button>
                    </form>

                    <div className="mt-6 p-4 bg-gray-50 rounded-md">
                        <h3 className="text-sm font-medium text-gray-700 mb-2">راهنمای ارسال اعلان:</h3>
                        <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                            <li>اعلان‌ها فقط برای کاربرانی که تلگرام خود را متصل کرده‌اند ارسال می‌شود</li>
                            <li>از ارسال اعلان‌های غیرضروری خودداری کنید</li>
                            <li>می‌توانید از مارک‌داون برای فرمت‌بندی متن استفاده کنید</li>
                            <li>حداکثر طول پیام 1000 کاراکتر است</li>
                        </ul>
                    </div>
                </div>
            </div>
        </AdminLayout>
    );
} 