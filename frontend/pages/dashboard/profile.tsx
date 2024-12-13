import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import DashboardLayout from '@/components/DashboardLayout';
import { toast } from 'react-toastify';
import { endpoints } from '@/services/api';
import { UserSettingsUpdate } from '@/types';

export default function Profile() {
    const { user, refreshUser } = useAuth();
    const [loading, setLoading] = useState(false);
    const [settings, setSettings] = useState<UserSettingsUpdate>({
        first_name: user?.first_name || '',
        last_name: user?.last_name || '',
        email: user?.email || '',
        phone: user?.phone || ''
    });

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);

        try {
            await endpoints.user.updateSettings(settings);
            await refreshUser();
            toast.success('تنظیمات با موفقیت به‌روز شد');
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'خطا در به‌روزرسانی تنظیمات');
        } finally {
            setLoading(false);
        }
    };

    const handleTelegramConnect = async () => {
        setLoading(true);
        try {
            const { data } = await endpoints.user.me();
            if (data.telegram_id) {
                // اگر قبلاً متصل شده، قطع اتصال کنیم
                await endpoints.user.updateSettings({ telegram_id: null });
                await refreshUser();
                toast.success('اتصال تلگرام با موفقیت قطع شد');
            } else {
                // ایجاد لینک اتصال
                const linkCode = `${user?.id}_${Math.random().toString(36).substr(2, 9)}`;
                const telegramLink = `https://t.me/YourBotName?start=${linkCode}`;
                window.open(telegramLink, '_blank');
            }
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'خطا در عملیات تلگرام');
        } finally {
            setLoading(false);
        }
    };

    return (
        <DashboardLayout>
            <div className="max-w-4xl mx-auto p-6">
                <h1 className="text-2xl font-bold mb-6">تنظیمات پروفایل</h1>

                <div className="bg-white rounded-lg shadow p-6 mb-6">
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700">
                                    نام
                                </label>
                                <input
                                    type="text"
                                    value={settings.first_name}
                                    onChange={(e) => setSettings({...settings, first_name: e.target.value})}
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">
                                    نام خانوادگی
                                </label>
                                <input
                                    type="text"
                                    value={settings.last_name}
                                    onChange={(e) => setSettings({...settings, last_name: e.target.value})}
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700">
                                ایمیل
                            </label>
                            <input
                                type="email"
                                value={settings.email}
                                onChange={(e) => setSettings({...settings, email: e.target.value})}
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700">
                                شماره موبایل
                            </label>
                            <input
                                type="tel"
                                value={settings.phone}
                                onChange={(e) => setSettings({...settings, phone: e.target.value})}
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                pattern="^(\+98|0)?9\d{9}$"
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                        >
                            {loading ? 'در حال ذخیره...' : 'ذخیره تغییرات'}
                        </button>
                    </form>
                </div>

                <div className="bg-white rounded-lg shadow p-6">
                    <h2 className="text-xl font-semibold mb-4">اتصال به تلگرام</h2>
                    
                    <div className="space-y-4">
                        {user?.telegram_id ? (
                            <>
                                <div className="text-green-600">
                                    ✓ اکانت تلگرام شما متصل است
                                </div>
                                <button
                                    onClick={handleTelegramConnect}
                                    disabled={loading}
                                    className="w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50"
                                >
                                    {loading ? 'در حال قطع اتصال...' : 'قطع اتصال تلگرام'}
                                </button>
                            </>
                        ) : (
                            <>
                                <p className="text-gray-600">
                                    برای اتصال حساب تلگرام خود، روی دکمه زیر کلیک کنید:
                                </p>
                                <button
                                    onClick={handleTelegramConnect}
                                    disabled={loading}
                                    className="w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                                >
                                    {loading ? 'در حال اتصال...' : 'اتصال به تلگرام'}
                                </button>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
} 