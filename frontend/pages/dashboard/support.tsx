import { useState, useEffect } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import { useAuth } from '@/contexts/AuthContext';
import { endpoints } from '@/services/api';
import { Ticket } from '@/types';
import { toast } from 'react-toastify';
import LoadingSpinner from '@/components/LoadingSpinner';

export default function Support() {
    const { user } = useAuth();
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [tickets, setTickets] = useState<Ticket[]>([]);
    const [subject, setSubject] = useState('');
    const [message, setMessage] = useState('');
    const [file, setFile] = useState<File | null>(null);

    useEffect(() => {
        fetchTickets();
    }, []);

    const fetchTickets = async () => {
        try {
            const { data } = await endpoints.tickets.list();
            setTickets(data);
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'خطا در دریافت تیکت‌ها');
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSubmitting(true);

        try {
            const formData = new FormData();
            formData.append('subject', subject);
            formData.append('message', message);
            if (file) {
                formData.append('file', file);
            }

            await endpoints.tickets.create(formData);
            toast.success('تیکت با موفقیت ارسال شد');
            
            // Reset form
            setSubject('');
            setMessage('');
            setFile(null);
            
            // Refresh tickets list
            fetchTickets();
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'خطا در ارسال تیکت');
        } finally {
            setSubmitting(false);
        }
    };

    if (loading) {
        return (
            <DashboardLayout>
                <div className="flex justify-center items-center h-64">
                    <LoadingSpinner />
                </div>
            </DashboardLayout>
        );
    }

    return (
        <DashboardLayout>
            <div className="max-w-4xl mx-auto p-6">
                <h1 className="text-2xl font-bold mb-8">پشتیبانی</h1>

                {/* فرم ارسال تیکت جدید */}
                <div className="bg-white rounded-lg shadow p-6 mb-8">
                    <h2 className="text-xl font-bold mb-4">تیکت جدید</h2>
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700">
                                موضوع
                            </label>
                            <input
                                type="text"
                                value={subject}
                                onChange={(e) => setSubject(e.target.value)}
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                required
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700">
                                پیام
                            </label>
                            <textarea
                                value={message}
                                onChange={(e) => setMessage(e.target.value)}
                                rows={4}
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                required
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700">
                                فایل پیوست (اختیاری)
                            </label>
                            <input
                                type="file"
                                onChange={(e) => setFile(e.target.files?.[0] || null)}
                                className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={submitting}
                            className="w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                        >
                            {submitting ? 'در حال ارسال...' : 'ارسال تیکت'}
                        </button>
                    </form>
                </div>

                {/* لیست تیکت‌ها */}
                <div className="bg-white rounded-lg shadow">
                    <div className="p-4 border-b">
                        <h2 className="text-xl font-bold">تیکت‌های قبلی</h2>
                    </div>

                    <div className="divide-y">
                        {tickets.length === 0 ? (
                            <div className="p-4 text-center text-gray-500">
                                هنوز تیکتی ثبت نکرده‌اید
                            </div>
                        ) : (
                            tickets.map((ticket) => (
                                <div key={ticket.id} className="p-4">
                                    <div className="flex justify-between items-start mb-2">
                                        <div>
                                            <h3 className="font-medium">{ticket.subject}</h3>
                                            <span className="text-sm text-gray-500">
                                                {new Date(ticket.created_at).toLocaleDateString('fa-IR')}
                                            </span>
                                        </div>
                                        <span className={`px-2 py-1 rounded-full text-xs ${
                                            ticket.status === 'open' 
                                                ? 'bg-green-100 text-green-800'
                                                : 'bg-gray-100 text-gray-800'
                                        }`}>
                                            {ticket.status === 'open' ? 'باز' : 'بسته شده'}
                                        </span>
                                    </div>
                                    <p className="text-gray-700 whitespace-pre-wrap">{ticket.message}</p>
                                    {ticket.file_path && (
                                        <a
                                            href={`${process.env.NEXT_PUBLIC_API_URL}/uploads/${ticket.file_path}`}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="mt-2 inline-flex items-center text-sm text-blue-600 hover:text-blue-500"
                                        >
                                            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                            </svg>
                                            دانلود فایل پیوست
                                        </a>
                                    )}
                                </div>
                            ))
                        )}
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
} 