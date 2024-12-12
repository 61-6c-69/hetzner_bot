import { useEffect, useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import DashboardLayout from '@/components/DashboardLayout';
import ServerCard from '@/components/ServerCard';
import { Server } from '@/types';

export default function Dashboard() {
  const { token } = useAuth();
  const [servers, setServers] = useState<Server[]>([]);
  const [balance, setBalance] = useState(0);
  const [stats, setStats] = useState({
    total_servers: 0,
    active_servers: 0,
    total_spent: 0
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      // دریافت همزمان اطلاعات
      const [serversRes, balanceRes, statsRes] = await Promise.all([
        fetch('/api/servers', {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch('/api/payments/balance', {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch('/api/dashboard/stats', {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ]);

      const [serversData, balanceData, statsData] = await Promise.all([
        serversRes.json(),
        balanceRes.json(),
        statsRes.json()
      ]);

      setServers(serversData);
      setBalance(balanceData.balance);
      setStats(statsData);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    }
  };

  return (
    <DashboardLayout>
      <div className="p-6">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-gray-500 text-sm">موجودی</h3>
            <p className="text-2xl font-bold">{balance.toLocaleString()} تومان</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-gray-500 text-sm">تعداد کل سرورها</h3>
            <p className="text-2xl font-bold">{stats.total_servers}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-gray-500 text-sm">سرورهای فعال</h3>
            <p className="text-2xl font-bold">{stats.active_servers}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-gray-500 text-sm">هزینه کل</h3>
            <p className="text-2xl font-bold">{stats.total_spent.toLocaleString()} تومان</p>
          </div>
        </div>

        {/* Servers List */}
        <h2 className="text-xl font-bold mb-4">سرورهای شما</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {servers.map(server => (
            <ServerCard key={server.id} server={server} onUpdate={fetchData} />
          ))}
        </div>
      </div>
    </DashboardLayout>
  );
} 