import { useEffect, useState } from 'react';
import { FiCheck, FiX } from 'react-icons/fi';
import { endpoints } from '@/services/api';
import { Transaction } from '@/types';
import AdminLayout from '@/components/AdminLayout';
import { toast } from 'react-toastify';

export default function AdminTransactions() {
    const [transactions, setTransactions] = useState<Transaction[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchTransactions();
    }, []);

    const fetchTransactions = async () => {
        try {
            const { data } = await endpoints.admin.listTransactions();
            setTransactions(data);
        } catch (error) {
            console.error('Error fetching transactions:', error);
            toast.error('خطا در دریافت لیست تراکنش‌ها');
        } finally {
            setLoading(false);
        }
    };

    const handleApprove = async (transactionId: number) => {
        try {
            await endpoints.admin.approveTransaction(transactionId);
            toast.success('تراکنش با موفقیت تایید شد');
            await fetchTransactions();
        } catch (error) {
            console.error('Error approving transaction:', error);
            toast.error('خطا در تایید تراکنش');
        }
    };

    const handleReject = async (transactionId: number) => {
        if (!confirm('آیا از رد این تراکنش اطمینان دارید؟')) return;
        
        try {
            await endpoints.admin.rejectTransaction(transactionId);
            toast.success('تراکنش با موفقیت رد شد');
            await fetchTransactions();
        } catch (error) {
            console.error('Error rejecting transaction:', error);
            toast.error('خطا در رد تراکنش');
        }
    };

    if (loading) {
        return (
            <AdminLayout>
                <div className="flex justify-center items-center h-full">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                </div>
            </AdminLayout>
        );
    }

    return (
        <AdminLayout>
            <div className="space-y-6">
                <div className="flex justify-between items-center">
                    <h1 className="text-2xl font-bold text-gray-800">مدیریت تراکنش‌ها</h1>
                    <div className="text-sm text-gray-600">
                        تعداد کل: {transactions.length}
                    </div>
                </div>

                <div className="bg-white rounded-lg shadow overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                                        شناسه تراکنش
                                    </th>
                                    <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                                        کاربر
                                    </th>
                                    <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                                        مبلغ
                                    </th>
                                    <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                                        نوع
                                    </th>
                                    <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                                        وضعیت
                                    </th>
                                    <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                                        تاریخ
                                    </th>
                                    <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                                        عملیات
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {transactions.map((transaction) => (
                                    <tr key={transaction.id} className="hover:bg-gray-50">
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="text-sm text-gray-900">
                                                {transaction.id}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="text-sm text-gray-500">
                                                {transaction.user_id}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="text-sm text-gray-900">
                                                {transaction.amount.toLocaleString()} تومان
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="text-sm text-gray-500">
                                                {transaction.type}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                                                transaction.status === 'completed'
                                                    ? 'bg-green-100 text-green-800'
                                                    : transaction.status === 'pending'
                                                    ? 'bg-yellow-100 text-yellow-800'
                                                    : 'bg-red-100 text-red-800'
                                            }`}>
                                                {transaction.status}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="text-sm text-gray-500">
                                                {new Date(transaction.created_at).toLocaleDateString('fa-IR')}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-left text-sm font-medium">
                                            {transaction.status === 'pending' && (
                                                <div className="flex space-x-2 space-x-reverse">
                                                    <button
                                                        onClick={() => handleApprove(transaction.id)}
                                                        className="text-green-600 hover:text-green-900"
                                                        title="تایید"
                                                    >
                                                        <FiCheck className="w-5 h-5" />
                                                    </button>
                                                    <button
                                                        onClick={() => handleReject(transaction.id)}
                                                        className="text-red-600 hover:text-red-900"
                                                        title="رد"
                                                    >
                                                        <FiX className="w-5 h-5" />
                                                    </button>
                                                </div>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </AdminLayout>
    );
}