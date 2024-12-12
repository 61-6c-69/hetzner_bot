import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import DashboardLayout from '@/components/DashboardLayout';
import { toast } from 'react-toastify';
import Cookies from 'js-cookie';

export default function Profile() {
  const { user, refreshUser } = useAuth();
  const [disconnecting, setDisconnecting] = useState(false);
  
  const getTelegramLink = () => {
    const linkCode = `${user.id}_${Math.random().toString(36).substr(2, 9)}`;
    return `https://t.me/YourBotName?start=${linkCode}`;
  };

  const disconnectTelegram = async () => {
    if (!confirm('آیا از قطع اتصال تلگرام مطمئن هستید؟')) return;
    
    setDisconnecting(true);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/user/telegram-disconnect`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${Cookies.get('token')}`
        }
      });

      if (res.ok) {
        toast.success('اتصال تلگرام با موفقیت قطع شد');
        await refreshUser();  // به‌روزرسانی اطلاعات کاربر
      } else {
        toast.error('خطا در قطع اتصال');
      }
    } catch (error) {
      toast.error('خطا در برقراری ارتباط');
    } finally {
      setDisconnecting(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto p-6">
        <h1 className="text-2xl font-bold mb-6">تنظیمات پروفایل</h1>

        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">اتصال به تلگرام</h2>
          
          {user?.telegram_id ? (
            <div className="space-y-4">
              <div className="text-green-600">
                ✓ اکانت تلگرام شما متصل است
              </div>
              <button
                onClick={disconnectTelegram}
                disabled={disconnecting}
                className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 disabled:opacity-50"
              >
                {disconnecting ? 'در حال قطع اتصال...' : 'قطع اتصال تلگرام'}
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              <p className="text-gray-600">
                برای اتصال حساب تلگرام خود، روی دکمه زیر کلیک کنید:
              </p>
              
              <a 
                href={getTelegramLink()}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-block bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
              >
                اتصال به تلگرام
              </a>
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
} 