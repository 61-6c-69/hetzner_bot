import { useState, useEffect } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import { useAuth } from '@/hooks/useAuth';

interface Ticket {
  id: number;
  message: string;
  response?: string;
  status: 'open' | 'closed';
  created_at: string;
}

export default function Support() {
  const { token } = useAuth();
  const [message, setMessage] = useState('');
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [file, setFile] = useState<File | null>(null);

  useEffect(() => {
    fetchTickets();
  }, []);

  const fetchTickets = async () => {
    try {
      const response = await fetch('/api/support/tickets', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const data = await response.json();
      setTickets(data);
    } catch (error) {
      console.error('Failed to fetch tickets:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('message', message);
    if (file) formData.append('file', file);

    try {
      await fetch('/api/support/tickets', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });
      setMessage('');
      setFile(null);
      fetchTickets();
    } catch (error) {
      console.error('Failed to create ticket:', error);
    }
  };

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto p-6">
        <h1 className="text-2xl font-bold mb-8">پشتیبانی</h1>

        {/* ارسال تیکت جدید */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-bold mb-4">تیکت جدید</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="پیام خود را بنویسید..."
              className="w-full p-2 border rounded-md h-32"
              required
            />
            <input
              type="file"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            />
            <button
              type="submit"
              className="w-full py-2 bg-blue-600 text-white rounded-md"
            >
              ارسال تیکت
            </button>
          </form>
        </div>

        {/* لیست تیکت‌ها */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="p-4 border-b">
            <h2 className="text-xl font-bold">تیکت‌های قبلی</h2>
          </div>
          <div className="divide-y">
            {tickets.map((ticket) => (
              <div key={ticket.id} className="p-4">
                <div className="flex justify-between items-start mb-2">
                  <span className="text-sm text-gray-500">
                    {new Date(ticket.created_at).toLocaleDateString('fa-IR')}
                  </span>
                  <span className={`px-2 py-1 rounded-full text-xs ${
                    ticket.status === 'open' 
                      ? 'bg-green-100 text-green-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    {ticket.status === 'open' ? 'باز' : 'بسته شده'}
                  </span>
                </div>
                <p className="text-gray-700">{ticket.message}</p>
                {ticket.response && (
                  <div className="mt-4 mr-4 p-4 bg-gray-50 rounded-md">
                    <p className="text-sm text-gray-500">پاسخ پشتیبانی:</p>
                    <p className="mt-1">{ticket.response}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
} 