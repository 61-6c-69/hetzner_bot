import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import DashboardLayout from '@/components/DashboardLayout';
import { useAuth } from '@/hooks/useAuth';
import { Line } from 'react-chartjs-2';

interface Log {
  id: number;
  timestamp: string;
  level: 'info' | 'warning' | 'error';
  message: string;
}

export default function ServerMonitoring() {
  const { token } = useAuth();
  const router = useRouter();
  const { id } = router.query;
  
  const [stats, setStats] = useState({
    cpu: [],
    memory: [],
    disk: [],
    network: []
  });

  const [logs, setLogs] = useState<Log[]>([]);
  const [timeRange, setTimeRange] = useState('24h');

  useEffect(() => {
    if (id) {
      fetchStats();
      fetchLogs();
      // هر 30 ثانیه آمار به‌روز شود
      const interval = setInterval(fetchStats, 30000);
      return () => clearInterval(interval);
    }
  }, [id, timeRange]);

  const fetchStats = async () => {
    try {
      const response = await fetch(`/api/servers/${id}/stats?range=${timeRange}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const fetchLogs = async () => {
    try {
      const response = await fetch(`/api/servers/${id}/logs`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setLogs(data);
    } catch (error) {
      console.error('Failed to fetch logs:', error);
    }
  };

  return (
    <DashboardLayout>
      <div className="p-6">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-2xl font-bold">مانیتورینگ سرور</h1>
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="px-4 py-2 border rounded-md"
          >
            <option value="1h">1 ساعت گذشته</option>
            <option value="24h">24 ساعت گذشته</option>
            <option value="7d">7 روز گذشته</option>
            <option value="30d">30 روز گذشته</option>
          </select>
        </div>

        {/* نمودارها */}
        <div className="grid grid-cols-2 gap-6 mb-8">
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">CPU</h3>
            <Line data={stats.cpu} options={{ responsive: true }} />
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">Memory</h3>
            <Line data={stats.memory} options={{ responsive: true }} />
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">Disk</h3>
            <Line data={stats.disk} options={{ responsive: true }} />
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">Network</h3>
            <Line data={stats.network} options={{ responsive: true }} />
          </div>
        </div>

        {/* لاگ‌ها */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-4 border-b">
            <h2 className="text-xl font-bold">لاگ‌های سیستم</h2>
          </div>
          <div className="p-4">
            <div className="space-y-2">
              {logs.map((log) => (
                <div
                  key={log.id}
                  className={`p-2 rounded ${
                    log.level === 'error'
                      ? 'bg-red-50 text-red-700'
                      : log.level === 'warning'
                      ? 'bg-yellow-50 text-yellow-700'
                      : 'bg-gray-50 text-gray-700'
                  }`}
                >
                  <div className="flex justify-between">
                    <span className="text-sm font-medium">
                      {new Date(log.timestamp).toLocaleString('fa-IR')}
                    </span>
                    <span className="text-sm">{log.level}</span>
                  </div>
                  <p className="mt-1">{log.message}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
} 