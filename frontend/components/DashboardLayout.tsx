import { useAuth } from '@/hooks/useAuth';
import Link from 'next/link';
import { useRouter } from 'next/router';

export default function DashboardLayout({ children }) {
  const { logout } = useAuth();
  const router = useRouter();

  const menuItems = [
    { href: '/dashboard', label: 'داشبورد', icon: '🏠' },
    { href: '/dashboard/servers', label: 'سرورها', icon: '🖥' },
    { href: '/dashboard/buy-server', label: 'خرید سرور', icon: '🛒' },
    { href: '/dashboard/transactions', label: 'تراکنش‌ها', icon: '💰' },
    { href: '/dashboard/support', label: 'پشتیبانی', icon: '📞' },
  ];

  return (
    <div className="min-h-screen flex">
      {/* Sidebar */}
      <div className="w-64 bg-gray-800 text-white">
        <div className="p-4">
          <h1 className="text-xl font-bold">پنل کاربری</h1>
        </div>
        <nav className="mt-8">
          {menuItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center px-4 py-3 ${
                router.pathname === item.href
                  ? 'bg-gray-900 text-white'
                  : 'text-gray-300 hover:bg-gray-700'
              }`}
            >
              <span className="mr-3">{item.icon}</span>
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="absolute bottom-0 w-64 p-4">
          <button
            onClick={logout}
            className="w-full py-2 text-center text-gray-300 hover:text-white"
          >
            خروج 🚪
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 bg-gray-100">
        <div className="p-4">{children}</div>
      </div>
    </div>
  );
} 