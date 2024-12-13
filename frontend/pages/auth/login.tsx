import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { endpoints } from '@/services/api';
import { toast } from 'react-toastify';

export default function Login() {
    const { login } = useAuth();
    const [phone, setPhone] = useState('');
    const [code, setCode] = useState('');
    const [step, setStep] = useState<'phone' | 'code'>('phone');
    const [loading, setLoading] = useState(false);

    const handleRequestOTP = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);

        try {
            await endpoints.auth.requestOTP(phone);
            setStep('code');
            toast.success('کد تایید ارسال شد');
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'خطا در ارسال کد تایید');
        } finally {
            setLoading(false);
        }
    };

    const handleVerifyOTP = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);

        try {
            const { data } = await endpoints.auth.verifyOTP(phone, code);
            await login(data.access_token);
            toast.success('ورود موفقیت‌آمیز');
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'کد وارد شده نامعتبر است');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100">
            <div className="max-w-md w-full p-6 bg-white rounded-lg shadow-lg">
                <h1 className="text-2xl font-bold text-center mb-6">ورود به حساب کاربری</h1>

                {step === 'phone' ? (
                    <form onSubmit={handleRequestOTP} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700">
                                شماره موبایل
                            </label>
                            <input
                                type="tel"
                                value={phone}
                                onChange={(e) => setPhone(e.target.value)}
                                placeholder="09123456789"
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                required
                                pattern="^(\+98|0)?9\d{9}$"
                            />
                        </div>
                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                        >
                            {loading ? 'در حال ارسال...' : 'دریافت کد تایید'}
                        </button>
                    </form>
                ) : (
                    <form onSubmit={handleVerifyOTP} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700">
                                کد تایید
                            </label>
                            <input
                                type="text"
                                value={code}
                                onChange={(e) => setCode(e.target.value)}
                                placeholder="کد 6 رقمی"
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                required
                                pattern="\d{6}"
                                maxLength={6}
                            />
                        </div>
                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                        >
                            {loading ? 'در حال بررسی...' : 'ورود'}
                        </button>
                        <button
                            type="button"
                            onClick={() => setStep('phone')}
                            className="w-full text-sm text-blue-600 hover:text-blue-500"
                        >
                            تغییر شماره موبایل
                        </button>
                    </form>
                )}
            </div>
        </div>
    );
}