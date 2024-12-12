import { useState } from 'react';
import AdminLayout from '@/components/AdminLayout';
import { useAuth } from '@/contexts/AuthContext';

export default function Notifications() {
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const { user } = useAuth();

  const sendNotification = async () => {
    if (!message.trim()) return;
    
    setLoading(true);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/admin/notifications`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${Cookies.get('token')}`
        },
        body: JSON.stringify({ message })
      });

      if (res.ok) {
        toast.success('اعلان با موفقیت ارسال شد');
        setMessage('');
      } else {
        toast.error('خطا در ارسال اعلان');
      }
    } catch (error) {
      toast.error('خطا در برقراری ارتباط');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AdminLayout>
      <div className="max-w-4xl mx-auto p-6">
        <h1 className="text-2xl font-bold mb-6">ارسال اعلان به کاربران</h1>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="space-y-4">
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="متن پیام..."
              className="w-full h-32 border p-2 rounded"
            />
            
            <button
              onClick={sendNotification}
              disabled={loading || !message.trim()}
              className="w-full bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'در حال ارسال...' : 'ارسال به همه کاربران'}
            </button>
          </div>
        </div>
      </div>
    </AdminLayout>
  );
} 