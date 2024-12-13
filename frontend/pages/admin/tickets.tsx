import { useEffect, useState } from 'react';
import { FiEye, FiMessageSquare } from 'react-icons/fi';
import { endpoints } from '@/services/api';
import { Ticket } from '@/types';
import AdminLayout from '@/components/AdminLayout';
import { toast } from 'react-toastify';
import Link from 'next/link';

export default function AdminTickets() {
    const [tickets, setTickets] = useState<Ticket[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchTickets();
    }, []);

    const fetchTickets = async () => {
        try {
            const { data } = await endpoints.admin.listTickets();
            setTickets(data);
        } catch (error) {
            console.error('Error fetching tickets:', error);
            toast.error('خطا در دریافت لیست تیکت‌ها');
        } finally {
            setLoading(false);
        }
    };

    const getPriorityColor = (priority: string) => {
        switch (priority) {
            case 'high':
                return 'bg-red-100 text-red-800';
            case 'medium':
                return 'bg-yellow-100 text-yellow-800';
            default:
                return 'bg-green-100 text-green-800';
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'open':
                return 'bg-green-100 text-green-800';
            case 'closed':
                return 'bg-gray-100 text-gray-800';
            case 'waiting_for_user':
                return 'bg-yellow-100 text-yellow-800';
            case 'waiting_for_admin':
                return 'bg-blue-100 text-blue-800';
            default:
                return 'bg-gray-100 text-gray-800';
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
                    <h1 className="text-2xl font-bold text-gray-800">مدیریت تیکت‌ها</h1>
                    <div className="text-sm text-gray-600">
                        تعداد کل: {tickets.length}
                    </div>
                </div>

                <div className="bg-white rounded-lg shadow overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                                        موضوع
                                    </th>
                                    <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                                        کاربر
                                    </th>
                                    <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                                        اولویت
                                    </th>
                                    <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                                        وضعیت
                                    </th>
                                    <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                                        تاریخ
                                    </th>
                                    <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                                        عملیات
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {tickets.map((ticket) => (
                                    <tr key={ticket.id} className="hover:bg-gray-50">
                                        <td className="px-6 py-4">
                                            <div className="text-sm font-medium text-gray-900">
                                                {ticket.subject}
                                            </div>
                                            <div className="text-sm text-gray-500 truncate max-w-md">
                                                {ticket.message}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="text-sm text-gray-900">ID: {ticket.user_id}</div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getPriorityColor(ticket.priority)}`}>
                                                {ticket.priority}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(ticket.status)}`}>
                                                {ticket.status}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="text-sm text-gray-500">
                                                {new Date(ticket.created_at).toLocaleDateString('fa-IR')}
                                            </div>
                                            <div className="text-sm text-gray-500">
                                                {new Date(ticket.updated_at).toLocaleTimeString('fa-IR')}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                            <div className="flex items-center space-x-3 space-x-reverse">
                                                <Link
                                                    href={`/admin/tickets/${ticket.id}`}
                                                    className="text-blue-600 hover:text-blue-900"
                                                    title="مشاهده"
                                                >
                                                    <FiEye className="w-5 h-5" />
                                                </Link>
                                                {ticket.status === 'waiting_for_admin' && (
                                                    <Link
                                                        href={`/admin/tickets/${ticket.id}`}
                                                        className="text-yellow-600 hover:text-yellow-900"
                                                        title="پاسخ"
                                                    >
                                                        <FiMessageSquare className="w-5 h-5" />
                                                    </Link>
                                                )}
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