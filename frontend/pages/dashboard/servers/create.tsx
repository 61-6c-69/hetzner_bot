import { useState } from 'react';
import { useRouter } from 'next/router';
import DashboardLayout from '@/components/DashboardLayout';
import { endpoints } from '@/services/api';
import { toast } from 'react-toastify';
import { ServerType, Location } from '@/types';

export default function CreateServer() {
    const router = useRouter();
    const [loading, setLoading] = useState(false);
    const [formData, setFormData] = useState({
        name: '',
        type: '',
        location: '',
        os: 'ubuntu_22_04', // Default OS
    });

    const serverTypes: ServerType[] = [
        { id: 'cx11', name: 'CX11', cpu: 1, memory: 2, disk: 20, price: 4.15 },
        { id: 'cx21', name: 'CX21', cpu: 2, memory: 4, disk: 40, price: 7.45 },
        { id: 'cx31', name: 'CX31', cpu: 2, memory: 8, disk: 80, price: 13.99 },
        { id: 'cx41', name: 'CX41', cpu: 4, memory: 16, disk: 160, price: 25.85 },
        { id: 'cx51', name: 'CX51', cpu: 8, memory: 32, disk: 240, price: 49.90 },
    ];

    const locations: Location[] = [
        { id: 'nbg1', name: 'نورنبرگ', country: 'آلمان' },
        { id: 'fsn1', name: 'فالکنشتاین', country: 'آلمان' },
        { id: 'hel1', name: 'هلسینکی', country: 'فنلاند' },
        { id: 'ash', name: 'اشبرن', country: 'آمریکا' },
    ];

    const operatingSystems = [
        { id: 'ubuntu_22_04', name: 'Ubuntu 22.04' },
        { id: 'ubuntu_20_04', name: 'Ubuntu 20.04' },
        { id: 'debian_11', name: 'Debian 11' },
        { id: 'centos_9', name: 'CentOS Stream 9' },
    ];

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        
        if (!formData.name || !formData.type || !formData.location) {
            toast.error('لطفاً تمام فیلدها را پر کنید');
            return;
        }

        setLoading(true);
        try {
            await endpoints.servers.create(formData);
            toast.success('سرور با موفقیت ایجاد شد');
            router.push('/dashboard/servers');
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'خطا در ایجاد سرور');
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const selectedType = serverTypes.find(type => type.id === formData.type);

    return (
        <DashboardLayout>
            <div className="max-w-4xl mx-auto p-6">
                <h1 className="text-2xl font-bold mb-6">ایجاد سرور جدید</h1>

                <form onSubmit={handleSubmit} className="space-y-6">
                    {/* نام سرور */}
                    <div className="bg-white rounded-lg shadow p-6">
                        <h2 className="text-lg font-semibold mb-4">مشخصات اصلی</h2>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    نام سرور
                                </label>
                                <input
                                    type="text"
                                    name="name"
                                    value={formData.name}
                                    onChange={handleChange}
                                    placeholder="مثال: my-server-1"
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    سیستم عامل
                                </label>
                                <select
                                    name="os"
                                    value={formData.os}
                                    onChange={handleChange}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                >
                                    {operatingSystems.map(os => (
                                        <option key={os.id} value={os.id}>
                                            {os.name}
                                        </option>
                                    ))}
                                </select>
                            </div>
                        </div>
                    </div>

                    {/* نوع سرور */}
                    <div className="bg-white rounded-lg shadow p-6">
                        <h2 className="text-lg font-semibold mb-4">انتخاب پلن</h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {serverTypes.map(type => (
                                <div
                                    key={type.id}
                                    className={`border rounded-lg p-4 cursor-pointer transition-all ${
                                        formData.type === type.id
                                            ? 'border-blue-500 bg-blue-50'
                                            : 'border-gray-200 hover:border-blue-300'
                                    }`}
                                    onClick={() => setFormData(prev => ({ ...prev, type: type.id }))}
                                >
                                    <div className="font-semibold text-lg mb-2">{type.name}</div>
                                    <div className="text-sm text-gray-600 space-y-1">
                                        <div>CPU: {type.cpu} هسته</div>
                                        <div>RAM: {type.memory} GB</div>
                                        <div>دیسک: {type.disk} GB</div>
                                        <div className="text-blue-600 font-medium mt-2">
                                            {type.price} یورو / ماه
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* موقعیت */}
                    <div className="bg-white rounded-lg shadow p-6">
                        <h2 className="text-lg font-semibold mb-4">انتخاب موقعیت</h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {locations.map(location => (
                                <div
                                    key={location.id}
                                    className={`border rounded-lg p-4 cursor-pointer transition-all ${
                                        formData.location === location.id
                                            ? 'border-blue-500 bg-blue-50'
                                            : 'border-gray-200 hover:border-blue-300'
                                    }`}
                                    onClick={() => setFormData(prev => ({ ...prev, location: location.id }))}
                                >
                                    <div className="font-semibold">{location.name}</div>
                                    <div className="text-sm text-gray-600">{location.country}</div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* خلاصه و تأیید */}
                    <div className="bg-white rounded-lg shadow p-6">
                        <h2 className="text-lg font-semibold mb-4">خلاصه سفارش</h2>
                        <div className="space-y-4">
                            <div className="flex justify-between py-2 border-b">
                                <span className="text-gray-600">نام سرور:</span>
                                <span className="font-medium">{formData.name || '-'}</span>
                            </div>
                            <div className="flex justify-between py-2 border-b">
                                <span className="text-gray-600">پلن:</span>
                                <span className="font-medium">
                                    {selectedType ? `${selectedType.name} (${selectedType.price} یورو / ماه)` : '-'}
                                </span>
                            </div>
                            <div className="flex justify-between py-2 border-b">
                                <span className="text-gray-600">موقعیت:</span>
                                <span className="font-medium">
                                    {locations.find(l => l.id === formData.location)?.name || '-'}
                                </span>
                            </div>
                            <div className="flex justify-between py-2 border-b">
                                <span className="text-gray-600">سیستم عامل:</span>
                                <span className="font-medium">
                                    {operatingSystems.find(os => os.id === formData.os)?.name || '-'}
                                </span>
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={loading || !formData.name || !formData.type || !formData.location}
                            className="w-full mt-6 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {loading ? 'در حال ایجاد سرور...' : 'ایجاد سرور'}
                        </button>
                    </div>
                </form>
            </div>
        </DashboardLayout>
    );
} 