import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { endpoints } from '@/services/api';
import { Ticket, TicketMessage } from '@/types';
import AdminLayout from '@/components/AdminLayout';
import { toast } from 'react-toastify';

export default function TicketDetail() {
    const router = useRouter();
    const { id } = router.query;
    const [ticket, setTicket] = useState<Ticket | null>(null);
    const [messages, setMessages] = useState<TicketMessage[]>([]);
    const [loading, setLoading] = useState(true);
    const [response, setResponse] = useState('');
    const [sending, setSending] = useState(false);

    useEffect(() => {
        if (id) {
            fetchTicket();
            fetchMessages();
        }
    }, [id]);

    const fetchTicket = async () => {
        try {
            const { data } = await endpoints.admin.listTickets();
            const foundTicket = data.find((t: Ticket) => t.id === Number(id));
            if (foundTicket) {
                setTicket(foundTicket);
            } else {
                toast.error('تیکت مورد نظر یافت نشد');
                router.push('/admin/tickets');
            }
        } catch (error) {
            console.error('Error fetching ticket:', error);
            toast.error('خطا در دریافت اطلاعات تیکت');
        }
    };

    const fetchMessages = async () => {
        try {
            const { data } = await endpoints.tickets.getMessages(Number(id));
            setMessages(data);
        } catch (error) {
            console.error('Error fetching messages:', error);
            toast.error('خطا در دریافت پیام‌ها');
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!response.trim()) return;

        setSending(true);
        try {
            await endpoints.admin.replyTicket(Number(id), response);
            toast.success('پاسخ با موفقیت ارسال شد');
            setResponse('');
            await fetchMessages();
        } catch (error) {
            console.error('Error sending reply:', error);
            toast.error('خطا در ارسال پاسخ');
        } finally {
            setSending(false);
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

    if (!ticket) {
        return null;
    }

    return (
        <AdminLayout>
            <div className="max-w-4xl mx-auto space-y-6">
                {/* Ticket Information */}
                <div className="bg-white rounded-lg shadow p-6">
                    <div className="flex justify-between items-start mb-4">
                        <div>
                            <h1 className="text-2xl font-bold text-gray-800">{ticket.subject}</h1>
                            <p className="text-sm text-gray-500">
                                کاربر: {ticket.user_id} | تاریخ: {new Date(ticket.created_at).toLocaleDateString('fa-IR')}
                            </p>
                        </div>
                        <span className={`px-2 py-1 rounded-full text-sm ${
                            ticket.status === 'open' 
                                ? 'bg-green-100 text-green-800'
                                : ticket.status === 'closed'
                                ? 'bg-gray-100 text-gray-800'
                                : 'bg-yellow-100 text-yellow-800'
                        }`}>
                            {ticket.status}
                        </span>
                    </div>
                    <p className="text-gray-700 whitespace-pre-wrap">{ticket.message}</p>
                    {ticket.file_path && (
                        <a 
                            href={ticket.file_path}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="mt-4 inline-flex items-center text-blue-600 hover:text-blue-800"
                        >
                            📎 دانلود فایل پیوست
                        </a>
                    )}
                </div>

                {/* Messages */}
                <div className="space-y-4">
                    {messages.map((message) => (
                        <div 
                            key={message.id}
                            className={`bg-white rounded-lg shadow p-4 ${
                                message.user_id === ticket.user_id
                                    ? 'mr-0 ml-12'
                                    : 'ml-0 mr-12 bg-blue-50'
                            }`}
                        >
                            <div className="flex justify-between items-start mb-2">
                                <span className="text-sm font-medium text-gray-900">
                                    {message.user_id === ticket.user_id ? 'کاربر' : 'پشتیبان'}
                                </span>
                                <span className="text-sm text-gray-500">
                                    {new Date(message.created_at).toLocaleString('fa-IR')}
                                </span>
                            </div>
                            <p className="text-gray-700 whitespace-pre-wrap">{message.message}</p>
                            {message.file_path && (
                                <a 
                                    href={message.file_path}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="mt-2 inline-flex items-center text-blue-600 hover:text-blue-800"
                                >
                                    📎 دانلود فایل پیوست
                                </a>
                            )}
                        </div>
                    ))}
                </div>

                {/* Reply Form */}
                {ticket.status !== 'closed' && (
                    <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow p-6">
                        <textarea
                            value={response}
                            onChange={(e) => setResponse(e.target.value)}
                            placeholder="پاسخ خود را بنویسید..."
                            className="w-full p-3 border rounded-lg h-32 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            disabled={sending}
                        />
                        <div className="mt-4 flex justify-end">
                            <button
                                type="submit"
                                disabled={sending || !response.trim()}
                                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
                            >
                                {sending ? 'در حال ارسال...' : 'ارسال پاسخ'}
                            </button>
                        </div>
                    </form>
                )}
            </div>
        </AdminLayout>
    );
} 