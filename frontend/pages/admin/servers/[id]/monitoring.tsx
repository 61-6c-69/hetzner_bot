import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { endpoints } from '@/services/api';
import { Server, ServerStats } from '@/types';
import AdminLayout from '@/components/AdminLayout';
import { toast } from 'react-toastify';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    ChartData
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
);

const chartOptions = {
    responsive: true,
    plugins: {
        legend: {
            position: 'top' as const,
        },
    },
    scales: {
        y: {
            beginAtZero: true,
            max: 100,
        },
    },
};

export default function ServerMonitoring() {
    const router = useRouter();
    const { id } = router.query;
    const [server, setServer] = useState<Server | null>(null);
    const [stats, setStats] = useState<ServerStats | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (id) {
            fetchServerInfo();
            const interval = setInterval(fetchStats, 30000); // Refresh every 30 seconds
            return () => clearInterval(interval);
        }
    }, [id]);

    const fetchServerInfo = async () => {
        try {
            const { data } = await endpoints.admin.listServers();
            const foundServer = data.find((s: Server) => s.id === Number(id));
            if (foundServer) {
                setServer(foundServer);
                await fetchStats();
            } else {
                setError('سرور مورد نظر یافت نشد');
                router.push('/admin/servers');
            }
        } catch (error) {
            console.error('Error fetching server:', error);
            setError('خطا در دریافت اطلاعات سرور');
        }
    };

    const fetchStats = async () => {
        try {
            const { data } = await endpoints.admin.getServerStats(Number(id));
            setStats(data);
        } catch (error) {
            console.error('Error fetching stats:', error);
            toast.error('خطا در دریافت آمار سرور');
        } finally {
            setLoading(false);
        }
    };

    const prepareChartData = (data: number[], labels: string[]): ChartData<'line'> => ({
        labels,
        datasets: [
            {
                label: 'درصد مصرف',
                data,
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.5)',
                tension: 0.1,
            },
        ],
    });

    if (loading) {
        return (
            <AdminLayout>
                <div className="flex justify-center items-center h-full">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                </div>
            </AdminLayout>
        );
    }

    if (error || !server || !stats) {
        return (
            <AdminLayout>
                <div className="text-center text-red-600">
                    {error || 'خطا در بارگذاری اطلاعات'}
                </div>
            </AdminLayout>
        );
    }

    return (
        <AdminLayout>
            <div className="max-w-7xl mx-auto space-y-6">
                {/* Server Info */}
                <div className="bg-white rounded-lg shadow p-6">
                    <h1 className="text-2xl font-bold text-gray-800 mb-4">
                        مانیتورینگ سرور: {server.name}
                    </h1>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="p-4 bg-gray-50 rounded-lg">
                            <div className="text-sm text-gray-600">IP</div>
                            <div className="text-lg font-medium">{server.ip}</div>
                        </div>
                        <div className="p-4 bg-gray-50 rounded-lg">
                            <div className="text-sm text-gray-600">نوع</div>
                            <div className="text-lg font-medium">{server.type}</div>
                        </div>
                        <div className="p-4 bg-gray-50 rounded-lg">
                            <div className="text-sm text-gray-600">وضعیت</div>
                            <div className={`text-lg font-medium ${
                                server.status === 'running' ? 'text-green-600' : 'text-red-600'
                            }`}>
                                {server.status}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Charts */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* CPU Usage */}
                    <div className="bg-white rounded-lg shadow p-6">
                        <h2 className="text-lg font-semibold text-gray-800 mb-4">CPU</h2>
                        <Line 
                            options={{
                                ...chartOptions,
                                plugins: {
                                    ...chartOptions.plugins,
                                    title: {
                                        display: true,
                                        text: 'درصد مصرف CPU'
                                    }
                                }
                            }}
                            data={prepareChartData(
                                stats.cpu.map(point => point.value),
                                stats.cpu.map(point => new Date(point.timestamp).toLocaleTimeString('fa-IR'))
                            )}
                        />
                    </div>

                    {/* Memory Usage */}
                    <div className="bg-white rounded-lg shadow p-6">
                        <h2 className="text-lg font-semibold text-gray-800 mb-4">حافظه</h2>
                        <Line 
                            options={{
                                ...chartOptions,
                                plugins: {
                                    ...chartOptions.plugins,
                                    title: {
                                        display: true,
                                        text: 'درصد مصرف حافظه'
                                    }
                                }
                            }}
                            data={prepareChartData(
                                stats.memory.map(point => point.value),
                                stats.memory.map(point => new Date(point.timestamp).toLocaleTimeString('fa-IR'))
                            )}
                        />
                    </div>

                    {/* Disk Usage */}
                    <div className="bg-white rounded-lg shadow p-6">
                        <h2 className="text-lg font-semibold text-gray-800 mb-4">دیسک</h2>
                        <Line 
                            options={{
                                ...chartOptions,
                                plugins: {
                                    ...chartOptions.plugins,
                                    title: {
                                        display: true,
                                        text: 'درصد مصرف دیسک'
                                    }
                                }
                            }}
                            data={prepareChartData(
                                stats.disk.map(point => point.value),
                                stats.disk.map(point => new Date(point.timestamp).toLocaleTimeString('fa-IR'))
                            )}
                        />
                    </div>

                    {/* Network Usage */}
                    <div className="bg-white rounded-lg shadow p-6">
                        <h2 className="text-lg font-semibold text-gray-800 mb-4">شبکه</h2>
                        <Line 
                            options={{
                                ...chartOptions,
                                scales: {
                                    y: {
                                        beginAtZero: true,
                                    },
                                },
                                plugins: {
                                    ...chartOptions.plugins,
                                    title: {
                                        display: true,
                                        text: 'مصرف شبکه (MB/s)'
                                    }
                                }
                            }}
                            data={{
                                labels: stats.network.map(point => 
                                    new Date(point.timestamp).toLocaleTimeString('fa-IR')
                                ),
                                datasets: [
                                    {
                                        label: 'ورودی',
                                        data: stats.network.map(point => point.in / 1024 / 1024), // Convert to MB
                                        borderColor: 'rgb(75, 192, 192)',
                                        backgroundColor: 'rgba(75, 192, 192, 0.5)',
                                        tension: 0.1,
                                    },
                                    {
                                        label: 'خروجی',
                                        data: stats.network.map(point => point.out / 1024 / 1024), // Convert to MB
                                        borderColor: 'rgb(255, 99, 132)',
                                        backgroundColor: 'rgba(255, 99, 132, 0.5)',
                                        tension: 0.1,
                                    }
                                ]
                            }}
                        />
                    </div>
                </div>
            </div>
        </AdminLayout>
    );
} 