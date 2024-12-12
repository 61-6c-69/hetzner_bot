import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import AdminLayout from '@/components/AdminLayout';
import { useAuth } from '@/hooks/useAuth';

export default function TicketDetail() {
    const router = useRouter();
    const { id } = router.query;
    const { token } = useAuth();
    const [ticket, setTicket] = useState(null);
    const [response, setResponse] = useState('');

    useEffect(() => {
        if (id) fetchTicket();
    }, [id]);

    const fetchTicket = async () => {
        const res = await fetch(`/api/support/tickets/${id}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        setTicket(data);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        await fetch(`/api/support/tickets/${id}/reply`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ response })
        });
        router.push('/admin/tickets');
    };

    if (!ticket) return <div>Loading...</div>;

    return (
        <AdminLayout>
            <div className="max-w-4xl mx-auto p-6">
                <div className="bg-white rounded-lg shadow p-6">
                    <h2 className="text-xl font-bold mb-4">جزئیات تیکت</h2>
                    <div className="mb-4">
                        <p className="text-gray-600">کاربر: {ticket.user.first_name}</p>
                        <p className="text-gray-600">تاریخ: {new Date(ticket.created_at).toLocaleDateString('fa-IR')}</p>
                        <p className="mt-4">{ticket.message}</p>
                        {ticket.file_path && (
                            <a 
                                href={ticket.file_path}
                                className="text-blue-600 hover:underline mt-2 block"
                            >
                                دانلود فایل پیوست
                            </a>
                        )}
                    </div>

                    <form onSubmit={handleSubmit} className="mt-8">
                        <textarea
                            value={response}
                            onChange={(e) => setResponse(e.target.value)}
                            placeholder="پاسخ خود را بنویسید..."
                            className="w-full p-2 border rounded-md h-32"
                            required
                        />
                        <button
                            type="submit"
                            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md"
                        >
                            ارسال پاسخ
                        </button>
                    </form>
                </div>
            </div>
        </AdminLayout>
    );
} 