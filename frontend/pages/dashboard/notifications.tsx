import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import DashboardLayout from '@/components/DashboardLayout';
import { toast } from 'react-toastify';
import Cookies from 'js-cookie';

export default function NotificationSettings() {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [settings, setSettings] = useState({
    server_notifications: true,  // اعلان‌های مربوط به سرور
    payment_notifications: true, // اعلان‌های پرداخت
    ticket_notifications: true,  // اعلان‌های تیکت
    low_balance_threshold: 50000 // حد اعلان موجودی کم
  });

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/user/notification-settings`, {
        headers: {
          'Authorization': `Bearer ${Cookies.get('token')}`
        }
      });
      if (res.ok) {
        const data = await res.json();
        setSettings(data);
      }
    } catch (error) {
      toast.error('خطا در دریافت تنظیمات');
    } finally {
      setLoading(false);
    }
  };

  const saveSettings = async () => {
    setSaving(true);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/user/notification-settings`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${Cookies.get('token')}`
        },
        body: JSON.stringify(settings)
      });

      if (res.ok) {
        toast.success('تنظیمات با موفقیت ذخیره شد');
      } else {
        toast.error('خطا در ذخیره تنظیمات');
      }
    } catch (error) {
      toast.error('خطا در برقراری ارتباط');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div>در حال بارگذاری...</div>;
  }

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto p-6">
        <h1 className="text-2xl font-bold mb-6">تنظیمات اعلان‌ها</h1>

        <div className="bg-white p-6 rounded-lg shadow space-y-6">
          {!user?.telegram_id && (
            <div className="bg-yellow-50 border border-yellow-200 text-yellow-700 p-4 rounded">
              ⚠️ برای دریافت اعلان‌ها، ابتدا باید تلگرام خود را متصل کنید.
            </div>
          )}

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <label className="text-gray-700">اعلان‌های سرور</label>
              <input
                type="checkbox"
                checked={settings.server_notifications}
                onChange={(e) => setSettings({...settings, server_notifications: e.target.checked})}
                className="toggle"
              />
            </div>

            <div className="flex items-center justify-between">
              <label className="text-gray-700">اعلان‌های پرداخت</label>
              <input
                type="checkbox"
                checked={settings.payment_notifications}
                onChange={(e) => setSettings({...settings, payment_notifications: e.target.checked})}
                className="toggle"
              />
            </div>

            <div className="flex items-center justify-between">
              <label className="text-gray-700">اعلان‌های تیکت</label>
              <input
                type="checkbox"
                checked={settings.ticket_notifications}
                onChange={(e) => setSettings({...settings, ticket_notifications: e.target.checked})}
                className="toggle"
              />
            </div>

            <div className="space-y-2">
              <label className="block text-gray-700">حد اعلان موجودی کم (تومان)</label>
              <input
                type="number"
                value={settings.low_balance_threshold}
                onChange={(e) => setSettings({...settings, low_balance_threshold: parseInt(e.target.value)})}
                className="border p-2 rounded w-full"
                min="0"
                step="10000"
              />
            </div>
          </div>

          <button
            onClick={saveSettings}
            disabled={saving || !user?.telegram_id}
            className="w-full bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {saving ? 'در حال ذخیره...' : 'ذخیره تنظیمات'}
          </button>
        </div>
      </div>
    </DashboardLayout>
  );
} 