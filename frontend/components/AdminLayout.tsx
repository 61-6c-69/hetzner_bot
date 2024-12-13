import { ReactNode } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { FiHome, FiServer, FiUsers, FiDollarSign, FiMessageSquare, FiBell } from 'react-icons/fi';

interface AdminLayoutProps {
    children: ReactNode;
}

const AdminLayout = ({ children }: AdminLayoutProps) => {
    const router = useRouter();
    const currentPath = router.pathname;

    const menuItems = [
        { path: '/admin', label: 'داشبورد', icon: FiHome },
        { path: '/admin/servers', label: 'سرورها', icon: FiServer },
        { path: '/admin/users', label: 'کاربران', icon: FiUsers },
        { path: '/admin/transactions', label: 'تراکنش‌ها', icon: FiDollarSign },
        { path: '/admin/tickets', label: 'تیکت‌ها', icon: FiMessageSquare },
        { path: '/admin/notifications', label: 'اعلان‌ها', icon: FiBell },
    ];

    return (
        <div className="min-h-screen bg-gray-100 flex">
            {/* Sidebar */}
            <aside className="w-64 bg-white shadow-lg">
                <div className="p-4">
                    <h1 className="text-xl font-bold text-gray-800">پنل مدیریت</h1>
                </div>
                <nav className="mt-4">
                    {menuItems.map((item) => {
                        const Icon = item.icon;
                        const isActive = currentPath === item.path;
                        return (
                            <Link
                                key={item.path}
                                href={item.path}
                                className={`flex items-center px-4 py-3 text-sm ${
                                    isActive
                                        ? 'bg-blue-50 text-blue-600 border-r-4 border-blue-600'
                                        : 'text-gray-600 hover:bg-gray-50'
                                }`}
                            >
                                <Icon className="w-5 h-5 ml-3" />
                                {item.label}
                            </Link>
                        );
                    })}
                </nav>
            </aside>

            {/* Main Content */}
            <main className="flex-1 p-8">
                {children}
            </main>
        </div>
    );
};

export default AdminLayout;