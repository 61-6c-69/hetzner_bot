import { useAuth } from '@/contexts/AuthContext';
import Link from 'next/link';

export default function Sidebar() {
  const { isAdmin } = useAuth();

  return (
    <nav>
      {/* منوهای عادی */}
      <Link href="/dashboard">داشبورد</Link>
      <Link href="/dashboard/servers">سرورها</Link>
      <Link href="/dashboard/notifications">تنظیمات اعلان‌ها</Link>
      
      {/* منوهای ادمین */}
      {isAdmin() && (
        <>
          <Link href="/admin/tickets">تیکت‌های کاربران</Link>
          <Link href="/admin/users">مدیریت کاربران</Link>
          <Link href="/admin/notifications">ارسال اعلان</Link>
        </>
      )}
    </nav>
  );
} 