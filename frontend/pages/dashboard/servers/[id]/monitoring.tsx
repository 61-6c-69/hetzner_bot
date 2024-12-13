import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import DashboardLayout from '@/components/DashboardLayout';
import { endpoints } from '@/services/api';
import { Server, ServerStats } from '@/types';
import { toast } from 'react-toastify';
import LoadingSpinner from '@/components/LoadingSpinner';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
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
        }
    },
    scales: {
        y: {
            beginAtZero: true,
            max: 100,
            ticks: {
                callback: (value: number) => `${value}%`
            }
        }
    }
};

export default function ServerMonitoring() {
    const router = useRouter();
    const { id } = router.query;
    const [server, setServer] = useState<Server | null>(null);
    const [stats, setStats] = useState<ServerStats | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        if (id) {
            fetchServerData();
            const interval = setInterval(fetchServerData, 30000); // Refresh every 30 seconds
            return () => clearInterval(interval);
        }
    }, [id]);

    const fetchServerData = async () => {
        try {
            // Fetch server details and stats in parallel
            const [serverRes, statsRes] = await Promise.all([
                endpoints.servers.get(Number(id)),
                endpoints.servers.stats(Number(id))
            ]);

            setServer(serverRes.data);
            setStats(statsRes.data);
            setError('');
        } catch (error: any) {
            setError(error.response?.data?.detail || 'خطا در دریافت اطلاعات سرور');
            toast.error(error.response?.data?.detail || 'خطا در دریافت اطلاعات سرور');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <DashboardLayout>
                <div className="flex justify-center items-center h-64">
                    <LoadingSpinner />
                </div>
            </DashboardLayout>
        );
    }

    if (error || !server || !stats) {
        return (
            <DashboardLayout>
                <div className="max-w-4xl mx-auto p-6">
                    <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                        {error || 'خطا در دریافت اطلاعات سرور'}
                    </div>
                </div>
            </DashboardLayout>
        );
    }

    // Prepare chart data
    const timestamps = stats.cpu.map(point => 
        new Date(point.timestamp).toLocaleTimeString('fa-IR')
    );

    const chartData = {
        labels: timestamps,
        datasets: [
            {
                label: 'CPU',
                data: stats.cpu.map(point => point.value),
                borderColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgba(255, 99, 132, 0.5)',
            },
            {
                label: 'RAM',
                data: stats.memory.map(point => point.value),
                borderColor: 'rgb(53, 162, 235)',
                backgroundColor: 'rgba(53, 162, 235, 0.5)',
            },
            {
                label: 'Disk',
                data: stats.disk.map(point => point.value),
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.5)',
            },
        ],
    };

    const networkData = {
        labels: timestamps,
        datasets: [
            {
                label: 'ورودی',
                data: stats.network.map(point => point.in / 1024 / 1024), // Convert to MB
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.5)',
            },
            {
                label: 'خروجی',
                data: stats.network.map(point => point.out / 1024 / 1024), // Convert to MB
                borderColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgba(255, 99, 132, 0.5)',
            },
        ],
    };

    return (
        <DashboardLayout>
            <div className="max-w-6xl mx-auto p-6">
                <div className="flex justify-between items-center mb-6">
                    <h1 className="text-2xl font-bold">مانیتورینگ سرور {server.name}</h1>
                    <span className={`px-3 py-1 rounded-full text-sm ${
                        server.status === 'running'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                    }`}>
                        {server.status === 'running' ? 'فعال' : 'غیرفعال'}
                    </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Resource Usage Chart */}
                    <div className="bg-white rounded-lg shadow p-6">
                        <h2 className="text-lg font-semibold mb-4">مصرف منابع</h2>
                        <Line options={chartOptions} data={chartData} />
                    </div>

                    {/* Network Usage Chart */}
                    <div className="bg-white rounded-lg shadow p-6">
                        <h2 className="text-lg font-semibold mb-4">مصرف شبکه (MB/s)</h2>
                        <Line
                            options={{
                                ...chartOptions,
                                scales: {
                                    y: {
                                        beginAtZero: true,
                                        ticks: {
                                            callback: (value: number) => `${value.toFixed(2)} MB/s`
                                        }
                                    }
                                }
                            }}
                            data={networkData}
                        />
                    </div>

                    {/* Server Info */}
                    <div className="bg-white rounded-lg shadow p-6">
                        <h2 className="text-lg font-semibold mb-4">اطلاعات سرور</h2>
                        <div className="space-y-2">
                            <div className="flex justify-between">
                                <span className="text-gray-600">نام:</span>
                                <span className="font-medium">{server.name}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">IP:</span>
                                <span className="font-medium">{server.ip}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">نوع:</span>
                                <span className="font-medium">{server.type}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">سیستم عامل:</span>
                                <span className="font-medium">{server.os}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600">موقعیت:</span>
                                <span className="font-medium">{server.location}</span>
                            </div>
                        </div>
                    </div>

                    {/* Current Usage */}
                    <div className="bg-white rounded-lg shadow p-6">
                        <h2 className="text-lg font-semibold mb-4">وضعیت فعلی</h2>
                        <div className="space-y-4">
                            <div>
                                <div className="flex justify-between mb-1">
                                    <span>CPU</span>
                                    <span>{stats.cpu[stats.cpu.length - 1]?.value.toFixed(1)}%</span>
                                </div>
                                <div className="w-full bg-gray-200 rounded-full h-2">
                                    <div
                                        className="bg-blue-600 h-2 rounded-full"
                                        style={{ width: `${stats.cpu[stats.cpu.length - 1]?.value}%` }}
                                    />
                                </div>
                            </div>
                            <div>
                                <div className="flex justify-between mb-1">
                                    <span>RAM</span>
                                    <span>{stats.memory[stats.memory.length - 1]?.value.toFixed(1)}%</span>
                                </div>
                                <div className="w-full bg-gray-200 rounded-full h-2">
                                    <div
                                        className="bg-green-600 h-2 rounded-full"
                                        style={{ width: `${stats.memory[stats.memory.length - 1]?.value}%` }}
                                    />
                                </div>
                            </div>
                            <div>
                                <div className="flex justify-between mb-1">
                                    <span>Disk</span>
                                    <span>{stats.disk[stats.disk.length - 1]?.value.toFixed(1)}%</span>
                                </div>
                                <div className="w-full bg-gray-200 rounded-full h-2">
                                    <div
                                        className="bg-yellow-600 h-2 rounded-full"
                                        style={{ width: `${stats.disk[stats.disk.length - 1]?.value}%` }}
                                    />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
} 