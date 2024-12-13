import {useState} from 'react';
import {useRouter} from 'next/router';
import DashboardLayout from '@/components/DashboardLayout';
import {useMutation, useQuery} from 'react-query';
import {endpoints} from '@/services/api';
import {toast} from 'react-toastify';
import {FiPower, FiRotateCw, FiTrash2} from 'react-icons/fi';
import {Server} from '@/types';

function calculateUsageHours(lastChargeAt: string): number {
  const lastCharge = new Date(lastChargeAt);
  const now = new Date();
  return Math.floor((now.getTime() - lastCharge.getTime()) / (1000 * 60 * 60));
}

export default function ServerDetails() {
  const router = useRouter();
  const { id } = router.query;
  const [isConfirmingDelete, setIsConfirmingDelete] = useState(false);

  const { data: server, isLoading, refetch } = useQuery<Server>(
    ['server', id],
    async () => {
      const response = await endpoints.servers.get(Number(id));
      return response.data;
    },
    {
      enabled: !!id,
      refetchInterval: 30000, // Refetch every 30 seconds
    }
  );

  const powerMutation = useMutation(
    async (action: 'start' | 'stop' | 'restart') => {
      await endpoints.servers.action(Number(id), action);
    },
    {
      onSuccess: () => {
        toast.success('عملیات با موفقیت انجام شد');
        refetch();
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.message || 'خطا در انجام عملیات');
      },
    }
  );

  const deleteMutation = useMutation(
    async () => {
      await endpoints.servers.delete(Number(id));
    },
    {
      onSuccess: () => {
        toast.success('سرور با موفقیت حذف شد');
        router.push('/dashboard/servers');
      },
      onError: (error: any) => {
        toast.error(error.response?.data?.message || 'خطا در حذف سرور');
      },
    }
  );

  if (isLoading || !server) {
    return (
      <DashboardLayout>
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold">{server.name}</h1>
          <div className="flex space-x-4 space-x-reverse">
            <button
              onClick={() => powerMutation.mutate('start')}
              disabled={server.status === 'running'}
              className={`px-4 py-2 rounded-md flex items-center ${
                server.status === 'running'
                  ? 'bg-gray-300 cursor-not-allowed'
                  : 'bg-green-500 hover:bg-green-600 text-white'
              }`}
            >
              <FiPower className="ml-2" />
              روشن کردن
            </button>
            <button
              onClick={() => powerMutation.mutate('stop')}
              disabled={server.status === 'stopped'}
              className={`px-4 py-2 rounded-md flex items-center ${
                server.status === 'stopped'
                  ? 'bg-gray-300 cursor-not-allowed'
                  : 'bg-red-500 hover:bg-red-600 text-white'
              }`}
            >
              <FiPower className="ml-2" />
              خاموش کردن
            </button>
            <button
              onClick={() => powerMutation.mutate('restart')}
              disabled={server.status === 'stopped'}
              className="px-4 py-2 bg-yellow-500 hover:bg-yellow-600 text-white rounded-md flex items-center"
            >
              <FiRotateCw className="ml-2" />
              ریستارت
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="server-info">
            <h3 className="text-lg font-semibold mb-4">اطلاعات سرور</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">وضعیت:</span>
                <span className={`font-bold ${
                  server.status === 'running' ? 'text-green-500' : 'text-red-500'
                }`}>
                  {server.status === 'running' ? 'روشن' : 'خاموش'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">آی‌پی:</span>
                <span className="font-bold">{server.ip}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">نوع سرور:</span>
                <span className="font-bold">{server.type}</span>
              </div>
            </div>
          </div>

          <div className="server-specs">
            <h3 className="text-lg font-semibold mb-4">مشخصات سخت‌افزاری</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">پردازنده:</span>
                <span className="font-bold">{server.specifications.cores} هسته</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">حافظه:</span>
                <span className="font-bold">{server.specifications.memory} گیگابایت</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">هارد:</span>
                <span className="font-bold">
                  {server.specifications.disk} گیگابایت {server.specifications.disk_type}
                </span>
              </div>
            </div>
          </div>

          <div className="server-costs">
            <h3 className="text-lg font-semibold mb-4">هزینه‌های سرور</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">هزینه ساعتی:</span>
                <span className="font-bold">{server.hourly_price.toLocaleString()} تومان</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">هزینه ماهانه تقریبی:</span>
                <span className="font-bold">{server.monthly_price.toLocaleString()} تومان</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">کارکرد فعلی:</span>
                <span className="font-bold">
                  {calculateUsageHours(server.last_charge_at)} ساعت
                </span>
              </div>
            </div>
          </div>

          <div className="server-dates">
            <h3 className="text-lg font-semibold mb-4">تاریخ‌ها</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">تاریخ ایجاد:</span>
                <span className="font-bold">
                  {new Date(server.created_at).toLocaleDateString('fa-IR')}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">آخرین شارژ:</span>
                <span className="font-bold">
                  {new Date(server.last_charge_at).toLocaleDateString('fa-IR')}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-8 border-t pt-6">
          <h3 className="text-lg font-semibold text-red-600 mb-4">حذف سرور</h3>
          {!isConfirmingDelete ? (
            <button
              onClick={() => setIsConfirmingDelete(true)}
              className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-md flex items-center"
            >
              <FiTrash2 className="ml-2" />
              حذف سرور
            </button>
          ) : (
            <div className="space-y-4">
              <p className="text-red-600">آیا از حذف این سرور اطمینان دارید؟ این عمل غیرقابل بازگشت است.</p>
              <div className="flex space-x-4 space-x-reverse">
                <button
                  onClick={() => deleteMutation.mutate()}
                  className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-md"
                >
                  بله، حذف شود
                </button>
                <button
                  onClick={() => setIsConfirmingDelete(false)}
                  className="px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white rounded-md"
                >
                  انصراف
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
} 