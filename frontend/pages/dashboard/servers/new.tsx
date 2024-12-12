import { useState } from 'react';
import { useRouter } from 'next/router';
import DashboardLayout from '@/components/DashboardLayout';
import { useAuth } from '@/hooks/useAuth';

export default function NewServer() {
    const router = useRouter();
    const { token } = useAuth();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const res = await fetch('/api/servers', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name: e.target.name.value,
                    type: e.target.type.value,
                    location: e.target.location.value,
                    os: e.target.os.value
                })
            });

            const data = await res.json();

            if (!res.ok) {
                if (data.detail?.message === 'موجودی ناکافی') {
                    setError(
                        `موجودی شما کافی نیست. حداقل موجودی مورد نیاز برای شروع: ${data.detail.required.toLocaleString()} تومان`
                    );
                    return;
                }
                throw new Error(data.detail || 'خطا در ایجاد سرور');
            }

            router.push(`/dashboard/servers/${data.id}`);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <DashboardLayout>
            <div className="max-w-4xl mx-auto p-6">
                <h1 className="text-2xl font-bold mb-6">سرور جدید</h1>

                {error && (
                    <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded mb-6">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                        <label className="block text-sm font-medium text-gray-700">
                            نام سرور
                        </label>
                        <input
                            type="text"
                            name="name"
                            required
                            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700">
                            نوع سرور
                        </label>
                        <select
                            name="type"
                            required
                            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
                        >
                            <option value="cx11">CX11 - 1 Core, 2GB RAM</option>
                            <option value="cx21">CX21 - 2 Cores, 4GB RAM</option>
                            <option value="cx31">CX31 - 2 Cores, 8GB RAM</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700">
                            لوکیشن
                        </label>
                        <select
                            name="location"
                            required
                            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
                        >
                            <option value="fsn1">آلمان (نورنبرگ)</option>
                            <option value="nbg1">آلمان (فرانکفورت)</option>
                            <option value="hel1">فنلاند (هلسینکی)</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700">
                            سیستم‌عامل
                        </label>
                        <select
                            name="os"
                            required
                            className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
                        >
                            <option value="ubuntu-20.04">Ubuntu 20.04</option>
                            <option value="debian-11">Debian 11</option>
                            <option value="centos-8">CentOS 8</option>
                        </select>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className={`w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${
                            loading ? 'opacity-50 cursor-not-allowed' : ''
                        }`}
                    >
                        {loading ? 'در حال ایجاد...' : 'ایجاد سرور'}
                    </button>
                </form>
            </div>
        </DashboardLayout>
    );
} 